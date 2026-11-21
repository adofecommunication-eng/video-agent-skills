#!/usr/bin/env python3
"""Musique originale + bruitages du spot « WELL CHRISTMAS » (30 s).

Esprit des références du client (spots motion design rythmés, ~130-140 BPM, whoosh,
pops, impacts, risers) mais composition et sons entièrement originaux, générés ici :
house festive à 128 BPM avec grelots de traîneau, cloches et basse ; le premier temps
tombe sur « NOËL ». Tous les bruitages sont calés sur spot.CUE / spot.CUTS.
Sortie : sources/musique-et-bruitages.wav (stéréo 44,1 kHz, 30 s).
"""
import math
import wave
from pathlib import Path

import numpy as np

import spot as S

HERE = Path(__file__).resolve().parent
SR, DUR, BPM = 44100, 30.0, 128
BEAT = 60 / BPM
BAR = 4 * BEAT
N = int(SR * DUR)
CUE, CUTS = S.CUE, S.CUTS
GRID0 = CUE["noel"]                       # premier temps fort
BREAKS = [(CUTS[0] - 0.05, CUE["piscine"]), (CUTS[7] - 0.05, CUE["gratuite"])]  # silences avant les chutes
END = 29.35
rng = np.random.default_rng(5)
mix = np.zeros((N, 2))


def midi(m):
    return 440 * 2 ** ((m - 69) / 12)


def lowpass(x, fc):
    a = math.exp(-2 * math.pi * fc / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def add(sig, t0, gain=1.0, pan=0.0):
    i = int(round(t0 * SR))
    if i >= N or i + len(sig) <= 0:
        return
    if i < 0:
        sig, i = sig[-i:], 0
    sig = sig[: N - i]
    l, r = math.sqrt(0.5 * (1 - pan)), math.sqrt(0.5 * (1 + pan))
    mix[i:i + len(sig), 0] += sig * gain * l
    mix[i:i + len(sig), 1] += sig * gain * r


def in_break(t):
    return any(a <= t < b for a, b in BREAKS)


def tt(n):
    return np.arange(int(n * SR)) / SR


# ---------------------------------------------------------------- instruments
def kick():
    t = tt(0.35)
    return np.sin(2 * np.pi * np.cumsum(48 + 110 * np.exp(-t * 30)) / SR) * np.exp(-t * 9)


def clap():
    t = tt(0.22)
    n = rng.normal(0, 1, len(t))
    n = n - lowpass(n, 900)
    env = np.exp(-t * 22) * (1 + 0.6 * (np.sin(2 * np.pi * 90 * t) > 0))
    return n * env * 0.6


def hat(open_=False):
    t = tt(0.25 if open_ else 0.06)
    n = rng.normal(0, 1, len(t))
    n = n - lowpass(n, 7000)
    return n * np.exp(-t * (14 if open_ else 70))


def sleigh():
    """Grelots : grappe de petits tintements métalliques aigus."""
    t = tt(0.12)
    s = np.zeros(len(t))
    for f in (5200, 6100, 7300, 8400):
        s += np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * np.exp(-t * rng.uniform(30, 55))
    n = rng.normal(0, 1, len(t))
    return (s * 0.25 + (n - lowpass(n, 6000)) * 0.3) * np.exp(-t * 25)


def bell(note, dur=1.2):
    """Cloche / glockenspiel (partiels inharmoniques)."""
    t = tt(dur)
    f = midi(note)
    s = (np.sin(2 * np.pi * f * t) + 0.45 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6)
         + 0.25 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 12))
    return s * np.exp(-t * 3.2)


def stab(notes, dur=0.28):
    t = tt(dur)
    s = sum(np.sin(2 * np.pi * midi(m) * t) + 0.3 * np.sin(4 * np.pi * midi(m) * t) for m in notes)
    return s / len(notes) * np.exp(-t * 9)


def bass(note, dur):
    t = tt(dur)
    f = midi(note)
    s = np.tanh(2.2 * np.sin(2 * np.pi * f * t)) + 0.4 * np.sin(np.pi * f * t)
    return s * np.minimum(1, t / 0.005) * np.exp(-t * 2.5)


