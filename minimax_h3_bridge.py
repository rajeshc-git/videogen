import os
import json
import uuid
import time
import requests
import asyncio
# pyrefly: ignore[missing-import]
from PIL import Image

COMFY_HOST = "127.0.0.1:8188"
COMFY_URL = f"http://{COMFY_HOST}"
USER_HOME = os.path.expanduser("~")
DEFAULT_COMFY_SHARED = os.path.join(USER_HOME, "AppData", "Local", "Comfy-Desktop", "ComfyUI-Shared")
SHARED_MODELS_PATH = os.environ.get("COMFY_MODELS_PATH", os.path.join(DEFAULT_COMFY_SHARED, "models"))
SHARED_OUTPUT_PATH = os.environ.get("COMFY_OUTPUT_PATH", os.path.join(DEFAULT_COMFY_SHARED, "output"))

REQUIRED_MODELS = [
    {
        "name": "minimax_h3_fl2va_pruned_int8_convrot.safetensors",
        "category": "diffusion_models",
        "target_dir": os.path.join(SHARED_MODELS_PATH, "diffusion_models"),
        "url": "https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors",
        "size_gb": 19.53,
        "desc": "MiniMax H3 INT8 ConvRot Diffusion Model (Joint Video + Native Audio)"
    },
    {
        "name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors",
        "category": "text_encoders",
        "target_dir": os.path.join(SHARED_MODELS_PATH, "text_encoders"),
        "url": "https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors",
        "size_gb": 14.61,
        "desc": "Qwen3-VL 32B NVFP4/AWQ Multimodal Text & Vision Encoder"
    },
    {
        "name": "minimax_h3_video_vae_int8_convrot.safetensors",
        "alt_names": ["minimax_h3_video_vae_fp16.safetensors"],
        "category": "vae",
        "target_dir": os.path.join(SHARED_MODELS_PATH, "vae"),
        "url": "https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_video_vae_int8_convrot.safetensors",
        "size_gb": 2.62,
        "desc": "MiniMax H3 Video VAE Decoder (INT8 ConvRot / FP16)"
    },
    {
        "name": "minimax_h3_audio_vae_fp32.safetensors",
        "category": "vae",
        "target_dir": os.path.join(SHARED_MODELS_PATH, "vae"),
        "url": "https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_audio_vae_fp32.safetensors",
        "size_gb": 0.56,
        "desc": "MiniMax H3 Audio VAE (Stereo Audio Decoder)"
    },
    {
        "name": "minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors",
        "category": "loras",
        "target_dir": os.path.join(SHARED_MODELS_PATH, "loras"),
        "url": "https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/loras/minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors",
        "size_gb": 1.82,
        "desc": "MiniMax H3 Turbo 8-Step LoRA (Faster Generation)"
    }
]

def check_models_status():
    """Checks which MiniMax H3 models exist on disk."""
    status = []
    all_ready = True
    for m in REQUIRED_MODELS:
        candidate_names = [m["name"]] + m.get("alt_names", [])
        found_name = m["name"]
        exists = False
        size_on_disk = 0
        found_path = os.path.join(m["target_dir"], m["name"])

        for c_name in candidate_names:
            c_path = os.path.join(m["target_dir"], c_name)
            if os.path.exists(c_path):
                s = os.path.getsize(c_path)
                if s > 1024 * 1024 * 50: # at least 50MB
                    exists = True
                    size_on_disk = s
                    found_name = c_name
                    found_path = c_path
                    break

        status.append({
            "name": found_name,
            "category": m["category"],
            "desc": m["desc"],
            "expected_gb": m["size_gb"],
            "size_gb": round(size_on_disk / (1024**3), 2),
            "exists": exists,
            "path": found_path
        })
        if not exists:
            all_ready = False
    return {"all_ready": all_ready, "models": status}

def check_comfy_online():
    """Verifies ComfyUI server is reachable."""
    try:
        r = requests.get(f"{COMFY_URL}/system_stats", timeout=2)
        if r.status_code == 200:
            data = r.json()
            device_name = "NVIDIA GPU"
            devices = data.get("devices", [])
            if devices:
                device_name = devices[0].get("name", "NVIDIA GPU")
            return {"online": True, "device": device_name, "version": data.get("system", {}).get("comfyui_version", "0.42")}
    except Exception:
        pass
    return {"online": False, "device": None, "version": None}

def prepare_9_16_image(input_image_path: str, output_path: str, target_width: int = 768, target_height: int = 1344) -> str:
    """
    Prepares the user's uploaded image WITHOUT ANY CROPPING.
    Preserves 100% of the original image content. Snaps dimensions to multiples of 32
    as required by the MiniMax H3 VAE encoder.
    """
    im = Image.open(input_image_path).convert("RGB")
    src_w, src_h = im.size

    # Snap to nearest multiple of 32 without cropping any pixels
    w = max(64, round(src_w / 32) * 32)
    h = max(64, round(src_h / 32) * 32)

    if (w, h) != (src_w, src_h):
        im = im.resize((w, h), Image.Resampling.LANCZOS)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    im.save(output_path, "PNG", quality=95)
    return output_path

