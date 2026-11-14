# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = [
#   "yt-dlp>=2025.1.1",
#   "imageio-ffmpeg>=0.6.0",
#   "faster-whisper>=1.1.0",
#   "opencv-python-headless>=4.9,<5",
#   "numpy>=1.26",
#   "google-genai>=1.0",
# ]
# ///
# kredit-maliki: Template oleh Maliki Saputra (@malikisaputra) — https://malikisaputra.biz.id · Lisensi Nonkomersial Maliki Studio 1.0 (alat/LISENSI.md): dilarang dijual ulang.
"""Klip — potong video panjang jadi klip pendek 9:16 (TikTok/Reels/Shorts).

Ditulis dari nol oleh Maliki Motion. Jalan lokal di Mac, tanpa API berbayar.

Contoh:
  uv run klip.py video.mp4
  uv run klip.py "https://www.youtube.com/watch?v=..." --jumlah 3 --durasi 30
  uv run klip.py video.mp4 --hanya-prompt          # Opsi B: siapkan prompt untuk Claude
  uv run klip.py video.mp4 --pilihan pilihan.json  # Opsi B: render pilihan Claude
  uv run klip.py video.mp4 --ai gemini              # pakai AI milik pengguna (kunci di file .env)
"""
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


# ── 1. Sumber video ─────────────────────────────────────────────────────────
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
            "js_runtimes": {"node": {}, "deno": {}},  # yt-dlp butuh runtime JS untuk YouTube
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


# ── 3. Transkrip ────────────────────────────────────────────────────────────
@dataclass
class Kata:
    mulai: float
    selesai: float
    teks: str


@dataclass
class Kalimat:
    mulai: float
    selesai: float
    teks: str
    kata: list[Kata]


