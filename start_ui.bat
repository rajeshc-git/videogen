@echo off
title VideoGen Studio - MiniMax H3 Localhost:7860
cd /d "%~dp0"
echo ====================================================
echo Starting VideoGen Studio (MiniMax H3 Native Audio + Video)
echo Connected to ComfyUI on http://127.0.0.1:8188
echo Local URL: http://localhost:7860
echo LAN URL:   http://192.168.7.93:7860
echo ====================================================

python server.py
pause
