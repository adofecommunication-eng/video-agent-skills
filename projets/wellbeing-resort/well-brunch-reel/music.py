#!/usr/bin/env python3
"""Fond musical léger (lounge / amapiano doux) pour le Reel Well Brunch.

100 BPM : un temps = 0,6 s, une mesure = 2,4 s. Les coupes du montage
(2,4 s · 6 s · 12 s · 15 s) tombent toutes sur un temps (4, 10, 20, 25).
Sortie : sources/musique-legere.wav (stéréo 44,1 kHz, 18 s).
"""
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
SR, DUR, BPM = 44100, 18.0, 100
BEAT = 60 / BPM
N = int(SR * DUR)
CUTS = [2.4, 6.0, 12.0, 15.0]
rng = np.random.default_rng(3)
t_all = np.arange(N) / SR


def midi(m):
    return 440 * 2 ** ((m - 69) / 12)


def lowpass(x, fc):
    """Filtre passe-bas un pôle (appliqué 2 fois = 12 dB/oct)."""
    a = np.exp(-2 * np.pi * fc / SR)
    for _ in range(2):
        y = np.empty_like(x)
        acc = 0.0
        for i, v in enumerate(x):
            acc = (1 - a) * v + a * acc
            y[i] = acc
        x = y
    return x


def env_adsr(n, a, r):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def add(buf, sig, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N:
        return
    sig = sig[: N - i]
    l, r = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
    buf[i:i + len(sig), 0] += sig * gain * l
    buf[i:i + len(sig), 1] += sig * gain * r


# accords (une mesure chacun) : Fmaj9 · Em7 · Dm9 · Cmaj7(add9) en boucle
CHORDS = [[53, 57, 60, 64, 67], [52, 55, 59, 62, 67], [50, 53, 57, 60, 64], [48, 52, 55, 59, 62]]
BASS = [41, 40, 38, 36]

music = np.zeros((N, 2))

# --- nappe (pad) : dents de scie désaccordées, filtrées, attaque lente
pad = np.zeros(N)
bar = 4 * BEAT
for b in range(int(DUR / bar) + 1):
    ch = CHORDS[b % 4]
    n = int(bar * SR) + int(0.4 * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for m in ch:
        for det in (-0.08, 0.08):
            f = midi(m + 12) * (1 + det / 100 * 6)
            s += 2 * ((t * f) % 1) - 1
    s *= env_adsr(n, 0.5, 0.5) / (len(ch) * 2)
    i = int(b * bar * SR)
    pad[i:i + n] += s[: max(0, N - i)]
pad = lowpass(pad, 1400)
music[:, 0] += pad * 0.20
music[:, 1] += np.roll(pad, int(0.011 * SR)) * 0.20  # léger élargissement stéréo

# --- piano électrique : accords en contretemps (dès 2,4 s)
for k in range(int(DUR / BEAT * 2)):
    t0 = k * BEAT / 2
    if t0 < 2.4 or k % 2 == 0 or t0 > 17.2:
        continue
    ch = CHORDS[int(t0 // bar) % 4]
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * midi(m + 12) * t) + 0.25 * np.sin(4 * np.pi * midi(m + 12) * t)
            for m in ch[1:])
    s *= np.exp(-t * 7) / 4
    add(music, s, t0, 0.13, pan=0.25 if k % 4 == 1 else -0.25)

# --- basse « log drum » douce : glissando descendant, motif syncopé (dès 2,4 s)
PATTERN = [0, 3, 6, 10, 11, 14]  # doubles-croches dans la mesure
for b in range(int(DUR / bar) + 1):
    for s16 in PATTERN:
        t0 = b * bar + s16 * BEAT / 4
        if t0 < 2.4 or t0 > 17.0:
            continue
        f = midi(BASS[b % 4] + (12 if s16 in (10, 11) else 0))
        n = int(0.35 * SR)
        t = np.arange(n) / SR
        ph = 2 * np.pi * np.cumsum(f * (1 + 0.6 * np.exp(-t * 40))) / SR
        s = np.tanh(1.6 * np.sin(ph)) * np.exp(-t * 9)
        add(music, s, t0, 0.30)

# --- kick doux sur les temps 1 et 3 (dès 2,4 s)
for k in range(int(DUR / BEAT)):
    t0 = k * BEAT
    if t0 < 2.4 or k % 2 or t0 > 17.0:
        continue
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    ph = 2 * np.pi * np.cumsum(50 + 90 * np.exp(-t * 35)) / SR
    add(music, np.sin(ph) * np.exp(-t * 14), t0, 0.32)

# --- shaker : doubles-croches, accent sur les contretemps (tout le long)
shk_n = int(0.06 * SR)
for k in range(int(DUR / (BEAT / 4))):
    t0 = k * BEAT / 4
    if t0 > 17.4:
        continue
    noise = rng.normal(0, 1, shk_n)
    noise = noise - lowpass(noise, 5000)  # passe-haut
    e = np.exp(-np.arange(shk_n) / SR * 60)
    g = 0.05 if k % 2 else 0.025
    add(music, noise * e, t0, g * (0.6 if t0 < 2.4 else 1), pan=0.35)

# --- transitions : souffle montant avant chaque coupe, impact + scintillement dessus
for c in CUTS:
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    noise = rng.normal(0, 1, n)
    sweep = noise - lowpass(noise, 1500)
    add(music, sweep * (t / t[-1]) ** 2.5 * 0.5, c - 0.9, 0.18)
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    boom = np.sin(2 * np.pi * np.cumsum(38 + 40 * np.exp(-t * 8)) / SR) * np.exp(-t * 3.5)
    shimmer = sum(np.sin(2 * np.pi * midi(m) * t) for m in (84, 88, 91, 96)) * np.exp(-t * 2.2) / 4
    add(music, boom, c, 0.30)
    add(music, shimmer, c, 0.05, pan=-0.3)
    add(music, np.roll(shimmer, 900), c, 0.05, pan=0.3)

# carte finale : on retire un peu d'énergie, puis fondu
music[int(17.0 * SR):] *= np.linspace(1, 0, N - int(17.0 * SR))[:, None]
music[: int(0.05 * SR)] *= np.linspace(0, 1, int(0.05 * SR))[:, None]
music /= np.abs(music).max() / 0.8

pcm = (music * 32767).astype("<i2")
import wave  # noqa: E402

dst = ROOT / "sources" / "musique-legere.wav"
with wave.open(str(dst), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("OK", dst)
