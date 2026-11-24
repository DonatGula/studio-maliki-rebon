// Sequential local batch generator. Each topic gets its own project folder.
import {readFileSync, writeFileSync, copyFileSync, existsSync, mkdirSync, renameSync} from 'node:fs';
import {join, resolve} from 'node:path';
import {spawnSync} from 'node:child_process';

const manifestPath = resolve(process.argv[2] ?? '');
if (!process.argv[2]) throw new Error('Manifest batch diperlukan.');
const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));
const results = [];
for (const item of manifest.items ?? []) {
  console.log(`\n=== [${item.no}/${manifest.items.length}] ${item.topic} ===`);
  try {
    const scriptArgs = [join('naskah.mjs'), item.topic, `--ai=${item.ai}`, `--gaya=${item.style}`,
      `--nama=${item.name}`, `--skills=${item.skills || 'auto'}`];
    const script = spawnSync(process.execPath, scriptArgs, {encoding: 'utf8', env: process.env, maxBuffer: 32 * 1024 * 1024});
    if (script.stdout) console.log(script.stdout.trim());
    if (script.status !== 0) throw new Error((script.stderr || script.stdout || 'Gagal membuat naskah').slice(-1200));
    const draft = join('naskah', item.name + '.json');
    mkdirSync(item.folder, {recursive: true});
    copyFileSync(draft, join(item.folder, 'naskah.json'));
    writeFileSync(join(item.folder, 'permintaan.json'), JSON.stringify({topik: item.topic, gaya: item.style, ai: item.ai, skills: item.skills}, null, 2));
    const renderArgs = [join('buat.mjs'), draft, `--gaya=${item.style}`, `--preset=${item.preset || 'shorts'}`];
    if (item.voice === 'voxcpm') renderArgs.push('--suara=voxcpm');
    const render = spawnSync(process.execPath, renderArgs, {encoding: 'utf8', env: process.env, maxBuffer: 64 * 1024 * 1024});
    if (render.stdout) console.log(render.stdout.trim());
    if (render.status !== 0) throw new Error((render.stderr || render.stdout || 'Gagal merender video').slice(-1800));
    const output = join('hasil', `${item.name}-${item.style}.mp4`);
    if (!existsSync(output)) throw new Error('File MP4 hasil render tidak ditemukan.');
    renameSync(output, join(item.folder, 'video.mp4'));
    results.push({name: item.name, topic: item.topic, ok: true, video: `/berkas/motion/${item.name}/video.mp4`});
    console.log(`✓ Selesai: ${item.name}`);
  } catch (error) {
    results.push({name: item.name, topic: item.topic, ok: false, error: String(error.message ?? error)});
    console.log(`✕ Gagal: ${String(error.message ?? error)}`);
  }
}
writeFileSync(manifest.summary, JSON.stringify(results, null, 2));
const ok = results.filter((x) => x.ok).length;
console.log(`\nBatch selesai: ${ok}/${results.length} video berhasil.`);
if (!ok) process.exitCode = 1;
