# Fondasi Integrasi Lemo-Opuscar

Status: Tahap 2 — riset dan rancangan integrasi  
Target branch: `feat/lemo-opuscar-foundation`  
Sumber referensi: https://github.com/lemomo-ai/lemo-opuscar

Dokumen ini adalah rancangan implementasi Studio Maliki Reborn. Ini bukan salinan dokumentasi, prompt, atau aset Lemo-Opuscar.

## 1. Keputusan integrasi

- Lemo-Opuscar dipakai sebagai referensi art direction, tata adegan, bahasa kamera, gerak, ritme, dan kategori gaya.
- Studio Maliki tidak mengganti Remotion dengan renderer Lemo-Opuscar. Remotion tetap menjadi satu-satunya renderer video aplikasi.
- Tidak menyalin atau membundel `DIRECTOR.md`, `TECHNIQUE.md`, `STYLE.md`, `DEMO.md`, prompt, poster, still, film demo, atau aset Lemo-Opuscar ke dalam aplikasi.
- Implementasi fitur dan prompt aplikasi ditulis mandiri untuk kebutuhan Studio Maliki. Bila suatu saat kode MIT dari Lemo-Opuscar benar-benar dipakai, file dan atribusinya harus ditinjau satu per satu terlebih dahulu.
- Tidak memasang toolchain Lemo-Opuscar lengkap sebagai dependency aplikasi pada tahap ini. Toolchain upstream meminta Node 20+, FFmpeg 7+, Python 3.11+/uv, dan dapat memasang paket tambahan per gaya; ini akan menambah beban instalasi dan membuat dua jalur render.
- Keluaran awal tetap vertikal 9:16 dan kompatibel dengan alur suara, subtitle, batch, preview, serta preset ekspor yang sudah ada.

## 2. Hasil pembacaan repository Studio Maliki

Bagian yang sudah ada dan akan menjadi titik integrasi:

| File | Tanggung jawab saat ini | Peran setelah pengembangan |
|---|---|---|
| `motion/PROMPT-NASKAH.md` | Instruksi AI untuk naskah per adegan | Dikembangkan agar menghasilkan arahan adegan visual, bukan daftar ikon |
| `motion/naskah.mjs` | Meminta AI dan menyimpan JSON storyboard | Menormalisasi metadata adegan baru sambil mempertahankan format lama |
| `motion/src/Video.tsx` | Composition Remotion, sequence, audio, subtitle, judul, dan klip | Tetap menjadi composition utama; memilih renderer visual per adegan |
| `motion/src/tema.tsx` | Tema, warna, tipografi, latar, dan dekorasi | Menyediakan token gaya visual, bukan pusat adegan karakter |
| `motion/src/ilustrasi.tsx` | Filter SVG untuk gaya ilustrasi | Tidak dianggap sebagai sistem karakter; dapat tetap dipakai untuk efek yang relevan |
| `motion/src/motionAdegan.tsx` | Adapter gerak/transisi sederhana | Diperluas setelah ada model scene dan komponen karakter |
| `motion/buat.mjs` | Menyiapkan suara dan props lalu menjalankan Remotion | Tetap menjadi entry point render |
| `motion/skills/engine.mjs` | Memilih dan menyusun panduan Motion Skills lama | Akan diganti/diadaptasi pada tahap prompt setelah sistem baru siap |

Catatan penting: properti `visual` saat ini adalah teks arahan/label; properti itu belum otomatis menghasilkan gambar adegan. `MotionAdegan` saat ini hanya membungkus konten yang sudah dirender dengan transformasi sederhana. Jadi integrasi tidak boleh menganggap fitur karakter dan lingkungan sudah tersedia.

## 3. Pemetaan konsep Lemo-Opuscar

README upstream saat diperiksa menyebut 99 gaya dalam 15 kategori. Indeks gaya menunjukkan ragam yang luas; tidak semua gaya adalah animasi karakter. Karena itu katalog tidak akan diperlakukan sebagai 99 template yang harus seluruhnya disalin.

Kelompok referensi yang paling relevan:

- **Painting & Illustration:** Crayon Picture Book, Watercolor Brush, Impasto Oil Painting, Urban Sketch, Colored-Pencil Science Illustration.
- **Cartoons:** 1930s Rubber Hose Cartoon, 80s Cel Anime, Sci-Fi Sitcom Toon, Mid-century Cartoon.
- **Traditional Crafts:** Shadow Puppetry, Ukiyo-e, Red Paper-cut, Paper-cut Lightbox.
- **3D & Miniature:** Paper Pop-up Book, Isometric People Scene, Crayon World 3D, Low-poly Isometric Island.
- **Sketch & Board:** dapat dipakai untuk variasi video penjelasan, bukan gaya utama karakter.

