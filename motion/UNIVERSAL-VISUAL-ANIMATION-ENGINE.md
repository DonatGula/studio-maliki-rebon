# Rancangan Universal Visual Animation Engine

Status: Proposal arsitektur dan roadmap — belum implementasi  
Branch: `docs/universal-visual-animation-engine`  
Proyek: Studio Maliki Reborn

## 1. Arah produk

Studio Maliki Reborn tidak dibatasi sebagai aplikasi animasi karakter 2D. Tujuannya adalah menjadi aplikasi **visual storytelling dan motion graphics** yang dapat memilih bahasa visual sesuai isi naskah.

Karakter manusia hanyalah salah satu pilihan visual. Dalam adegan tertentu, fokus utama dapat berupa objek, tipografi, ilustrasi, diagram, lingkungan, atau gabungan beberapa elemen.

Prinsip utama:

> Visual mengikuti cerita; cerita tidak dipaksakan mengikuti satu jenis animasi.

Naskah dan topik yang berbeda harus dapat menghasilkan komposisi visual yang berbeda tanpa membuat renderer khusus untuk setiap cerita.

## 2. Mode fokus visual

Setiap adegan dapat memilih satu fokus utama atau menggabungkan beberapa fokus.

| Mode | Fokus | Contoh penggunaan |
|---|---|---|
| `character` | Karakter manusia/figur | Dialog, aktivitas, emosi, gerakan tubuh |
| `object` | Benda atau produk | Ponsel, jam, kendaraan, makanan, produk |
| `typography` | Kata, huruf, angka | Hook, kutipan, statistik, penekanan narasi |
| `graphic` | Bentuk, diagram, peta, infografik | Edukasi, penjelasan proses, data |
| `environment` | Ruang dan suasana | Kota, kamar, dapur, lanskap |
| `mixed` | Kombinasi beberapa lapisan | Karakter + objek + teks + lingkungan |

Mode adalah arahan komposisi, bukan template video tetap. Satu video dapat berganti mode dari adegan ke adegan.

## 3. Contoh bahasa visual

### A. Character-based storytelling
Contoh: seseorang menerima kabar mengejutkan.
- Karakter membaca ponsel.
- Kepala dan tubuh bereaksi.
- Kamera mendekat ke ekspresi.
- Objek ponsel tetap terhubung dengan tangan.

### B. Object-based storytelling
Contoh: memperkenalkan sebuah ponsel.
- Ponsel muncul dari gelap.
- Kamera melakukan push-in.
- Perangkat berputar dan layar menyala.
- Detail fitur ditunjukkan melalui callout dan label.

Karakter tidak diperlukan jika tidak membantu cerita.

### C. Kinetic typography
Contoh: video motivasi atau hook.
- Kata kunci masuk dengan timing yang mengikuti narasi.
- Skala, posisi, mask, dan susunan kata berubah untuk memberi penekanan.
- Kalimat panjang dipecah menjadi unit yang mudah dibaca.
- Tipografi tidak boleh menutupi subtitle atau informasi penting.

### D. Illustrative motion graphics
Contoh: menjelaskan koneksi internet.
- Titik dan garis membentuk jaringan.
- Peta atau diagram muncul bertahap.
- Panah dan label menjelaskan alur.
- Elemen bergerak untuk memperjelas hubungan, bukan sekadar dekorasi.

### E. Mixed visual storytelling
Contoh: menjelaskan dampak teknologi.
- Hook tipografi.
- Perangkat digital tampil sebagai objek utama.
- Diagram memperlihatkan hubungan antarperangkat.
- Karakter muncul hanya saat dibutuhkan untuk menunjukkan dampak pada manusia.

## 4. Arsitektur yang diusulkan

Pisahkan sistem berdasarkan tanggung jawab. Semua tetap berjalan dalam satu timeline Remotion dan renderer komposisi yang terkoordinasi.

