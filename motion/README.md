# Motion — dari topik jadi video motion graphic 9:16

Cukup tulis naskah per adegan. Alat ini membuat suara narator, subtitle dengan kata kunci disorot, dan animasi, lalu merender
MP4 **1080×1920**. Ada 3 gaya: `garis`, `neon`, `kertas`. Render di Mac sendiri, tanpa watermark.
Riset ada di `dokumentasi/22-riset-alat-motion.md`.

## Langkah 1 — Pasang Node.js (sekali saja)
Unduh versi LTS dari https://nodejs.org lalu pasang. ffmpeg tidak perlu dipasang terpisah karena Remotion sudah membawanya.

## Langkah 2 — Pasang alat
```bash
cd alat/motion
npm install
```

## Langkah 3 — Coba contoh
```bash
node buat.mjs naskah/contoh.json
```
Hasilnya `hasil/contoh-garis.mp4`. Coba gaya lain:
```bash
node buat.mjs naskah/contoh.json --gaya=neon
```

## Opsi A — Gratis
1. Buka Claude (akun gratis), salin isi `PROMPT-NASKAH.md`, lalu ganti `[TOPIK]` dengan topikmu.
2. Simpan balasan JSON dari Claude sebagai `naskah/topikku.json`.
3. Render:
```bash
node buat.mjs naskah/topikku.json
```
Suara memakai **Damayanti** (suara Indonesia bawaan macOS, gratis).
Ingin suara sendiri? Rekam satu file WAV per adegan, lalu taruh di `rekaman/topikku/01.wav`, `02.wav`, dan seterusnya. Alat otomatis memakainya.

## Opsi B — Berbayar
- **Claude Pro + Claude Code:** ketik *"buat video motion tentang [topik] dengan alat/motion, gaya neon, lalu render"*.
  Claude Code akan menulis JSON, menjalankan `buat.mjs`, dan merevisi sampai pas.
- **Suara lebih natural (ElevenLabs, berbayar):** buat suara tiap adegan, simpan sebagai WAV ke `rekaman/topikku/NN.wav`, lalu render lagi.

## Isi naskah JSON
| Kolom | Arti |
|---|---|
| `judul` | judul video |
| `gaya` | `garis` / `neon` / `kertas` |
| `handle` | teks di pojok atas, mis. `@akunmu` |
| `aksen` | (opsional) warna utama, mis. `"#22C55E"` |
| `adegan[].judul` | tulisan besar di layar (2–5 kata, kata terakhir diberi warna aksen) |
| `adegan[].teks` | kalimat narasi, juga dipakai sebagai subtitle |
| `adegan[].kunci` | kata yang disorot di subtitle |
| `adegan[].ikon` | emoji besar di atas judul |

## Pratinjau dan ubah tampilan
```bash
npm run studio
```
Remotion Studio terbuka di browser. Tema setiap gaya ada di `src/Video.tsx` (objek `TEMA` dan komponen `Latar`).

## Lisensi Remotion
Gratis untuk individu dan perusahaan sampai 3 orang (remotion.dev/license). Tim yang lebih besar perlu lisensi Company.

## Hibrid: klip asli + kartu animasi (gabungan dengan `alat/klip`)
Satu reel yang menyelipkan kartu animasi di antara klip asli: pembuka → kartu "Momen 1" → klip 1 → kartu "Momen 2" → klip 2 → ajakan.
1. Potong dulu video panjangnya dengan `alat/klip` (hasilnya `alat/klip/hasil-klip/klip.json` dan `klip-NN.mp4`).
2. Buat naskah hibrid:
```bash
node hibrid.mjs ../klip/hasil-klip --gaya=neon --judul="Judul videomu" --handle=@akunmu
```
3. Ubah teks kartu di `naskah/hibrid.json` sendiri (gratis) atau minta Claude (Pro: Claude Code bisa langsung mengedit dan merender).
4. Render:
```bash
node buat.mjs naskah/hibrid.json
```
Setiap adegan yang punya `"video": "path/ke/klip.mp4"` diputar layar penuh dengan label judul di atas (subtitle karaoke sudah ada dari `alat/klip`).
Adegan tanpa `video` menjadi kartu animasi bersuara. Kartu dan klip bisa dicampur dalam urutan apa pun.

