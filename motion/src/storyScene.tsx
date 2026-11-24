import React from 'react';
import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';

export type KarakterStory = {
  id: string;
  nama?: string;
  deskripsi?: string;
  warna?: string[];
  ciriTetap?: string[];
};

export type AdeganStory = {
  visual?: string;
  lingkungan?: string;
  karakter?: string[];
  objek?: string[];
  aksi?: Array<{subjek?: string; gerakan?: string} | string>;
  kamera?: {framing?: string; angle?: string; gerak?: string};
};

type Props = {adegan: AdeganStory; karakter?: KarakterStory[]};

const Character: React.FC<{x: number; y: number; color: string; frame: number; action: string}> = ({x, y, color, frame, action}) => {
  const walk = /jalan|berjalan|lari|berlari/i.test(action);
  const sit = /duduk|tidur|berbaring/i.test(action);
  const wave = /lamba|menyapa|menunjuk|angkat|pegang|mengambil/i.test(action);
  const bob = walk ? Math.sin(frame / 3) * 13 : Math.sin(frame / 12) * 3;
  const arm = wave ? -48 + Math.sin(frame / 7) * 8 : walk ? Math.sin(frame / 3) * 25 : 8;
  return (
    <g transform={`translate(${x} ${y + bob})`}>
      <ellipse cx="0" cy="315" rx="94" ry="20" fill="#1e293b" opacity=".16" />
      <g transform={sit ? 'translate(0 65) rotate(-12)' : undefined}>
        <path d="M-38 190 L-55 300 Q-58 316 -42 320 L-8 320 L8 220 L20 320 L55 320 Q70 315 62 298 L42 190Z" fill="#26364a" />
        <path d="M-66 105 Q-72 95 -85 110 L-112 190 Q-120 210 -101 218 Q-84 222 -76 202 L-43 150" fill={color} stroke="#26364a" strokeWidth="13" strokeLinecap="round" />
        <path d={`M66 105 Q75 95 87 110 L${wave ? 110 : 122} ${wave ? 35 : 190} Q${wave ? 120 : 132} ${wave ? 18 : 210} ${wave ? 101 : 102} ${wave ? 10 : 218} Q${wave ? 84 : 84} ${wave ? 5 : 222} 76 202 L43 150`} fill={color} stroke="#26364a" strokeWidth="13" strokeLinecap="round" />
        <path d="M-58 90 Q-72 120 -58 200 Q0 225 58 200 Q72 120 58 90 Q0 65 -58 90Z" fill={color} stroke="#26364a" strokeWidth="8" />
      </g>
      <path d="M-58 8 Q-60 -72 0 -78 Q62 -72 58 8 L48 60 Q0 88 -48 60Z" fill="#f1bd91" stroke="#26364a" strokeWidth="8" />
      <path d="M-62 0 Q-80 -68 -24 -88 Q38 -112 65 -50 L58 -8 Q28 -42 0 -48 Q-30 -18 -62 0Z" fill="#24252b" />
      <circle cx="-22" cy="18" r="5" fill="#20242b" /><circle cx="22" cy="18" r="5" fill="#20242b" />
      <path d="M-12 43 Q0 52 12 43" fill="none" stroke="#9a5148" strokeWidth="5" strokeLinecap="round" />
    </g>
  );
};

