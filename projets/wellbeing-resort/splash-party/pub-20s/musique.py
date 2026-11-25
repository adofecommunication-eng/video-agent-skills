#!/usr/bin/env python3
"""Bande-son de la pub Splash Party (20,1 s) avec les sons fournis par le client :
  - musique : sons/musique-beach-vibes.mp3 ; le « drop » du morceau (16,31 s) tombe à 3,72 s,
    quand toutes les infos du flyer sont posées (la montée du morceau accompagne l'ouverture) ;
  - bruitages : extraits des packs sons/sfx1, sfx4, sfx5, sfx6 (découpés à la main), calés sur pub.py.
Sortie : bande-son.wav (stéréo 48 kHz). Le mixage final (-14 LUFS) est fait par pub.py.
"""
import subprocess
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SONS = HERE / "sons"
SR, DUR = 48000, 20.1
N = int(SR * DUR)
DROP_SRC, DROP_VID = 16.31, 3.72


def load(name, start=0.0, dur=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(start), "-i", str(SONS / name)]
    if dur:
        cmd += ["-t", str(dur)]
    cmd += ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, dtype="<f4").reshape(-1, 2).astype(np.float64)


def clip(name, a, b):
    """Extrait un son d'un pack, normalisé (crête -6 dB), avec fondus de 5 ms."""
    x = load(name, a, b - a)
    x = x / (np.abs(x).max() + 1e-9) * 0.5
    f = int(0.005 * SR)
    x[:f] *= np.linspace(0, 1, f)[:, None]
    x[-f:] *= np.linspace(1, 0, f)[:, None]
    return x


sfx = np.zeros((N, 2))


def add(x, t0, g=1.0):
    i = int(t0 * SR)
    if i >= N:
        return
    x = x[: N - i]
    sfx[i:i + len(x)] += x * g


# sons découpés dans les packs (repérés par analyse : bruit/tonal, durée, attaque)
WHOOSH_LONG = clip("sfx4.mp3", 10.01, 11.01)     # souffle ample
WHOOSH_MED = clip("sfx5.mp3", 5.58, 6.61)        # souffle
SWOOSH_IN = clip("sfx5.mp3", 4.55, 5.02)         # souffle qui arrive
SWISH = clip("sfx1.mp3", 5.37, 5.62)             # coup sec
SHORT_AIR = clip("sfx4.mp3", 4.65, 4.98)         # souffle court (flous du titre)
SHIMMER = clip("sfx1.mp3", 1.52, 3.21)           # scintillement
SPARKLE = clip("sfx1.mp3", 8.16, 8.49)           # éclat aigu
BOOM = clip("sfx1.mp3", 0.11, 0.47)              # impact
LOW_HIT = clip("sfx5.mp3", 3.38, 4.05)           # coup grave
POP = clip("sfx5.mp3", 1.93, 2.08)               # pop
POP2 = clip("sfx1.mp3", 1.05, 1.16)              # pop court
CLICK = clip("sfx4.mp3", 0.54, 0.59)             # clic (écriture)
RISER = clip("sfx6.mp3", 6.83, 8.54)             # montée

add(WHOOSH_LONG, 0.0, 0.55)              # SPLASH apparaît
add(SHIMMER, 0.5, 0.35)                  # PARTY se dessine
add(POP, 1.0, 0.5)                       # date
add(SWISH, 1.05, 0.5)                    # bandeau
add(WHOOSH_MED, 1.25, 0.45)              # le bloc remonte
add(BOOM, 2.2, 0.55)                     # bloc « Entrée »
for k, t0 in enumerate(np.arange(2.35, 3.6, 0.09)):   # infos qui s'inscrivent
    add(CLICK, t0, 0.22 if k % 2 else 0.16)
add(RISER, DROP_VID - len(RISER) / SR, 0.35)          # montée jusqu'au drop
add(POP2, 3.7, 0.55)                     # pastille
add(SWOOSH_IN, 4.6, 0.5)                 # macaron qui arrive
add(LOW_HIT, 5.05, 0.5)
add(SPARKLE, 5.15, 0.35)
for k, g in enumerate([5.1, 8.05, 12.55, 15.55, 18.05]):   # flous de mouvement du titre
    add(SHORT_AIR if k % 2 else SWISH, g, 0.4)

music = load("musique-beach-vibes.mp3", DROP_SRC - DROP_VID, DUR)
music = np.pad(music, ((0, max(0, N - len(music))), (0, 0)))[:N]
fi, fo = int(0.25 * SR), int(1.4 * SR)
music[:fi] *= np.linspace(0, 1, fi)[:, None]
music[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
mix = music * 0.62 + sfx
mix /= np.abs(mix).max() / 0.89
with wave.open(str(HERE / "bande-son.wav"), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print("OK")
