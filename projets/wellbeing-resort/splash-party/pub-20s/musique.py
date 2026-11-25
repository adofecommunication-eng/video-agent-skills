#!/usr/bin/env python3
"""Musique originale + bruitages de la pub Splash Party (20,1 s), dans l'esprit de la référence
(house estivale ~129 BPM, montée filtrée à l'ouverture, souffles sur les apparitions, pop du macaron),
entièrement synthétisés ici : aucun extrait de la musique de la vidéo de référence.
Sortie : musique.wav
"""
import math
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SR, DUR, BPM = 44100, 20.1, 129
BEAT = 60 / BPM
N = int(SR * DUR)
mix = np.zeros((N, 2))
rng = np.random.default_rng(12)


def tt(d):
    return np.arange(int(d * SR)) / SR


def lp(x, fc):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X / np.sqrt(1 + (f / fc) ** 4), len(x))


def midi(m):
    return 440 * 2 ** ((m - 69) / 12)


def add(sig, t0, g=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N:
        return
    sig = sig[: N - i]
    mix[i:i + len(sig), 0] += sig * g * math.sqrt(0.5 * (1 - pan))
    mix[i:i + len(sig), 1] += sig * g * math.sqrt(0.5 * (1 + pan))


def kick():
    t = tt(0.35)
    return np.sin(2 * np.pi * np.cumsum(48 + 110 * np.exp(-t * 30)) / SR) * np.exp(-t * 9)


def clap():
    t = tt(0.2)
    n = rng.normal(0, 1, len(t))
    return (n - lp(n, 1100)) * np.exp(-t * 22) * 0.6


def hat(o=False):
    t = tt(0.22 if o else 0.05)
    n = rng.normal(0, 1, len(t))
    return (n - lp(n, 7000)) * np.exp(-t * (16 if o else 80))


def bass(m, d):
    t = tt(d)
    return np.tanh(2 * np.sin(2 * np.pi * midi(m) * t)) * np.exp(-t * 3) * np.minimum(1, t / 0.004)


def chord(ns, d):
    t = tt(d)
    s = sum(2 * ((t * midi(m) * (1 + k * 0.003)) % 1) - 1 for k, m in enumerate(ns) for _ in range(1))
    return lp(s / len(ns), 2200) * np.exp(-t * 3.5)


def pluck(m):
    t = tt(0.4)
    return (np.sin(2 * np.pi * midi(m) * t) + 0.3 * np.sin(4 * np.pi * midi(m) * t)) * np.exp(-t * 9)


CH = [[57, 60, 64, 67], [53, 57, 60, 64], [55, 59, 62, 65], [52, 55, 59, 62]]   # Lam7 · Famaj7 · Sol · Mim7
ROOT = [45, 41, 43, 40]
MEL = [76, None, 72, 74, 76, None, 79, 76, 74, None, 72, None, 69, 72, None, None]
DROP = 4 * BEAT * 2          # la batterie entre après 2 mesures (≈ 3,7 s), quand le flyer est posé

bar = 4 * BEAT
for b in range(int(DUR / bar) + 1):
    t0 = b * bar
    c = chord(CH[b % 4], bar)
    if t0 < DROP:
        c = lp(c, 500 + 2500 * t0 / DROP)
    add(c, t0, 0.16, pan=0.1)
    for k in range(8):
        tk = t0 + k * BEAT / 2
        if t0 >= DROP or k % 2 == 0:
            add(bass(ROOT[b % 4] + (12 if k % 2 else 0), BEAT / 2 * 0.9), tk, 0.18 if t0 >= DROP else 0.1)
for k in range(int(DUR / BEAT) + 1):
    t0 = k * BEAT
    if t0 >= DROP:
        add(kick(), t0, 0.6)
        if k % 2:
            add(clap(), t0, 0.3)
    add(hat(True), t0 + BEAT / 2, 0.05 if t0 >= DROP else 0.025, pan=-0.3)
for k in range(int(DUR / (BEAT / 4)) + 1):
    if k * BEAT / 4 >= DROP:
        add(hat(), k * BEAT / 4, 0.03, pan=0.3)
for k in range(int(DUR / (BEAT / 2)) + 1):
    m = MEL[k % len(MEL)]
    if m and k * BEAT / 2 >= DROP:
        add(pluck(m), k * BEAT / 2, 0.08, pan=0.2)


# ---------------------------------------------------------------- bruitages (calés sur pub.py)
def whoosh(d=0.5):
    t = tt(d)
    n = rng.normal(0, 1, len(t))
    return (n - lp(n, 1500)) * np.sin(np.pi * t / d) ** 2


def riser(d):
    t = tt(d)
    n = rng.normal(0, 1, len(t))
    return (n - lp(n, 1200)) * (t / d) ** 2.5


def pop():
    t = tt(0.1)
    return np.sin(2 * np.pi * np.cumsum(500 + 1800 * t / 0.1) / SR) * np.exp(-t * 40)


def tick():
    t = tt(0.02)
    return np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 300)


def impact():
    t = tt(1.0)
    return np.sin(2 * np.pi * np.cumsum(40 + 80 * np.exp(-t * 10)) / SR) * np.exp(-t * 4)


add(whoosh(0.6), 0.05, 0.25)                 # titre qui apparaît
add(whoosh(0.8), 0.45, 0.2, pan=-0.3)        # « PARTY » qui s'écrit
add(whoosh(0.35), 0.95, 0.2, pan=0.3)        # date
add(whoosh(0.3), 1.12, 0.22, pan=-0.3)       # bandeau
add(whoosh(0.7), 1.5, 0.2)                   # le bloc remonte
add(riser(DROP - 2.0), 2.0, 0.22)            # montée vers l'entrée de la batterie
add(impact(), DROP, 0.4)
for t0 in np.arange(2.35, 3.9, 0.075):        # infos qui s'inscrivent
    add(tick(), t0, 0.06, pan=-0.2)
add(pop(), 3.7, 0.35)                        # pastille
add(whoosh(0.4), 4.85, 0.25)                 # macaron
add(pop(), 5.05, 0.45)
for g in [5.1, 8.05, 12.55, 15.55, 18.05]:   # flous de mouvement sur le titre
    add(whoosh(0.3), g, 0.18, pan=float(rng.uniform(-0.5, 0.5)))

f0 = int((DUR - 1.2) * SR)
mix[f0:] *= np.linspace(1, 0, N - f0)[:, None] ** 1.5
mix /= np.abs(mix).max() / 0.85
with wave.open(str(HERE / "musique.wav"), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print("OK")
