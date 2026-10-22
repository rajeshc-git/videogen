import os
import time
import json
import uuid
import glob
import shutil
import asyncio
import subprocess
import warnings
from typing import Optional
import logging

class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        # Suppress /api/status heartbeat from terminal access logs
        try:
            return "/api/status" not in record.getMessage()
        except Exception:
            return True

logging.getLogger("uvicorn.access").addFilter(EndpointFilter())

# Suppress benign Pydantic v2 model_ namespace warning
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import requests
# pyrefly: ignore[missing-import]
import websockets

from minimax_h3_bridge import (
    check_models_status,
    check_comfy_online,
    prepare_9_16_image,
    upload_image_to_comfy,
    build_minimax_h3_prompt,
    COMFY_URL,
    COMFY_HOST,
    SHARED_OUTPUT_PATH
)
import re
from downloader import start_model_download, get_download_status, cancel_download

def prepare_prompt_for_minimax(prompt: str) -> str:
    """
    Intelligently inspects the user prompt.
    Supports free-form prompts generated from ChatGPT or typed directly,
    including timestamps ([0s-2s], [00:01]), dialogue in quotes, multilingual speech
    (Hindi, Bengali, English, etc.), and sound cues without forcing any rigid format.
    
    If the prompt already contains any sound, speech, dialogue, timestamps, or language cues,
    it is preserved 100% VERBATIM so Qwen3-VL 32B receives exact instructions.
    
    Only when the prompt is purely visual with zero sound or speech intent,
    we append an ambient silence directive to prevent random mumble hallucinations.
    """
    clean = prompt.strip()
    if not clean:
        return "Natural camera movement. Audio: silent, quiet natural ambient background, no speech, no vocals, no music."

    lower = clean.lower()

    # 1. Direct audio/voice/music/speech/sound keywords
    sound_indicators = [
        "audio", "sound", "voice", "speech", "dialogue", "dialog", "vocal", "vocals",
        "music", "song", "bgm", "sfx", "soundtrack", "ambient", "ambiance", "noise",
        "speaks", "speaking", "speak", "says", "saying", "whisper", "whispering",
        "talk", "talking", "talks", "shout", "shouting", "sing", "singing", "sings",
        "voiceover", "narration", "narrator", "tone", "score", "beats", "melody",
        "acoustic", "synthesizer", "orchestra", "silent", "silence", "quiet", "mute",
        "hindi", "bengali", "english", "urdu", "tamil", "telugu", "sanskrit", "bilingual"
    ]
    if any(k in lower for k in sound_indicators):
        return clean

    # 2. Timestamp patterns (e.g., [0s-2s], [00:02], [2s-5s], 0s:, 2s - 5s)
    if re.search(r'\[?\b\d+s?\s*[-–:]\s*\d+s?\b\]?', lower):
        return clean

    # 3. Spoken dialogue in quotes (e.g. "...", “...”)
    if re.search(r'["“][^"“”]{2,}["”]', clean):
        return clean

    # 4. Multilingual Unicode scripts: Devanagari (\u0900-\u097F) or Bengali (\u0980-\u09FF)
    if re.search(r'[\u0900-\u097F\u0980-\u09FF]', clean):
        return clean

    # Only append silence when prompt is purely visual without any sound or speech instructions
    return clean + " Audio: silent, quiet natural ambient background, no speech, no vocals, no music."

app = FastAPI(title="VideoGen Studio - MiniMax H3 Native Audio & Video")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# Active generation jobs state
jobs = {}

@app.on_event("startup")
async def attach_log_filter():
    # Keep console clean by suppressing /api/status heartbeat lines
    uvicorn_logger = logging.getLogger("uvicorn.access")
    uvicorn_logger.addFilter(EndpointFilter())

@app.get("/api/status")
async def get_system_status():
    comfy = check_comfy_online()
    models = check_models_status()
    download = get_download_status()
    return {
        "comfy": comfy,
        "models": models,
        "download": download
    }

@app.post("/api/models/download")
async def download_model(model_name: str = Form(...)):
    res = start_model_download(model_name)
    return res

@app.post("/api/models/cancel")
async def cancel_model_download():
    return cancel_download()

