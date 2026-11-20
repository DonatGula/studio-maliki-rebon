"""Bersama: ffmpeg, log, kata hook."""
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


AKAR = Path(__file__).resolve().parent.parent  # folder alat/klip (font, emoji, model, .env)

KATA_HOOK = {
    # kata yang sering membuka momen menarik (ID + EN)
    "rahasia", "ternyata", "jangan", "kenapa", "gimana", "bagaimana", "penting", "masalahnya",
    "kesalahan", "cara", "tips", "gila", "serius", "pertama", "akhirnya", "intinya", "wow",
    "secret", "never", "why", "how", "mistake", "actually", "important", "crazy",
}


def ffmpeg() -> str:
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def log(msg: str) -> None:
    print(f"• {msg}", flush=True)
