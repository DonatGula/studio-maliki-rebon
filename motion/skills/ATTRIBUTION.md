# Motion Skills — attribution

Studio Maliki Reborn mengintegrasikan panduan dari proyek [iart-ai/motion-skills](https://github.com/iart-ai/motion-skills).

## Pack yang sudah dibundel

- [motion-design-skills](https://github.com/iart-ai/motion-design-skills)
- [tiktok-video-skills](https://github.com/iart-ai/tiktok-video-skills)
- [explainer-video-skills](https://github.com/iart-ai/explainer-video-skills)
- [kinetic-typography-skills](https://github.com/iart-ai/kinetic-typography-skills)
- [javascript-animation-skills](https://github.com/iart-ai/javascript-animation-skills)

Delapan file `SKILL.md` dari lima pack di atas saat ini disertakan secara lokal. Status tersebut juga dicatat pada `packs.json`.

## Katalog lengkap

Katalog `packs.json` mencatat seluruh 19 pack dan 56 skill dari proyek upstream, termasuk pack yang belum dibundel. Pack berstatus `catalog` adalah daftar integrasi lanjutan, bukan klaim bahwa seluruh skill-nya sudah dapat dipilih atau digunakan saat ini.

## Cara integrasi

Skill packs mengajarkan alur kerja kreatif kepada AI. Skill bukan plugin renderer. Studio Maliki Reborn tetap memakai pipeline AI → storyboard JSON → Remotion. Metadata visual/gerak/transisi dari AI akan diterapkan secara bertahap pada renderer dan editor.

Repositori pack upstream menggunakan lisensi MIT. Salinan lisensi dan pemberitahuan hak cipta sumber disertakan di `motion/skills/iart-ai/LICENSE`. Integrasi ini tidak mengubah lisensi utama Studio Maliki yang tercantum di `../LISENSI.md`.

Sumber katalog utama: https://github.com/iart-ai/motion-skills