Gaya default Studio Maliki tetap mengikuti video referensi yang dipilih pengguna: **2D Animated Storytelling** dengan karakter, lingkungan, properti, staging, gerakan, dan kamera. Nama ini adalah profil visual internal Studio Maliki, bukan klaim bahwa ia merupakan salah satu gaya resmi Lemo-Opuscar.

Gaya alternatif dipilih berdasarkan kecocokan topik dan dapat dipilih pengguna. Pilihan gaya tidak boleh mengubah struktur data inti storyboard.

## 4. Arsitektur target

Alur target:

```text
Topik / naskah pengguna
        |
        v
AI Script + Storyboard
        |
        v
Scene Schema (data terstruktur dan tervalidasi)
        |
        +--> Style Profile (palet, bentuk, tekstur, aturan animasi)
        |
        +--> Character Bible (identitas, proporsi, pakaian, warna, ekspresi)
        |
        +--> Environment & Props (lokasi, latar, benda, posisi)
        |
        +--> Shot Direction (framing, angle, kamera, durasi, aksi)
        |
        v
Scene Visual Renderer (komponen React/SVG/Canvas deterministik)
        |
        v
Remotion Composition
        |
        +--> Narasi / audio
        +--> Subtitle
        +--> Transisi
        |
        v
MP4 + preset ekspor
```

Prinsip arsitektur:

1. Data storyboard menjelaskan *apa yang terjadi*; style profile menjelaskan *bagaimana tampilannya*; renderer menggambar hasilnya.
2. Identitas karakter disimpan di tingkat proyek dan dirujuk oleh banyak adegan agar penampilan tetap konsisten.
3. Latar dan properti menjadi elemen adegan tersendiri, bukan satu emoji/ikon besar.
4. Gerak karakter, gerak kamera, dan transisi dipisah agar dapat diedit secara mandiri.
5. Render harus deterministik: frame yang sama menghasilkan gambar yang sama; tidak menggunakan nilai acak tanpa seed atau state yang bergantung pada urutan render.
6. Renderer harus dapat fallback ke visual sederhana yang valid jika sebuah aset tidak tersedia; jangan menggagalkan seluruh video.
7. Data proyek lama tetap dapat dibuka. Kolom baru bersifat opsional dan normalisasi dilakukan sebelum render.

## 5. Bentuk data adegan yang diusulkan

Ini rancangan skema, belum implementasi:

```json
{
  "judul": "Kenapa tubuh butuh tidur?",
  "gaya": "storytelling-2d",
  "motion": {
    "styleId": "storytelling-2d",
    "aspectRatio": "9:16"
  },
  "karakter": [
    {
      "id": "tokoh-utama",
      "deskripsi": "remaja dengan kaus biru dan rambut hitam",
      "warna": ["#..."],
      "ciriTetap": ["kaus biru", "rambut hitam"]
    }
  ],
  "adegan": [
    {
      "judul": "Tubuh mulai lelah",
      "teks": "Saat malam tiba, tubuh mulai memberi sinyal untuk beristirahat.",
      "durasi": 5,
      "visual": "Kamar tidur sederhana pada malam hari",
      "karakter": ["tokoh-utama"],
      "lingkungan": "kamar-tidur-malam",
      "objek": ["tempat-tidur", "lampu-meja"],
      "aksi": [
        {"subjek": "tokoh-utama", "gerakan": "menguap lalu berjalan ke tempat tidur"}
      ],
      "kamera": {
        "framing": "medium",
        "angle": "eye-level",
        "gerak": "slow-push-in"
      },
      "transisi": "cut"
    }
  ]
}
```

Ketentuan kompatibilitas:

- Kolom lama `judul`, `teks`, `kunci`, `ikon`, `gambar`, `durasi`, `suara`, `klip`, `visual`, `gerak`, dan `transisi` tidak dihapus secara mendadak.
- `ikon` tetap boleh menjadi aksen kecil bila sesuai, tetapi bukan visual utama.
- `gambar` lama tetap dapat dipakai untuk proyek lama.
- Properti baru akan divalidasi dan dinormalisasi sebelum mencapai Remotion.
- Bentuk final skema akan ditetapkan saat Tahap 3 setelah prototipe renderer dipilih.

