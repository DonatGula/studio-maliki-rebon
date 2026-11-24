# Motion Skills di Studio Maliki Reborn

Sumber upstream: [iart-ai/motion-skills](https://github.com/iart-ai/motion-skills)

## Status integrasi

- **Bundled**: skill files sudah disalin ke `iart-ai/` dan dapat dipakai engine.
- **Catalog**: pack sudah terdaftar sebagai target integrasi, tetapi file skill-nya belum dibundel dan belum bisa dipilih oleh generator.

Daftar mesin yang menjadi sumber kebenaran:
- `registry.json`: skill yang benar-benar tersedia secara lokal dan dapat dipakai engine.
- `packs.json`: katalog seluruh 19 pack upstream beserta jumlah skill dan status integrasinya.

Jangan menambahkan ID skill ke `registry.json` sebelum file `SKILL.md` yang sesuai benar-benar tersedia. Ini mencegah generator memilih instruksi yang tidak ada.

## Ringkasan pack

| Pack | Jumlah skill | Status |
|---|---:|---|
| TikTok / Reels / Shorts | 4 | Bundled |
| Text-message Stories | 1 | Catalog |
| YouTube / Podcast | 2 | Catalog |
| E-commerce Product Video | 3 | Catalog |
| Advertising / Brand Campaign | 3 | Catalog |
| Data Visualization | 3 | Catalog |
| Explainer / Educational | 5 | Bundled |
| Editorial Map Animation | 1 | Catalog |
| Web / UI Animation | 9 | Catalog |
| Motion Design | 9 | Bundled |
| Kinetic Typography | 1 | Bundled |
| Freelance Motion Workflow | 5 | Catalog |
| 3D / WebGL Animation | 3 | Catalog |
| Math / Scientific Animation | 1 | Catalog |
| Generative Illustration | 1 | Catalog |
| JavaScript / Canvas Animation | 2 | Bundled |
| Transparent Lower Thirds | 1 | Catalog |
| B-roll for Talking Head | 1 | Catalog |
| AI Talking Head Video | 1 | Catalog |

Total upstream: 19 pack, 56 skill. Pada integrasi lokal saat ini, baru 8 file skill dari lima pack yang dibundel.

## Urutan integrasi lanjutan yang disarankan

Untuk target konten Shorts, TikTok, dan Reels, prioritaskan:
1. YouTube Video dan B-roll.
2. Data Animation dan Map Animation.
3. E-commerce dan Ad Video.
4. Text-message Video dan Talking Head.
5. Sisanya sesuai kebutuhan, terutama pack WebGL/Manim yang mungkin membutuhkan renderer atau dependency berbeda.

Setiap pack baru perlu ditinjau isi, dependensi, lisensi, dan kecocokannya dengan Remotion sebelum ditambahkan ke registry. Skill yang mengandalkan GSAP, Three.js, Manim, WebM alpha, atau layanan AI eksternal tidak otomatis kompatibel dengan renderer Studio Maliki.

## Prinsip kompatibilitas

Motion Skills adalah panduan untuk AI, bukan renderer. Remotion tetap menjadi renderer utama. Instruksi dari skill upstream harus diterjemahkan menjadi storyboard dan efek yang memang didukung aplikasi; jangan menganggap contoh kode dari pack lain dapat langsung dijalankan tanpa adaptasi.

Sumber dan atribusi: [ATTRIBUTION.md](ATTRIBUTION.md).
