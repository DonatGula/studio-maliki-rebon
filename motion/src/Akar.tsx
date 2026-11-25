import React from 'react';
import {Composition} from 'remotion';
import {Video, Props, totalFrame, FPS, Adegan} from './Video';
import {KarakterStory} from './storyScene';
// Props bawaan ditulis di sini (bukan impor naskah/contoh.json): installer tidak menyertakan folder naskah,
// dan render sungguhan selalu memakai --props dari buat.mjs.
const contoh = {
  judul: 'Contoh', gaya: 'garis', handle: '',
  adegan: [{judul: 'Contoh', teks: 'Tulis naskahmu di Studio Maliki.', kunci: ['naskahmu'], ikon: '🎬', durasi: 3}],
};

// Data pengujian Storytelling 2D — tidak mengganti template lama
const karakterUji: KarakterStory[] = [
  {
    id: 'karakter-utama',
    nama: 'Ani',
    deskripsi: 'Karakter uji 2D',
    warna: ['#4f86b7', '#26364a'],
    tampilan: {
      kulit: '#f1bd91',
      rambut: '#24252b',
      baju: '#4f86b7',
      celana: '#26364a',
      aksesoris: '#e8c56d',
    },
  },
];

const adeganUji: Adegan[] = [
  {
    judul: 'Pengujian 2D',
    teks: 'Ani duduk di ruangan tamu memegang ponsel.',
    kunci: ['Ani', 'ponsel'],
    durasi: 4,
    lingkungan: 'ruangan tamu siang',
    karakter: ['karakter-utama'],
    objek: ['meja', 'kursi', 'ponsel'],
    aksi: [{subjek: 'karakter-utama', gerakan: 'duduk memegang ponsel'}],
    kamera: {framing: 'medium', angle: 'eye-level', gerak: 'static'},
  },
];

const propsStorytelling2D: Props = {
  judul: 'Storytelling 2D — Uji Coba',
  gaya: 'garis',
  handle: '',
  aksen: '#4f86b7',
  adegan: adeganUji,
  motion: {styleId: 'storytelling-2d'},
  karakter: karakterUji,
};

export const Akar: React.FC = () => (
  <>
    <Composition
      id="Motion"
      component={Video}
      fps={FPS}
      width={1080}
      height={1920}
      durationInFrames={totalFrame(contoh as unknown as Props)}
      defaultProps={contoh as unknown as Props}
      calculateMetadata={({props}) => ({durationInFrames: totalFrame(props)})}
    />
    <Composition
      id="Motion-Storytelling2D"
      component={Video}
      fps={FPS}
      width={1080}
      height={1920}
      durationInFrames={totalFrame(propsStorytelling2D)}
      defaultProps={propsStorytelling2D}
      calculateMetadata={({props}) => ({durationInFrames: totalFrame(props)})}
    />
  </>
);
