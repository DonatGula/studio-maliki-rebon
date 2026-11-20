"""Pilih momen (heuristik) dan prompt untuk AI."""
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
from .sumber import *  # noqa: F401,F403
from .transkrip import *  # noqa: F401,F403
from .umum import AKAR

# ── 4. Pilih momen (Opsi A, gratis) ─────────────────────────────────────────
@dataclass
class Klip:
    mulai: float
    selesai: float
    judul: str
    skor: float = 0.0
    alasan: str = ""
    caption: str = ""
    kutipan: str = ""
    kata_kunci: list = field(default_factory=list)


def nilai_heatmap(heatmap: list[dict], a: float, b: float) -> float:
    vals = [p.get("value", 0) for p in heatmap if p.get("end_time", 0) > a and p.get("start_time", 0) < b]
    return float(np.mean(vals)) if vals else 0.0


HOOK_AWAL = re.compile(r"^(rahasia|ternyata|kenapa|mengapa|gimana|bagaimana|cara|jangan|penting|gratis|pertama|intinya|tips|salah|"
                       r"wajib|harus|bayangkan|sebenarnya|fakta|stop|bahaya|jarang|kebanyakan|kunci|terbukti|nyangka|serius|asli|"
                       r"parah|gila|secret|never|why|how|mistake|actually|important|crazy)")


def bersih_kata(w: str) -> str:
    return w.strip().strip("\"'(),.?!:;…").lower()


def is_hook(w: str) -> bool:
    return bool(HOOK_AWAL.match(bersih_kata(w)))


def kalimat_utuh(kal: list[Kalimat]) -> list[Kalimat]:
    """Pecah ulang per KALIMAT dari kata-kata: titik/tanya/seru, atau jeda > 1,2 dtk = batas kalimat."""
    kata = [k for s in kal for k in s.kata]
    if not kata:
        return kal
    hasil, mulai = [], 0
    for i, k in enumerate(kata):
        akhir = k.teks.rstrip("\"')").endswith((".", "?", "!", "…"))
        jeda = i + 1 < len(kata) and kata[i + 1].mulai - k.selesai > 1.2
        if akhir or jeda or i == len(kata) - 1:
            isi = kata[mulai:i + 1]
            hasil.append(Kalimat(isi[0].mulai, isi[-1].selesai, " ".join(x.teks for x in isi), isi))
            mulai = i + 1
    return hasil