def transkrip(file: Path, model: str, bahasa: str | None) -> list[Kalimat]:
    from faster_whisper import WhisperModel
    log(f"Transkripsi dengan faster-whisper model '{model}' (pertama kali akan mengunduh model)…")
    m = WhisperModel(model, device="cpu", compute_type="int8")
    sr = 16000  # decode sendiri dengan ffmpeg bawaan → tidak bergantung versi PyAV
    raw = subprocess.run([ffmpeg(), "-v", "error", "-i", str(file), "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
    segs, info = m.transcribe(audio, language=bahasa, word_timestamps=True, vad_filter=True)
    hasil = []
    for s in segs:
        kata = [Kata(w.start, w.end, w.word.strip()) for w in (s.words or []) if w.word.strip()]
        hasil.append(Kalimat(s.start, s.end, s.text.strip(), kata))
    log(f"Bahasa terdeteksi: {info.language}, {len(hasil)} kalimat.")
    return hasil


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


def pilih_momen(kal: list[Kalimat], energi: np.ndarray, heatmap: list[dict],
                durasi: float, jumlah: int, panjang_video: float, arahan: str = "") -> list[Klip]:
    kata_arahan = {w for w in re.findall(r"\w+", arahan.lower()) if len(w) > 3}
    if not kal:
        # tanpa ucapan: pakai energi audio saja
        kal = [Kalimat(float(t), float(t + 1), "", []) for t in range(int(panjang_video))]
    kandidat: list[Klip] = []
    for i, k in enumerate(kal):
        a = k.mulai
        j = i
        while j + 1 < len(kal) and kal[j + 1].selesai - a <= durasi * 1.25:
            j += 1
        b = kal[j].selesai
        if b - a < durasi * 0.6:
            continue
        teks = " ".join(x.teks for x in kal[i:j + 1])
        e = float(energi[int(a):max(int(b), int(a) + 1)].mean()) if len(energi) > 1 else 0
        kata = re.findall(r"\w+", teks.lower())
        padat = min(len(kata) / max(b - a, 1) / 3.0, 1.0)  # ~3 kata/detik = padat
        hook = 1.0 if set(re.findall(r"\w+", k.teks.lower())) & KATA_HOOK else 0.0
        tanya = 0.5 if "?" in k.teks else 0.0
        hm = nilai_heatmap(heatmap, a, b)
        if heatmap:
            skor = 0.45 * hm + 0.2 * e + 0.15 * padat + 0.15 * hook + 0.05 * tanya
        else:
            skor = 0.35 * e + 0.25 * padat + 0.3 * hook + 0.1 * tanya
        if kata_arahan and kata_arahan & set(kata):
            skor += 0.3
        alasan = f"heatmap {hm:.2f}, energi {e:.2f}, padat {padat:.2f}, hook {'ya' if hook else 'tidak'}"
        judul = (k.teks[:60] or f"Klip {a:.0f}s").strip()
        kandidat.append(Klip(round(a, 2), round(b, 2), judul, round(skor, 4), alasan))
    kandidat.sort(key=lambda c: c.skor, reverse=True)
    terpilih: list[Klip] = []
    for c in kandidat:
        if all(c.selesai <= t.mulai or c.mulai >= t.selesai for t in terpilih):
            terpilih.append(c)
        if len(terpilih) == jumlah:
            break
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


# ── 4c. AI milik pengguna (Gemini / Claude / OpenAI-compatible seperti Ollama) ─
def baca_env() -> dict:
    """Baca .env di folder skrip lalu timpa dengan variabel lingkungan."""
    import os
    env = {}
    f = Path(__file__).with_name(".env")
    if f.exists():
        for baris in f.read_text(encoding="utf-8").splitlines():
            if "=" in baris and not baris.strip().startswith("#"):
                k, v = baris.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    env.update({k: v for k, v in os.environ.items() if k in env or k.endswith(("_API_KEY", "_MODEL", "_BASE_URL"))})
    return env


def tanya_ai(penyedia: str, prompt: str) -> str:
    env = baca_env()
    if penyedia == "gemini":
        from google import genai
        kunci = env.get("GEMINI_API_KEY") or sys.exit("Isi GEMINI_API_KEY di .env (gratis: aistudio.google.com/apikey)")
        from google.genai import errors as gerr
        # model utama dulu, lalu cadangan bertier gratis (aistudio.google.com/docs/pricing, 13 Nov 2026)
        urutan = [env.get("GEMINI_MODEL", "gemini-3.8-flash"), "gemini-3.8-flash", "gemini-3.6-flash",
                  "gemini-3.5-flash-lite", "gemini-3.1-flash-lite"]
        urutan = list(dict.fromkeys(urutan))
        pesan = ""
        # simpan client di variabel: kalau tidak, client ditutup sebelum permintaan dikirim
        from google.genai import types as gtypes
        # batas waktu 90 dtk per percobaan (milidetik) supaya tidak menggantung saat server Gemini penuh
        with genai.Client(api_key=kunci, http_options=gtypes.HttpOptions(timeout=90_000)) as klien:
            for model in urutan:
                for coba in range(2):
                    try:
                        r = klien.models.generate_content(model=model, contents=prompt)
                        if model != urutan[0]:
                            log(f"Memakai model cadangan {model}.")
                        return r.text or ""
                    except gerr.APIError as e:
                        pesan = f"{model}: {e.code} {getattr(e, 'message', '') or e}"
                        if e.code in (400, 401, 403):
                            sys.exit(f"Kunci Gemini ditolak ({e.code}). Cek kuncinya di Pengaturan AI.")
                        log(f"Gemini {model} sibuk/limit ({e.code}), mencoba lagi…")
                        time.sleep(3 * (coba + 1))
                    except Exception as e:  # noqa: BLE001 — batas waktu / jaringan
                        pesan = f"{model}: {type(e).__name__}"
                        log(f"Gemini {model} tidak menjawab ({type(e).__name__}), mencoba model lain…")
                        break
        sys.exit(f"Semua model Gemini sedang sibuk atau kuota habis. Coba lagi nanti, atau pakai AI Lokal.\n{pesan}")
    if penyedia in ("claude-code", "codex", "opencode"):
        return tanya_langganan(penyedia, prompt)
    if penyedia == "openai":
        import urllib.request
        url = env.get("OPENAI_BASE_URL", "http://localhost:11434/v1").rstrip("/") + "/chat/completions"
        data = json.dumps({"model": env.get("OPENAI_MODEL", "gemma3:4b"),
                           "messages": [{"role": "user", "content": prompt}]}).encode()
        req = urllib.request.Request(url, data=data, headers={
            "Content-Type": "application/json", "Authorization": f"Bearer {env.get('OPENAI_API_KEY', 'ollama')}"})
        with urllib.request.urlopen(req, timeout=600) as resp:
            return json.loads(resp.read())["choices"][0]["message"]["content"]
    sys.exit(f"Penyedia AI tidak dikenal: {penyedia} (pilih lokal, gemini, openai, claude-code, codex, opencode)")


def cari_cli(nama: str) -> str | None:
    import os
    import shutil
    studio_cli = Path.home() / ".studio-maliki" / "cli"
    for c in (shutil.which(nama), str(studio_cli / "bin" / nama), str(studio_cli / f"{nama}.cmd"),
              str(Path.home() / ".local/bin" / nama), f"/opt/homebrew/bin/{nama}",
              f"/usr/local/bin/{nama}", str(Path.home() / ".npm-global/bin" / nama)):
        if c and Path(c).exists():
            return c
    if os.name == "nt":
        return shutil.which(nama + ".cmd") or shutil.which(nama + ".exe")
    return None


def tanya_langganan(penyedia: str, prompt: str) -> str:
    """Pakai langganan pengguna lewat CLI resmi yang sudah login di laptopnya (tanpa kunci API).

    claude-code: Claude Code (Claude Pro/Max)  → `claude -p` tanpa alat, tanpa menyimpan sesi
    codex:       Codex CLI (ChatGPT Plus/Pro)  → `codex exec -` sandbox read-only bawaan
    opencode:    OpenCode (model/langganan apa pun yang sudah login di OpenCode) → `opencode run --agent plan`
    """
    import os
    import tempfile
    nama = {"claude-code": "claude", "codex": "codex", "opencode": "opencode"}[penyedia]
    label = {"claude": "Claude Code", "codex": "Codex", "opencode": "OpenCode"}[nama]
    cli = cari_cli(nama)
    if not cli:
        sys.exit(f"CLI '{nama}' belum terpasang. Pasang lalu login sekali di Terminal "
                 f"({ {'claude': 'claude', 'codex': 'codex login', 'opencode': 'opencode auth login'}[nama] }), "
                 "kemudian coba lagi.")
    env = os.environ.copy()
    # kunci API di lingkungan akan membuat CLI menagih API, bukan langganan → buang
    for kunci in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "OPENAI_API_KEY", "CODEX_API_KEY"):
        env.pop(kunci, None)
    if nama == "opencode" and env.get("GEMINI_API_KEY") and not env.get("GOOGLE_GENERATIVE_AI_API_KEY"):
        # OpenCode membaca kunci Google dari nama variabel ini; pakai kunci Gemini yang sudah disimpan pengguna
        env["GOOGLE_GENERATIVE_AI_API_KEY"] = env["GEMINI_API_KEY"]
    with tempfile.TemporaryDirectory() as tmp:
        if nama == "claude":
            cmd = [cli, "-p", "--tools", "", "--output-format", "text", "--no-session-persistence"]
            if os.environ.get("CLAUDE_CODE_MODEL"):
                cmd += ["--model", os.environ["CLAUDE_CODE_MODEL"]]
        elif nama == "codex":
            cmd = [cli, "exec", "--skip-git-repo-check", "-o", str(Path(tmp) / "jawab.txt")]
            if os.environ.get("CODEX_MODEL"):
                cmd += ["--model", os.environ["CODEX_MODEL"]]
            cmd.append("-")
        else:
            # agent "plan" = hanya membaca/menjawab, tidak mengubah berkas
            cmd = [cli, "run", "--agent", "plan"]
            if os.environ.get("OPENCODE_MODEL"):
                cmd += ["--model", os.environ["OPENCODE_MODEL"]]
        log(f"Meminta {label} (langganan) memilih/menulis…")
        try:
            r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, encoding="utf-8",
                               cwd=tmp, env=env, timeout=600)
        except subprocess.TimeoutExpired:
            sys.exit(f"{nama} tidak menjawab dalam 10 menit.")
        if r.returncode != 0:
            alasan = re.sub(r"\x1b\[[0-9;]*m", "", (r.stderr or r.stdout)).strip()[-600:]
            sys.exit(f"{nama} gagal (kode {r.returncode}). Pastikan sudah login dan kuota langganan masih ada.\n{alasan}")
        f = Path(tmp) / "jawab.txt"
        return f.read_text(encoding="utf-8") if f.exists() else r.stdout


def ambil_json(teks: str):
    m = re.search(r"\[.*\]|\{.*\}", teks, re.S)
    if not m:
        sys.exit("Balasan AI tidak berisi JSON:\n" + teks[:500])
    return json.loads(m.group(0))


