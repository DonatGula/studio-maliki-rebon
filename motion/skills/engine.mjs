// kredit-maliki: integrasi Motion Skills untuk Studio Maliki Reborn.
// Sumber skill: iart-ai/motion-skills dan pack resminya (lihat ATTRIBUTION.md).
import {readFileSync, existsSync} from 'node:fs';
import {join, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';

const DIR = dirname(fileURLToPath(import.meta.url));
const ROOT = join(DIR, 'skills', 'iart-ai');
const registry = JSON.parse(readFileSync(join(DIR, 'skills', 'registry.json'), 'utf8'));

const norm = (s) => String(s ?? '').toLocaleLowerCase('id-ID');
export function pilihMotionSkills(topik, manual = 'auto') {
  if (manual && manual !== 'auto') {
    const requested = manual.split(',').map((s) => s.trim()).filter(Boolean);
    const valid = new Set(registry.skills.map((s) => s.id));
    const invalid = requested.filter((s) => !valid.has(s));
    if (invalid.length) throw new Error('Motion Skill tidak dikenal: ' + invalid.join(', ') +
      '. Pilihan: ' + [...valid].join(', '));
    return [...new Set(requested)].slice(0, 5);
  }
  const text = norm(topik);
  const ranked = registry.skills.map((skill) => ({
    id: skill.id,
    score: skill.keywords.reduce((n, word) => n + (text.includes(norm(word)) ? 1 : 0), 0),
    always: skill.always,
  })).sort((a, b) => b.score - a.score);
  const chosen = ranked.filter((s) => s.always || s.score > 0).slice(0, 5).map((s) => s.id);
  return chosen.length ? chosen : ['animation-principles', 'motion-art-direction', 'remotion-video', 'short-form-video'];
}

export function susunPanduanMotion(topik, manual = 'auto') {
  const ids = pilihMotionSkills(topik, manual);
  const sections = ids.map((id) => {
    const skill = registry.skills.find((s) => s.id === id);
    const path = join(ROOT, skill.file);
    if (!existsSync(path)) return '';
    // Batasi token prompt. File sumber lengkap tetap disimpan untuk referensi dan pengembangan.
    const body = readFileSync(path, 'utf8').slice(0, 5200);
    return `\n### Skill: ${id}\nSumber: https://github.com/${registry.packs.find((p) => p.skills.includes(id))?.repository ?? 'iart-ai/motion-skills'}\n${body}`;
  }).filter(Boolean);
  const idsJson = JSON.stringify(ids);
  const instruction = `
## Motion Skills yang dipilih
Skill aktif: ${ids.join(', ')}.
Gunakan prinsip-prinsip berikut sebagai arahan kreatif, bukan menyalin contoh mentah.
- Rancang satu motion language yang konsisten untuk seluruh video.
- Tentukan hierarki visual: hero, support, texture; jangan gerakkan semua elemen sekaligus.
- Gunakan easing yang sesuai, stagger seperlunya, anticipation/follow-through yang ringan, dan jeda agar teks terbaca.
- Sesuaikan ide animasi dengan komposisi Remotion Studio Maliki yang sudah ada. Jangan mengarang komponen, package, file asset, atau kemampuan renderer yang belum tersedia.
- Video utama tetap vertikal 9:16 dan berbahasa Indonesia. Jaga teks singkat, area aman, kontras, dan keterbacaan di layar ponsel.
- Skill JavaScript Animation, Audiogram, B-roll, Infographic, dan Map Animation adalah arahan storyboard. Jangan menganggap dependency, script, template, layanan eksternal, atau file referensi dari pack upstream sudah terpasang.
- B-roll hanya boleh merujuk klip yang memang disediakan pengguna; jangan mengarang footage, transkrip bertiming, atau path asset.
- Audiogram tidak boleh memakai analyser real-time atau mengklaim waveform audio-synced jika data audio tidak tersedia. Utamakan visualisasi sederhana yang deterministik.
- Infografis harus memakai angka yang ada di sumber/topik; jangan mengarang statistik. Peta harus memakai lokasi dan rute yang disebutkan atau diberikan pengguna.
- Bila sebuah efek memerlukan package atau renderer yang belum tersedia, jelaskan sebagai arahan visual sederhana yang bisa diwujudkan oleh Remotion bawaan; jangan menambah dependency otomatis.
- Sertakan metadata storyboard agar bisa diedit pada tahap editor berikutnya, tetapi pertahankan kolom JSON lama.
Tambahkan properti tingkat atas "motion": {"skills": ${idsJson}, "arah_visual": "ringkasan satu kalimat", "bahasa_gerak": "aturan gerak singkat"}.
Pada setiap objek adegan, tambahkan "visual": "apa yang terlihat", "gerak": "aksi/gerakan visual yang disarankan", dan "transisi": "cara masuk/keluar singkat".
Jangan mengubah bentuk "judul", "gaya", "handle", atau "adegan" yang sudah digunakan aplikasi.
`;
  return instruction + '\n' + sections.join('\n');
}
