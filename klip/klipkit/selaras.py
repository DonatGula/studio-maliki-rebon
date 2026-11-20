"""Penyelaras waktu (forced alignment) untuk transkrip yang teksnya benar tapi waktunya kasar (mis. dari Gemini).

Model CTC multibahasa MMS (torchaudio MMS_FA, ±1,2 GB, sekali unduh) memetakan tiap huruf ke audio. Teks satu potongan
Gemini diselaraskan ke seluruh audio potongan itu sekaligus, jadi waktu Gemini (bisa melenceng puluhan detik) tidak
dipakai sama sekali. Hasilnya waktu per kata dari audio, bukan tebakan."""
from __future__ import annotations

import re
import unicodedata

import numpy as np

from .umum import *  # noqa: F401,F403
from .transkrip import Kata

SR = 16000


def _bersih(k: str) -> str:
    k = unicodedata.normalize("NFKD", k.lower())
    k = "".join(c for c in k if not unicodedata.combining(c))
    k = {"0": "nol", "1": "satu", "2": "dua", "3": "tiga", "4": "empat", "5": "lima", "6": "enam", "7": "tujuh",
         "8": "delapan", "9": "sembilan"}.get(k, k) if k.isdigit() and len(k) == 1 else k
    return re.sub(r"[^a-z']", "", k)


class Penyelaras:
    def __init__(self):
        import torch
        from torchaudio.pipelines import MMS_FA as B
        log("Memuat penyelaras waktu (MMS, pertama kali mengunduh ±1,2 GB)…")
        self.torch = torch
        self.model = B.get_model(with_star=True).eval()
        self.kamus = B.get_dict(star="*")
        self.rasio = B.sample_rate / SR

    def _emisi(self, audio: np.ndarray):
        t = self.torch
        with t.inference_mode():
            x = t.from_numpy(audio).unsqueeze(0)
            # potong 30 dtk supaya memori kecil; emisi disambung (frame 20 ms)
            bag = [self.model(x[:, i:i + 30 * SR])[0] for i in range(0, x.shape[1], 30 * SR)]
            return t.cat(bag, dim=1)

    def selaraskan(self, audio: np.ndarray, kalimat: list, a: float, b: float) -> int:
        """Selaraskan SEMUA kalimat ke audio[a:b] sekaligus (waktu lama diabaikan, cukup urutannya). Token <star>
        di ujung dan di antara kalimat menyerap ucapan yang tidak ada di teks. Mengubah .mulai/.selesai/.kata (waktu
        absolut); kalimat yang tak terpetakan dibiarkan. Kembalikan jumlah kalimat yang berhasil."""
        import torchaudio.functional as F
        t = self.torch
        a, b = max(0.0, a), min(len(audio) / SR, b)
        bintang = self.kamus["*"]
        token, idx = [bintang], []  # idx: (kalimat, posisi kata, token awal, token akhir)
        for gi, k in enumerate(kalimat):
            for n, w in enumerate(k.teks.split()):
                s = len(token)
                token += [self.kamus[c] for c in _bersih(w) if c in self.kamus]
                if len(token) > s:
                    idx.append((gi, n, s, len(token)))
            token.append(bintang)
        if not idx:
            return 0
        em = self._emisi(audio[int(a * SR):int(b * SR)])
        if em.shape[1] < len(token):
            return 0
        try:
            lab, skor = F.forced_align(em, t.tensor([token], dtype=t.int32), blank=0)
        except RuntimeError as e:
            log(f"Penyelaras gagal di {a:.0f}-{b:.0f} dtk ({e}); waktu Gemini dipakai.")
            return 0
        spans = F.merge_tokens(lab[0], skor[0].exp())  # satu span per token, urut
        dt = (b - a) / em.shape[1]
        waktu = {(gi, n): (a + spans[s].start * dt, a + spans[e - 1].end * dt) for gi, n, s, e in idx}
        ok = 0
        for gi, k in enumerate(kalimat):
            baru = []
            for n, w in enumerate(k.teks.split()):
                if (gi, n) in waktu:
                    m, e = waktu[(gi, n)]
                elif baru:  # kata tanpa huruf (angka/simbol) menempel ke kata sebelumnya
                    m = e = baru[-1].selesai
                else:
                    continue
                baru.append(Kata(round(m, 3), round(e, 3), w))
            if baru:
                k.kata, k.mulai, k.selesai = baru, baru[0].mulai, baru[-1].selesai
                ok += 1
        return ok
