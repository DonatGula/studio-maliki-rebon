# Motion Skills — attribution

Studio Maliki Reborn mengintegrasikan panduan dari proyek [iart-ai/motion-skills](https://github.com/iart-ai/motion-skills).

## Pack yang sudah dibundel

- [motion-design-skills](https://github.com/iart-ai/motion-design-skills)
- [tiktok-video-skills](https://github.com/iart-ai/tiktok-video-skills)
- [explainer-video-skills](https://github.com/iart-ai/explainer-video-skills)
- [kinetic-typography-skills](https://github.com/iart-ai/kinetic-typography-skills)
- [javascript-animation-skills](https://github.com/iart-ai/javascript-animation-skills)
- [youtube-video-skills](https://github.com/iart-ai/youtube-video-skills) — audiogram
- [b-roll-skills](https://github.com/iart-ai/b-roll-skills) — talking-head-b-roll
- [data-animation-skills](https://github.com/iart-ai/data-animation-skills) — animated-infographic
- [map-animation-skills](https://github.com/iart-ai/map-animation-skills) — map-animation

Dua belas file `SKILL.md` dari sembilan pack (empat pack tambahan terintegrasi sebagian) saat ini disertakan secara lokal. Status tersebut juga dicatat pada `packs.json`.

## Katalog lengkap

Katalog `packs.json` mencatat seluruh 19 pack dan 56 skill dari proyek upstream. Status `partial` berarti hanya sebagian skill dalam pack tersebut yang disertakan; `catalog` berarti pack masih berupa daftar integrasi lanjutan.

## Cara integrasi

Skill packs mengajarkan alur kerja kreatif kepada AI. Skill bukan plugin renderer. Studio Maliki Reborn tetap memakai pipeline AI → storyboard JSON → Remotion. Metadata visual/gerak/transisi dari AI akan diterapkan secara bertahap pada renderer dan editor.

Repositori pack upstream menggunakan lisensi MIT. Salinan lisensi dan pemberitahuan hak cipta sumber disertakan di `motion/skills/iart-ai/LICENSE`. Integrasi ini tidak mengubah lisensi utama Studio Maliki yang tercantum di `../LISENSI.md`.

Sumber katalog utama: https://github.com/iart-ai/motion-skills