```text
Naskah / topik
     |
     v
Storyboard & arahan visual
     |
     v
Scene Schema tervalidasi
     |
     +--> Visual Focus / Art Direction
     |
     +--> Character Layer
     |
     +--> Object Layer
     |
     +--> Typography Layer
     |
     +--> Graphic / Illustration Layer
     |
     +--> Environment Layer
     |
     +--> Camera & Composition
     |
     +--> Transition & Timing
     |
     v
Universal Scene Renderer
     |
     v
Remotion Composition
     |
     +--> Narasi / audio
     +--> Subtitle
     +--> Klip dan elemen proyek lama
     |
     v
MP4
```

### Tanggung jawab lapisan

| Lapisan | Tanggung jawab |
|---|---|
| Storyboard | Menentukan apa yang terjadi dalam adegan |
| Visual direction | Memilih fokus, gaya, mood, dan hierarki visual |
| Character engine | Pose, anatomi, gerak, ekspresi, interaksi karakter |
| Object engine | Posisi, transformasi, rotasi, interaksi, dan relasi objek |
| Typography engine | Animasi huruf/kata, keterbacaan, timing narasi |
| Graphic engine | Bentuk, garis, diagram, peta, infografik |
| Environment engine | Latar, kedalaman, suasana, dan elemen lingkungan |
| Camera & composition | Framing, fokus, skala, pan, zoom, parallax, safe area |
| Transition engine | Perpindahan antarscene/layer |
| Renderer | Menggambar semua layer secara deterministik |

Tidak semua layer harus aktif pada setiap adegan. Renderer harus menerima kombinasi layer sesuai data adegan.

## 5. Prinsip desain dan kualitas gerak

Motion graphics tidak boleh berarti menambahkan efek sebanyak mungkin. Setiap gerakan harus memiliki tujuan komunikasi.

Teknik yang dapat dipertimbangkan:
- **Anticipation:** persiapan sebelum gerakan utama.
- **Overshoot dan settling:** melewati target sedikit lalu stabil, bila sesuai karakter gerak.
- **Secondary motion:** gerakan lanjutan pada bagian tubuh atau elemen yang relevan.
- **Easing:** perubahan kecepatan yang terkontrol.
- **Parallax:** perbedaan gerak antar-lapisan untuk memberi kedalaman.
- **Mask reveal:** menampilkan elemen melalui masking.
- **Match cut:** menghubungkan adegan lewat bentuk, arah, atau gerakan yang serupa.
- **Kinetic typography:** teks menjadi elemen visual aktif.
- **Motion blur:** digunakan secara selektif bila membantu kesan gerak.

Teknik tersebut merupakan referensi desain umum. Implementasi, kode, prompt, dan preset untuk Studio Maliki harus ditulis mandiri. Jangan menyalin atau membundel materi berlisensi dari skill atau proyek referensi tanpa memeriksa izinnya.

### Aturan kualitas
1. Gerak harus membantu menjelaskan cerita atau mengarahkan perhatian.
2. Hindari efek berlebihan yang membuat pesan sulit dibaca.
3. Jaga hierarki visual: fokus utama, pendukung, lalu dekorasi.
4. Gerak karakter dan objek harus memiliki hubungan spasial yang masuk akal.
5. Teks, subtitle, dan elemen grafis harus memiliki area aman dan tidak bertumpuk.
6. Setiap frame harus dapat dirender ulang secara deterministik.

## 6. Rancangan data adegan

Berikut contoh konseptual. Ini belum merupakan schema final atau implementasi.