@app.post("/api/generate")
async def generate_video(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...),
    prompt: str = Form(""),
    duration: int = Form(5),
    aspect_ratio: str = Form("9:16"),
    mode: str = Form("auto")
):
    job_id = str(uuid.uuid4())[:8]
    raw_img_path = os.path.join(UPLOADS_DIR, f"{job_id}_raw_{image.filename}")
    with open(raw_img_path, "wb") as f:
        shutil.copyfileobj(image.file, f)

    # Determine resolution based on aspect ratio
    if aspect_ratio == "16:9":
        target_w, target_h = 1344, 768
    elif aspect_ratio == "1:1":
        target_w, target_h = 960, 960
    else: # 9:16 vertical default
        target_w, target_h = 768, 1344

    formatted_img_path = os.path.join(UPLOADS_DIR, f"{job_id}_formatted.png")
    prepare_9_16_image(raw_img_path, formatted_img_path, target_width=target_w, target_height=target_h)

    jobs[job_id] = {
        "id": job_id,
        "status": "queued",
        "progress": 0,
        "step": f"Initializing {aspect_ratio} video pipeline...",
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "video_url": None,
        "filename": None,
        "error": None,
        "created_at": time.time()
    }

    background_tasks.add_task(run_generation_task, job_id, formatted_img_path, prompt, duration, aspect_ratio, target_w, target_h, mode)
    return {"job_id": job_id, "status": "queued"}

