# Universal Visual Animation Engine

Status: Proposal arsitektur dan roadmap — belum implementasi  
Branch: `docs/universal-visual-animation-engine`  
Proyek: Studio Maliki Reborn

## 1. Arah produk

Studio Maliki Reborn tidak dibatasi sebagai aplikasi animasi karakter 2D. Tujuannya adalah menjadi aplikasi visual storytelling dan motion graphics yang memilih bahasa visual sesuai isi naskah.

Fokus visual setiap adegan dapat berupa:
- `character`: karakter manusia/figur.
- `object`: benda atau produk.
- `typography`: kata, huruf, dan angka.
- `graphic`: bentuk, diagram, peta, dan infografik.
- `environment`: ruang, latar, dan suasana.
- `mixed`: kombinasi beberapa lapisan.

Karakter bukan fokus wajib. Satu video dapat berpindah fokus dari tipografi ke objek, grafis, lingkungan, lalu karakter jika memang dibutuhkan cerita.

> Visual mengikuti cerita; cerita tidak dipaksakan mengikuti satu jenis animasi.

## 2. Arsitektur yang diusulkan

Semua layer tetap menggunakan satu timeline Remotion dan satu renderer komposisi terkoordinasi.

```text
Naskah/topik
  -> Storyboard & visual direction
  -> Scene schema tervalidasi
  -> Character / Object / Typography / Graphic / Environment layers
  -> Camera, composition, transition, timing
  -> Universal Scene Renderer (Remotion)
  -> Audio, subtitle, legacy clips
  -> MP4
```

| Lapisan | Tanggung jawab |
|---|---|
| Storyboard | Menentukan isi dan urutan adegan |
| Visual direction | Memilih fokus, gaya, mood, dan hierarki visual |
| Character engine | Pose, anatomi, gerak, ekspresi, interaksi |
| Object engine | Posisi, transformasi, pivot, dan relasi objek |
| Typography engine | Animasi teks, keterbacaan, timing |
| Graphic engine | Bentuk, garis, diagram, peta, infografik |
| Environment engine | Latar, kedalaman, dan suasana |
| Camera/composition | Framing, fokus, skala, pan, zoom, parallax, safe area |
| Transition engine | Perpindahan antar-scene/layer |
| Renderer | Menggambar semua layer deterministik |

Tidak semua layer aktif di setiap scene. Data lama harus tetap didukung melalui adapter/normalisasi. Aksi yang belum didukung tidak boleh dipalsukan; berikan fallback atau peringatan yang jelas.

## 3. Contoh bahasa visual

### Character-based
Seseorang menerima kabar mengejutkan: membaca ponsel, bereaksi, kamera mendekat ke ekspresi. Ponsel tetap terhubung dengan tangan.

### Object-based
Video produk: ponsel muncul, berputar, layar menyala, kamera mendekat, fitur ditunjukkan dengan callout. Karakter tidak diperlukan.

### Kinetic typography
Hook atau kutipan: frasa pendek muncul bertahap, kata kunci diberi penekanan ukuran/warna/posisi, teks bergerak melalui mask dan layering. Teks harus tetap akurat dan terbaca.

### Illustrative motion graphics
Video edukasi: titik dan garis membentuk jaringan, peta/diagram muncul bertahap, panah dan label menjelaskan hubungan.

### Mixed storytelling
Hook tipografi, perangkat digital sebagai objek utama, diagram hubungan, lalu karakter muncul hanya untuk menunjukkan dampak pada manusia.

## 4. Prinsip desain dan kualitas gerak

Gerakan harus membantu menjelaskan cerita atau mengarahkan perhatian, bukan sekadar menambah efek.

Teknik yang dapat dipakai sesuai konteks:
- Anticipation: persiapan sebelum gerakan utama.
- Overshoot dan settling: melewati target sedikit lalu stabil.
- Secondary motion: gerakan lanjutan pada bagian tubuh atau elemen.
- Easing: percepatan dan perlambatan terkontrol.
- Parallax: perbedaan gerak antar-layer untuk memberi kedalaman.
- Mask reveal dan clipping: mengungkap elemen secara terarah.
- Match cut: menghubungkan scene lewat bentuk, arah, atau gerakan.
- Kinetic typography: teks menjadi elemen visual aktif.
- Motion blur dan soft shadow: digunakan selektif.
- Dynamic composition: komposisi asimetris, ruang kosong, layering, dan hierarki fokus.

