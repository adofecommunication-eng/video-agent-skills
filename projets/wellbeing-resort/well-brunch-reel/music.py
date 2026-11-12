#!/usr/bin/env python3
"""Fond musical léger (lounge / amapiano doux) pour le Reel Well Brunch, calé sur la voix off.

- 100 BPM, grille rythmique ancrée sur le mot « PAR » (2,75 s) : le groove démarre pile sur la question.
- Silence de suspense entre « …une seule question : » et « par quoi commencer ? ».
- Impacts sur PAR / QUOI / COMMENCER, sur « Buffet » et sur « BRUNCH » ; souffle montant avant chaque coupe.
- Scintillement sur chaque activité prononcée, petit compteur qui « tique » pendant que le prix défile.
Les instants viennent de render.CUE / render.CUTS (une seule source de vérité).
Sortie : sources/musique-legere.wav (stéréo 44,1 kHz, 18 s).
"""
import wave
from pathlib import Path

import numpy as np

import render as R

ROOT = Path(__file__).resolve().parent
SR, DUR, BPM = 44100, 18.0, 100
BEAT = 60 / BPM
BAR = 4 * BEAT
N = int(SR * DUR)
CUE, CUTS = R.CUE, R.CUTS
GRID0 = CUE["par"]          # premier temps du groove
SUSP = (CUE["suspense"], CUE["par"])
END = 17.2
rng = np.random.default_rng(3)


def midi(m):
    return 440 * 2 ** ((m - 69) / 12)


def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    for _ in range(2):
        y = np.empty_like(x)
        acc = 0.0
        for i, v in enumerate(x):
            acc = (1 - a) * v + a * acc
            y[i] = acc
        x = y
    return x


def env(n, a, r):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def add(buf, sig, t0, gain=1.0, pan=0.0):
    i = int(round(t0 * SR))
    if i >= N or i + len(sig) <= 0:
        return
    if i < 0:
        sig, i = sig[-i:], 0
    sig = sig[: N - i]
    l, r = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
    buf[i:i + len(sig), 0] += sig * gain * l
    buf[i:i + len(sig), 1] += sig * gain * r


def in_susp(t):
    return SUSP[0] <= t < SUSP[1]


CHORDS = [[53, 57, 60, 64, 67], [52, 55, 59, 62, 67], [50, 53, 57, 60, 64], [48, 52, 55, 59, 62]]
BASS = [41, 40, 38, 36]
music = np.zeros((N, 2))


def bar_index(t):
    return int(np.floor((t - GRID0) / BAR)) % 4


# --- nappe : une mesure par accord, grille ancrée sur GRID0 ; coupée pendant le suspense
pad = np.zeros(N)
for b in range(-2, int((DUR - GRID0) / BAR) + 2):
    t0 = GRID0 + b * BAR
    ch = CHORDS[b % 4]
    n = int((BAR + 0.4) * SR)
    t = np.arange(n) / SR
    s = sum(2 * ((t * midi(m + 12) * (1 + d)) % 1) - 1 for m in ch for d in (-0.004, 0.004))
    s = s * env(n, 0.5, 0.5) / (len(ch) * 2)
    i = int(t0 * SR)
    lo, hi = max(0, i), min(N, i + n)
    if hi > lo:
        pad[lo:hi] += s[lo - i:hi - i]
pad = lowpass(pad, 1400)
gate = np.ones(N)
a, b = int(SUSP[0] * SR), int(SUSP[1] * SR)
gate[a:b] = np.linspace(1, 0, b - a) ** 3  # la nappe s'éteint dans le silence
music[:, 0] += pad * gate * 0.20
music[:, 1] += np.roll(pad * gate, int(0.011 * SR)) * 0.20

# --- shaker en doubles-croches sur toute la grille (discret avant la question)
shk_n = int(0.06 * SR)
k0 = int(np.floor(-GRID0 / (BEAT / 4)))
for k in range(k0, int((END - GRID0) / (BEAT / 4))):
    t0 = GRID0 + k * BEAT / 4
    if t0 < 0 or in_susp(t0):
        continue
    noise = rng.normal(0, 1, shk_n)
    noise = noise - lowpass(noise, 5000)
    e = np.exp(-np.arange(shk_n) / SR * 60)
    g = (0.05 if k % 2 else 0.025) * (0.5 if t0 < GRID0 else 1)
    add(music, noise * e, t0, g, pan=0.35)

