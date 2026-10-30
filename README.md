# 🎬 VidGen

<div align="center">

```
__      ___     _  _____             
\ \    / (_)   | |/ ____|            
 \ \  / / _  __| | |  __  ___ _ __   
  \ \/ / | |/ _` | | |_ |/ _ \ '_ \  
   \  /  | | (_| | |__| |  __/ | | | 
    \/   |_|\__,_|\_____|\___|_| |_| 
```

### Next-Generation Image-to-Video & Text-to-Video Studio with Joint Native Audio & Video Diffusion

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-Integrated-FF6F00?style=for-the-badge&logo=target&logoColor=white)](https://github.com/comfyanonymous/ComfyUI)
[![MiniMax H3](https://img.shields.io/badge/Model-MiniMax_H3-792EE5?style=for-the-badge&logo=huggingface&logoColor=white)](https://huggingface.co/Comfy-Org/MiniMax-H3)
[![Qwen3-VL 32B](https://img.shields.io/badge/Encoder-Qwen3--VL_32B-0080FF?style=for-the-badge&logo=openai&logoColor=white)](https://huggingface.co/Comfy-Org/MiniMax-H3)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Supported-007808?style=for-the-badge&logo=ffmpeg&logoColor=white)](https://ffmpeg.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](#license)

<br/>

**VidGen Studio** is a high-performance local AI video creation suite that leverages the groundbreaking **MiniMax H3** multimodal diffusion architecture and **Qwen3-VL 32B** encoder to generate high-definition video with **synchronized, native stereo audio** directly from static images or pure text prompts.

[✨ Key Features](#-key-features) • [⚡ One-Click Runner](#-one-click-runner-windows) • [🛠️ Tech Stack](#️-technology-stack) • [📦 Model Setup](#-required-models) • [🚀 Manual Installation](#-manual-installation)

---

</div>

## 🌟 Key Features

- **Dual Creation Modes: Image-to-Video & Text-to-Video**  
  Effortlessly animate images or create complete cinematic scenes from scratch using pure text prompts with zero context contamination between modes.
- **Joint Native Audio & Video Synthesis**  
  Unlike traditional pipelines that mute outputs or require disjointed post-dubbing, MiniMax H3 denoises video frames and stereo audio latents concurrently inside a single unified diffusion model.
- **Multimodal Intelligence with Qwen3-VL 32B**  
  Natural prompt interpretation supporting complex timestamp cues (`[0s-2s]`), character dialogue in quotes, multilingual speech (English, Hindi, Bengali, etc.), and custom audio instructions without rigid formatting.
- **Multiple Aspect Ratios**  
  - 📱 **9:16 Vertical (768 × 1344)** — Optimized for Instagram Reels, YouTube Shorts, and TikTok.
  - 🖥️ **16:9 Cinematic (1344 × 768)** — Widescreen cinematic storytelling and landscapes.
  - 🔲 **1:1 Square (960 × 960)** — Social posts and avatars.
  - 🖼️ **Original (Native Proportions)** — Dynamic aspect ratio preservation with zero stretching.
- **Turbo 8-Step LoRA Acceleration**  
  Dramatically reduces inference time while maintaining sharp temporal consistency and rich audio fidelity.
- **Live Real-Time WebSocket Telemetry**  
  Real-time node-by-node feedback (model loading, text encoding, latent denoising, VAE audio/video decoding) streamed directly to the browser UI.
- **Automatic Uploads Cleanup**  
  Temporary uploaded images are automatically deleted immediately after video generation to keep local storage clean.
- **Persistent Gallery & Video Player**  
  Browse, preview, download, and manage previously generated videos with prompt metadata preserved.

---

## ⚡ One-Click Runner (Windows)

The repository includes a ready-to-use batch launcher for Windows:

```
📁 VidGen
  └── 🚀 start_ui.bat  <-- DOUBLE CLICK TO START
```

### How to use `start_ui.bat`:

1. Ensure **ComfyUI** is running on your machine (`http://127.0.0.1:8188`).
2. Double-click **`start_ui.bat`** in the project folder.
3. The launcher will automatically check dependencies and start the FastAPI server on port **`7860`**.
4. Open your web browser and navigate to:
   - **Local:** [http://localhost:7860](http://localhost:7860)
   - **LAN (Network):** `http://<your-local-ip>:7860`

> 💡 *Note: You can close the server at any time by pressing `Ctrl + C` in the command terminal.*

---

## 🛠️ Technology Stack

| Component | Technology / Library | Purpose |
| :--- | :--- | :--- |
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/) | High-speed asynchronous REST API & static file serving |
| **Realtime Protocol** | [WebSockets](https://websockets.readthedocs.io/) | Streaming real-time ComfyUI denoising and node execution progress |
| **Diffusion Backend** | [ComfyUI](https://github.com/comfyanonymous/ComfyUI) | Distributed graph workflow execution engine |
| **Diffusion Model** | **MiniMax H3 INT8 ConvRot** | Joint multimodal Video + Stereo Audio generation |
| **Text & Vision LLM** | **Qwen3-VL 32B (NVFP4 / AWQ)** | High-precision prompt embedding and image understanding |
| **Decoders** | MiniMax Video VAE + Audio VAE | High-fidelity stereo audio & frame reconstruction |
| **Media Processing** | [FFmpeg](https://ffmpeg.org/), [Pillow](https://python-pillow.org/), [SoundFile](https://python-soundfile.readthedocs.io/), [NumPy](https://numpy.org/) | Aspect-ratio smart cropping, audio synthesis & remuxing |
| **Frontend** | Modern Vanilla HTML5 / CSS3 / ES6+ | Glassmorphic dark studio UI with zero external build step dependencies |

---

## 📦 Required Models

VidGen Studio connects to ComfyUI's model directories. You can download the models directly from the **Model Manager** tab inside the web UI, or manually download them to your ComfyUI models folder:

| Model File | Category | Target Folder | Approx. Size |
| :--- | :--- | :--- | :--- |
| `minimax_h3_fl2va_pruned_int8_convrot.safetensors` | Diffusion Model | `models/diffusion_models/` | ~19.5 GB |
| `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` | Text/Vision Encoder | `models/text_encoders/` | ~14.6 GB |
| `minimax_h3_video_vae_int8_convrot.safetensors` | Video VAE | `models/vae/` | ~2.6 GB |
| `minimax_h3_audio_vae_fp32.safetensors` | Audio VAE | `models/vae/` | ~0.56 GB |
| `minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors` | Turbo LoRA | `models/loras/` | ~1.8 GB |

Official Hugging Face repository: [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3)

---

## 🚀 Manual Installation

If you prefer to run the application manually or are on Linux/macOS:

### 1. Clone the repository
```bash
git clone https://github.com/rajeshc-git/videogen.git
cd videogen
```

### 2. Set up a Python Virtual Environment
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux / macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Ensure FFmpeg is Installed
Make sure `ffmpeg` is accessible in your system's `PATH`:
```bash
ffmpeg -version
```

### 5. Start the Server
```bash
python server.py
```
Open **[http://localhost:7860](http://localhost:7860)** in your browser.

---

## 📁 Project Structure

```text
VidGen/
├── .gitignore              # Ignores generated media, caches, and environment files
├── requirements.txt        # Python package requirements
├── start_ui.bat            # One-click Windows runner script
├── server.py               # FastAPI backend with ComfyUI bridge & endpoints
├── minimax_h3_bridge.py    # ComfyUI workflow builder & model discovery
├── downloader.py           # Resumable multi-threaded model downloader
├── audio_engine.py         # Stereo audio synthesizer & soundscape generator
├── static/                 # Web interface assets
│   ├── index.html          # Responsive single-page application layout
│   ├── favicon.svg         # Monochrome video camera/play logo
│   └── og-image.png        # Dual-tone social share hero card
├── uploads/                # Auto-cleaned directory for input images
└── outputs/                # Rendered videos and audio files (user-managed)
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/status` | Returns ComfyUI connectivity and model readiness status |
| `POST` | `/api/generate` | Enqueues a new Image-to-Video or Text-to-Video generation job |
| `GET` | `/api/progress/{job_id}` | Polls real-time step message, denoising node, and percentage |
| `GET` | `/api/history` | Retrieves list of all generated videos with prompts and metadata |
| `POST` | `/api/history/delete` | Deletes a video file and unlinks it from ComfyUI history |
| `POST` | `/api/history/clear` | Purges all videos, resets queue, and clears temporary uploads |
| `GET` | `/api/videos/{filename}` | Streams generated MP4 video |
| `GET` | `/api/download/{filename}` | Downloads video as attachment |
| `POST` | `/api/models/download` | Initiates asynchronous model download |
| `POST` | `/api/models/cancel` | Cancels active model download |
| `POST` | `/api/system/free` | Requests ComfyUI to clear GPU cache |

---

## 🤝 Contributing

Contributions, bug reports, and feature requests are welcome!  
Feel free to open an issue or submit a pull request on the [GitHub repository](https://github.com/rajeshc-git/videogen).

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