const Room: React.FC<{kind: string; frame: number}> = ({kind, frame}) => {
  const night = /malam|tidur|kamar/i.test(kind);
  const kitchen = /dapur|masak|makan/i.test(kind);
  const outside = /jalan|taman|luar|kota/i.test(kind);
  const wall = night ? '#26334d' : kitchen ? '#f2dfc3' : outside ? '#a9d8d0' : '#f3dfc8';
  return (
    <>
      <rect width="1080" height="1920" fill={wall} />
      {outside ? <>
        <circle cx="830" cy="280" r="105" fill="#ffe5a0" />
        <path d="M0 1160 Q260 950 520 1150 T1080 1080 V1500 H0Z" fill="#83ae86" />
        <path d="M0 1320 Q300 1180 620 1320 T1080 1250 V1920 H0Z" fill="#6d9875" />
        {[130, 870].map((x) => <g key={x}><rect x={x} y="820" width="35" height="470" fill="#795b43" /><circle cx={x+15} cy="780" r="125" fill="#548b66" /></g>)}
      </> : <>
        <path d="M0 1450 H1080 V1920 H0Z" fill={night ? '#8c6d60' : '#c99c72'} />
        <rect x="90" y="230" width="300" height="360" rx="12" fill={night ? '#536b91' : '#b7dce7'} stroke="#fff0d8" strokeWidth="24" />
        <path d="M240 230 V590 M90 410 H390" stroke="#fff0d8" strokeWidth="15" />
        {kitchen ? <>
          <rect x="120" y="1050" width="840" height="280" rx="18" fill="#b77e54" />
          <rect x="170" y="950" width="180" height="100" rx="12" fill="#e8e2d6" />
          <rect x="410" y="960" width="220" height="90" rx="12" fill="#d1a75e" />
          <circle cx="760" cy="970" r="85" fill="#e9e3d8" />
        </> : <>
          <rect x="600" y="1120" width="360" height="270" rx="26" fill="#9a6c58" />
          <rect x="570" y="1080" width="420" height="90" rx="30" fill="#d9b9a2" />
          <rect x="640" y="900" width="280" height="190" rx="18" fill="#f1e4d5" />
          <rect x="835" y="650" width="26" height="340" fill="#74513f" />
          <path d="M790 650 Q850 530 920 650Z" fill="#f3c56c" />
        </>}
      </>}
      <path d="M0 1450 H1080" stroke="#493d37" strokeWidth="12" opacity=".25" />
      {night && <g opacity=".75"><circle cx="770" cy="260" r="7" fill="#fff2bd" /><circle cx="900" cy="390" r="5" fill="#fff2bd" /><circle cx="600" cy="170" r="6" fill="#fff2bd" /></g>}
    </>
  );
};


const SceneObjects: React.FC<{items: string[]; frame: number}> = ({items, frame}) => (
  <g>
    {items.slice(0, 5).map((item, i) => {
      const name = item.toLowerCase();
      const x = 150 + i * 190;
      const y = 1280 + Math.sin(frame / 16 + i) * 3;
      if (/ponsel|hp|telepon|phone/.test(name)) return <g key={item + i} transform={`translate(${x} ${y}) rotate(-8)`}>
        <rect x="-42" y="-76" width="84" height="150" rx="14" fill="#26364a" /><rect x="-34" y="-62" width="68" height="120" rx="7" fill="#a9d8e5" />
        <circle cy="65" r="4" fill="#e9e5dc" />
      </g>;
      if (/buku|book/.test(name)) return <g key={item + i} transform={`translate(${x} ${y}) rotate(5)`}>
        <path d="M-68 -55 Q-10 -70 0 -42 V55 Q-30 32 -68 48Z" fill="#e9c66f" stroke="#70543d" strokeWidth="7" />
        <path d="M0 -42 Q30 -70 68 -55 V48 Q30 32 0 55Z" fill="#f5e7bd" stroke="#70543d" strokeWidth="7" />
        <path d="M-48 -28 H-12 M16 -28 H48 M-48 -8 H-12 M16 -8 H48" stroke="#a58c63" strokeWidth="4" />
      </g>;
      if (/kopi|gelas|cangkir|cup/.test(name)) return <g key={item + i} transform={`translate(${x} ${y})`}>
        <path d="M-42 -42 H36 L28 50 Q0 66 -30 50Z" fill="#f5eee2" stroke="#8c6550" strokeWidth="7" />
        <path d="M36 -25 Q82 -38 72 8 Q65 34 31 22" fill="none" stroke="#8c6550" strokeWidth="9" />
        <path d="M-25 -28 H25" stroke="#9a6045" strokeWidth="8" />
      </g>;
      if (/laptop|komputer/.test(name)) return <g key={item + i} transform={`translate(${x} ${y})`}>
        <rect x="-78" y="-68" width="156" height="105" rx="9" fill="#526477" stroke="#26364a" strokeWidth="8" />
        <rect x="-66" y="-56" width="132" height="80" fill="#9bd1dc" />
        <path d="M-96 42 H96 L75 62 H-75Z" fill="#d5dce1" stroke="#526477" strokeWidth="6" />
      </g>;
      if (/bola|ball/.test(name)) return <g key={item + i} transform={`translate(${x} ${y})`}>
        <circle r="54" fill="#e58a54" stroke="#7d4c39" strokeWidth="7" />
        <path d="M-50 -15 Q0 15 50 -15 M-15 -50 Q15 0 -15 50" fill="none" stroke="#f7d7a7" strokeWidth="7" />
      </g>;
      if (/pintu|door/.test(name)) return <g key={item + i} transform={`translate(${x} ${y})`}>
        <rect x="-48" y="-125" width="96" height="220" rx="8" fill="#a87956" stroke="#654c3b" strokeWidth="8" />
        <circle cx="28" cy="-12" r="7" fill="#f1d08a" />
      </g>;
      return <g key={item + i} transform={`translate(${x} ${y})`}>
        <rect x="-48" y="-45" width="96" height="90" rx="12" fill="#d6b28b" stroke="#795b43" strokeWidth="6" />
        <path d="M-28 -20 H28 M-28 0 H28 M-28 20 H10" stroke="#9a7959" strokeWidth="5" />
      </g>;
    })}
  </g>
);

