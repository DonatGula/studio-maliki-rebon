"""Sumber video (yt-dlp/file), info video, energi audio."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path

import numpy as np
from .umum import *  # noqa: F401,F403
from .umum import AKAR

# ── 1. Sumber video ─────────────────────────────────────────────────────────
def _runtime_js() -> dict:
    """Deno bawaan paket pip `deno` (ikut installer) → tidak bergantung Node.js di komputer pengguna.
    Tanpa runtime JS, YouTube menolak sebagian besar format (laporan: Windows 'gagal mengunduh')."""
    rt: dict = {}
    try:
        import deno
        rt["deno"] = {"path": deno.find_deno_bin()}
    except Exception:
        rt["deno"] = {}
    rt["node"] = {}
    return rt


def ambil_sumber(sumber: str, kerja: Path) -> tuple[Path, list[dict], str]:
    """Kembalikan (file video, heatmap YouTube atau [], judul)."""
    if re.match(r"^https?://", sumber):
        import yt_dlp
        log("Mengunduh video (maks 1080p) dengan yt-dlp…")
        opsi = {
            "outtmpl": str(kerja / "sumber.%(ext)s"),
            "format": "bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[height<=1080][ext=mp4]/b",
            "merge_output_format": "mp4",
            "ffmpeg_location": ffmpeg(),
            "quiet": True, "no_warnings": True, "noprogress": True,
            "js_runtimes": _runtime_js(),  # yt-dlp butuh runtime JS untuk tantangan YouTube
        }
        with yt_dlp.YoutubeDL(opsi) as ydl:
            info = ydl.extract_info(sumber, download=True)
        file = next(kerja.glob("sumber.*"))
        return file, info.get("heatmap") or [], info.get("title") or "video"
    p = Path(sumber).expanduser().resolve()
    if not p.exists():
        sys.exit(f"File tidak ditemukan: {p}")
    return p, [], p.stem


def info_video(file: Path) -> tuple[float, int, int]:
    import cv2
    cap = cv2.VideoCapture(str(file))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    n = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return (n / fps if n else 0.0), w, h


# ── 2. Energi audio per detik ───────────────────────────────────────────────
def energi_audio(file: Path) -> np.ndarray:
    sr = 16000
    raw = subprocess.run(
        [ffmpeg(), "-v", "error", "-i", str(file), "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"],
        capture_output=True, check=True).stdout
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
    n = len(a) // sr
    if n == 0:
        return np.zeros(1)
    rms = np.sqrt((a[: n * sr].reshape(n, sr) ** 2).mean(axis=1))
    return (rms - rms.min()) / (np.ptp(rms) + 1e-9)
