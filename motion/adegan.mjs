// Regenerate one storyboard scene using the configured AI provider.
// Usage: node adegan.mjs <input.json> <scene-index-1-based> <provider> <output.json>
import {readFileSync, writeFileSync} from 'node:fs';
import {bacaEnv, tanyaAI} from './ai.mjs';
import {susunPanduanMotion} from './skills/engine.mjs';

const [input, rawIndex, provider = 'gemini', output] = process.argv.slice(2);
if (!input || !rawIndex || !output) throw new Error('Argumen: input.json nomor-adegan provider output.json');
const index = Number(rawIndex) - 1;
const data = JSON.parse(readFileSync(input, 'utf8'));
const scene = data.adegan?.[index];
if (!scene) throw new Error('Nomor adegan tidak ditemukan.');
const skills = (data.motion?.skills ?? []).join(',');
const guide = susunPanduanMotion(data.judul ?? 'video pendek', skills || 'auto');
const prompt = `Kamu editor storyboard video pendek profesional. Buat ulang HANYA satu adegan dari naskah video berikut.
Pertahankan tujuan cerita, konsistensi gaya, bahasa Indonesia, dan kesinambungan dengan adegan sebelum/sesudahnya.
Jangan mengubah fakta atau menambah klaim yang tidak ada. Narasi maksimal 2 kalimat singkat.
Balas HANYA satu objek JSON valid dengan field: judul, teks, kunci (array string), ikon, visual, gerak, transisi, durasi (angka detik).
Judul video: ${data.judul ?? ''}
Gaya visual: ${data.gaya ?? 'garis'}
Konteks sebelumnya: ${JSON.stringify(data.adegan.slice(Math.max(0,index-1), index))}
Adegan yang diganti: ${JSON.stringify(scene)}
Konteks sesudahnya: ${JSON.stringify(data.adegan.slice(index+1,index+2))}
Panduan Motion Skills:
${guide}`;
const answer = await tanyaAI(provider, prompt, bacaEnv(), 'meregenerasi adegan');
const match = answer.match(/\{[\s\S]*\}/);
if (!match) throw new Error('AI tidak mengembalikan objek JSON.');
const fresh = JSON.parse(match[0]);
for (const key of ['judul','teks','ikon','visual','gerak','transisi']) {
  if (fresh[key] !== undefined && typeof fresh[key] !== 'string') throw new Error(`Field ${key} harus berupa teks.`);
}
if (typeof fresh.teks !== 'string' || !fresh.teks.trim()) throw new Error('AI mengembalikan adegan tanpa narasi.');
if (fresh.kunci !== undefined && !Array.isArray(fresh.kunci)) throw new Error('Field kunci harus berupa daftar.');
writeFileSync(output, JSON.stringify(fresh, null, 2));
console.log('Adegan berhasil dibuat ulang.');