# grille d'accords (une mesure chacun) : Do · La m · Fa · Sol
CHORDS = [[60, 64, 67, 72], [57, 60, 64, 69], [53, 57, 60, 65], [55, 59, 62, 67]]
ROOTS = [36, 33, 29, 31]
# mélodie de cloches originale (doubles-croches sur 2 mesures, None = silence)
MELO = [76, None, 79, None, 81, 79, 76, None, 74, None, 76, 79, None, None, 72, None,
        77, None, 76, None, 74, 72, 74, None, 79, None, 76, None, 74, None, None, None]


def grid_times(step, start=GRID0, end=END):
    k0 = math.floor((0 - start) / step)
    k = k0
    while True:
        t = start + k * step
        if t >= end:
            return
        if t >= 0:
            yield k, t
        k += 1


# intro : grelots + nappe de cloches en montée vers « NOËL »
for k, t in grid_times(BEAT / 4, end=GRID0):
    add(sleigh(), t, 0.10 + 0.12 * t / GRID0, pan=0.3)
for i, m in enumerate([72, 76, 79, 84]):
    add(bell(m, 1.4), 0.05 + i * 0.2, 0.10, pan=-0.2 + 0.13 * i)

# groove principal
for k, t in grid_times(BEAT):
    if in_break(t):
        continue
    add(kick(), t, 0.55)
    if k % 2 == 1:
        add(clap(), t, 0.35, pan=0.05)
    add(hat(open_=True), t + BEAT / 2, 0.06, pan=-0.25)
for k, t in grid_times(BEAT / 4):
    if not in_break(t):
        add(sleigh(), t, 0.10 if k % 2 else 0.06, pan=0.35)
for k, t in grid_times(BAR):
    if in_break(t):
        continue
    ch = CHORDS[k % 4]
    for j in range(8):  # basse en croches, accents sur les temps
        tj = t + j * BEAT / 2
        if not in_break(tj):
            add(bass(ROOTS[k % 4] + (12 if j % 2 else 0), BEAT / 2 * 0.9), tj, 0.20)
    for j in (1, 3, 5, 7):  # stabs en contretemps
        tj = t + j * BEAT / 2
        if not in_break(tj):
            add(stab(ch), tj, 0.10, pan=0.2 if j % 4 == 1 else -0.2)
for k, t in grid_times(BEAT / 4):
    note = MELO[k % len(MELO)]
    if note is not None and not in_break(t) and t > GRID0:
        add(bell(note, 0.9), t, 0.07, pan=-0.15)

# ---------------------------------------------------------------- bruitages
def whoosh(dur=0.35, up=True):
    t = tt(dur)
    n = rng.normal(0, 1, len(t))
    env = np.sin(np.pi * t / dur) ** 2
    # balayage : mélange de deux filtrages selon la position
    lo, hi = lowpass(n, 600), n - lowpass(n, 2500)
    w = t / dur if up else 1 - t / dur
    return (lo * (1 - w) + hi * w) * env


def pop():
    t = tt(0.12)
    return np.sin(2 * np.pi * np.cumsum(900 * np.exp(-t * 25) + 300) / SR) * np.exp(-t * 35)


def impact():
    t = tt(1.4)
    boom = np.sin(2 * np.pi * np.cumsum(35 + 60 * np.exp(-t * 9)) / SR) * np.exp(-t * 3.5)
    n = rng.normal(0, 1, len(t))
    crack = (n - lowpass(n, 1500)) * np.exp(-t * 30)
    return boom + 0.35 * crack


def sparkle(n_notes=7):
    out = np.zeros(int(1.2 * SR))
    for i in range(n_notes):
        b = bell(int(rng.choice([84, 88, 91, 96, 100])), 0.6)
        j = int(rng.uniform(0, 0.5) * SR)
        out[j:j + len(b)] += b[: len(out) - j] * rng.uniform(0.4, 1)
    return out