```json
{
  "judul": "Memahami era digital",
  "durasi": 12,
  "adegan": [
    {
      "id": "scene-01",
      "durasi": 3,
      "visualFocus": "typography",
      "mood": "bold",
      "layers": [
        {
          "type": "typography",
          "id": "headline",
          "text": "ERA DIGITAL",
          "animation": {
            "enter": "word-reveal",
            "emphasis": "scale-pop"
          }
        }
      ],
      "kamera": { "framing": "wide" },
      "transisi": "match-cut"
    },
    {
      "id": "scene-02",
      "durasi": 4,
      "visualFocus": "object",
      "layers": [
        {
          "type": "object",
          "id": "smartphone",
          "asset": "smartphone-basic",
          "animation": {
            "enter": "rise",
            "actions": ["rotate", "screen-glow"]
          }
        },
        {
          "type": "graphic",
          "id": "connection-lines",
          "animation": { "enter": "draw-on" }
        }
      ],
      "kamera": { "framing": "close-up", "gerak": "push-in" }
    },
    {
      "id": "scene-03",
      "durasi": 5,
      "visualFocus": "mixed",
      "layers": [
        { "type": "character", "id": "tokoh-utama", "action": "look-at-device" },
        { "type": "object", "id": "smartphone", "action": "held-by-character" },
        { "type": "typography", "id": "message", "text": "Terhubung setiap saat" }
      ]
    }
  ]
}
```

Ketentuan:
- Schema final harus divalidasi dengan tipe dan validator yang sesuai dengan stack proyek.
- Nama aksi di contoh hanya ilustrasi; jangan menganggapnya sudah didukung renderer.
- Data lama tetap dapat dibaca melalui adapter/normalisasi.
- Layer yang tidak dikenal atau aset yang tidak tersedia harus menghasilkan fallback yang aman, bukan membuat seluruh render gagal.
- Posisi, durasi, dan transformasi harus berbasis frame Remotion, bukan timer browser.

## 7. Hubungan dengan AI Storyboard

AI nantinya tidak langsung menghasilkan kode animasi. AI menghasilkan data adegan terstruktur.

Alur yang diharapkan:
1. Membaca naskah dan memahami tujuan setiap bagian.
2. Memecah naskah menjadi adegan dengan durasi yang masuk akal.
3. Memilih fokus visual: character, object, typography, graphic, environment, atau mixed.
4. Menentukan layer yang diperlukan.
5. Menentukan aksi, timing, kamera, transisi, dan hubungan antarobjek.
6. Memvalidasi apakah aset dan aksi tersedia.
7. Jika aksi tidak didukung, memilih pendekatan alternatif atau memberi peringatan yang jelas.
8. Mengirim data tervalidasi ke renderer.

AI harus dapat memilih adegan tanpa karakter jika karakter tidak dibutuhkan. AI juga tidak boleh mengarang kemampuan animasi yang belum tersedia.

## 8. Tahap implementasi yang diusulkan

Tahap ini memperluas rencana setelah fondasi animasi karakter, bukan menganggap semua fitur sudah tersedia.

### Tahap 4.7 — Universal Visual Animation Foundation
- Audit renderer dan schema yang sudah ada.
- Tetapkan kontrak layer dan visual focus.
- Buat satu scene renderer yang dapat menyusun beberapa jenis layer.
- Pastikan jalur karakter lama tetap bekerja.
- Validasi kompatibilitas proyek lama.

### Tahap 4.8 — Object Animation
- Transformasi objek: position, scale, rotation, opacity.
- Reusable object actions dan motion presets.
- Anchor/pivot dan relasi antarobjek.
- Interaksi objek-karakter hanya jika target kontak dapat dihitung dengan benar.
- Uji produk/ponsel, pintu, panci, gelas, dan objek umum.

### Tahap 4.9 — Kinetic Typography
- Animasi per kata, baris, dan karakter.
- Reveal, emphasis, stagger, mask, dan layout adaptif.
- Sinkronisasi opsional dengan narasi.
- Safe area untuk subtitle dan judul.

### Tahap 4.10 — Graphic & Illustration Animation
- Bentuk, garis, panah, diagram, peta, dan callout.
- Animasi draw-on, reveal, morph sederhana bila stabil.
- Komposisi infografik yang reusable.

