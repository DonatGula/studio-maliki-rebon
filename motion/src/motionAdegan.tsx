// kredit-maliki: adapter metadata Motion Skills → animasi native Remotion.
import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';

type Props = {
  children: React.ReactNode;
  visual?: string;
  gerak?: string;
  transisi?: string;
};

const norm = (value?: string) => String(value ?? '').toLocaleLowerCase('id-ID');

export const MotionAdegan: React.FC<Props> = ({children, visual, gerak, transisi}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const move = norm(gerak);
  const transition = norm(transisi);
  const hasMotion = Boolean(move.trim() || transition.trim());

  // File proyek lama yang belum punya metadata tetap dirender persis seperti sebelumnya.
  if (!hasMotion) return <>{children}</>;

  const masuk = spring({frame, fps, config: {damping: 18, stiffness: 120}});
  const fade = interpolate(frame, [0, 12], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const zoom = transition.includes('zoom') || transition.includes('membesar') || transition.includes('scale');
  const fromLeft = transition.includes('kiri') || transition.includes('left');
  const fromRight = transition.includes('kanan') || transition.includes('right');
  const fromTop = transition.includes('atas') || transition.includes('top');
  const fromBottom = transition.includes('bawah') || transition.includes('bottom');
  const isFade = transition.includes('fade') || transition.includes('pudar') || transition.includes('memudar');
  const xStart = fromLeft ? -56 : fromRight ? 56 : 0;
  const yStart = fromTop ? -48 : fromBottom ? 48 : 18;
  const entryX = interpolate(masuk, [0, 1], [xStart, 0]);
  const entryY = interpolate(masuk, [0, 1], [yStart, 0]);
  const entryScale = zoom ? interpolate(masuk, [0, 1], [0.88, 1]) : 1;

  let floatY = 0;
  let pulseScale = 1;
  let rotate = 0;
  if (/melayang|mengambang|floating|float/.test(move)) floatY = Math.sin(frame / 18) * 9;
  if (/denyut|berdenyut|pulse|detak/.test(move)) pulseScale = 1 + Math.sin(frame / 8) * 0.025;
  if (/putar|berputar|rotate|rotasi/.test(move)) rotate = Math.sin(frame / 24) * 2.5;
  if (/geser|bergeser|pan kanan|pan kiri/.test(move)) floatY = 0, rotate = 0;

  const opacity = isFade ? fade : interpolate(masuk, [0, 1], [0.35, 1]);
  const transform = `translate(${entryX}px, ${entryY + floatY}px) scale(${entryScale * pulseScale}) rotate(${rotate}deg)`;

  return (
    <AbsoluteFill
      aria-label={visual || undefined}
      title={visual || undefined}
      data-motion={gerak || undefined}
      data-transition={transisi || undefined}
      style={{opacity, transform, transformOrigin: 'center center'}}
    >
      {children}
    </AbsoluteFill>
  );
};