def splash_sfx():
    t = tt(1.2)
    n = rng.normal(0, 1, len(t))
    body = lowpass(n, 2500) * np.exp(-t * 4) * 1.8
    s = body.copy()
    for _ in range(14):  # bulles
        f = rng.uniform(600, 1800)
        j = int(rng.uniform(0.1, 0.9) * SR)
        bt = tt(0.06)
        bub = np.sin(2 * np.pi * np.cumsum(f * (1 + 2 * bt / 0.06)) / SR) * np.exp(-bt * 60)
        s[j:j + len(bub)] += bub[: len(s) - j] * 0.3
    return s


def riser(dur):
    t = tt(dur)
    n = rng.normal(0, 1, len(t))
    hp = n - lowpass(n, 1200)
    tone = np.sin(2 * np.pi * np.cumsum(200 + 1400 * (t / dur) ** 2) / SR) * 0.15
    return (hp * 0.6 + tone) * (t / dur) ** 2.2


def liquid_swoosh():
    t = tt(0.45)
    n = rng.normal(0, 1, len(t))
    s = lowpass(n, 1200) * np.sin(np.pi * t / 0.45) * 2
    gl = np.sin(2 * np.pi * np.cumsum(900 - 700 * t / 0.45) / SR) * np.exp(-t * 5) * 0.25
    return s + gl


def tick():
    t = tt(0.025)
    return np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 250)


C = CUE
for t0 in [C["cette"], C["fete"], C["aubord"], C["wbr"], C["date"] + 0.35, CUTS[3], C["tombola"], C["nuitee"],
           C["natation"], C["etqui"], C["an2027"] - 0.55, C["entree"], C["adresse"] + 0.6]:
    add(whoosh(0.35), t0 - 0.12, 0.35, pan=float(rng.uniform(-0.4, 0.4)))
for t0 in C["prog"]:
    add(whoosh(0.3), t0 - 0.12, 0.3, pan=-0.3)
    add(pop(), t0 + 0.12, 0.3)
for t0 in [C["heures"], C["pourtous"], C["natation"] - 0.25, CUTS[-1] + 0.05, CUTS[-1] + 0.5]:
    add(pop(), t0, 0.35)
for t0, g in [(C["noel"], 0.55), (C["piscine"], 0.45), (C["wellchristmas"], 0.45), (C["wellchristmas"] + 0.22, 0.5),
              (C["date"], 0.55), (C["miss"], 0.5), (C["miss"] + 0.25, 0.4), (C["an2027"] + 0.25, 0.45),
              (C["agagner"], 0.4), (C["gratuite"], 0.7), (CUTS[-1] + 0.15, 0.4), (C["adresse"] + 0.9, 0.4)]:
    add(impact(), t0, g)
for t0 in [C["noel"], C["wellchristmas"] + 0.22, C["date"], C["miss"] + 0.2, C["gratuite"], C["prix_fin"]]:
    add(sparkle(), t0, 0.12, pan=float(rng.uniform(-0.3, 0.3)))
add(splash_sfx(), C["piscine"] - 0.02, 0.5)
for b in [CUTS[0], CUTS[1], CUTS[3], CUTS[5], CUTS[7]]:  # transitions « éclaboussure »
    add(liquid_swoosh(), b - S.XD, 0.4)
add(riser(C["gratuite"] - CUTS[7] + 0.4), CUTS[7] - 0.4, 0.4)
add(riser(CUE["piscine"] - CUTS[0]), CUTS[0], 0.25)
for t0 in np.arange(C["prix"], C["prix_fin"], 0.06):
    add(tick(), t0, 0.25, pan=-0.2)
add(bell(91, 1.5), C["prix_fin"], 0.25)
add(bell(96, 1.5), C["prix_fin"] + 0.04, 0.15)
add(impact(), END - 0.05, 0.4)
add(sparkle(10), END - 0.05, 0.15)

# fondu et normalisation
f0 = int((END + 0.1) * SR)
mix[f0:] *= np.linspace(1, 0, N - f0)[:, None] ** 2
mix /= np.abs(mix).max() / 0.85
dst = HERE / "sources" / "musique-et-bruitages.wav"
with wave.open(str(dst), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print("OK", dst)
