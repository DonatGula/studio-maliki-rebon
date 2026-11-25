// kredit-maliki: Template oleh Maliki Saputra (@malikisaputra) — https://malikisaputra.biz.id · Lisensi Nonkomersial Maliki Studio 1.0 (alat/LISENSI.md): dilarang dijual ulang.
// Topik → naskah JSON memakai AI milik pengguna (isi .env; lihat .env.contoh).
// Pakai: node naskah.mjs "topik video" [--ai=gemini|openai|claude-code|codex|opencode] [--gaya=neon] [--nama=topikku]
// Tanpa kunci API? Pakai PROMPT-NASKAH.md di Claude/Gemini/ChatGPT gratis lalu simpan JSON-nya sendiri.
import {writeFileSync, mkdirSync, readFileSync} from 'node:fs';
import {bacaEnv, tanyaAI, berhenti} from './ai.mjs';
import {susunPanduanMotion, pilihMotionSkills} from './skills/engine.mjs';

const argv = process.argv.slice(2);
const opsi = Object.fromEntries(argv.filter((a) => a.startsWith('--')).map((a) => a.slice(2).split('=')));
const topik = argv.filter((a) => !a.startsWith('--')).join(' ');
if (!topik) {
  console.error('Tulis topiknya, mis.: node naskah.mjs "3 kebiasaan pagi produktif"');
  process.exit(1);
}
const env = bacaEnv();
const penyedia = (opsi.ai ?? env.AI ?? 'gemini').toLowerCase();
const skillMode = opsi.skills ?? 'auto';
let skillIds = [];
let panduanMotion = '';
try { skillIds = pilihMotionSkills(topik, skillMode); panduanMotion = susunPanduanMotion(topik, skillMode); }
catch (e) { berhenti(e.message); }
const prompt = readFileSync('PROMPT-NASKAH.md', 'utf8').replace('[TOPIK]', topik) + '\n\n' + panduanMotion;
const tanya = () => tanyaAI(penyedia, prompt, env, 'menulis naskah');

console.log(`• Meminta AI '${penyedia}' menulis naskah: ${topik}`);
console.log(`• Motion Skills: ${skillIds.join(', ')}`);
const teks = await tanya();
const m = teks.match(/\{[\s\S]*\}/);
if (!m) berhenti('Balasan AI tidak berisi JSON:\n' + teks.slice(0, 500));
const naskah = JSON.parse(m[0]);
if (opsi.gaya) naskah.gaya = opsi.gaya;
naskah.motion = {...(naskah.motion ?? {}), styleId: naskah.motion?.styleId ?? 'storytelling-2d', aspectRatio: '9:16', skills: skillIds};
if (!Array.isArray(naskah.karakter)) naskah.karakter = [];
naskah.karakter = naskah.karakter.filter((k) => k && typeof k.id === 'string').map((k, i) => ({
  id: k.id,
  nama: typeof k.nama === 'string' ? k.nama : `Karakter ${i + 1}`,
  deskripsi: typeof k.deskripsi === 'string' ? k.deskripsi : '',
  warna: Array.isArray(k.warna) ? k.warna.filter((w) => typeof w === 'string').slice(0, 4) : [],
  ciriTetap: Array.isArray(k.ciriTetap) ? k.ciriTetap.map(String).slice(0, 8) : [],
}));
naskah.handle = env.HANDLE || ''; // nama akun hanya dari pengaturan pengguna — AI kadang mengarang akun
// judul layar berupa label ("Hook", "Tips 1") → ganti dengan 4 kata awal narasi
for (const a of naskah.adegan ?? []) {
  if (!Array.isArray(a.karakter)) a.karakter = [];
  if (!Array.isArray(a.objek)) a.objek = [];
  if (!Array.isArray(a.aksi)) a.aksi = [];
  if (a.kamera && typeof a.kamera !== 'object') delete a.kamera;
  if (typeof a.lingkungan !== 'string') a.lingkungan = typeof a.visual === 'string' ? a.visual : 'ruangan sederhana';
  if (!a.judul || /^(hook|tips?\s*\d*|penutup|pembuka|adegan\s*\d+|cta|intro|outro)$/i.test(a.judul.trim()))
    a.judul = String(a.teks ?? '').replace(/[.,!?]+$/, '').split(/\s+/).slice(0, 4).join(' ');
}
if (!Array.isArray(naskah.adegan) || !naskah.adegan.length) berhenti('JSON tidak punya daftar "adegan".');
const nama = opsi.nama ?? topik.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 40);
mkdirSync('naskah', {recursive: true});
writeFileSync(`naskah/${nama}.json`, JSON.stringify(naskah, null, 2));
console.log(`• naskah/${nama}.json: ${naskah.adegan.length} adegan. Periksa dulu, lalu: node buat.mjs naskah/${nama}.json`);
