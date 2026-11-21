#!/usr/bin/env python3
"""Musique originale + bruitages du spot « WELL CHRISTMAS » (30 s).

Esprit des références du client (spots motion design rythmés, ~130-140 BPM, whoosh,
pops, impacts, risers) mais composition et sons entièrement originaux, générés ici :
house festive à 128 BPM avec grelots de traîneau, cloches et basse ; le premier temps
tombe sur « NOËL ». Bruitages de Noël synthétisés (grelots, carillons, cloches,
boîte à musique, papier cadeau), tous calés sur spot.CUE / spot.CUTS.
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

# ---------------------------------------------------------------- bruitages de Noël
# Tous synthétisés ici (aucun son extrait d'une autre vidéo) :
# grelots de traîneau secoués, carillon magique, cloches, boîte à musique, papier cadeau, étoiles.
def jingle_shake(dur=0.6, density=90, bright=1.0):
    """Grelots de traîneau secoués : nuée de petits grelots aléatoires."""
    out = np.zeros(int(dur * SR))
    for _ in range(int(density * dur)):
        j = int(rng.uniform(0, dur * 0.9) * SR)
        t = tt(rng.uniform(0.05, 0.12))
        f0 = rng.uniform(3800, 6800) * bright
        s = sum(np.sin(2 * np.pi * f0 * r * t + rng.uniform(0, 6)) for r in (1, 1.47, 2.09)) / 3
        s *= np.exp(-t * rng.uniform(35, 60))
        env = math.sin(math.pi * j / len(out)) ** 0.7
        out[j:j + len(s)] += s[: len(out) - j] * env
    return out


def chime_gliss(notes=(84, 88, 91, 96, 100), step=0.05, up=True):
    """Carillon magique : arpège rapide de clochettes."""
    seq = notes if up else notes[::-1]
    out = np.zeros(int((len(seq) * step + 1.3) * SR))
    for i, m in enumerate(seq):
        b = bell(m, 1.2)
        j = int(i * step * SR)
        out[j:j + len(b)] += b[: len(out) - j]
    return out / 2


def church_bell(note=60, dur=2.5):
    t = tt(dur)
    f = midi(note)
    s = (np.sin(2 * np.pi * f * t) + 0.6 * np.sin(2 * np.pi * f * 2.0 * t) * np.exp(-t * 1.5)
         + 0.5 * np.sin(2 * np.pi * f * 2.4 * t) * np.exp(-t * 2) + 0.3 * np.sin(2 * np.pi * f * 3.0 * t) * np.exp(-t * 3)
         + 0.25 * np.sin(2 * np.pi * f * 4.2 * t) * np.exp(-t * 4))
    return s * np.exp(-t * 1.6) * np.minimum(1, t / 0.003)


def music_box(note):
    t = tt(0.5)
    f = midi(note)
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 3.9 * t) * np.exp(-t * 20)
    return s * np.exp(-t * 7)


def paper_rustle(dur=0.4):
    """Froissement de papier cadeau."""
    n = rng.normal(0, 1, int(dur * SR))
    hp = n - lowpass(n, 2000)
    crackle = (rng.random(len(n)) < 0.004) * rng.normal(0, 3, len(n))
    env = np.sin(np.pi * np.arange(len(n)) / len(n)) * (0.6 + 0.4 * np.sin(np.arange(len(n)) / SR * 70) ** 2)
    return (hp * 0.5 + crackle) * env


def jingle_whoosh(dur=0.4):
    """Souffle + grelots : pour les glissements et les rubans d'or."""
    t = tt(dur)
    n = rng.normal(0, 1, len(t))
    w = (n - lowpass(n, 1800)) * np.sin(np.pi * t / dur) ** 2 * 0.6
    j = jingle_shake(dur, 70)
    return w + j[: len(w)] * 0.8


def bell_pop(note=91):
    """« Pop » de clochette pour les apparitions."""
    t = tt(0.1)
    p = np.sin(2 * np.pi * np.cumsum(700 * np.exp(-t * 30) + 250) / SR) * np.exp(-t * 40)
    b = bell(note, 0.8)
    out = np.zeros(len(b))
    out[: len(p)] += p * 0.8
    return out + b * 0.6


def xmas_impact(note=48):
    """Impact de Noël : grosse caisse grave + cloche d'église + grelots."""
    t = tt(1.6)
    boom = np.sin(2 * np.pi * np.cumsum(35 + 60 * np.exp(-t * 9)) / SR) * np.exp(-t * 3.5)
    cb = church_bell(note, 1.6)
    js = jingle_shake(0.7, 140)
    out = boom * 0.9 + cb * 0.35
    out[: len(js)] += js * 0.6
    return out


def twinkle(n_notes=7):
    """Poussière d'étoiles : clochettes aiguës éparpillées."""
    out = np.zeros(int(1.3 * SR))
    for _ in range(n_notes):
        b = bell(int(rng.choice([88, 91, 93, 96, 100, 103])), 0.7)
        j = int(rng.uniform(0, 0.55) * SR)
        out[j:j + len(b)] += b[: len(out) - j] * rng.uniform(0.4, 1)
    return out