export const StoryScene: React.FC<Props> = ({adegan, karakter = []}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = spring({frame, fps, config: {damping: 18, stiffness: 90}});
  const actionText = (adegan.aksi ?? []).map((a) => typeof a === 'string' ? a : a?.gerakan ?? '').join(' ');
  const ids = adegan.karakter?.length ? adegan.karakter : [karakter[0]?.id ?? 'tokoh-utama'];
  const selected: KarakterStory[] = ids.map((id) => karakter.find((c) => c.id === id) ?? {id, warna: []});
  const kind = adegan.lingkungan ?? adegan.visual ?? 'ruangan sederhana';
  const framing = adegan.kamera?.framing ?? 'medium';
  const scale = framing === 'close-up' || framing === 'closeup' ? 1.22 : framing === 'wide' ? .88 : 1;
  const cameraX = adegan.kamera?.gerak?.includes('pan') ? Math.sin(frame / 36) * 24 : 0;
  const cameraScale = adegan.kamera?.gerak?.includes('push') ? interpolate(frame, [0, fps * 2], [1, 1.08], {extrapolateRight: 'clamp'}) : scale;
  const positions = selected.length > 1 ? selected.map((_, i) => 360 + i * (360 / (selected.length - 1))) : [540];
  return (
    <div style={{position: 'absolute', inset: 0, overflow: 'hidden', background: '#ead8c2'}}>
      <svg viewBox="0 0 1080 1920" width="100%" height="100%" preserveAspectRatio="xMidYMid slice">
        <g transform={`translate(${cameraX} 0) scale(${cameraScale})`} style={{transformOrigin: '540px 960px'}}>
          <Room kind={kind} frame={frame} />
          <SceneObjects items={adegan.objek ?? []} frame={frame} />
          <g opacity={interpolate(enter, [0, 1], [0, 1])}>
            {selected.map((c, i) => <Character key={c.id} x={positions[i]} y={1040} color={c.warna?.[0] ?? (i ? '#d68b58' : '#4f86b7')} frame={frame} action={actionText} />)}
          </g>
          <rect x="0" y="0" width="1080" height="1920" fill="url(#storyShade)" />
        </g>
        <defs><linearGradient id="storyShade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#172033" stopOpacity=".12" /><stop offset=".68" stopColor="#172033" stopOpacity="0" /><stop offset="1" stopColor="#172033" stopOpacity=".12" /></linearGradient></defs>
      </svg>
    </div>
  );
};
