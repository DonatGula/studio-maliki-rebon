import React from 'react';

export type CharacterDesign = {
  id: string;
  nama?: string;
  deskripsi?: string;
  warna?: string[];
  ciriTetap?: string[];
  tampilan?: {
    kulit?: string;
    rambut?: string;
    baju?: string;
    celana?: string;
    aksesoris?: string;
  };
};

export type EnvironmentSpec = {
  jenis?: string;
  waktu?: string;
  warnaLatar?: string;
};

const Figure: React.FC<{design: CharacterDesign; x: number; y: number; frame: number; action: string}> = ({design, x, y, frame, action}) => {
  const colors = design.tampilan ?? {};
  const shirt = colors.baju ?? design.warna?.[0] ?? '#4f86b7';
  const pants = colors.celana ?? '#26364a';
  const skin = colors.kulit ?? '#f1bd91';
  const hair = colors.rambut ?? '#24252b';
  const walk = /jalan|berjalan|lari|berlari/i.test(action);
  const sit = /duduk|tidur|berbaring/i.test(action);
  const raise = /lamba|menyapa|menunjuk|angkat|mengambil/i.test(action);
  const swing = walk ? Math.sin(frame / 3) * 22 : 0;
  const bob = walk ? Math.abs(Math.sin(frame / 3)) * -10 : Math.sin(frame / 12) * 2;
  return (
    <g transform={`translate(${x} ${y + bob})`}>
      <ellipse cx="0" cy="315" rx="82" ry="17" fill="#1e293b" opacity=".15" />
      <g transform={sit ? 'translate(0 75) rotate(-10)' : undefined}>
        <path d="M-38 190 L-52 292 Q-58 315 -38 318 L-5 318 L8 225 L20 318 L53 318 Q68 314 60 292 L40 190Z" fill={pants} />
        <path d={`M-58 112 Q-73 102 -84 124 L-111 190 Q-119 210 -100 217 Q-82 222 -74 201 L-40 150`} fill={shirt} stroke="#26364a" strokeWidth="12" strokeLinecap="round" />
        <path d={`M58 112 Q73 102 84 124 L${raise ? 104 : 116} ${raise ? 35 : 190} Q${raise ? 112 : 126} ${raise ? 18 : 210} ${raise ? 94 : 98} ${raise ? 12 : 217} Q${raise ? 78 : 80} ${raise ? 8 : 220} 74 201 L40 150`} fill={shirt} stroke="#26364a" strokeWidth="12" strokeLinecap="round" />
        <path d="M-58 90 Q-72 120 -58 200 Q0 225 58 200 Q72 120 58 90 Q0 65 -58 90Z" fill={shirt} stroke="#26364a" strokeWidth="8" />
      </g>
      <path d="M-58 8 Q-60 -72 0 -78 Q62 -72 58 8 L48 60 Q0 88 -48 60Z" fill={skin} stroke="#26364a" strokeWidth="8" />
      <path d="M-62 0 Q-80 -68 -24 -88 Q38 -112 65 -50 L58 -8 Q28 -42 0 -48 Q-30 -18 -62 0Z" fill={hair} />
      <circle cx="-22" cy="18" r="5" fill="#20242b" /><circle cx="22" cy="18" r="5" fill="#20242b" />
      <path d="M-12 43 Q0 52 12 43" fill="none" stroke="#9a5148" strokeWidth="5" strokeLinecap="round" />
      {colors.aksesoris ? <path d="M-44 5 Q0 -12 44 5" fill="none" stroke={colors.aksesoris} strokeWidth="9" /> : null}
      {walk ? <g transform={`translate(0 0) rotate(${swing / 4})`} /> : null}
    </g>
  );
};

export const StoryCharacter: React.FC<{design: CharacterDesign; x: number; y: number; frame: number; action: string}> = (props) => <Figure {...props} />;

export const StoryEnvironment: React.FC<{spec: EnvironmentSpec}> = ({spec}) => {
  const label = `${spec.jenis ?? ''} ${spec.waktu ?? ''}`.toLowerCase();
  const night = /malam|night/.test(label);
  const kitchen = /dapur|kitchen/.test(label);
  const outside = /luar|taman|jalan|kota|outdoor/.test(label);
  const wall = spec.warnaLatar ?? (night ? '#26334d' : kitchen ? '#f2dfc3' : outside ? '#a9d8d0' : '#f3dfc8');
  return <g>
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
    {night ? <g opacity=".75"><circle cx="770" cy="260" r="7" fill="#fff2bd" /><circle cx="900" cy="390" r="5" fill="#fff2bd" /><circle cx="600" cy="170" r="6" fill="#fff2bd" /></g> : null}
  </g>;
};

export const StoryProp: React.FC<{name: string; x: number; y: number}> = ({name, x, y}) => {
  const n = name.toLowerCase();
  return <g transform={`translate(${x} ${y})`}>
    {/ponsel|hp|telepon|phone/.test(n) ? <><rect x="-42" y="-76" width="84" height="150" rx="14" fill="#26364a" /><rect x="-34" y="-62" width="68" height="120" rx="7" fill="#a9d8e5" /></> :
    /buku|book/.test(n) ? <><path d="M-68 -55 Q-10 -70 0 -42 V55 Q-30 32 -68 48Z" fill="#e9c66f" stroke="#70543d" strokeWidth="7" /><path d="M0 -42 Q30 -70 68 -55 V48 Q30 32 0 55Z" fill="#f5e7bd" stroke="#70543d" strokeWidth="7" /></> :
    /kopi|gelas|cangkir|cup/.test(n) ? <><path d="M-42 -42 H36 L28 50 Q0 66 -30 50Z" fill="#f5eee2" stroke="#8c6550" strokeWidth="7" /><path d="M36 -25 Q82 -38 72 8 Q65 34 31 22" fill="none" stroke="#8c6550" strokeWidth="9" /></> :
    /laptop|komputer/.test(n) ? <><rect x="-78" y="-68" width="156" height="105" rx="9" fill="#526477" stroke="#26364a" strokeWidth="8" /><rect x="-66" y="-56" width="132" height="80" fill="#9bd1dc" /><path d="M-96 42 H96 L75 62 H-75Z" fill="#d5dce1" stroke="#526477" strokeWidth="6" /></> :
    /bola|ball/.test(n) ? <circle r="54" fill="#e58a54" stroke="#7d4c39" strokeWidth="7" /> :
    /pintu|door/.test(n) ? <><rect x="-48" y="-125" width="96" height="220" rx="8" fill="#a87956" stroke="#654c3b" strokeWidth="8" /><circle cx="28" cy="-12" r="7" fill="#f1d08a" /></> :
    <><rect x="-48" y="-45" width="96" height="90" rx="12" fill="#d6b28b" stroke="#795b43" strokeWidth="6" /><path d="M-28 -20 H28 M-28 0 H28 M-28 20 H10" stroke="#9a7959" strokeWidth="5" /></>}
  </g>;
};
