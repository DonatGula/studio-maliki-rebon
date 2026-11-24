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
2. **Tinjau & edit** — setiap adegan tampil sebagai kartu editor. Ubah judul layar, ikon, narasi, kata kunci subtitle, durasi, arahan visual, gerakan, dan transisi. Urutan adegan dapat dipindah, adegan dapat ditambah/dihapus, dan draft bisa disimpan tanpa render.
3. **Render video** — tombol Render video mengirim naskah yang sudah diedit ke backend lokal, lalu Remotion membuat MP4.

Naskah disimpan di folder proyek lokal sebagai `naskah.json`. Jika browser ditutup, draft terakhir yang disimpan tetap ada di folder data Studio. Untuk membuka proyek draft, gunakan Riwayat; editor adegan akan ditampilkan lagi saat proyek draft dimuat.

Studio juga dapat dibuka langsung di browser dengan menjalankan `uv run studio.py --browser` dari folder `studio`; alamat lokal default adalah `http://127.0.0.1:8787`. Server hanya mendengarkan di komputer sendiri.

## Editor storyboard, preview adegan, dan timeline

Studio lokal menyediakan alur kerja bertahap:
- Tinjau naskah AI sebelum render.
- Edit tiap adegan, termasuk judul, narasi, ikon, durasi, arahan visual, gerak, dan transisi.
- Simpan draft, atur urutan, tambah/hapus adegan.
- Render preview satu adegan saja (540×960) atau minta AI membuat ulang satu adegan tanpa mengganti adegan lainnya.
- Timeline visual menunjukkan proporsi durasi tiap adegan dan dapat dipakai untuk melompat ke kartu adegan terkait.

## Produksi batch

Di halaman Motion, masukkan 1–5 topik (satu topik per baris) pada bagian Batch Production. Aplikasi membuat naskah dan merendernya satu per satu ke folder proyek terpisah. Jika satu topik gagal, item berikutnya tetap dicoba; hasil dan kegagalan tiap topik dilaporkan di halaman hasil batch.

## Preset ekspor

- `shorts`: YouTube Shorts, kanvas 1080×1920, CRF 18.
- `tiktok`: TikTok, kanvas 1080×1920, CRF 20.
- `reels`: Instagram/Facebook Reels, kanvas 1080×1920, CRF 19.
- `draft`: render cepat 540×960, CRF 23.
- `high`: 1350×2400, CRF 16.

Ketiga preset platform menggunakan rasio 9:16; perbedaannya adalah profil kompresi. Preview adegan menggunakan profil draft agar proses pemeriksaan lebih cepat.

## Motion Skills

Generator naskah memakai panduan Motion Skills dari proyek [iart-ai/motion-skills](https://github.com/iart-ai/motion-skills). Remotion tetap menjadi renderer utama; skill adalah instruksi kreatif untuk AI, bukan plugin renderer.

Saat ini tersedia 16 file skill dari 11 pack:
- Motion Design
- TikTok / Short-form Video
- Explainer Video
- Kinetic Typography
- JavaScript Animation
- YouTube / Podcast (Audiogram)
- B-roll for Talking Head
- Data Animation (Infografis)
- Map Animation
- E-commerce Video (Slideshow, Demo Produk, Promo)
- Ad Creative Video

Katalog `skills/packs.json` mencatat seluruh 19 pack dan 56 skill upstream. Empat pack sudah lengkap dan tujuh pack masih parsial. Skill yang belum disalin ke folder lokal tidak ditawarkan ke engine.

Pemilihan otomatis berdasarkan topik mempertahankan empat skill fondasi dan menambahkan skill topikal yang paling relevan. Pemilihan manual dibatasi maksimal lima skill, baik dari UI maupun CLI:

```bash
node naskah.mjs "Fakta menarik tentang luar angkasa" --skills=explainer-video,kinetic-typography
```

ID skill lokal yang tersedia:
`animation-principles`, `motion-art-direction`, `remotion-video`, `short-form-video`, `caption-animation`, `explainer-video`, `kinetic-typography`, `javascript-animation`, `audiogram`, `talking-head-b-roll`, `animated-infographic`, `map-animation`, `photo-slideshow`, `product-demo-video`, `promo-video`, dan `ad-creative-video`.

### Metadata storyboard ke renderer

- `visual`: menjadi konteks utama saat generator SVG AI membuat ilustrasi adegan (jika fitur gambar AI diaktifkan).
- `gerak`: adapter native Remotion mengenali arahan sederhana seperti melayang, berdenyut, dan berputar.
- `transisi`: adapter mengenali fade, slide dari arah tertentu, dan zoom saat adegan masuk.
- Adapter tidak menambahkan dependency baru. Arahan yang membutuhkan asset atau library eksternal tidak otomatis dijalankan.

Penerapan gerak/transisi masih berbasis kata kunci, bukan motion DSL lengkap. Hasil akhir perlu diperiksa saat pengujian visual. Field lama dan struktur JSON naskah tetap dipertahankan.

Atribusi dan lisensi sumber: [skills/ATTRIBUTION.md](skills/ATTRIBUTION.md). Skill packs upstream menggunakan MIT; integrasi ini tidak mengubah lisensi utama Studio Maliki yang tercantum di `../LISENSI.md`.