Hindari slideshow dengan fade/slide berulang, glitch berlebihan, rotasi acak, kilatan tanpa alasan, dan transisi yang menutupi informasi.

## 5. Rancangan data adegan (konseptual)

Contoh berikut hanya gambaran schema, bukan kontrak final atau klaim bahwa semua aksi telah tersedia.

```json
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
  "camera": { "framing": "close-up", "movement": "push-in" }
}
```

Schema final perlu tipe dan validasi yang sesuai stack proyek. Semua posisi, durasi, dan transformasi berbasis frame Remotion, bukan timer browser.

## 6. Integrasi AI Storyboard

AI tidak menghasilkan kode renderer. AI menghasilkan data scene terstruktur:
1. Memahami naskah dan tujuan tiap bagian.
2. Membagi naskah menjadi adegan.
3. Memilih visual focus (character, object, typography, graphic, environment, mixed).
4. Menentukan layer, aksi, timing, kamera, dan transisi.
5. Memvalidasi aset serta kemampuan yang tersedia.
6. Memilih alternatif atau memberi peringatan jika aksi tidak didukung.
7. Mengirim data tervalidasi ke renderer.

AI harus dapat memilih scene tanpa karakter. AI tidak boleh mengarang kemampuan animasi yang belum tersedia.

## 7. Pemetaan skill Motion Graphics by Nalarka

Berkas yang ditinjau langsung dari ZIP:
- `SKILL.md`
- `references/panduan-visual.md`
- `references/render-dan-verifikasi.md`

Skill tersebut adalah workflow produksi explainer motion graphics, bukan engine karakter atau library animasi siap pakai. Pemetaan di bawah mengadaptasi prinsip dan tekniknya ke Studio Maliki Reborn.

### 7.1 Arah visual dan art direction

Dari `panduan-visual.md`:
- Referensi menjadi tolok ukur kualitas, bukan cetakan. Pelajari palet, hierarki tipografi, layering, ritme, transisi, kedalaman, dan relasi gerak-suara.
- Jangan menyalin shot, komposisi, posisi teks, atau urutan animasi frame demi frame.
- Gaya editorial modern/minimalis/premium adalah salah satu opsi, bukan gaya wajib setiap video.
- Komposisi asimetris, ruang kosong yang disengaja, layering, cut-out, ilustrasi, ikon, bayangan, kedalaman, masking, dan motion blur dapat dipilih sesuai aset/topik.
- Hindari slideshow: setiap scene perlu ide visual sendiri, bukan gambar statis dengan fade/slide berulang.
- Jika tidak ada gambar user, visual dapat dibuat dari bentuk geometris, ikon vektor, diagram, angka, dan tipografi.

Penerapan: buat art direction per scene dan aturan hierarki visual, bukan satu template warna/layout yang dipaksakan ke semua video.

### 7.2 Kinetic typography

Dari `panduan-visual.md`:
- Teks dapat muncul bersama kata yang diucapkan.
- Gunakan mask reveal, animasi kata/huruf bertahap, overshoot terkontrol, animasi letter spacing, clipping, layering, atau teks yang muncul dari balik objek.
- Penekanan dapat memakai bobot, warna, ukuran, dan posisi.
- Pecah paragraf menjadi frasa pendek; sorot kata kunci.
- Pisahkan judul, kata kunci, teks pendukung, dan label.
- Gunakan font asli melalui kode, bukan teks generatif berbentuk gambar, agar ejaan akurat.
- Pertahankan makna dan ejaan naskah.

Penerapan: Typography Layer perlu mendukung animasi per karakter/kata/frasa/baris, layout adaptif, safe area, dan sinkronisasi narasi opsional. Subtitle harus terpisah dari judul dan kinetic text agar tidak bertumpuk.