def upload_image_to_comfy(image_path: str) -> str:
    """Uploads an image to ComfyUI /upload/image endpoint."""
    with open(image_path, "rb") as f:
        filename = f"videogen_{int(time.time())}_{os.path.basename(image_path)}"
        files = {"image": (filename, f, "image/png")}
        r = requests.post(f"{COMFY_URL}/upload/image", files=files, timeout=15)
        if r.status_code == 200:
            return filename
        raise Exception(f"ComfyUI upload failed: {r.text}")

def build_minimax_h3_prompt(uploaded_filename: str, prompt_text: str, duration_sec: int = 5, seed: int = None, width: int = 768, height: int = 1344):
    """
    Converts the official MiniMax H3 template into a runnable ComfyUI API prompt payload.
    """
    if seed is None:
        seed = int(time.time() * 1000) % 1000000000000000

    # MiniMax H3 native API workflow graph:
    # 1. LoadImage (user uploaded image)
    # 2. MiniMaxH3ImageToVideo (processes positive prompt, first_frame, resolution, duration)
    # 3. UNETLoader (minimax_h3_fl2va_pruned_int8_convrot)
    # 4. CLIPLoader (qwen3vl_32b_minimax_h3_nvfp4_awq, type: minimax)
    # 5. LoraLoaderModelOnly (turbo 8-step LoRA)
    # 6. BasicGuider + KSamplerSelect + BasicScheduler + SamplerCustomAdvanced
    # 7. VAEDecode (video) + VAEDecodeAudio (audio)
    # 8. CreateVideo (combines video frames + native stereo audio)
    # 9. SaveVideo (saves mp4 to output directory)
    workflow = {
        "1": {
            "inputs": {
                "image": uploaded_filename,
                "upload": "image"
            },
            "class_type": "LoadImage"
        },
        "2": {
            "inputs": {
                "unet_name": "minimax_h3_fl2va_pruned_int8_convrot.safetensors",
                "weight_dtype": "default"
            },
            "class_type": "UNETLoader"
        },
        "3": {
            "inputs": {
                "clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors",
                "type": "minimax"
            },
            "class_type": "CLIPLoader"
        },
        "4": {
            "inputs": {
                "vae_name": "minimax_h3_video_vae_int8_convrot.safetensors" if os.path.exists(os.path.join(SHARED_MODELS_PATH, "vae", "minimax_h3_video_vae_int8_convrot.safetensors")) else "minimax_h3_video_vae_fp16.safetensors"
            },
            "class_type": "VAELoader"
        },
        "5": {
            "inputs": {
                "vae_name": "minimax_h3_audio_vae_fp32.safetensors"
            },
            "class_type": "VAELoader"
        },
        "6": {
            "inputs": {
                "model": ["2", 0],
                "lora_name": "minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors",
                "strength_model": 1.0
            },
            "class_type": "LoraLoaderModelOnly"
        },
        "7": {
            "inputs": {
                "clip": ["3", 0],
                "vae": ["4", 0],
                "prompt": prompt_text,
                "width": width,
                "height": height,
                "length": max(5, round(duration_sec * 24)) + (5 - (max(5, round(duration_sec * 24)) % 17)) % 17,
                "first_frame": ["1", 0]
            },
            "class_type": "MiniMaxH3ImageToVideo"
        },
        "8": {
            "inputs": {
                "sampler_name": "euler"
            },
            "class_type": "KSamplerSelect"
        },
        "9": {
            "inputs": {
                "model": ["6", 0],
                "scheduler": "simple",
                "steps": 8,
                "denoise": 1.0
            },
            "class_type": "BasicScheduler"
        },
        "10": {
            "inputs": {
                "model": ["6", 0],
                "conditioning": ["7", 0]
            },
            "class_type": "BasicGuider"
        },
        "11": {
            "inputs": {
                "noise_seed": seed
            },
            "class_type": "RandomNoise"
        },
        "12": {
            "inputs": {
                "noise": ["11", 0],
                "guider": ["10", 0],
                "sampler": ["8", 0],
                "sigmas": ["9", 0],
                "latent_image": ["7", 1]
            },
            "class_type": "SamplerCustomAdvanced"
        },
        "13": {
            "inputs": {
                "samples": ["12", 0],
                "vae": ["4", 0]
            },
            "class_type": "VAEDecode"
        },
        "14": {
            "inputs": {
                "samples": ["12", 1],
                "vae": ["5", 0]
            },
            "class_type": "VAEDecodeAudio"
        },
        "15": {
            "inputs": {
                "images": ["13", 0],
                "audio": ["14", 0],
                "fps": 24.0,
                "codec": "auto"
            },
            "class_type": "CreateVideo"
        },
        "16": {
            "inputs": {
                "video": ["15", 0],
                "filename_prefix": "VideoGen_MiniMaxH3",
                "format": "auto"
            },
            "class_type": "SaveVideo"
        }
    }
    return workflow