def splash_sfx():
    t = tt(1.2)
    n = rng.normal(0, 1, len(t))
    s = lowpass(n, 2500) * np.exp(-t * 4) * 1.8
    for _ in range(14):
        f = rng.uniform(600, 1800)
        j = int(rng.uniform(0.1, 0.9) * SR)
        bt = tt(0.06)
        bub = np.sin(2 * np.pi * np.cumsum(f * (1 + 2 * bt / 0.06)) / SR) * np.exp(-bt * 60)
        s[j:j + len(bub)] += bub[: len(s) - j] * 0.3
    return s


def jingle_riser(dur):
    """Montée : grelots de plus en plus denses + glissando de clochettes."""
    out = jingle_shake(dur, 160) * np.linspace(0.1, 1, int(dur * SR)) ** 2
    steps = int(dur / 0.06)
    for i in range(steps):
        b = music_box(72 + i * 24 // max(1, steps))
        j = int(i * 0.06 * SR)
        out[j:j + len(b)] += b[: len(out) - j] * 0.25 * (i / steps)
    return out


def curtain():
    t = tt(0.9)
    n = rng.normal(0, 1, len(t))
    return lowpass(n, 900) * np.sin(np.pi * t / 0.9) ** 1.5 * 2.2


C = CUE
# glissements de texte : souffle à grelots
for t0 in [C["cette"], C["fete"], C["aubord"], C["wbr"], C["tombola"], C["nuitee"], C["natation"], C["etqui"],
           C["an2027"] - 0.55, C["entree"], C["adresse"] + 0.6]:
    add(jingle_whoosh(0.4), t0 - 0.14, 0.32, pan=float(rng.uniform(-0.4, 0.4)))
# étiquettes cadeau : une note de boîte à musique chacune (mélodie montante)
for t0, m in zip(C["prog"], [79, 83, 86, 91]):
    add(paper_rustle(0.25), t0 - 0.1, 0.25, pan=-0.3)
    add(bell_pop(m), t0 + 0.08, 0.35)
# apparitions (pastilles, « OU », logo) : pops de clochette
for t0, m in [(C["heures"], 88), (C["pourtous"], 84), (C["natation"] - 0.25, 86), (CUTS[-1] + 0.05, 91),
              (CUTS[-1] + 0.5, 96)]:
    add(bell_pop(m), t0, 0.35)
# grands moments : impact de Noël
for t0, g, note in [(C["noel"], 0.6, 48), (C["wellchristmas"], 0.4, 55), (C["wellchristmas"] + 0.22, 0.5, 48),
                    (C["date"], 0.55, 52), (C["agagner"], 0.4, 55), (C["miss"], 0.5, 50),
                    (C["miss"] + 0.25, 0.35, 55), (C["an2027"] + 0.25, 0.4, 52), (C["gratuite"], 0.75, 45),
                    (CUTS[-1] + 0.15, 0.4, 48), (C["adresse"] + 0.9, 0.4, 52)]:
    add(xmas_impact(note), t0, g)
# carillon magique + poussière d'étoiles sur les explosions de confettis
for t0 in [C["noel"], C["wellchristmas"] + 0.22, C["date"], C["miss"] + 0.2, C["gratuite"], C["prix_fin"]]:
    add(chime_gliss(), t0 - 0.02, 0.18, pan=float(rng.uniform(-0.3, 0.3)))
    add(twinkle(), t0 + 0.1, 0.12)
# le cadeau tremble (grelots + froissement), le couvercle saute
for a, b in [(C["cette"] + 0.1, C["noel"] - 0.06), (C["entree"] + 0.1, C["gratuite"] - 0.04)]:
    add(jingle_shake(b - a, 120) * np.linspace(0.3, 1, int((b - a) * SR)), a, 0.35)
    add(paper_rustle(b - a), a, 0.25)
add(bell_pop(96), C["noel"] - 0.06, 0.4)
# piscine : plouf + petite clochette pour le bonnet
add(splash_sfx(), C["piscine"] - 0.02, 0.5)
add(bell_pop(100), C["piscine"] + 0.45, 0.3)
# calendrier : page qui se tourne
add(paper_rustle(0.35), C["date"] - 0.15, 0.4)
# tombola : boîte à musique qui « compte », puis cloche
for i, t0 in enumerate(np.arange(C["prix"], C["prix_fin"], 0.07)):
    add(music_box(84 + (i % 5) * 2), t0, 0.18, pan=-0.2)
add(church_bell(67, 2.0), C["prix_fin"], 0.25)
add(chime_gliss(up=False), C["prix_fin"] + 0.05, 0.15)
# rideau de velours
add(curtain(), C["etqui"] - 0.05, 0.4)
add(chime_gliss((79, 84, 88, 91, 96, 100, 103), 0.07), C["etqui"] + 0.2, 0.15)
# transitions
add(splash_sfx(), CUTS[0] - S.XD, 0.25)
for b in [CUTS[1], CUTS[2], CUTS[3], CUTS[4], CUTS[5], CUTS[7], CUTS[8]]:
    add(jingle_whoosh(0.45), b - S.XD, 0.3, pan=float(rng.uniform(-0.5, 0.5)))
# montées vers « PISCINE » et « GRATUITE »
add(jingle_riser(C["piscine"] - CUTS[0]), CUTS[0], 0.3)
add(jingle_riser(C["gratuite"] - CUTS[7] + 0.4), CUTS[7] - 0.4, 0.4)
# final : cloche + grelots qui s'éteignent
add(church_bell(48, 2.5), END - 0.05, 0.4)
add(jingle_shake(1.2, 100), END - 0.05, 0.3)
add(twinkle(10), END, 0.15)

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