### Tahap 4.11 — Environment, Depth & Composition
- Layer latar depan/tengah/belakang.
- Parallax deterministik.
- Pengaturan mood dan pencahayaan ilustratif.
- Camera framing dan komposisi lintas-layer.

### Tahap 4.12 — Mixed Visual Storytelling
- Kombinasikan character, object, typography, graphic, dan environment dalam satu adegan.
- Tentukan urutan layer dan fokus perhatian.
- Uji perpindahan fokus antaradegan.

### Tahap 4.13 — Validation & Regression
Uji minimal:
1. Cerita yang berpusat pada karakter.
2. Video produk yang berpusat pada objek.
3. Video teks/quote yang berpusat pada tipografi.
4. Video edukasi berbasis diagram.
5. Video campuran beberapa layer.

Semua harus memakai renderer dan kontrak data yang sama, bukan renderer khusus per cerita.

### Tahap 5 — AI Storyboard Integration
Dimulai setelah jenis layer utama dan validasi visual cukup stabil. AI memilih bahasa visual berdasarkan naskah dan hanya menggunakan kemampuan yang sudah tersedia.

Tahap 6–8 (Scene Editor, Batch Production, Testing & Optimization) kemudian disesuaikan untuk mendukung layer-layer baru.

## 9. Kriteria penerimaan

Fondasi universal dapat dianggap siap untuk AI Storyboard jika:
- Satu renderer dapat menyusun semua jenis layer yang telah diimplementasikan.
- Adegan dapat berfokus pada objek atau tipografi tanpa karakter.
- Satu video dapat menggabungkan beberapa fokus visual.
- Data adegan dapat diubah tanpa menulis renderer khusus untuk tiap cerita.
- Semua animasi deterministik berdasarkan frame.
- Judul dan subtitle tidak bertumpuk.
- Proyek lama tetap dapat dirender.
- Build, preview, dan render MP4 berhasil.
- Contact sheet atau bukti visual diperiksa, bukan hanya hasil TypeScript/bundling.

## 10. Batasan dan keputusan yang belum ditetapkan

- Belum diputuskan apakah objek akan memakai SVG, asset gambar, atau kombinasi; pilih berdasarkan kebutuhan dan biaya render.
- Belum ada skeletal rig/IK profesional yang dinyatakan selesai.
- Belum ada physics simulation yang diwajibkan.
- Belum semua jenis animasi objek, teks, dan grafis tersedia.
- Belum ditentukan apakah AI akan menghasilkan layout final atau hanya arahan layout yang kemudian disusun renderer.
- Belum ada perubahan kode aplikasi dalam dokumen proposal ini.

## 11. Batasan lisensi dan kompatibilitas proyek

- Remotion tetap menjadi renderer video utama.
- Jangan mengganti atau merusak jalur Klip, audio, subtitle, batch, preview, dan export.
- Pertahankan format proyek lama dan field lama melalui normalisasi/backward compatibility.
- Jangan menambahkan dependency tanpa alasan yang terukur.
- Pertahankan lisensi dan atribusi Studio Maliki yang sudah berlaku.
- Motion Graphics by Nalarka dan proyek referensi lain dipakai sebagai inspirasi teknik saja. Jangan menyalin kode, prompt, preset, aset, atau dokumentasi yang lisensinya tidak mengizinkan redistribusi ke aplikasi.
- Lisensi setiap dependency dan aset visual harus diperiksa sebelum dimasukkan.

## 12. Status

Dokumen ini adalah **proposal arah produk dan arsitektur**. Dokumen ini belum mengubah implementasi aplikasi, belum membuktikan bahwa semua jenis animasi tersedia, dan tidak menyatakan Tahap 4.7 telah lulus.

Langkah pertama setelah proposal disetujui adalah audit kode aktual pada branch kerja, lalu menyusun schema layer minimum dan prototipe yang paling kecil. Implementasi dilakukan bertahap dengan render visual sebagai kriteria penerimaan.