### 7.3 Animasi aset

Dari `panduan-visual.md`:
- Scale in/out, gerak terarah, rotasi halus.
- Parallax dan lapisan kedalaman.
- Mask reveal, zoom kamera, cropping kreatif.
- Floating motion dan secondary motion.
- Motion blur dan bayangan lembut secara terkontrol.
- Aset boleh dipotong, diubah ukuran, diposisikan, dimasking, dan ditumpuk selama detail penting tidak hilang dan gambar tidak diregangkan.
- Jika tool cut-out tidak tersedia, gunakan masking/framing dan jangan menjanjikan cut-out otomatis.

Penerapan: Object/Asset Layer perlu memiliki transformasi reusable (position, scale, rotation, opacity, anchor/pivot), reveal, depth, dan hubungan visual dengan teks.

### 7.4 Transisi

Dari `panduan-visual.md`:
- Pilihan meliputi match cut, whip, directional wipe, mask reveal, shape/scale transition, typography-driven transition, parallax berlapis, motion blur, dan elemen grafis yang berpindah antar-scene.
- Pilih sesuai isi, hubungkan elemen antar-scene jika sesuai.
- Hindari glitch berlebihan, rotasi acak, kilatan tanpa alasan, dan transisi yang menutupi penjelasan.
- Transisi harus berada di dalam durasi total; durasi video tidak boleh bertambah karena transisi.

Penerapan: transition engine menyediakan opsi terarah yang dapat dipilih per scene, dengan validasi durasi dan tanpa frame kosong.

### 7.5 Sinkronisasi voiceover dan musik

Dari `panduan-visual.md` dan `SKILL.md`:
- Voiceover menjadi acuan timing utama bila tersedia.
- Tampilkan teks saat frasa diucapkan; munculkan aset saat relevan; beri penekanan pada kata kunci.
- Sisakan jeda visual untuk informasi yang perlu dicerna.
- Animasi dapat mengikuti ritme pembicara dan beat musik bila mendukung narasi.
- Voiceover tidak boleh dipercepat, dipotong, atau dipadatkan diam-diam.
- Musik harus berada di bawah voiceover; ducking saat narasi aktif.
- Efek suara digunakan hemat; hindari clipping, distorsi, dan keheningan tak disengaja.
- Musik sintetis sederhana harus dijelaskan apa adanya jika dibuat otomatis.

Penerapan: audio-aware timeline bersifat opsional dan tidak membuat semua proyek wajib memakai voiceover atau musik.

### 7.6 Render deterministik dan verifikasi

Dari `render-dan-verifikasi.md`:
- Cek tool/versi lingkungan sebelum memilih pipeline; jangan mengasumsikan FFmpeg, ffprobe, Python/Pillow/numpy, browser, TTS, atau font tersedia.
- Pipeline yang dibahas mencakup Python (Pillow/numpy), HTML/CSS/JS dengan browser headless, Remotion/Node, dan filtergraph FFmpeg. Pilih yang benar-benar tersedia.
- Render frame dari waktu/frame secara deterministik; hindari state tersembunyi dan angka acak berubah (gunakan seed tetap bila random diperlukan).
- Timeline disimpan sebagai data segmen yang dapat disetel.
- Motion blur dapat dihitung dari beberapa sub-frame jika layak.
- Verifikasi MP4 aktual: durasi, jumlah frame, FPS, codec, resolusi, keterbacaan teks, aset, transisi, frame hitam/beku, dan kualitas audio.
- Ekstrak frame kunci/contact sheet dan periksa visual hasil akhir, bukan hanya build atau preview.

Penerapan: QA Studio Maliki harus menggunakan spesifikasi ekspor proyek/pengguna, mengukur metadata file aktual, memeriksa frame, serta melaporkan keterbatasan dengan jujur.

### 7.7 Ketentuan skill yang tidak otomatis menjadi aturan produk

`SKILL.md` menetapkan workflow spesifik untuk explainer pendek: maksimum 60 detik, 30 fps, MP4 H.264 + AAC, urutan kerja naskah/voiceover/aset, serta ketentuan ekspor dan serah-terima tertentu.