# ── 5. Bingkai: deteksi wajah ───────────────────────────────────────────────
def info_wajah(file: Path, a: float, b: float, w: int, h: int) -> dict:
    """Median posisi & ukuran wajah (0..1) di rentang klip. Tanpa wajah → tengah."""
    import cv2
    det = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    cap = cv2.VideoCapture(str(file))
    xs, ys, ss = [], [], []
    t = a
    langkah = max((b - a) / 12, 0.8)
    while t < b:
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, fr = cap.read()
        if not ok:
            break
        g = cv2.cvtColor(cv2.resize(fr, (w // 2, h // 2)), cv2.COLOR_BGR2GRAY)
        f = det.detectMultiScale(g, 1.1, 5, minSize=(30, 30))
        if len(f):
            x, y, fw, fh = max(f, key=lambda r: r[2] * r[3])
            xs.append((x + fw / 2) / (w / 2))
            ys.append((y + fh / 2) / (h / 2))
            ss.append(fw / (w / 2))
        t += langkah
    cap.release()
    if not xs:
        return {"ada": False, "x": 0.5, "y": 0.35, "s": 0.18}
    return {"ada": True, "x": float(np.median(xs)), "y": float(np.median(ys)), "s": float(np.median(ss))}


_JEJAK_SIAP: dict[tuple[float, float], list] = {}  # jejak tersimpan di klip.json (dipakai pratinjau Studio & render)


def jejak_wajah(file: Path, a: float, b: float, w: int, h: int) -> list[tuple[float, float]]:
    siap = _JEJAK_SIAP.get((round(a, 2), round(b, 2)))
    if siap:
        return [tuple(x) for x in siap]
    """Titik kunci (detik relatif klip, posisi-x 0..1) untuk bingkai yang mengikuti pembicara.

    1) sampel tiap 0,25 dtk → deteksi pergantian kamera (histogram berubah drastis)
    2) per adegan: wajah depan + profil (kiri & kanan); posisi diambil per jendela 1,5 dtk lalu dihaluskan
    3) adegan tanpa wajah → memakai posisi adegan sebelumnya, atau tengah
    """
    import cv2
    depan = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    profil = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")
    cap = cv2.VideoCapture(str(file))
    LB = 640  # lebar analisis: wajah kecil di shot lebar tetap terdeteksi
    sk = LB / w
    sampel = []  # (t, histogram, [(x, luas)])
    t = a
    while t < b:
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, fr = cap.read()
        if not ok:
            break
        kecil = cv2.resize(fr, (LB, int(h * sk)))
        abu = cv2.cvtColor(kecil, cv2.COLOR_BGR2GRAY)
        hist = cv2.calcHist([cv2.cvtColor(kecil, cv2.COLOR_BGR2HSV)], [0, 1], None, [24, 16], [0, 180, 0, 256])
        cv2.normalize(hist, hist)
        wajah = []
        if round((t - a) / 0.25) % 2 == 0:  # deteksi wajah tiap 0,5 dtk (hemat waktu)
            for (x, y, fw, fh) in depan.detectMultiScale(abu, 1.1, 5, minSize=(20, 20)):
                wajah.append(((x + fw / 2) / LB, fw * fh))
            for (x, y, fw, fh) in profil.detectMultiScale(abu, 1.1, 5, minSize=(20, 20)):
                wajah.append(((x + fw / 2) / LB, fw * fh * 0.8))
            for (x, y, fw, fh) in profil.detectMultiScale(cv2.flip(abu, 1), 1.1, 5, minSize=(20, 20)):
                wajah.append((1 - (x + fw / 2) / LB, fw * fh * 0.8))
        sampel.append((t - a, hist, wajah))
        t += 0.25
    cap.release()
    if not sampel:
        return [(0.0, 0.5)]
    # 1) potongan adegan
    batas = [0]
    for i in range(1, len(sampel)):
        if cv2.compareHist(sampel[i - 1][1], sampel[i][1], cv2.HISTCMP_CORREL) < 0.55:
            batas.append(i)
    batas.append(len(sampel))
    kunci: list[tuple[float, float]] = []
    terakhir = 0.5
    for s0, s1 in zip(batas, batas[1:]):
        adegan = sampel[s0:s1]
        mulai_ad = adegan[0][0]
        akhir_ad = adegan[-1][0] + 0.25
        # 2) per jendela 1,5 dtk: wajah terbesar (pembicara paling dekat kamera)
        titik = []
        jendela = 6
        for j in range(0, len(adegan), jendela):
            semua = [f for s in adegan[j:j + jendela] for f in s[2]]
            if semua:
                # shot berdua: JANGAN rata-ratakan dua orang yang berjauhan (hasilnya ruang kosong di tengah).
                # Kelompokkan wajah per posisi, pilih kelompok terkuat; condong ke orang yang sedang diikuti.
                kel: list[list[tuple[float, float]]] = []
                for f in sorted(semua):
                    if kel and f[0] - kel[-1][-1][0] < 0.12:
                        kel[-1].append(f)
                    else:
                        kel.append([f])
                acuan = titik[-1][1] if titik else terakhir
                def skor(g: list[tuple[float, float]]) -> float:
                    pusat = float(np.average([f[0] for f in g], weights=[f[1] for f in g]))
                    return sum(f[1] for f in g) * (1.35 if abs(pusat - acuan) < 0.12 else 1.0)
                pilih = max(kel, key=skor)
                x = float(np.average([f[0] for f in pilih], weights=[f[1] for f in pilih]))
                titik.append((adegan[j][0] + min(jendela, len(adegan) - j) * 0.125, x))
        if not titik:
            titik = [(mulai_ad, terakhir)]
        # haluskan: geser maksimal mengikuti, tapi abaikan getaran kecil (< 4% lebar)
        halus = [titik[0]]
        for tt, x in titik[1:]:
            halus.append((tt, x if abs(x - halus[-1][1]) > 0.04 else halus[-1][1]))
        kunci.append((mulai_ad, halus[0][1]))  # lompat tegas di potongan kamera
        for i, (tt, x) in enumerate(halus[1:], 1):
            # pindah orang (jauh) di shot yang sama → potong cepat, jangan geser melewati ruang kosong
            if abs(x - halus[i - 1][1]) > 0.25:
                kunci.append((max(tt - 0.08, kunci[-1][0] + 0.01), halus[i - 1][1]))
            kunci.append((tt, x))
        kunci.append((max(akhir_ad - 0.04, mulai_ad), halus[-1][1]))
        terakhir = halus[-1][1]
    return kunci


def potong_jejak(w: int, h: int, rasio: float, kunci: list[tuple[float, float]]) -> str:
    """Crop berasio tetap dengan posisi-x yang berubah menurut waktu (interpolasi linear antar titik kunci)."""
    if w / h > rasio:
        ch = h // 2 * 2
        cw = int(ch * rasio) // 2 * 2
    else:
        cw = w // 2 * 2
        ch = int(cw / rasio) // 2 * 2
    if len(kunci) == 1 or cw >= w:
        x0 = int(min(max(kunci[0][1] * w - cw / 2, 0), w - cw))
        return f"crop={cw}:{ch}:{x0}:{(h - ch) // 2}"
    px = [(t, min(max(x * w - cw / 2, 0), w - cw)) for t, x in kunci]
    # bangun ekspresi bertingkat: if(lt(t,t1), lerp, if(lt(t,t2), …))
    expr = f"{px[-1][1]:.1f}"
    for (t0, x0), (t1, x1) in reversed(list(zip(px, px[1:]))):
        if t1 - t0 < 0.05:
            seg = f"{x1:.1f}"
        else:
            seg = f"{x0:.1f}+({x1 - x0:.1f})*(t-{t0:.2f})/{t1 - t0:.2f}"
        expr = f"if(lt(t,{t1:.2f}),{seg},{expr})"
    expr = expr.replace(",", "\\,")
    return f"crop={cw}:{ch}:{expr}:{(h - ch) // 2}"


def potong(w: int, h: int, rasio: float, cx: float, cy: float = 0.5, skala: float = 1.0) -> str:
    """Filter crop ffmpeg berasio `rasio` (lebar/tinggi) di sekitar titik (cx, cy). skala<1 = memperbesar (zoom)."""
    if w / h > rasio:
        ch = int(h * skala) // 2 * 2
        cw = int(ch * rasio) // 2 * 2
    else:
        cw = int(w * skala) // 2 * 2
        ch = int(cw / rasio) // 2 * 2
    cw, ch = min(cw, w // 2 * 2), min(ch, h // 2 * 2)
    x = int(min(max(cx * w - cw / 2, 0), w - cw))
    y = int(min(max(cy * h - ch / 2, 0), h - ch))
    return f"crop={cw}:{ch}:{x}:{y}"


# ── 6. Subtitle & banner (ASS) ──────────────────────────────────────────────
def waktu_ass(t: float) -> str:
    t = max(t, 0)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def warna_ass(hexa: str, alfa: str = "00") -> str:
    hexa = (hexa or "#FFFFFF").lstrip("#")
    return f"&H{alfa}{hexa[4:6]}{hexa[2:4]}{hexa[0:2]}".upper()


def tanpa_emoji(t: str) -> str:
    # libass tidak bisa menggambar emoji berwarna (muncul kotak) → buang
    return re.sub(r"[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u200D]", "", t).strip()


def ubah_huruf(t: str, mode: str) -> str:
    t = tanpa_emoji(t)
    return t.upper() if mode == "kapital" else t.lower() if mode == "kecil" else t


UKURAN = {"kecil": 0.82, "sedang": 1.0, "besar": 1.22}  # pengali ukuran preset
FONT_DIR = Path(__file__).resolve().parent / "font"  # font OFL dibundel → hasil sama di Mac & Windows

# Preset "Gaya klip" — pola dari riset dokumentasi/26 (bukan tiruan tampilan alat/kreator mana pun).
# mode: warna (kata aktif berwarna+membesar) · pop (grup memantul masuk, kata kunci berwarna) · komik (tepi tebal,
# kata kunci berwarna, kata aktif memantul) · tebal (kata aktif tipis→tebal) · karaoke (warna mengisi kata) ·
# terbaca (kotak hitam, teks kuning, kata aktif putih) · polos (tanpa sorot)
PRESET = {
    "sorot":   dict(font="Archivo Black", tebal=0, huruf="kapital", per=3, uk=78, warna="#FFD400", mode="warna", tepi=6, bayang=2),
    "pop":     dict(font="Anton", tebal=0, huruf="kapital", per=2, uk=112, warna="#FFD400", mode="pop", tepi=4, bayang=5),
    "komik":   dict(font="Bangers", tebal=0, huruf="kapital", per=3, uk=104, warna="#3BE477", mode="komik", tepi=10, bayang=0, spasi=2),
    "halus":   dict(font="Montserrat Light", font_aktif="Montserrat", tebal=0, huruf="kecil", per=4, uk=62, warna="#FFFFFF",
                    mode="tebal", tepi=1, bayang=4),
    "karaoke": dict(font="Montserrat ExtraBold", tebal=0, huruf="biasa", per=6, uk=66, warna="#FFD400", mode="karaoke", tepi=5, bayang=0),
    "terbaca": dict(font="Montserrat ExtraBold", tebal=0, huruf="kapital", per=4, uk=66, warna="#FFE600", mode="terbaca",
                    kotak="&H00000000", tepi=14, bayang=0),
    "minimal": dict(font="Montserrat Medium", tebal=0, huruf="biasa", per=6, uk=60, warna="#FFFFFF", mode="polos", tepi=2, bayang=3),
    "podcast": dict(font="Montserrat ExtraBold", tebal=0, huruf="kapital", per=3, uk=74, warna="#FFD400", mode="warna", tepi=5,
                    bayang=0, latar="blur", banner_kotak="&H00000000", progres=True),
    "maliki":  dict(font="Space Grotesk", tebal=1, huruf="biasa", per=3, uk=72, warna="#22D3EE", mode="warna",
                    kotak="&H38170F0B", tepi=16, bayang=0, banner_kotak="&H38170F0B", banner_warna="#22D3EE", progres=True),
}
LAMA = {"sorot": "sorot", "kotak": "terbaca", "garis": "minimal"}  # gaya_sub versi lama → preset


def gaya_akhir(g: dict) -> dict:
    """Preset sebagai dasar, lalu pilihan manual pengguna menimpanya."""
    nama = g.get("preset") or LAMA.get(g.get("gaya_sub", "sorot"), "sorot")
    c = {**PRESET.get(nama, PRESET["sorot"]), "preset": nama}
    for k in ("font", "warna", "huruf", "latar"):
        if g.get(k):
            if k == "font" and g[k] != c["font"]:
                c.pop("font_aktif", None)
                c["tebal"] = 1 if g[k] not in ("Archivo Black", "Anton", "Bangers") and "Bold" not in g[k] else 0
            c[k] = g[k]
    for k in ("progres", "zoom", "akun"):
        if k in g:
            c[k] = g[k]
    c["uk"] = int(c["uk"] * UKURAN.get(g.get("ukuran", "sedang"), 1.0))
    return c


def _norm(t: str) -> str:
    return re.sub(r"[^\w]", "", t.lower())


KATA_UMUM = set("yang dengan untuk karena tetapi kemudian sebenarnya mereka sendiri seperti bagaimana apakah sesuatu memang begitu "
                "akhirnya ternyata pokoknya soalnya makanya sebelumnya sesudahnya biasanya because really actually something".split())


def kunci_klip(kata: list, klip: Klip) -> set:
    """Kata kunci dari AI; kalau tidak ada (mode Lokal), pilih kata panjang/angka ±1 per 6 kata."""
    if klip.kata_kunci:
        return {_norm(w) for x in klip.kata_kunci for w in str(x).split()
                if (len(_norm(w)) >= 3 or _norm(w).isdigit()) and _norm(w) not in KATA_UMUM | {"sih", "dong", "deh", "nih", "kok", "yang"}}
    hasil = set()
    for i in range(0, len(kata), 6):
        calon = [_norm(k.teks) for k in kata[i:i + 6]]
        calon = [c for c in calon if (any(ch.isdigit() for ch in c) or len(c) >= 7) and c not in KATA_UMUM]
        if calon:
            hasil.add(max(calon, key=lambda c: (any(ch.isdigit() for ch in c), len(c))))
    return hasil


def tulis_ass(kal: list[Kalimat], klip: Klip, out: Path, g: dict, bar_atas: int) -> None:
    c = gaya_akhir(g)
    font, uk, mode = c["font"], c["uk"], c["mode"]
    sorot = warna_ass(c["warna"])
    putih = "&H00FFFFFF"
    # posisi_y = persen dari atas → MarginV untuk perataan bawah
    marg = int(1920 * (1 - float(g.get("posisi_y", 72)) / 100))
    spasi = c.get("spasi", 0)
    if c.get("kotak"):  # BorderStyle 3: kotak memakai OutlineColour
        utama = (f"Style: Utama,{font},{uk},{sorot if mode == 'terbaca' else putih},{putih},{c['kotak']},{c['kotak']},"
                 f"{c['tebal']},0,0,0,100,100,{spasi},0,3,{c['tepi']},0,2,90,90,{marg},1")
    elif mode == "karaoke":  # Primary = sudah terisi, Secondary = belum
        utama = f"Style: Utama,{font},{uk},{sorot},{putih},&H00000000,&H64000000,{c['tebal']},0,0,0,100,100,0,0,1,{c['tepi']},{c['bayang']},2,90,90,{marg},1"
    else:
        bayang = "&H78000000" if c["bayang"] else "&H64000000"
        utama = (f"Style: Utama,{font},{uk},{putih},{putih},&H00000000,{bayang},{c['tebal']},0,0,0,100,100,{spasi},0,1,"
                 f"{c['tepi']},{c['bayang']},2,90,90,{marg},1")
    banner_v = max(70, bar_atas // 2 - 70) if bar_atas > 160 else 150
    bw = warna_ass(c.get("banner_warna", "#FFFFFF"))
    fb, tb = (c["font_aktif"], 1) if c.get("font_aktif") else (font, c["tebal"])  # banner selalu tebal
    if c.get("banner_kotak"):
        banner = f"Style: Banner,{fb},{int(uk * 0.72)},{bw},{bw},{c['banner_kotak']},{c['banner_kotak']},{tb},0,0,0,100,100,0,0,3,18,0,8,80,80,{banner_v},1"
    else:
        banner = f"Style: Banner,{fb},{max(int(uk * 0.85), 54)},{bw},{bw},&H00000000,&H00000000,{tb},0,0,0,100,100,0,0,1,5,0,8,80,80,{banner_v},1"
    akun_style = f"Style: Akun,{font},34,&H40FFFFFF,&H40FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,2,0,8,80,80,{banner_v + int(uk * 1.1)},1"
    kepala = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
{utama}
{banner}
{akun_style}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    a, b = klip.mulai, klip.selesai
    baris = []
    bersih = lambda t: t.replace("{", "").replace("}", "")  # noqa: E731
    if g.get("banner", True) and klip.judul:
        teks = bersih(f"{g.get('awalan', '')}{klip.judul}{g.get('akhiran', '')}")
        baris.append(f"Dialogue: 1,{waktu_ass(0)},{waktu_ass(b - a)},Banner,,0,0,0,,{ubah_huruf(teks, 'kapital')}")
    if c.get("akun"):
        baris.append(f"Dialogue: 1,{waktu_ass(0)},{waktu_ass(b - a)},Akun,,0,0,0,,{bersih(str(c['akun']))[:40]}")
    if g.get("subtitle", True):
        kata = [k for s in kal for k in s.kata if k.selesai > a and k.mulai < b]
        kunci = kunci_klip(kata, klip)
        per = c["per"]
        huruf = c.get("huruf", "kapital")
        for i in range(0, len(kata), per):
            grup = kata[i:i + per]
            teks = [bersih(ubah_huruf(x.teks, huruf)) for x in grup]
            if mode == "karaoke":
                isi = []
                for j, x in enumerate(grup):
                    dur = ((grup[j + 1].mulai if j + 1 < len(grup) else x.selesai) - x.mulai)
                    isi.append("{\\kf" + str(max(int(dur * 100), 1)) + "}" + teks[j])
                baris.append(f"Dialogue: 0,{waktu_ass(grup[0].mulai - a)},{waktu_ass(grup[-1].selesai - a)},Utama,,0,0,0,,{' '.join(isi)}")
                continue
            for j, aktif in enumerate(grup):
                m = aktif.mulai - a
                sl = (grup[j + 1].mulai if j + 1 < len(grup) else grup[-1].selesai) - a
                isi = []
                for x, t in zip(grup, teks):
                    kk = _norm(x.teks) in kunci
                    if mode == "polos":
                        isi.append(t)
                    elif mode == "tebal":
                        isi.append(("{\\fn" + c["font_aktif"] + "\\b1}" if c.get("font_aktif") else "{\\b1}") + t + "{\\r}"
                                   if x is aktif else t)
                    elif mode == "terbaca":
                        isi.append("{\\c" + putih + "&}" + t + "{\\r}" if x is aktif else t)
                    elif mode in ("pop", "komik"):
                        warna = "{\\c" + sorot + "&}" if kk else ""
                        if x is aktif:
                            skala = "125" if mode == "komik" else "110"
                            isi.append("{" + warna.strip("{}") + "\\fscx" + skala + "\\fscy" + skala +
                                       "\\t(0,110,\\fscx106\\fscy106)}" + t + "{\\r}")
                        else:
                            isi.append(warna + t + ("{\\r}" if warna else ""))
                    else:  # warna
                        isi.append("{\\c" + sorot + "&\\fscx110\\fscy110}" + t + "{\\r}" if x is aktif else t)
                awal = "{\\fscx70\\fscy70\\t(0,120,\\fscx100\\fscy100)}" if mode == "pop" and j == 0 else ""
                baris.append(f"Dialogue: 0,{waktu_ass(m)},{waktu_ass(sl)},Utama,,0,0,0,,{awal}{' '.join(isi)}")
    out.write_text(kepala + "\n".join(baris) + "\n", encoding="utf-8")


def detik_kunci(kal: list[Kalimat], klip: Klip) -> list[float]:
    """Detik (relatif klip) kata kunci untuk zoom punch-in, berjarak minimal 3 detik, maks 8."""
    kata = [k for s in kal for k in s.kata if k.selesai > klip.mulai and k.mulai < klip.selesai]
    kunci, hasil = kunci_klip(kata, klip), []
    for k in kata:
        if _norm(k.teks) in kunci and (not hasil or k.mulai - klip.mulai - hasil[-1] >= 3):
            hasil.append(max(k.mulai - klip.mulai, 0))
    return hasil[:8]


# ── 7. Render satu klip dengan gaya ─────────────────────────────────────────
RASIO = {"9:16": 9 / 16, "1:1": 1.0, "4:3": 4 / 3, "16:9": 16 / 9}
FOKUS = {"kiri": 0.35, "tengah": 0.5, "kanan": 0.65}


def render(file: Path, klip: Klip, kal: list[Kalimat], out: Path, kerja: Path, w: int, h: int, g: dict) -> None:
    rasio = g.get("rasio", "9:16")
    layout = g.get("layout", "tunggal")
    fokus = g.get("fokus", "auto")
    wajah = info_wajah(file, klip.mulai, klip.selesai, w, h) if layout != "tunggal" else None
    cx = FOKUS.get(fokus, 0.5)
    durasi = klip.selesai - klip.mulai
    graf = []
    bar_atas = 0

    if layout == "facecam" and wajah:
        # atas 40%: wajah diperbesar · bawah 60%: isi layar (gameplay/presentasi)
        zoom = min(max(wajah["s"] * 3.2, 0.25), 1.0)
        graf.append(f"[0:v]split=2[va][vb]")
        graf.append(f"[va]{potong(w, h, 1080 / 768, wajah['x'], wajah['y'], zoom)},scale=1080:768,setsar=1[atas]")
        graf.append(f"[vb]{potong(w, h, 1080 / 1152, 0.5, 0.5)},scale=1080:1152,setsar=1[bawah]")
        graf.append("[atas][bawah]vstack=inputs=2[vid]")
    elif layout == "pip" and wajah:
        zoom = min(max(wajah["s"] * 2.4, 0.2), 1.0)
        graf.append(f"[0:v]split=2[va][vb]")
        graf.append(f"[va]{potong(w, h, 9 / 16, 0.5, 0.5)},scale=1080:1920,setsar=1[utama]")
        graf.append(f"[vb]{potong(w, h, 1.0, wajah['x'], wajah['y'], zoom)},scale=380:380,setsar=1,"
                    f"pad=392:392:6:6:color=0x22D3EE[kecil]")
        graf.append("[utama][kecil]overlay=x=W-w-60:y=220[vid]")
    elif rasio == "9:16":
        if fokus == "auto":  # ikuti pembicara per adegan, termasuk saat kamera berganti
            crop = potong_jejak(w, h, 9 / 16, jejak_wajah(file, klip.mulai, klip.selesai, w, h))
        else:
            crop = potong(w, h, 9 / 16, cx)
        graf.append(f"[0:v]{crop},scale=1080:1920:flags=lanczos,setsar=1[vid]")
    else:
        r = RASIO.get(rasio, 1.0)
        ih = int(1080 / r) // 2 * 2
        bar_atas = (1920 - ih) // 2
        graf.append("[0:v]split=2[va][vb]")
        crop = potong_jejak(w, h, r, jejak_wajah(file, klip.mulai, klip.selesai, w, h)) if fokus == "auto" \
            else potong(w, h, r, cx)
        graf.append(f"[va]{crop},scale=1080:{ih}:flags=lanczos,setsar=1[isi]")
        if gaya_akhir(g).get("latar", "hitam") == "blur":
            graf.append(f"[vb]{potong(w, h, 9 / 16, 0.5)},scale=540:960,boxblur=20:2,scale=1080:1920,eq=brightness=-0.08,setsar=1[latar]")
        else:
            graf.append(f"[vb]scale=1080:1920,drawbox=c=black:t=fill,setsar=1[latar]")
        graf.append(f"[latar][isi]overlay=x=0:y={bar_atas}[vid]")

    c = gaya_akhir(g)
    v = "vid"  # label video saat ini di filtergraph
    # zoom punch-in singkat pada kata kunci
    if c.get("zoom"):
        tt = detik_kunci(kal, klip)
        if tt:
            import cv2
            cap = cv2.VideoCapture(str(file)); fps = cap.get(cv2.CAP_PROP_FPS) or 30; cap.release()
            z = "+".join(f"between(it,{t:.2f},{t + 0.8:.2f})" for t in tt)
            graf.append(f"[{v}]zoompan=z='1+0.08*({z})':x='iw/2-(iw/zoom/2)':y='ih*0.4-(ih/zoom*0.4)':d=1:s=1080x1920:fps={fps:.3f}[vz]")
            v = "vz"
    # progress bar tipis di bawah (maju sesuai durasi klip)
    if c.get("progres"):
        graf.append(f"color=c={c['warna']}:s=1080x10:r=30:d={durasi:.2f}[pb]")
        graf.append(f"[{v}][pb]overlay=x='-W+W*t/{durasi:.2f}':y=H-10:eof_action=pass[vp]")
        v = "vp"
    if g.get("subtitle", True) or g.get("banner", True) or c.get("akun"):
        ass = kerja / f"{out.stem}.ass"
        tulis_ass(kal, klip, ass, g, bar_atas)
        fdir = kerja / "font"
        if FONT_DIR.exists() and not fdir.exists():
            try:
                fdir.symlink_to(FONT_DIR, target_is_directory=True)
            except OSError:  # Windows tanpa izin symlink → salin
                import shutil as _sh
                _sh.copytree(FONT_DIR, fdir)
        graf.append(f"[{v}]subtitles=filename='{ass.name}':fontsdir=font[vout]")
    else:
        graf.append(f"[{v}]null[vout]")

    # audio: suara asli (boost) + musik latar + SFX hook
    masukan = ["-ss", f"{klip.mulai:.2f}", "-t", f"{durasi:.2f}", "-i", str(file.resolve())]
    aud = [f"[0:a]volume={float(g.get('suara', 100)) / 100:.2f}[a0]"]
    campur = ["[a0]"]
    idx = 1
    musik = g.get("musik")
    if musik and Path(musik).exists():
        masukan += ["-stream_loop", "-1", "-i", str(Path(musik).resolve())]
        aud.append(f"[{idx}:a]volume={float(g.get('volume_musik', 18)) / 100:.2f},atrim=0:{durasi:.2f},"
                   f"afade=t=out:st={max(durasi - 1.5, 0):.2f}:d=1.5[am]")
        campur.append("[am]")
        idx += 1
    sfx = g.get("sfx")
    if sfx and Path(sfx).exists():
        masukan += ["-i", str(Path(sfx).resolve())]
        aud.append(f"[{idx}:a]volume=0.9[as]")
        campur.append("[as]")
        idx += 1
    if len(campur) > 1:
        aud.append(f"{''.join(campur)}amix=inputs={len(campur)}:duration=first:normalize=0,alimiter=limit=0.95[aout]")
    else:
        aud.append("[a0]anull[aout]")

    subprocess.run([
        ffmpeg(), "-y", "-v", "error", *masukan,
        "-filter_complex", ";".join(graf + aud), "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out.resolve()),
    ], check=True, cwd=kerja)


# ── 8. Subtitle dari berkas .srt & rentang ──────────────────────────────────
def detik(t: str) -> float:
    t = t.strip().replace(",", ".")
    bag = [float(x) for x in t.split(":")]
    s = 0.0
    for b in bag:
        s = s * 60 + b
    return s


def baca_srt(p: Path) -> list[Kalimat]:
    """SRT/TXT bertanda waktu → kalimat; waktu per kata dibagi rata (cukup untuk subtitle)."""
    teks = p.read_text(encoding="utf-8", errors="replace")
    hasil = []
    for blok in re.split(r"\n\s*\n", teks.strip()):
        m = re.search(r"(\d[\d:.,]*)\s*-->\s*(\d[\d:.,]*)", blok)
        if not m:
            continue
        isi = " ".join(b for b in blok[m.end():].strip().splitlines() if b.strip())
        isi = re.sub(r"<[^>]+>", "", isi).strip()
        a, b = detik(m.group(1)), detik(m.group(2))
        kata = isi.split()
        if not kata:
            continue
        lang = (b - a) / len(kata)
        hasil.append(Kalimat(a, b, isi, [Kata(a + i * lang, a + (i + 1) * lang, k) for i, k in enumerate(kata)]))
    if not hasil:
        sys.exit("Berkas subtitle tidak berisi penanda waktu (format SRT: 00:00:01,000 --> 00:00:03,000).")
    return hasil


def baca_rentang(r: str | None, panjang: float) -> tuple[float, float]:
    if not r:
        return 0.0, panjang
    a, _, b = r.partition("-")
    return detik(a) if a else 0.0, min(detik(b), panjang) if b else panjang


# ── Utama ───────────────────────────────────────────────────────────────────
def muat_transkrip(file: Path, a, kerja: Path) -> list[Kalimat]:
    if a.subtitle_file:
        log(f"Memakai subtitle dari {Path(a.subtitle_file).name}.")
        return baca_srt(Path(a.subtitle_file))
    cache = kerja / f"transkrip-{file.stem}-{a.model}.json"
    if cache.exists():
        log("Transkrip diambil dari cache.")
        return [Kalimat(k["mulai"], k["selesai"], k["teks"], [Kata(**x) for x in k["kata"]])
                for k in json.loads(cache.read_text())]
    kal = transkrip(file, a.model, a.bahasa)
    cache.write_text(json.dumps([asdict(k) for k in kal], ensure_ascii=False))
    return kal


def analisis(a, keluar: Path, kerja: Path) -> None:
    file, heatmap, judul = ambil_sumber(a.sumber, kerja)
    panjang, w, h = info_video(file)
    log(f"Video: {judul} — {panjang:.0f} detik, {w}x{h}. Heatmap YouTube: {'ada' if heatmap else 'tidak ada'}.")
    semua = muat_transkrip(file, a, kerja)
    ra, rb = baca_rentang(a.rentang, panjang)
    kal = [k for k in semua if k.selesai > ra and k.mulai < rb]
    if a.rentang:
        log(f"Rentang analisis: {ra:.0f}–{rb:.0f} detik ({len(kal)} kalimat).")

    if a.hanya_prompt:
        out = keluar / "prompt-claude.md"
        tulis_prompt(kal, a.durasi, a.jumlah, out, a.arahan)
        log(f"Prompt siap: {out}\n  Tempel ke Claude, simpan balasannya sebagai pilihan.json, lalu jalankan:\n"
            f"  uv run klip.py \"{a.sumber}\" --pilihan pilihan.json")
        return

    ringkasan, hashtag = "", []
    penyedia = (a.ai or baca_env().get("AI", "lokal")).lower()
    if a.pilihan or penyedia != "lokal":
        if a.pilihan:
            data = json.loads(Path(a.pilihan).read_text(encoding="utf-8"))
            sumber_ai = "pilihan.json"
        else:
            log(f"Meminta AI '{penyedia}' memilih momen…")
            tulis_prompt(kal, a.durasi, a.jumlah, kerja / "prompt.md", a.arahan)
            data = ambil_json(tanya_ai(penyedia, (kerja / "prompt.md").read_text(encoding="utf-8")))
            sumber_ai = penyedia
        if isinstance(data, dict):
            ringkasan, hashtag = data.get("ringkasan", ""), data.get("hashtag", [])
            data = data.get("klip", [])
        klips = [Klip(float(d["mulai"]), float(d["selesai"]), d.get("judul", ""), float(d.get("skor", 0) or 0),
                      d.get("alasan", ""), d.get("caption", ""), "",
                      [str(x) for x in (d.get("kata_kunci") or []) if x][:8]) for d in data]
        hooks = [d.get("hook") for d in data]
        # model kecil (mis. Ollama) kadang memilih potongan terlalu pendek → perpanjang ke akhir kalimat terdekat dari target
        for k in klips:
            if k.selesai - k.mulai < a.durasi * 0.6:
                target = k.mulai + a.durasi
                akhir = [x.selesai for x in kal if x.selesai >= target - 2]
                k.selesai = min(akhir[0] if akhir else target, panjang or target)
                log(f"Momen “{k.judul}” terlalu pendek → diperpanjang ke {k.selesai - k.mulai:.0f} dtk.")
        log(f"Memakai {len(klips)} momen dari {sumber_ai}.")
    else:
        log("Mencari momen terbaik (heatmap + energi suara + kepadatan kata + kata hook)…")
        klips = pilih_momen(kal, energi_audio(file), heatmap, a.durasi, a.jumlah, panjang, a.arahan)
        hooks = [None] * len(klips)
        sumber_ai = "lokal"

    daftar = []
    for i, (k, hk) in enumerate(zip(klips, hooks), 1):
        isi = [x for x in kal if x.selesai > k.mulai and x.mulai < k.selesai]
        k.kutipan = " ".join(x.teks for x in isi)[:400]
        if not k.caption:
            k.caption = k.judul
        if hk is None:
            kena = [x for x in isi if set(re.findall(r"\w+", x.teks.lower())) & KATA_HOOK or "?" in x.teks]
            hk = (kena[0] if kena else (isi[0] if isi else k)).mulai
        daftar.append({**asdict(k), "no": i, "hook": round(float(hk), 1), "file": ""})

    try:
        en = energi_audio(file)
        langkah = max(len(en) // 120, 1)
        energi_ringkas = [round(float(en[i:i + langkah].mean()), 3) for i in range(0, len(en), langkah)]
    except Exception:  # noqa: BLE001
        energi_ringkas = []
    # sumber untuk pratinjau di Studio + gambar kecil untuk riwayat
    tautan = keluar / f"sumber{file.suffix}"
    if not tautan.exists():
        try:
            tautan.symlink_to(file)
        except OSError:
            import shutil
            shutil.copy(file, tautan)
    t_gambar = (klips[0].mulai + 2) if klips else min(5, panjang / 2)
    subprocess.run([ffmpeg(), "-y", "-v", "error", "-ss", f"{t_gambar:.1f}", "-i", str(file), "-frames:v", "1",
                    "-vf", "scale=320:-2", str(keluar / "gambar.jpg")], check=False)
    (keluar / "info.json").write_text(json.dumps({
        "judul": judul, "durasi": round(panjang, 1), "lebar": w, "tinggi": h, "heatmap": heatmap,
        "energi": energi_ringkas, "ai": sumber_ai, "ringkasan": ringkasan, "hashtag": hashtag,
        "sumber": str(file), "pratinjau": tautan.name, "rentang": [ra, rb],
    }, ensure_ascii=False), encoding="utf-8")
    (keluar / "klip.json").write_text(json.dumps(daftar, ensure_ascii=False, indent=2), encoding="utf-8")
    (keluar / "transkrip.json").write_text(json.dumps([asdict(k) for k in kal], ensure_ascii=False), encoding="utf-8")
    log(f"Analisis selesai: {len(daftar)} momen.")


def render_terpilih(keluar: Path, kerja: Path, pilih: str | None, gaya: dict) -> None:
    info = json.loads((keluar / "info.json").read_text(encoding="utf-8"))
    daftar = json.loads((keluar / "klip.json").read_text(encoding="utf-8"))
    kal = [Kalimat(k["mulai"], k["selesai"], k["teks"], [Kata(**x) for x in k["kata"]])
           for k in json.loads((keluar / "transkrip.json").read_text(encoding="utf-8"))]
    nomor = {int(x) for x in pilih.split(",")} if pilih else {d["no"] for d in daftar}
    file = Path(info["sumber"])
    if not file.exists():
        file = keluar / info["pratinjau"]
    w, h = info.get("lebar"), info.get("tinggi")
    if not w:
        _, w, h = info_video(file)
    target = [d for d in daftar if d["no"] in nomor]
    for d in daftar:
        if d.get("jejak"):
            _JEJAK_SIAP[(round(d["mulai"], 2), round(d["selesai"], 2))] = d["jejak"]
    for n, d in enumerate(target, 1):
        k = Klip(d["mulai"], d["selesai"], d.get("judul_banner") or d["judul"], d.get("skor", 0),
                 kata_kunci=d.get("kata_kunci") or [])
        out = keluar / f"klip-{d['no']:02d}.mp4"
        log(f"Render {n}/{len(target)} {out.name}: {k.mulai:.1f}–{k.selesai:.1f}s  “{d['judul']}”")
        render(file, k, kal, out, kerja, w, h, gaya)
        d["file"] = out.name
        (keluar / "klip.json").write_text(json.dumps(daftar, ensure_ascii=False, indent=2), encoding="utf-8")
    (keluar / "gaya.json").write_text(json.dumps(gaya, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"Selesai. {len(target)} klip di {keluar}")


def main() -> None:
    p = argparse.ArgumentParser(description="Potong video panjang jadi klip pendek 9:16.")
    p.add_argument("sumber", nargs="?", help="file video atau link YouTube")
    p.add_argument("--jumlah", type=int, default=3, help="jumlah klip (default 3)")
    p.add_argument("--durasi", type=int, default=30, help="target detik per klip (default 30)")
    p.add_argument("--model", default="small", help="model whisper: tiny/base/small/medium/large-v3")
    p.add_argument("--bahasa", default=None, help="kode bahasa, mis. id atau en (default otomatis)")
    p.add_argument("--keluar", default="hasil-klip", help="folder hasil")
    p.add_argument("--tanpa-wajah", action="store_true", help="bingkai tengah, jangan ikuti wajah")
    p.add_argument("--tanpa-subtitle", action="store_true")
    p.add_argument("--warna", default=None, help="warna sorot subtitle (hex); kosong = warna preset")
    p.add_argument("--hanya-prompt", action="store_true", help="Opsi B: tulis prompt Claude lalu berhenti")
    p.add_argument("--pilihan", help="Opsi B: JSON momen dari Claude")
    p.add_argument("--arahan", default="", help="momen yang dicari, mis. 'momen lucu' atau 'tips praktis'")
    p.add_argument("--ai", default=None, help="pemilih momen: lokal (default), gemini, openai (Ollama dll.), "
                        "claude-code (langganan Claude), codex (langganan ChatGPT), opencode")
    p.add_argument("--rentang", help="bagian video yang dianalisis, mis. 10:00-25:30")
    p.add_argument("--subtitle-file", help="pakai subtitle .srt sendiri (lewati transkripsi)")
    p.add_argument("--hanya-analisis", action="store_true", help="cari momen tanpa render")
    p.add_argument("--render", action="store_true", help="render dari hasil analisis di --keluar")
    p.add_argument("--jejak", type=int, help="hitung jejak wajah klip nomor N (disimpan di klip.json, dipakai pratinjau)")
    p.add_argument("--pilih", help="nomor klip yang dirender, mis. 1,3,4 (default semua)")
    p.add_argument("--uji-ai", help="uji sambungan AI (lokal/gemini/openai/claude-code/codex/opencode)")
    p.add_argument("--gaya", help="JSON gaya render (rasio, latar, fokus, layout, banner, subtitle, musik, …)")
    a = p.parse_args()

    if a.uji_ai:
        if a.uji_ai == "lokal":
            print("SIAP (mode lokal tidak memakai AI luar)")
            return
        jawab = tanya_ai(a.uji_ai, "Ini uji sambungan. Balas persis satu kata saja: SIAP").strip()
        print(jawab[:200])
        return

    keluar = Path(a.keluar).resolve()
    kerja = keluar / ".kerja"
    kerja.mkdir(parents=True, exist_ok=True)
    gaya = {**({"warna": a.warna} if a.warna else {}), "subtitle": not a.tanpa_subtitle, "fokus": "tengah" if a.tanpa_wajah else "auto",
            "banner": False}
    if a.gaya:
        isi = a.gaya if a.gaya.lstrip().startswith("{") else Path(a.gaya).read_text(encoding="utf-8")
        gaya.update(json.loads(isi))

    if a.jejak:
        info = json.loads((keluar / "info.json").read_text(encoding="utf-8"))
        daftar = json.loads((keluar / "klip.json").read_text(encoding="utf-8"))
        d = next(x for x in daftar if x["no"] == a.jejak)
        file = Path(info["sumber"])
        if not file.exists():
            file = keluar / info["pratinjau"]
        w, h = info.get("lebar"), info.get("tinggi")
        if not w:
            _, w, h = info_video(file)
        d["jejak"] = [[round(t, 2), round(x, 3)] for t, x in jejak_wajah(file, d["mulai"], d["selesai"], w, h)]
        (keluar / "klip.json").write_text(json.dumps(daftar, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(d["jejak"]))
        return
    if a.render:
        render_terpilih(keluar, kerja, a.pilih, gaya)
        return
    if not a.sumber:
        sys.exit("Isi file video atau link YouTube.")
    analisis(a, keluar, kerja)
    if a.hanya_analisis or a.hanya_prompt:
        return
    render_terpilih(keluar, kerja, a.pilih, gaya)


if __name__ == "__main__":
    main()