## Topik → naskah otomatis dengan AI milikmu sendiri (opsional)
```bash
cp .env.contoh .env
```
Isi kunci AI-mu di `.env` (Gemini gratis, Ollama gratis, atau OpenAI-compatible; langganan Claude/ChatGPT lewat CLI di Studio), lalu:
```bash
node naskah.mjs "3 kebiasaan pagi produktif" --ai=gemini --gaya=neon
```
```bash
node buat.mjs naskah/3-kebiasaan-pagi-produktif.json
```
Periksa isi naskah sebelum render, karena AI bisa salah. Langganan Claude Pro **tidak** termasuk API. Pengguna Pro pakai
`PROMPT-NASKAH.md` di claude.ai, atau minta Claude Code membuat naskah dan merender langsung.
File `.env` berisi kuncimu. Jangan dibagikan ke orang lain.


## Alur baru: tinjau naskah sebelum render

Dari halaman Motion di Studio, proses sekarang dipisah menjadi dua tahap:

1. **Buat naskah** — AI menghasilkan naskah/storyboard JSON, atau pengguna memasukkan JSON sendiri.
2. **Tinjau & edit** — naskah ditampilkan di editor JSON dalam browser. Periksa judul, teks narasi, jumlah adegan, dan metadata visual; perubahan dapat dilakukan sebelum render.
3. **Render video** — tombol Render video mengirim naskah yang sudah diedit ke backend lokal, lalu Remotion membuat MP4.

Naskah disimpan di folder proyek lokal sebagai `naskah.json`. Jika browser ditutup setelah tahap pertama, proyek dan naskah tetap ada di folder data Studio. Untuk membuka proyek draft, gunakan Riwayat/ folder proyek; editor draft akan ditampilkan lagi saat proyek draft dimuat.

Studio juga dapat dibuka langsung di browser dengan menjalankan `uv run studio.py --browser` dari folder `studio`; alamat lokal default adalah `http://127.0.0.1:8787`. Server hanya mendengarkan di komputer sendiri.

## Motion Skills (integrasi awal)

Generator naskah kini memakai panduan Motion Skills dari proyek iart.ai untuk membantu AI menentukan arah visual, bahasa gerak, dan storyboard per adegan. Remotion tetap menjadi renderer; Motion Skills bukan plugin rendering.

Skill pack awal yang disertakan:
- Motion Design (animation principles, art direction, Remotion)
- TikTok / Short-form Video (short-form structure, animated captions)
- Explainer Video
- Kinetic Typography
- JavaScript Animation (sebagai referensi storyboard; bukan pengganti pipeline Remotion)

Secara default skill dipilih otomatis dari topik. Untuk memilih manual melalui terminal:

```bash
node naskah.mjs "Fakta menarik tentang luar angkasa" --skills=explainer-video,kinetic-typography
```

ID skill yang tersedia: `animation-principles`, `motion-art-direction`, `remotion-video`, `short-form-video`, `caption-animation`, `explainer-video`, `kinetic-typography`, dan `javascript-animation`. Gunakan `--skills=auto` untuk pemilihan otomatis.

Hasil JSON tetap mempertahankan struktur naskah lama dan menambahkan metadata `motion.skills`, `motion.arah_visual`, `motion.bahasa_gerak`, serta arahan `visual`, `gerak`, dan `transisi` per adegan. Metadata ini menjadi dasar editor storyboard/adegan pada fase berikutnya. Renderer saat ini tetap menggunakan field visual yang sudah didukung oleh template yang ada.

Atribusi dan lisensi sumber: [skills/ATTRIBUTION.md](skills/ATTRIBUTION.md). Skill packs upstream menggunakan MIT; integrasi ini tidak mengubah lisensi utama Studio Maliki yang tercantum di `../LISENSI.md`.