Itu adalah ketentuan skill untuk workflow tersebut, bukan keputusan produk Studio Maliki Reborn. Jangan memaksakan batas 60 detik, kewajiban voiceover, resolusi, codec, orientasi, atau prosedur pengumpulan aset ke semua proyek. Ikuti spesifikasi proyek dan pilihan pengguna. Ketentuan 30 fps/H.264/AAC dapat digunakan jika sesuai konfigurasi ekspor proyek.

## 8. Roadmap yang diusulkan

### 4.7 — Universal Visual Animation Foundation
- Audit renderer/schema aktual.
- Tetapkan kontrak layer dan visual focus.
- Bangun scene renderer yang menyusun beberapa jenis layer.
- Pastikan jalur karakter dan proyek lama tetap bekerja.

### 4.8 — Object & Asset Animation
- Transformasi position, scale, rotation, opacity, anchor/pivot.
- Reusable object actions, reveal, floating, parallax.
- Interaksi karakter-objek hanya jika target kontak dapat dihitung dan terlihat benar.

### 4.9 — Kinetic Typography
- Animasi per karakter/kata/frasa/baris.
- Reveal, emphasis, stagger, mask, clipping, layering.
- Layout adaptif dan safe area untuk subtitle/judul.

### 4.10 — Graphic & Illustration Animation
- Bentuk, garis, panah, diagram, peta, callout.
- Draw-on, reveal, dan morph sederhana bila stabil.

### 4.11 — Environment, Depth & Composition
- Layer foreground/midground/background.
- Parallax deterministik, framing, mood, dan komposisi lintas-layer.

### 4.12 — Mixed Visual Storytelling
- Gabungkan character, object, typography, graphic, environment dalam satu scene.
- Atur urutan layer, hierarki fokus, dan perpindahan fokus antar-scene.

### 4.13 — Validation & Regression
Uji cerita character-focused, video produk object-focused, typography/quote, edukasi diagram, dan video campuran. Semua menggunakan renderer dan kontrak data yang sama.

### Tahap 5 — AI Storyboard Integration
Dimulai setelah layer yang dipilih memiliki dukungan renderer dan validasi visual. AI memilih bahasa visual berdasarkan naskah dan hanya menggunakan kemampuan yang benar-benar tersedia.

## 9. Kriteria penerimaan

- Satu renderer menyusun seluruh layer yang telah diimplementasikan.
- Scene dapat berfokus pada objek atau tipografi tanpa karakter.
- Satu video dapat menggabungkan beberapa fokus visual.
- Data scene berubah tanpa renderer khusus per cerita.
- Animasi deterministik berdasarkan frame.
- Teks dan subtitle tidak bertumpuk.
- Proyek lama tetap dapat dirender.
- Build, preview, dan MP4 berhasil.
- Contact sheet/frame kunci dan file ekspor aktual diperiksa.

## 10. Batasan, lisensi, dan kompatibilitas

- Remotion tetap renderer video utama.
- Jangan merusak jalur Klip, audio, subtitle, batch, preview, dan export.
- Pertahankan format proyek lama melalui adapter/normalisasi.
- Jangan menambah dependency tanpa alasan terukur.
- Pertahankan lisensi dan atribusi Studio Maliki.
- Skill Nalarka digunakan sebagai referensi teknik/workflow. Jangan menyalin kode, prompt, preset, aset, atau dokumentasi ke produk tanpa memeriksa izin dan lisensinya.
- Belum diputuskan apakah aset akan berupa SVG, gambar, atau kombinasi; pilih berdasarkan audit dan kebutuhan.
- Belum semua jenis animasi object, typography, dan graphic tersedia.
- Dokumen ini proposal, bukan implementasi dan bukan bukti Tahap 4.7 lulus.

## 11. Langkah berikutnya

Audit kode aktual pada branch kerja, bandingkan kemampuan yang sudah ada dengan pemetaan di atas, tetapkan kontrak layer minimum, lalu buat prototipe kecil. Implementasi bertahap; render visual menjadi kriteria penerimaan, bukan hanya TypeScript atau bundling.
