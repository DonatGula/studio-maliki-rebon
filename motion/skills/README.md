# Motion Skills di Studio Maliki Reborn

Sumber upstream: [iart-ai/motion-skills](https://github.com/iart-ai/motion-skills)

## Status integrasi

- **Bundled**: seluruh skill dari pack tersebut sudah tersedia secara lokal.
- **Partial**: sebagian skill pack sudah tersedia dan dapat dipilih oleh engine.
- **Catalog**: pack baru tercatat sebagai target integrasi; skill-nya belum bisa dipilih.

Daftar mesin yang menjadi sumber kebenaran:
- `registry.json`: skill yang benar-benar tersedia secara lokal dan dapat dipakai engine.
- `packs.json`: katalog seluruh 19 pack upstream beserta jumlah skill dan status integrasinya.

Jangan menambahkan ID skill ke `registry.json` sebelum file `SKILL.md` yang sesuai benar-benar tersedia. Ini mencegah generator memilih instruksi yang tidak ada.

## Ringkasan pack

| Pack | Jumlah skill | Status |
|---|---:|---|
| TikTok / Reels / Shorts | 4 | Partial (2 skills bundled) |
| Text-message Stories | 1 | Catalog |
| YouTube / Podcast | 2 | Partial (1 skill bundled) |
| E-commerce Product Video | 3 | Catalog |
| Advertising / Brand Campaign | 3 | Catalog |
| Data Visualization | 3 | Partial (1 skill bundled) |
| Explainer / Educational | 5 | Partial (1 skill bundled) |
| Editorial Map Animation | 1 | Bundled |
| Web / UI Animation | 9 | Catalog |
| Motion Design | 9 | Partial (3 skills bundled) |
| Kinetic Typography | 1 | Bundled |
| Freelance Motion Workflow | 5 | Catalog |
| 3D / WebGL Animation | 3 | Catalog |
| Math / Scientific Animation | 1 | Catalog |
| Generative Illustration | 1 | Catalog |
| JavaScript / Canvas Animation | 2 | Partial (1 skill bundled) |
| Transparent Lower Thirds | 1 | Catalog |
| B-roll for Talking Head | 1 | Bundled |
| AI Talking Head Video | 1 | Catalog |

Total upstream: 19 pack, 56 skill. Saat ini 12 file skill dari sembilan pack sudah tersedia: tiga pack lengkap dan enam pack parsial.

## Urutan integrasi lanjutan yang disarankan

Untuk target konten Shorts, TikTok, dan Reels, prioritaskan:
1. Lengkapi YouTube Video dan Data Animation yang masih parsial.
2. Integrasikan E-commerce dan Ad Video.
3. Tambahkan Text-message Video dan Talking Head.
4. Lanjutkan pack lain sesuai kebutuhan, terutama WebGL/Manim yang mungkin memerlukan renderer atau dependency berbeda.

Setiap pack baru perlu ditinjau isi, dependensi, lisensi, dan kecocokannya dengan Remotion sebelum ditambahkan ke registry. Skill yang mengandalkan GSAP, Three.js, Manim, WebM alpha, atau layanan AI eksternal tidak otomatis kompatibel dengan renderer Studio Maliki.

## Prinsip kompatibilitas

Motion Skills adalah panduan untuk AI, bukan renderer. Remotion tetap menjadi renderer utama. Instruksi dari skill upstream harus diterjemahkan menjadi storyboard dan efek yang memang didukung aplikasi; jangan menganggap contoh kode dari pack lain dapat langsung dijalankan tanpa adaptasi.

Sumber dan atribusi: [ATTRIBUTION.md](ATTRIBUTION.md).