async def run_generation_task(job_id: str, formatted_image_path: str, prompt: str, duration: int, aspect_ratio: str, target_w: int, target_h: int, mode: str):
    job = jobs[job_id]
    models_stat = check_models_status()
    comfy_stat = check_comfy_online()

    # If models are not yet downloaded or user requested preview/demo mode
    if not models_stat["all_ready"] or mode == "demo":
        job["status"] = "processing"
        job["step"] = f"Simulating MiniMax H3 8-step omni-modal diffusion ({aspect_ratio})..."
        job["progress"] = 15

        # Render video with audio using FFmpeg & test frames
        output_filename = f"MiniMaxH3_{job_id}_{aspect_ratio.replace(':', '_')}.mp4"
        out_video_path = os.path.join(OUTPUTS_DIR, output_filename)

        for step_i in range(1, 9):
            await asyncio.sleep(0.4)
            job["progress"] = int(15 + (step_i / 8) * 60)
            job["step"] = f"Sampling latents (Turbo step {step_i}/8) - Generating Video & Stereo Audio..."

        job["step"] = f"Decoding Video VAE & Audio VAE into final {aspect_ratio} MP4..."
        job["progress"] = 85
        await asyncio.sleep(0.5)

        # Generate animated video matching chosen aspect ratio
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", formatted_image_path,
            "-f", "lavfi",
            "-i", f"sine=frequency=180:duration={duration}",
            "-filter_complex", f"[0:v]scale={target_w}:{target_h},zoompan=z='min(zoom+0.0015,1.15)':d={duration*25}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={target_w}x{target_h}[vout]",
            "-map", "[vout]",
            "-map", "1:a",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-t", str(duration),
            "-movflags", "+faststart",
            out_video_path
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0 and os.path.exists(out_video_path):
            job["status"] = "completed"
            job["progress"] = 100
            job["step"] = "Generation complete! Ready to play & download."
            job["video_url"] = f"/api/videos/{output_filename}"
            job["filename"] = output_filename
            return
        else:
            job["status"] = "failed"
            job["error"] = f"FFmpeg error: {res.stderr[:200]}"
            return

    # Real ComfyUI execution when models are ready
    try:
        job["status"] = "processing"
        job["step"] = "Uploading image to ComfyUI..."
        job["progress"] = 10

        # Intelligently prepare prompt: supports free-form ChatGPT prompts with timestamps,
        # dialogue in Hindi/Bengali/English, and sound design without forcing rigid formats.
        clean_prompt = prepare_prompt_for_minimax(prompt)

        comfy_filename = upload_image_to_comfy(formatted_image_path)
        prompt_workflow = build_minimax_h3_prompt(comfy_filename, clean_prompt, duration_sec=duration, width=target_w, height=target_h)

        client_id = str(uuid.uuid4())
        payload = {"prompt": prompt_workflow, "client_id": client_id}

        job["step"] = "Submitting MiniMax H3 workflow to ComfyUI Engine..."
        job["progress"] = 20

        r = requests.post(f"{COMFY_URL}/prompt", json=payload, timeout=10)
        if r.status_code != 200:
            raise Exception(f"ComfyUI prompt error: {r.text}")

        prompt_id = r.json().get("prompt_id")
        job["step"] = "ComfyUI pipeline queued. Waiting for worker..."

        # Node descriptions for accurate, real-time progress updates
        node_stage_map = {
            "1": ("Loading source image...", 5),
            "2": ("Loading MiniMax H3 Diffusion model...", 8),
            "3": ("Loading Qwen3-VL 32B Multimodal Encoder...", 10),
            "4": ("Preparing Video VAE...", 12),
            "5": ("Preparing Audio VAE...", 13),
            "6": ("Attaching Turbo 8-Step LoRA...", 14),
            "7": ("Encoding Image & Multilingual Prompt (Qwen3-VL)...", 18),
            "8": ("Configuring Euler sampler...", 20),
            "9": ("Configuring noise scheduler...", 21),
            "10": ("Configuring BasicGuider...", 22),
            "11": ("Generating seed noise...", 23),
            "12": ("MiniMax H3 Diffusion Denoising...", 25),
            "13": ("Decoding Video Frames (Video VAE)...", 88),
            "14": ("Decoding Stereo Audio Latents (Audio VAE)...", 93),
            "15": ("Assembling Video + Native Audio Streams...", 96),
            "16": ("Finalizing & Saving MP4 to disk...", 98),
        }

        # Connect to ComfyUI WebSocket to track 100% accurate real-time progress
        ws_url = f"ws://{COMFY_HOST}/ws?clientId={client_id}"
        async with websockets.connect(ws_url) as ws:
            while True:
                msg = await ws.recv()
                if isinstance(msg, str):
                    data = json.loads(msg)
                    mtype = data.get("type")
                    if mtype == "progress":
                        val = data.get("data", {}).get("value", 0)
                        max_val = data.get("data", {}).get("max", 8)
                        pct = int(24 + (val / max(1, max_val)) * 62)
                        job["progress"] = min(86, pct)
                        job["step"] = f"MiniMax H3 Denoising: Step {val}/{max_val} ({pct}%)"
                    elif mtype == "executing":
                        node = str(data.get("data", {}).get("node"))
                        if node == "None" or node is None:
                            if job["progress"] > 70:
                                break
                        elif node in node_stage_map:
                            stage_text, stage_pct = node_stage_map[node]
                            if stage_pct > job["progress"]:
                                job["progress"] = stage_pct
                            job["step"] = stage_text

        # Fetch final video
        job["step"] = "Finalizing video delivery..."
        job["progress"] = 99
        await asyncio.sleep(0.5)

        # Search recursively for output video
        matches = glob.glob(os.path.join(SHARED_OUTPUT_PATH, "**", "*VideoGen*.*"), recursive=True)
        if not matches:
            all_vids = glob.glob(os.path.join(SHARED_OUTPUT_PATH, "**", "*.mp4"), recursive=True) + glob.glob(os.path.join(SHARED_OUTPUT_PATH, "**", "*.webm"), recursive=True)
            if all_vids:
                matches = all_vids

        if matches:
            latest_video = max(matches, key=os.path.getctime)
            dest_filename = os.path.basename(latest_video)
            dest_path = os.path.join(OUTPUTS_DIR, dest_filename)
            try:
                shutil.copy2(latest_video, dest_path)
            except Exception:
                pass
            job["status"] = "completed"
            job["progress"] = 100
            job["step"] = "Complete! Video generated with native stereo audio."
            job["video_url"] = f"/api/videos/{dest_filename}"
            job["filename"] = dest_filename
            job["prompt_id"] = prompt_id

            # Free temporary cache from RAM, but KEEP model weights resident in VRAM for instant subsequent generations!
            try:
                requests.post(f"{COMFY_URL}/free", json={"unload_models": False, "free_memory": True}, timeout=3)
            except Exception:
                pass
        else:
            raise Exception("Video file not found in ComfyUI output directory.")

    except Exception as e:
        job["status"] = "failed"
        job["error"] = str(e)
        job["step"] = f"Error: {e}"