# --- groove (dès PAR) : kick doux 1 et 3, basse log drum syncopée, piano en contretemps
for k in range(int((END - GRID0) / BEAT)):
    t0 = GRID0 + k * BEAT
    if k % 2 == 0:
        n = int(0.3 * SR)
        t = np.arange(n) / SR
        add(music, np.sin(2 * np.pi * np.cumsum(50 + 90 * np.exp(-t * 35)) / SR) * np.exp(-t * 14), t0, 0.32)
PATTERN = [0, 3, 6, 10, 11, 14]
for bb in range(int((END - GRID0) / BAR) + 1):
    for s16 in PATTERN:
        t0 = GRID0 + bb * BAR + s16 * BEAT / 4
        if t0 > END - 0.2:
            continue
        f = midi(BASS[bb % 4] + (12 if s16 in (10, 11) else 0))
        n = int(0.35 * SR)
        t = np.arange(n) / SR
        ph = 2 * np.pi * np.cumsum(f * (1 + 0.6 * np.exp(-t * 40))) / SR
        add(music, np.tanh(1.6 * np.sin(ph)) * np.exp(-t * 9), t0, 0.30)
for k in range(int((END - GRID0) / (BEAT / 2))):
    if k % 2 == 0:
        continue
    t0 = GRID0 + k * BEAT / 2
    ch = CHORDS[bar_index(t0)]
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * midi(m + 12) * t) + 0.25 * np.sin(4 * np.pi * midi(m + 12) * t) for m in ch[1:])
    add(music, s * np.exp(-t * 7) / 4, t0, 0.13, pan=0.25 if k % 4 == 1 else -0.25)


# --- effets
def riser(t_end, dur, gain):
    n = int(dur * SR)
    t = np.arange(n) / SR
    noise = rng.normal(0, 1, n)
    sweep = noise - lowpass(noise, 1500)
    add(music, sweep * (t / t[-1]) ** 2.5, t_end - dur, gain)


def impact(t0, gain_boom=0.30, gain_shim=0.05, clap=0.0):
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    boom = np.sin(2 * np.pi * np.cumsum(38 + 40 * np.exp(-t * 8)) / SR) * np.exp(-t * 3.5)
    shimmer = sum(np.sin(2 * np.pi * midi(m) * t) for m in (84, 88, 91, 96)) * np.exp(-t * 2.2) / 4
    add(music, boom, t0, gain_boom)
    add(music, shimmer, t0, gain_shim, pan=-0.3)
    add(music, np.roll(shimmer, 900), t0, gain_shim, pan=0.3)
    if clap:
        m = int(0.18 * SR)
        noise = rng.normal(0, 1, m)
        noise = noise - lowpass(noise, 1200)
        add(music, noise * np.exp(-np.arange(m) / SR * 25), t0, clap)


def ting(t0, note, gain=0.06):
    n = int(0.7 * SR)
    t = np.arange(n) / SR
    s = (np.sin(2 * np.pi * midi(note) * t) + 0.4 * np.sin(2 * np.pi * midi(note + 12) * t)) * np.exp(-t * 6)
    add(music, s, t0, gain, pan=0.2)


# suspense : souffle aspiré qui monte jusqu'à « PAR »
riser(CUE["par"], 0.45, 0.30)
# PAR / QUOI / COMMENCER : trois coups, le dernier le plus fort
impact(CUE["par"], 0.32, 0.02, clap=0.10)
impact(CUE["quoi"], 0.32, 0.02, clap=0.10)
impact(CUE["commencer"], 0.42, 0.07, clap=0.14)
# coupes : souffle montant + impact doux
for c in CUTS:
    riser(c, 0.8, 0.16)
    impact(c, 0.22, 0.04)
# activités : un scintillement par mot prononcé
for i, ta in enumerate(CUE["act"]):
    ting(ta, [79, 81, 84, 86, 88][i])
# prix qui défile : tic-tic-tic puis « ding »
for tt in np.arange(CUE["prix"], CUE["prix_fin"], 0.05):
    m = int(0.02 * SR)
    add(music, rng.normal(0, 1, m) * np.exp(-np.arange(m) / SR * 300), tt, 0.05, pan=-0.2)
ting(CUE["prix_fin"], 91, 0.09)
# BRUNCH
impact(CUE["brunch"], 0.36, 0.07, clap=0.12)

# fondu final
music[int(END * SR):] *= np.linspace(1, 0, N - int(END * SR))[:, None] ** 2
music[: int(0.05 * SR)] *= np.linspace(0, 1, int(0.05 * SR))[:, None]
music /= np.abs(music).max() / 0.8

dst = ROOT / "sources" / "musique-legere.wav"
with wave.open(str(dst), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((music * 32767).astype("<i2").tobytes())
print("OK", dst)