## 6. Strategi visual awal

Urutan implementasi yang disarankan:

1. **Prototipe 2D berbasis kode** memakai React/SVG dan bentuk-bentuk reusable untuk karakter, pose, properti, dan latar. Ini mengurangi dependency dan menjaga render konsisten.
2. **Character Bible** untuk mengunci proporsi, palet, pakaian, rambut, dan ciri khas tokoh.
3. **Pose dan aksi** yang dapat dipakai ulang: berdiri, berjalan, duduk, menunjuk, memegang, mengambil, membuka, menoleh, dan bereaksi.
4. **Kamera**: wide/medium/close-up, pan, push-in, pull-out, dan parallax latar.
5. **Aset gambar eksternal** (jika kelak dipakai) harus punya identitas, sumber, lisensi, dan fallback yang jelas. Tidak mengandalkan layanan gambar berbayar sebagai syarat render dasar.

Jangan mencoba membangun 99 gaya sekaligus. Tahap pertama renderer harus membuktikan satu adegan karakter lengkap dan konsisten dalam gaya default.

## 7. Batasan lisensi dan atribusi

Pemeriksaan LICENSE upstream pada 24 November 2026 menemukan pemisahan lisensi berikut:

- Kode Lemo-Opuscar: MIT.
- File dokumentasi Markdown, termasuk `DIRECTOR.md`, `TECHNIQUE.md`, dan semua `STYLE.md`: CC BY-NC 4.0.
- Film demo, poster, still, dan subtitle demo tertentu: CC BY 4.0, dengan atribusi dan tetap tunduk pada hak pihak ketiga.
- Film yang dibuat pengguna dengan library: dinyatakan milik pembuat film, tetapi aset pihak ketiga yang dipakai tetap mengikuti lisensinya.
- LICENSE juga memberi izin tambahan untuk membaca, mengikuti, menyalin, dan mengadaptasi dokumentasi untuk membuat film sendiri, termasuk film komersial, serta memasukkannya ke file proyek film yang diserahkan. Izin tambahan itu secara eksplisit tidak mencakup membagikan dokumentasi/adaptasinya di luar orang dan file proyek film tersebut, atau menjualnya. Memasukkan dokumentasi/prompt itu ke dalam produk atau layanan memerlukan lisensi komersial menurut bagian COMMERCIAL LICENCE.

Karena Studio Maliki adalah aplikasi yang didistribusikan sebagai perangkat lunak, rancangan aman untuk tahap ini adalah:

- Jangan salin/bundel Markdown, prompt, STYLE.md, demo, still, poster, atau aset upstream ke aplikasi.
- Tulis prompt dan style profile Studio Maliki secara mandiri; gunakan hanya kebutuhan dan keputusan visual pengguna sebagai spesifikasi.
- Jangan menyalin karakter, shot spesifik, logo, musik, font, foto, atau aset pihak ketiga dari demo.
- Jika ingin mengemas dokumentasi atau prompt Lemo-Opuscar ke dalam aplikasi, minta dan dapatkan lisensi tertulis yang sesuai terlebih dahulu.
- Pertahankan seluruh kredit dan syarat lisensi Maliki yang sudah ada. Integrasi ini tidak mengubah lisensi dasar proyek.
- Pemeriksaan ini bukan nasihat hukum; sebelum distribusi komersial aplikasi atau layanan, minta konfirmasi pemegang hak bila ada keraguan.

Referensi lisensi: https://github.com/lemomo-ai/lemo-opuscar/blob/main/LICENSE

## 8. Batas Tahap 2 dan kriteria selesai

Termasuk Tahap 2:

- Memetakan fitur dan file yang akan disentuh.
- Memilih pendekatan integrasi yang mempertahankan Remotion.
- Menentukan batas lisensi dan aset yang boleh/tidak boleh dibundel.
- Menetapkan arsitektur target dan rancangan skema awal.

Tidak termasuk Tahap 2:

- Menghapus 24 template/gaya lama.
- Mengubah generator naskah produksi.
- Mengimplementasikan karakter/rig/renderer baru.
- Menambah dependency atau mengubah pipeline installer.
- Mengubah UI editor atau batch.

Tahap 2 dianggap selesai setelah rancangan ini ditinjau. Tahap 3 baru dimulai dengan prototipe renderer 2D satu adegan dan tidak akan menghapus jalur lama sebelum uji render berhasil.