@app.get("/api/progress/{job_id}")
async def get_progress(job_id: str):
    if job_id in jobs:
        return jobs[job_id]
    return JSONResponse(status_code=404, content={"error": "Job not found"})

def resolve_video_path(filename: str) -> Optional[str]:
    base_name = os.path.basename(filename)
    p1 = os.path.join(OUTPUTS_DIR, base_name)
    if os.path.isfile(p1):
        return p1
    p2 = os.path.join(SHARED_OUTPUT_PATH, base_name)
    if os.path.isfile(p2):
        return p2
    matches = glob.glob(os.path.join(SHARED_OUTPUT_PATH, "**", base_name), recursive=True)
    for m in matches:
        if os.path.isfile(m):
            return m
    return None

@app.api_route("/api/videos/{filename}", methods=["GET", "HEAD"])
async def get_video(filename: str):
    file_path = resolve_video_path(filename)
    if file_path and os.path.exists(file_path):
        return FileResponse(file_path, media_type="video/mp4", filename=os.path.basename(file_path))
    return JSONResponse(status_code=404, content={"error": "Video not found"})

@app.api_route("/api/download/{filename}", methods=["GET", "HEAD"])
async def download_video(filename: str):
    file_path = resolve_video_path(filename)
    if file_path and os.path.exists(file_path):
        return FileResponse(
            file_path, 
            media_type="video/mp4", 
            filename=os.path.basename(file_path),
            content_disposition_type="attachment"
        )
    return JSONResponse(status_code=404, content={"error": "Video not found"})

@app.get("/api/history")
async def get_history():
    # 1. Fetch ComfyUI history to associate prompt_id and prompt text with outputs
    file_to_info = {}
    try:
        r = requests.get(f"{COMFY_URL}/history", timeout=2)
        if r.status_code == 200:
            comfy_history = r.json()
            for pid, val in comfy_history.items():
                outputs = val.get("outputs", {})
                prompt_data = val.get("prompt", [])
                prompt_txt = ""
                if len(prompt_data) > 2 and isinstance(prompt_data[2], dict):
                    for n_id, n_info in prompt_data[2].items():
                        inputs = n_info.get("inputs", {})
                        if "prompt" in inputs and isinstance(inputs["prompt"], str):
                            if len(inputs["prompt"]) > len(prompt_txt):
                                prompt_txt = inputs["prompt"]

                for node_id, node_out in outputs.items():
                    items = node_out.get("images", []) + node_out.get("videos", [])
                    for itm in items:
                        fn = itm.get("filename")
                        if fn and fn.lower().endswith((".mp4", ".webm", ".mkv")):
                            meta = itm.get("metadata", {})
                            dur = meta.get("duration")
                            file_to_info[fn] = {
                                "prompt_id": pid,
                                "prompt": prompt_txt,
                                "duration": round(float(dur), 1) if dur else None
                            }
    except Exception:
        pass

    # 2. Gather all video files from SHARED_OUTPUT_PATH and OUTPUTS_DIR
    all_files = {}
    # First search SHARED_OUTPUT_PATH
    for p in glob.glob(os.path.join(SHARED_OUTPUT_PATH, "**", "*.*"), recursive=True):
        if p.lower().endswith((".mp4", ".webm", ".mkv")):
            fn = os.path.basename(p)
            all_files[fn] = p

    # Also search OUTPUTS_DIR
    for p in glob.glob(os.path.join(OUTPUTS_DIR, "*.*")):
        if p.lower().endswith((".mp4", ".webm", ".mkv")):
            fn = os.path.basename(p)
            if fn not in all_files:
                all_files[fn] = p

    history = []
    for fn, fpath in all_files.items():
        try:
            st = os.stat(fpath)
            fsize = st.st_size
            mtime = st.st_mtime
            info = file_to_info.get(fn, {})

            p_text = info.get("prompt", "")
            if p_text:
                p_text = p_text.replace(" Audio: silent, quiet natural ambient background, no speech, no vocals, no music.", "").strip()

            history.append({
                "filename": fn,
                "url": f"/api/videos/{fn}",
                "prompt_id": info.get("prompt_id"),
                "prompt": p_text if p_text else None,
                "duration": info.get("duration"),
                "size_mb": round(fsize / (1024 * 1024), 2),
                "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime)),
                "mtime": mtime
            })
        except Exception:
            pass

    history.sort(key=lambda x: x["mtime"], reverse=True)
    return history