def pilih_momen(kal: list[Kalimat], energi: np.ndarray, heatmap: list[dict],
                durasi: float, jumlah: int, panjang_video: float, arahan: str = "") -> list[Klip]:
    """Momen = rangkaian kalimat utuh, diberi skor, judul, dan alasan (sama dengan aplikasi Klip HP)."""
    kata_arahan = {w for w in re.findall(r"\w+", arahan.lower()) if len(w) > 3}
    if not kal:
        # tanpa ucapan: pakai energi audio saja
        kal = [Kalimat(float(t), float(t + 1), "", []) for t in range(int(panjang_video))]
    kal = kalimat_utuh(kal)
    kandidat: list[Klip] = []
    for i, k in enumerate(kal):
        for j in range(i, len(kal)):
            a, b = k.mulai, kal[j].selesai
            pj = b - a
            if pj > durasi * 1.2:
                break
            if pj < durasi * 0.6:
                continue
            isi = kal[i:j + 1]
            kata = [x for s in isi for x in s.kata]
            teks = " ".join(s.teks for s in isi)
            semua_kata = re.findall(r"\w+", teks.lower())
            hooks = list(dict.fromkeys(bersih_kata(x.teks) for x in kata if is_hook(x.teks)))
            padat = len(semua_kata) / max(pj, 1)  # kata per detik
            tanya = sum(1 for s in isi if s.teks.rstrip().endswith("?"))
            pembuka = any(is_hook(x.teks) for x in k.kata[:6]) or ("?" in k.teks)
            e = float(energi[int(a):max(int(b), int(a) + 1)].mean()) if len(energi) > 1 else 0
            hm = nilai_heatmap(heatmap, a, b)
            skor = (padat * 14 + len(hooks) * 7 + tanya * 5 + (14 if pembuka else 0)
                    - abs(pj - durasi) / durasi * 10 + e * 10 + hm * 30)
            if kata_arahan and kata_arahan & set(semua_kata):
                skor += 20
            alasan = [x for x in ("pembuka kuat" if pembuka else "", "ada pertanyaan" if tanya else "",
                                  f"{len(hooks)} kata pemikat" if hooks else "", "bicara padat" if padat >= 2.6 else "",
                                  "sering diputar ulang" if hm > 0.5 else "", "sesuai arahan" if kata_arahan & set(semua_kata) else "") if x]
            judul = (k.teks[:70] or f"Klip {a:.0f}s").strip()
            kandidat.append(Klip(round(a, 2), round(b, 2), judul, skor, " · ".join(alasan) or "kalimat utuh"))
    if not kandidat and kal:
        b = min(kal[-1].selesai, kal[0].mulai + durasi)
        kandidat = [Klip(round(kal[0].mulai, 2), round(b, 2), (kal[0].teks[:70] or "Klip").strip(), 50, "kalimat utuh")]
    kandidat.sort(key=lambda c: c.skor, reverse=True)
    terpilih: list[Klip] = []
    for c in kandidat:
        if all(c.selesai <= t.mulai or c.mulai >= t.selesai for t in terpilih):
            terpilih.append(c)
        if len(terpilih) == jumlah:
            break
    if terpilih:  # skor tampilan 0–99 relatif terhadap momen terbaik
        top, bawah = terpilih[0].skor, terpilih[-1].skor
        for c in terpilih:
            c.skor = int(min(max(60 + 39 * (c.skor - bawah) / max(top - bawah, 1), 1), 99))
    return sorted(terpilih, key=lambda c: c.mulai)


# ── 4b. Opsi B: prompt untuk Claude ─────────────────────────────────────────
def tulis_prompt(kal: list[Kalimat], durasi: int, jumlah: int, out: Path, arahan: str = "") -> None:
    baris = "\n".join(f"[{k.mulai:.1f}-{k.selesai:.1f}] {k.teks}" for k in kal)
    out.write_text(f"""Kamu editor video pendek. Di bawah ini transkrip video dengan waktu (detik).
Pilih {jumlah} momen paling menarik untuk TikTok/Reels, masing-masing sekitar {durasi} detik.{(chr(10) + "Fokus pengguna: " + arahan) if arahan else ""}
Syarat: mulai di awal kalimat, selesai di akhir kalimat, ada hook di 3 detik pertama, tidak saling tumpang tindih.
Judul, caption, dan ringkasan HANYA boleh memakai fakta & angka yang ada di transkrip — jangan mengarang angka, waktu, atau klaim.
"hook" = detik kalimat paling memancing perhatian di dalam klip. Bahasa judul & caption mengikuti bahasa transkrip.
"kata_kunci" = 3-6 KATA TUNGGAL (bukan frasa) persis seperti di transkrip klip itu yang paling penting (angka, nama, kata emosi), untuk diberi warna di subtitle.
Balas HANYA JSON seperti ini, tanpa teks lain:
{{"ringkasan": "2 kalimat ringkasan isi video", "hashtag": ["#tagsatu", "#tagdua", "#tagtiga"],
 "klip": [{{"mulai": 12.3, "selesai": 41.0, "hook": 14.0, "judul": "judul singkat", "alasan": "kenapa menarik", "skor": 0.9, "caption": "caption siap posting + 3 hashtag", "kata_kunci": ["kata", "penting"]}}]}}

TRANSKRIP:
{baris}
""", encoding="utf-8")
