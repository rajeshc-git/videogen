import os
import time
import threading
import requests
from minimax_h3_bridge import REQUIRED_MODELS

# Global download state
active_download = {
    "is_downloading": False,
    "model_name": None,
    "total_bytes": 0,
    "downloaded_bytes": 0,
    "percent": 0.0,
    "speed_mb": 0.0,
    "eta_seconds": 0,
    "status": "idle",
    "error": None
}
_download_thread = None

def _download_worker(model_info):
    global active_download
    url = model_info["url"]
    target_dir = model_info["target_dir"]
    filename = model_info["name"]
    target_file = os.path.join(target_dir, filename)
    part_file = target_file + ".part"

    os.makedirs(target_dir, exist_ok=True)
    active_download["is_downloading"] = True
    active_download["model_name"] = filename
    active_download["status"] = "connecting"
    active_download["error"] = None

    headers = {"User-Agent": "Mozilla/5.0"}
    resume_byte = 0
    if os.path.exists(part_file):
        resume_byte = os.path.getsize(part_file)
        headers["Range"] = f"bytes={resume_byte}-"

    try:
        r = requests.get(url, headers=headers, stream=True, timeout=30)
        if r.status_code not in (200, 206):
            raise Exception(f"HTTP error {r.status_code}")

        total = int(r.headers.get("Content-Length", 0)) + resume_byte
        active_download["total_bytes"] = total
        active_download["downloaded_bytes"] = resume_byte
        active_download["status"] = "downloading"

        mode = "ab" if resume_byte > 0 else "wb"
        start_time = time.time()
        last_calc_time = start_time
        bytes_since_calc = 0

        with open(part_file, mode) as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024): # 1MB chunks
                if not active_download["is_downloading"]:
                    # Cancelled
                    active_download["status"] = "cancelled"
                    return
                if chunk:
                    f.write(chunk)
                    resume_byte += len(chunk)
                    bytes_since_calc += len(chunk)
                    active_download["downloaded_bytes"] = resume_byte

                    if total > 0:
                        active_download["percent"] = round((resume_byte / total) * 100.0, 1)

                    now = time.time()
                    elapsed = now - last_calc_time
                    if elapsed >= 1.0:
                        speed = (bytes_since_calc / (1024 * 1024)) / elapsed
                        active_download["speed_mb"] = round(speed, 2)
                        rem_bytes = max(0, total - resume_byte)
                        if speed > 0:
                            active_download["eta_seconds"] = int((rem_bytes / (1024 * 1024)) / speed)
                        last_calc_time = now
                        bytes_since_calc = 0

        if os.path.exists(target_file):
            os.remove(target_file)
        os.rename(part_file, target_file)
        active_download["status"] = "completed"
        active_download["is_downloading"] = False
        active_download["percent"] = 100.0
    except Exception as e:
        active_download["error"] = str(e)
        active_download["status"] = "failed"
        active_download["is_downloading"] = False

def start_model_download(model_name: str) -> dict:
    global _download_thread, active_download
    if active_download["is_downloading"]:
        return {"success": False, "message": f"Already downloading {active_download['model_name']}"}

    target_info = next((m for m in REQUIRED_MODELS if m["name"] == model_name), None)
    if not target_info:
        return {"success": False, "message": f"Model {model_name} not found in required list"}

    _download_thread = threading.Thread(target=_download_worker, args=(target_info,), daemon=True)
    _download_thread.start()
    return {"success": True, "message": f"Started download for {model_name}"}

def get_download_status():
    return active_download

def cancel_download():
    global active_download
    if active_download["is_downloading"]:
        active_download["is_downloading"] = False
        return {"success": True, "message": "Cancelling download..."}
    return {"success": False, "message": "No active download"}