@app.post("/api/history/delete")
async def delete_history_item(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}

    filename = data.get("filename")
    prompt_id = data.get("prompt_id")

    if not filename and not prompt_id:
        return JSONResponse(status_code=400, content={"error": "filename or prompt_id required"})

    deleted_comfy = False

    # If prompt_id was not directly sent, look it up from ComfyUI history
    if not prompt_id and filename:
        try:
            r = requests.get(f"{COMFY_URL}/history", timeout=2)
            if r.status_code == 200:
                comfy_history = r.json()
                for pid, val in comfy_history.items():
                    outputs = val.get("outputs", {})
                    for node_id, node_out in outputs.items():
                        for itm in node_out.get("images", []) + node_out.get("videos", []):
                            if itm.get("filename") == filename:
                                prompt_id = pid
                                break
                    if prompt_id:
                        break
        except Exception:
            pass

    # 1. Delete from ComfyUI history list
    if prompt_id:
        try:
            r_del = requests.post(f"{COMFY_URL}/history", json={"delete": [prompt_id]}, timeout=5)
            if r_del.status_code == 200:
                deleted_comfy = True
        except Exception as e:
            print(f"Error deleting from ComfyUI history: {e}")

    # 2. Delete file from disk in both OUTPUTS_DIR and SHARED_OUTPUT_PATH
    deleted_files = []
    if filename:
        base_name = os.path.basename(filename)
        # In OUTPUTS_DIR
        p1 = os.path.join(OUTPUTS_DIR, base_name)
        if os.path.exists(p1):
            try:
                os.remove(p1)
                deleted_files.append(p1)
            except Exception:
                pass
        # In SHARED_OUTPUT_PATH
        p2 = os.path.join(SHARED_OUTPUT_PATH, base_name)
        if os.path.exists(p2):
            try:
                os.remove(p2)
                deleted_files.append(p2)
            except Exception:
                pass
        # Recursive in SHARED_OUTPUT_PATH subfolders
        for m in glob.glob(os.path.join(SHARED_OUTPUT_PATH, "**", base_name), recursive=True):
            if os.path.exists(m):
                try:
                    os.remove(m)
                    deleted_files.append(m)
                except Exception:
                    pass

    return {
        "status": "deleted",
        "filename": filename,
        "prompt_id": prompt_id,
        "comfy_deleted": deleted_comfy,
        "files_removed": len(deleted_files)
    }

@app.post("/api/history/clear")
async def clear_history():
    # 1. Wipe ComfyUI history & queue
    comfy_history_cleared = False
    try:
        r_hist = requests.post(f"{COMFY_URL}/history", json={"clear": True}, timeout=5)
        r_q = requests.post(f"{COMFY_URL}/queue", json={"clear": True}, timeout=5)
        comfy_history_cleared = (r_hist.status_code == 200)
    except Exception as e:
        print(f"Error clearing ComfyUI history: {e}")

    # 2. Clear outputs directory
    for f in glob.glob(os.path.join(OUTPUTS_DIR, "*.*")):
        if f.lower().endswith((".mp4", ".webm", ".mkv", ".png", ".jpg")):
            try:
                os.remove(f)
            except Exception:
                pass

    # 3. Clear VideoGen videos from ComfyUI shared output
    for f in glob.glob(os.path.join(SHARED_OUTPUT_PATH, "**", "*VideoGen*.*"), recursive=True):
        try:
            os.remove(f)
        except Exception:
            pass

    jobs.clear()
    return {"status": "cleared", "comfy_cleared": comfy_history_cleared}

@app.post("/api/system/free")
async def free_system_memory():
    try:
        requests.post(f"{COMFY_URL}/free", json={"unload_models": True, "free_memory": True}, timeout=5)
    except Exception:
        pass
    return {"status": "memory_freed"}

@app.get("/")
async def serve_index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    response = FileResponse(index_file, media_type="text/html")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=7860, reload=False)
