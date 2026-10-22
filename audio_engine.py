import os
import math
import subprocess
import numpy as np
# pyrefly: ignore[missing-import]
import soundfile as sf

class AudioEngine:
    """
    Synthesizes and muxes audio soundtracks into video generations.
    Provides several rich cinematic sound presets (Ambient, Cyberpunk, Nature, Lo-Fi, Epic, Dreamy)
    as well as custom audio file merging using FFmpeg.
    """

    PRESETS = [
        {"id": "cinematic_epic", "name": "Cinematic Epic", "desc": "Dramatic orchestral swells, low sub-bass pulse, cinematic impact", "icon": "🎬"},
        {"id": "cyberpunk_pulse", "name": "Cyberpunk Pulse", "desc": "Retro-futuristic synth arpeggio with driving electronic bass", "icon": "⚡"},
        {"id": "ambient_drift", "name": "Ambient Drift", "desc": "Ethereal space pads, soft atmospheric reverb, tranquil harmony", "icon": "🌌"},
        {"id": "serene_nature", "name": "Serene Nature", "desc": "Organic ocean waves, soothing wind breeze, gentle birdsong", "icon": "🌿"},
        {"id": "lofi_chill", "name": "Lo-Fi Warmth", "desc": "Warm electric piano chords with vintage vinyl warmth", "icon": "☕"},
        {"id": "action_trailer", "name": "Action Trailer", "desc": "Deep hybrid braam, rising tension, punchy rhythmic drive", "icon": "🔥"},
    ]

    @staticmethod
    def synthesize_preset(preset_id: str, duration: float, sample_rate: int = 44100) -> np.ndarray:
        """Synthesizes high-definition stereo audio for a given preset and duration."""
        num_samples = int(duration * sample_rate)
        t = np.linspace(0, duration, num_samples, endpoint=False)
        left = np.zeros(num_samples, dtype=np.float32)
        right = np.zeros(num_samples, dtype=np.float32)

        # Smooth envelope: fade-in and fade-out to prevent clicks and loop smoothly
        fade_in_len = min(int(0.6 * sample_rate), num_samples // 4)
        fade_out_len = min(int(0.8 * sample_rate), num_samples // 4)
        env = np.ones(num_samples, dtype=np.float32)
        if fade_in_len > 0:
            env[:fade_in_len] = np.sin(np.linspace(0, np.pi / 2, fade_in_len)) ** 2
        if fade_out_len > 0:
            env[-fade_out_len:] = np.sin(np.linspace(np.pi / 2, 0, fade_out_len)) ** 2

        if preset_id == "cyberpunk_pulse":
            # 120 BPM driving pulse with sawtooth-like harmonics
            bpm = 120.0
            beat_freq = bpm / 60.0
            # Bass drone (F#1 = ~46.25 Hz)
            f0 = 46.25
            sub = 0.35 * np.sin(2 * np.pi * f0 * t) + 0.15 * np.sin(2 * np.pi * (f0 * 2) * t)
            # 16th note synth pulse
            pulse_env = (0.5 * (1.0 + np.sin(2 * np.pi * (beat_freq * 4) * t))) ** 3
            # Chord melody notes (F#, A, C#, E)
            notes = [185.0, 220.0, 277.18, 329.63]
            melody = np.zeros(num_samples, dtype=np.float32)
            step_len = sample_rate / (beat_freq * 4)
            for i in range(num_samples):
                note_idx = int(i // step_len) % len(notes)
                freq = notes[note_idx]
                melody[i] = math.sin(2 * math.pi * freq * (i / sample_rate))
            melody *= pulse_env * 0.25
            left = (sub + melody * 0.9) * env
            right = (sub + melody * 1.1) * env

        elif preset_id == "ambient_drift":
            # Lush D major / B minor pads (D3, F#3, A3, E4, A4)
            pad_freqs = [146.83, 185.00, 220.00, 329.63, 440.00]
            for i, f in enumerate(pad_freqs):
                lfo = 0.5 + 0.5 * np.sin(2 * np.pi * (0.2 + 0.07 * i) * t)
                phase_l = i * 0.3
                phase_r = i * 0.6
                left += (0.12 * np.sin(2 * np.pi * f * t + phase_l) * lfo).astype(np.float32)
                right += (0.12 * np.sin(2 * np.pi * (f * 1.002) * t + phase_r) * lfo).astype(np.float32)
            # Add light high shimmering air
            noise = np.random.normal(0, 0.015, num_samples).astype(np.float32)
            left = (left + noise) * env
            right = (right + noise) * env

        elif preset_id == "serene_nature":
            # Ocean waves and wind breeze modulation
            # Modulated white noise filtered by low frequency swell
            raw_noise = np.random.normal(0, 0.2, num_samples).astype(np.float32)
            # Wave period ~ 4-5 seconds
            wave_lfo = (0.5 + 0.5 * np.sin(2 * np.pi * 0.22 * t)) ** 2
            ocean = raw_noise * wave_lfo * 0.4
            # Add soft tonal resonant drone (E2 = ~82.4 Hz)
            drone = 0.15 * np.sin(2 * np.pi * 82.41 * t) + 0.08 * np.sin(2 * np.pi * 164.81 * t)
            left = (ocean + drone) * env
            right = (ocean * 1.1 + drone * 0.9) * env

        elif preset_id == "lofi_chill":
            # Warm chord progression (Cmaj7 -> Am7)
            # Chord 1: C3 (130.81), E3 (164.81), G3 (196.00), B3 (246.94)
            # Chord 2: A2 (110.00), C3 (130.81), E3 (164.81), G3 (196.00)
            chord1 = [130.81, 164.81, 196.00, 246.94]
            chord2 = [110.00, 130.81, 164.81, 196.00]
            chord_period = sample_rate * 2.5
            chords = np.zeros(num_samples, dtype=np.float32)
            for i in range(num_samples):
                curr = chord1 if (int(i // chord_period) % 2 == 0) else chord2
                val = 0.0
                for freq in curr:
                    val += math.sin(2 * math.pi * freq * (i / sample_rate))
                chords[i] = val * 0.06
            # Vinyl crackle
            crackle = np.zeros(num_samples, dtype=np.float32)
            rand_clicks = np.random.rand(num_samples) < 0.0012
            crackle[rand_clicks] = np.random.uniform(-0.15, 0.15, np.sum(rand_clicks))
            # Sub bass
            bass = 0.25 * np.sin(2 * np.pi * 65.41 * t)
            left = (chords + bass + crackle) * env
            right = (chords * 1.05 + bass * 0.95 + crackle) * env

        elif preset_id == "action_trailer":
            # Deep cinematic braam (reese bass) + tension riser
            f_start = 55.0
            sub_pulse = 0.4 * np.sin(2 * np.pi * f_start * t) + 0.25 * np.sin(2 * np.pi * (f_start * 1.01) * t)
            # Metallic distortion harmonic
            sub_pulse += 0.15 * np.tanh(sub_pulse * 2.5)
            # Tension riser in higher octave
            riser = 0.12 * np.sin(2 * np.pi * (110.0 + (t / duration) * 80.0) * t)
            left = (sub_pulse + riser) * env
            right = (sub_pulse * 0.95 + riser * 1.05) * env

        else: # cinematic_epic (default)
            # Massive cinematic chord with deep sub, warm cello, and soaring upper harmonic
            root = 65.41 # C2
            harmonics = [root, root * 1.5, root * 2.0, root * 2.5, root * 3.0]
            cinematic = np.zeros(num_samples, dtype=np.float32)
            for idx, h in enumerate(harmonics):
                amp = 0.28 / (idx + 1)
                detune = 1.0 + (0.002 * (idx % 2 == 0 and 1 or -1))
                cinematic += (amp * np.sin(2 * np.pi * (h * detune) * t)).astype(np.float32)
            # Sub rumble
            sub = 0.3 * np.sin(2 * np.pi * 32.7 * t)
            left = (cinematic + sub) * env
            right = (cinematic * 1.05 + sub * 0.95) * env

        # Peak normalization to -1.0 dB
        stereo = np.stack([left, right], axis=1)
        max_val = np.max(np.abs(stereo))
        if max_val > 0.001:
            stereo = (stereo / max_val) * 0.88

        return stereo

    @classmethod
    def create_audio_track(cls, preset_id: str, duration: float, output_wav_path: str) -> str:
        """Generates the WAV file on disk for a preset and duration."""
        stereo = cls.synthesize_preset(preset_id, duration)
        os.makedirs(os.path.dirname(os.path.abspath(output_wav_path)), exist_ok=True)
        sf.write(output_wav_path, stereo, 44100, subtype='PCM_16')
        return output_wav_path

    @classmethod
    def mux_video_and_audio(cls, video_path: str, audio_path: str, output_path: str) -> bool:
        """
        Uses FFmpeg to mux the generated audio track onto the video.
        Uses -c:v copy to preserve video quality without re-encoding,
        encodes audio to pristine AAC stereo (320kbps), and truncates audio to exact video length.
        """
        try:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            cmd = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-i", audio_path,
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "320k",
                "-shortest",
                "-movflags", "+faststart",
                output_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                # If copy failed (e.g. keyframe boundary or format issue), fallback to re-encoding
                fallback_cmd = [
                    "ffmpeg", "-y",
                    "-i", video_path,
                    "-i", audio_path,
                    "-c:v", "libx264",
                    "-pix_fmt", "yuv420p",
                    "-c:a", "aac",
                    "-b:a", "320k",
                    "-shortest",
                    "-movflags", "+faststart",
                    output_path
                ]
                res2 = subprocess.run(fallback_cmd, capture_output=True, text=True)
                return res2.returncode == 0
            return True
        except Exception as e:
            print(f"Error in mux_video_and_audio: {e}")
            return False

    @staticmethod
    def get_video_duration(video_path: str) -> float:
        """Reads video duration using ffprobe."""
        try:
            cmd = [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                video_path
            ]
            out = subprocess.check_output(cmd, text=True).strip()
            return float(out)
        except Exception:
            return 5.0 # default fallback 5.0 seconds
