#!/usr/bin/env python3
"""Bande-son originale du spot « SPLASH PARTY » (60 s) : musique + bruitages façon bande-annonce.

Tout est synthétisé ici (aucun son récupéré ailleurs) :
  - ouverture : nappe grave, battements de cœur, tic-tac ; « braams » de cuivres sur 3 · 2 · 1 ;
    souffle inversé qui aspire vers « SPLASH »
  - « SPLASH » : chute en afro-house ensoleillée à 120 BPM (grosse caisse, shaker, congas,
    basse log drum, marimba) ; temps forts exportés pour les pulsations d'image
  - révélation émotionnelle : la rythmique s'efface, nappe chaude et piano
  - montée vers « PLOUF » puis final : impact, accord final, applaudissements et cris de joie
  - bruitages « After Effects » : whooshs, impacts avec réverbération, plouf d'eau réaliste,
    bulles, scratch de vinyle, carillon de couronne, tic de compteur.
Sorties : sources/musique.wav, sources/bruitages.wav, sources/temps-forts.json
"""
import json
import math
import wave
from pathlib import Path

import numpy as np

import spot as S

HERE = Path(__file__).resolve().parent
SR, DUR, BPM = 44100, S.DUR, 120
INTRO = S.INTRO
BEAT = 60 / BPM
BAR = 4 * BEAT
N = int(SR * DUR)
C, CUTS = S.CUE, S.CUTS
GRID0 = C["splash"]
EMO = (CUTS[6], CUTS[7])            # section émotion : pas de batterie
END_HIT = 58.4 + INTRO
rng = np.random.default_rng(9)
music = np.zeros((N, 2))
sfx = np.zeros((N, 2))
wet = np.zeros((N, 2))              # envoi vers la réverbération


def midi(m):
    return 440 * 2 ** ((m - 69) / 12)


def tt(d):
    return np.arange(int(d * SR)) / SR


def lowpass(x, fc):
    a = math.exp(-2 * math.pi * fc / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def lp_fast(x, fc):
    """Passe-bas par FFT (pour les longs signaux)."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / np.sqrt(1 + (f / fc) ** 4)
    return np.fft.irfft(X, len(x))


def add(buf, sig, t0, gain=1.0, pan=0.0, send=0.0):
    i = int(round(t0 * SR))
    if i >= N or i + len(sig) <= 0:
        return
    if i < 0:
        sig, i = sig[-i:], 0
    sig = sig[: N - i]
    l, r = math.sqrt(0.5 * (1 - pan)), math.sqrt(0.5 * (1 + pan))
    buf[i:i + len(sig), 0] += sig * gain * l
    buf[i:i + len(sig), 1] += sig * gain * r
    if send:
        wet[i:i + len(sig), 0] += sig * gain * send * l
        wet[i:i + len(sig), 1] += sig * gain * send * r


def grid(step, start, end):
    k = math.ceil((start - GRID0) / step - 1e-9)
    while True:
        t = GRID0 + k * step
        if t >= end:
            return
        yield k, t
        k += 1


def groove_on(t):
    return GRID0 <= t < END_HIT and not (EMO[0] <= t < EMO[1]) and not (C["attend"] - 0.1 <= t < C["plouf"])


# ---------------------------------------------------------------- instruments
def kick():
    t = tt(0.4)
    return np.sin(2 * np.pi * np.cumsum(45 + 120 * np.exp(-t * 28)) / SR) * np.exp(-t * 8) * 1.1


def shaker():
    t = tt(0.07)
    n = rng.normal(0, 1, len(t))
    return (n - lowpass(n, 6000)) * np.exp(-t * 55)


def conga(f):
    t = tt(0.25)
    return np.sin(2 * np.pi * np.cumsum(f * (1 + 0.5 * np.exp(-t * 40))) / SR) * np.exp(-t * 14)


def clap():
    t = tt(0.25)
    n = rng.normal(0, 1, len(t))
    n = n - lowpass(n, 1000)
    return n * np.exp(-t * 20) * (1 + 0.5 * (np.sin(2 * np.pi * 80 * t) > 0)) * 0.6


def logdrum(note, d=0.35):
    t = tt(d)
    f = midi(note)
    ph = 2 * np.pi * np.cumsum(f * (1 + 0.5 * np.exp(-t * 35))) / SR
    return np.tanh(1.8 * np.sin(ph)) * np.exp(-t * 7)


def marimba(note, d=0.6):
    t = tt(d)
    f = midi(note)
    return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 18)) * np.exp(-t * 6)


def pad(notes, d):
    t = tt(d)
    s = sum(np.sin(2 * np.pi * midi(m) * t + k) + 0.3 * np.sin(2 * np.pi * midi(m) * 2.003 * t)
            for k, m in enumerate(notes))
    env = np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 0.8)
    return s / len(notes) * env


def piano(note, d=1.8):
    t = tt(d)
    f = midi(note)
    s = sum(np.sin(2 * np.pi * f * k * t) / k ** 1.4 * np.exp(-t * (1.5 + k)) for k in range(1, 6))
    return s * np.minimum(1, t / 0.004)


def braam(root=33, d=2.2):
    """« Braam » de bande-annonce : accord de cuivres graves saturés qui s'ouvre."""
    t = tt(d)
    s = np.zeros(len(t))
    for m in (root, root + 7, root + 12, root + 15):
        for det in (-0.006, 0.0, 0.006):
            s += 2 * ((t * midi(m) * (1 + det)) % 1) - 1
    s = np.tanh(s / 4)
    # filtre qui s'ouvre : mélange progressif de version filtrée / brillante
    dark = lp_fast(s, 300)
    bright = lp_fast(s, 2200)
    w = np.minimum(1, t / 0.25) * np.exp(-t * 1.2)
    out = dark * (1 - w) + bright * w
    return out * np.minimum(1, t / 0.02) * np.exp(-t * 1.1)


# ---------------------------------------------------------------- musique
# ouverture (0 – 2 s) : le groove démarre tout de suite, puis se coupe pour le compte à rebours
OPEN_END = C["trois"] - 0.05
for k, t0 in grid(BEAT, 0.0, OPEN_END):
    if t0 >= 0:
        add(music, kick(), t0, 0.62)
        if k % 2:
            add(music, clap(), t0, 0.3, send=0.2)
for k, t0 in grid(BEAT / 4, 0.0, OPEN_END):
    if t0 >= 0:
        add(music, shaker(), t0, 0.07 if k % 2 else 0.04, pan=0.35)
for k, t0 in grid(BAR, -BAR, OPEN_END):
    for s16 in (0, 3, 6, 10, 11, 14):
        tj = t0 + s16 * BEAT / 4
        if 0 <= tj < OPEN_END:
            add(music, logdrum(45 + (12 if s16 in (10, 11) else 0)), tj, 0.3)
# compte à rebours : roulement de caisse claire qui accélère vers « SPLASH »
d_roll = C["splash"] - C["trois"]
for i in range(60):
    tr = C["trois"] + d_roll * (1 - (1 - i / 60) ** 1.6)
    if tr >= C["splash"] - 0.03:
        break
    add(music, clap(), tr, 0.05 + 0.25 * (i / 60), send=0.2)

# groove afro-house
CH = [[57, 60, 64], [55, 59, 62], [53, 57, 60], [55, 59, 62]]   # La m · Sol · Fa · Sol
ROOT = [45, 43, 41, 43]
MEL = [76, None, 72, 74, None, 76, 79, None, 76, None, 74, 72, None, 69, None, None]
beats_out = [round(t0, 3) for k, t0 in grid(BEAT, 0.0, OPEN_END) if t0 >= 0]
for k, t0 in grid(BEAT, GRID0, END_HIT):
    if not groove_on(t0):
        continue
    add(music, kick(), t0, 0.62)
    beats_out.append(round(t0, 3))
    if k % 2 == 1:
        add(music, clap(), t0, 0.3, send=0.2)
for k, t0 in grid(BEAT / 4, GRID0, END_HIT):
    if groove_on(t0):
        add(music, shaker(), t0, 0.07 if k % 2 else 0.04, pan=0.35)
for k, t0 in grid(BEAT / 4, GRID0, END_HIT):
    if groove_on(t0) and k % 16 in (3, 6, 10, 14):
        add(music, conga(220 if k % 16 in (3, 10) else 330), t0, 0.22, pan=-0.3)
for k, t0 in grid(BAR, GRID0, END_HIT):
    for s16 in (0, 3, 6, 10, 11, 14):
        tj = t0 + s16 * BEAT / 4
        if groove_on(tj):
            add(music, logdrum(ROOT[k % 4] + (12 if s16 in (10, 11) else 0)), tj, 0.3)
for k, t0 in grid(BEAT / 2, GRID0, END_HIT):
    note = MEL[k % len(MEL)]
    if note and groove_on(t0):
        add(music, marimba(note), t0, 0.12, pan=0.2, send=0.15)
for k, t0 in grid(BAR, GRID0, END_HIT):
    if groove_on(t0):
        add(music, pad(CH[k % 4], BAR), t0, 0.08, send=0.2)

# émotion : nappe chaude + piano
emo_len = EMO[1] - EMO[0] + 0.6
add(music, pad([57, 60, 64, 69], emo_len), EMO[0] - 0.2, 0.22, send=0.5)
for i, (tn, nt) in enumerate([(0.0, 76), (0.6, 72), (1.2, 74), (1.8, 76), (2.4, 79), (3.0, 81)]):
    add(music, piano(nt), EMO[0] + tn, 0.18, send=0.6)

# montée vers PLOUF : nappe filtrée qui se tend
d = C["plouf"] - C["attend"] + 0.1
t = tt(d)
riser = sum(2 * ((t * midi(m) * (1 + 0.004 * k)) % 1) - 1 for k, m in enumerate((57, 64, 69, 76)))
riser = lp_fast(riser, 2500) * (t / d) ** 1.8 * 0.25
add(music, riser, C["attend"] - 0.1, 1.0, send=0.3)

# final : accord et dernier coup
add(music, pad([57, 60, 64, 69, 72], 5.5), C["plouf"], 0.22, send=0.6)
add(music, braam(33, 3.0), END_HIT, 0.45, send=0.6)
add(music, piano(69, 3), END_HIT, 0.25, send=0.6)


# ---------------------------------------------------------------- bruitages « After Effects »
def whoosh(d=0.45, f0=300, f1=4000):
    t = tt(d)
    n = rng.normal(0, 1, len(t))
    env = np.sin(np.pi * t / d) ** 2
    out = np.zeros(len(t))
    seg = 8
    for j in range(seg):  # balayage spectral par segments
        a, b = j * len(t) // seg, (j + 1) * len(t) // seg
        fc = f0 * (f1 / f0) ** (j / seg)
        out[a:b] = lowpass(n[a:b], fc) * (1 + j / seg)
    return out * env


def impact():
    t = tt(2.0)
    boom = np.sin(2 * np.pi * np.cumsum(32 + 70 * np.exp(-t * 7)) / SR) * np.exp(-t * 3)
    n = rng.normal(0, 1, len(t))
    crack = (n - lowpass(n, 1800)) * np.exp(-t * 25)
    metal = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * 6) for f in (523, 1187, 2210)) / 3
    return boom + 0.4 * crack + 0.15 * metal


def reverse_swell(d=1.2):
    t = tt(d)
    n = rng.normal(0, 1, len(t))
    tail = lowpass(n, 3000) * np.exp(-t * 3)
    return tail[::-1] * 0.8


def water_splash(big=1.0):
    t = tt(1.3)
    n = rng.normal(0, 1, len(t))
    body = lowpass(n, 1800) * np.exp(-t * 5) * 1.6
    hiss = (n - lowpass(n, 4000)) * np.exp(-t * 3.5) * 0.6
    s = body + hiss
    for _ in range(int(20 * big)):  # gouttes
        j = int(rng.uniform(0.05, 1.0) * SR)
        bt = tt(0.05)
        f = rng.uniform(700, 2200)
        drop = np.sin(2 * np.pi * np.cumsum(f * (1 + 2.5 * bt / 0.05)) / SR) * np.exp(-bt * 70)
        s[j:j + len(drop)] += drop[: len(s) - j] * 0.35
    return s * big


def plop(f=900):
    t = tt(0.12)
    return np.sin(2 * np.pi * np.cumsum(f * (1 + 3 * t / 0.12)) / SR) * np.exp(-t * 35)


def bubbles_sfx(d=0.6, n_=14):
    out = np.zeros(int(d * SR))
    for _ in range(n_):
        p = plop(rng.uniform(600, 1600))
        j = int(rng.uniform(0, d - 0.12) * SR)
        out[j:j + len(p)] += p * rng.uniform(0.3, 1)
    return out


def scratch():
    t = tt(0.5)
    rate = np.sin(2 * np.pi * 4 * t) * 0.9
    ph = np.cumsum(220 * (1 + rate)) / SR
    s = (2 * (ph % 1) - 1) * np.abs(rate)
    n = rng.normal(0, 1, len(t))
    return (lowpass(s, 1800) + 0.3 * (n - lowpass(n, 2000)) * np.abs(rate)) * 0.8


def chime():
    out = np.zeros(int(1.8 * SR))
    for i, m in enumerate((84, 88, 91, 96, 100)):
        x = tt(1.4)
        b = (np.sin(2 * np.pi * midi(m) * x) + 0.4 * np.sin(2 * np.pi * midi(m) * 2.76 * x) * np.exp(-x * 6)) * np.exp(-x * 3)
        j = int(i * 0.06 * SR)
        out[j:j + len(b)] += b
    return out / 2


def tick():
    x = tt(0.03)
    return np.sin(2 * np.pi * 3000 * x) * np.exp(-x * 250)


def applause(d=6.0):
    out = np.zeros(int(d * SR))
    claps = int(d * 220)
    for _ in range(claps):
        j = int(rng.uniform(0, d - 0.05) * SR)
        x = tt(0.03)
        n = rng.normal(0, 1, len(x))
        c = (n - lowpass(n, 1200)) * np.exp(-x * rng.uniform(120, 200))
        out[j:j + len(c)] += c * rng.uniform(0.2, 1)
    t = tt(d)
    env = np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 2.0)
    crowd = lp_fast(rng.normal(0, 1, len(t)), 900) * 0.6
    return (out * 0.5 + crowd) * env


def cheer(d=2.5):
    """Cris de joie stylisés : voyelles « wouh » synthétiques noyées dans la foule."""
    t = tt(d)
    s = np.zeros(len(t))
    for _ in range(10):
        f0 = rng.uniform(220, 520)
        vib = 1 + 0.02 * np.sin(2 * np.pi * rng.uniform(4, 7) * t)
        glide = 1 + 0.25 * np.exp(-t * 2)
        ph = 2 * np.pi * np.cumsum(f0 * vib * glide) / SR
        v = sum(np.sin(k * ph) / k for k in range(1, 6))
        s += lp_fast(v, 1500) * rng.uniform(0.3, 1)
    env = np.minimum(1, t / 0.15) * np.exp(-t * 0.9)
    return s / 10 * env


# ---------------------------------------------------------------- bruitages façon « MrBeast » (recréés ici)
def shutter():
    """Déclic d'appareil photo (image arrêtée)."""
    out = np.zeros(int(0.25 * SR))
    for j0, f in ((0, 2400), (0.07, 1800)):
        x = tt(0.04)
        n = rng.normal(0, 1, len(x))
        c_ = ((n - lowpass(n, 1500)) * 0.7 + np.sin(2 * np.pi * f * x) * 0.4) * np.exp(-x * 120)
        j = int(j0 * SR)
        out[j:j + len(c_)] += c_
    return out


def boom():
    """Boom grave très saturé (type « vine boom ») pour les grandes révélations."""
    t = tt(1.4)
    body = np.sin(2 * np.pi * np.cumsum(38 + 120 * np.exp(-t * 22)) / SR)
    s_ = np.tanh(4.0 * body) * np.exp(-t * 3.2)
    n = rng.normal(0, 1, len(t))
    click = (n - lowpass(n, 2500)) * np.exp(-t * 90) * 0.8
    return (s_ + click) * 0.9


def ka_ching():
    """Caisse enregistreuse : clac mécanique + clochette brillante."""
    out = np.zeros(int(1.2 * SR))
    for j0 in (0.0, 0.06):
        x = tt(0.05)
        n = rng.normal(0, 1, len(x))
        c_ = (lowpass(n, 3000) * 1.2 + np.sin(2 * np.pi * 900 * x)) * np.exp(-x * 90)
        j = int(j0 * SR)
        out[j:j + len(c_)] += c_ * 0.6
    x = tt(1.0)
    bell_ = sum(np.sin(2 * np.pi * f * x) * a_ for f, a_ in ((2637, 1), (3951, .6), (5274, .35), (6580, .2)))
    j = int(0.11 * SR)
    out[j:j + len(x)] += bell_ * np.exp(-x * 4.5) * 0.5
    return out


def ding(f=1760):
    """Ding brillant (apparition de texte / notification)."""
    x = tt(0.9)
    return (np.sin(2 * np.pi * f * x) + 0.5 * np.sin(2 * np.pi * f * 2.01 * x) * np.exp(-x * 8)) * np.exp(-x * 5)


def pop_toon():
    """Pop de bulle cartoon."""
    x = tt(0.09)
    return np.sin(2 * np.pi * np.cumsum(400 + 1800 * x / 0.09) / SR) * np.exp(-x * 45)


def swish(d=0.22):
    """Swoosh court et sec des coupes rapides."""
    x = tt(d)
    n = rng.normal(0, 1, len(x))
    hp = n - lowpass(n, 2500)
    env = (x / d) ** 2 * np.exp(-((x - d * 0.75) / (d * 0.2)) ** 2) * 3
    return hp * env


def riser_fast(d=1.0):
    x = tt(d)
    n = rng.normal(0, 1, len(x))
    tone = np.sin(2 * np.pi * np.cumsum(300 + 2200 * (x / d) ** 2) / SR)
    return ((n - lowpass(n, 1500)) * 0.5 + tone * 0.35) * (x / d) ** 2.5


def glitch_sfx(d=0.16):
    x = tt(d)
    s_ = np.sign(np.sin(2 * np.pi * 180 * x)) * (rng.random(len(x)) < 0.6)
    s_ = np.repeat(s_[::300], 300)[:len(x)]
    return s_ * 0.5 * np.exp(-x * 10)


def cartoon_boing():
    x = tt(0.45)
    f = 220 + 160 * np.sin(2 * np.pi * 9 * x) * np.exp(-x * 5)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 6)


B = C
# accroche : boom sur l'ouverture, dings sur les bandeaux
add(sfx, boom(), 0.0, 0.55, send=0.3)
add(sfx, ding(1568), 0.3, 0.25)
add(sfx, ding(2093), 0.62, 0.22)
# compte à rebours : boom + glitch sur chaque chiffre, montée vers SPLASH
for t0 in (B["trois"], B["deux"], B["un"]):
    add(sfx, boom(), t0, 0.6, send=0.3)
    add(sfx, glitch_sfx(), t0, 0.25)
add(sfx, riser_fast(B["splash"] - B["trois"]), B["trois"], 0.35)
# SPLASH : plouf + gros boom
add(sfx, water_splash(1.3), B["splash"] - 0.05, 0.7, send=0.4)
add(sfx, boom(), B["splash"], 0.75, send=0.5)
# titres et grands moments : boom
for t0 in [B["party"], B["party"] + 0.25, B["dj"] + 0.4, CUTS[8], B["miss"] + 0.2]:
    add(sfx, boom(), t0, 0.55, send=0.4)
# bandeaux et textes : dings et pops
for t0, f in [(B["samedi"], 1760), (B["wbr"], 2093), (B["heures"] + 0.15, 1568), (B["heures"] + 1.2, 2349),
              (B["petits"], 1760), (B["auprog"], 2093), (B["piscine"] + 0.4, 2349), (B["danses"] + 0.3, 1760),
              (B["dj"] + 1.0, 2093), (B["enfant"], 1568), (B["rafr"], 2093), (B["acces"], 2349), (B["faims"], 1760),
              (B["nourriture"] + 0.6, 2093), (B["famille"], 1568), (B["resa"], 2093), (B["nums"][-1] + 0.8, 2349),
              (B["fin"] + 1.1, 1760), (B["fin"] + 3.0, 2093)]:
    add(sfx, ding(f), t0, 0.2, pan=float(rng.uniform(-0.3, 0.3)))
# programme : swoosh + boom à chaque mot, pop sur les disques de couleur
for t0 in [B["piscine"], B["danses"], B["karaoke"], B["billard"], B["babyfoot"], B["jeux"], B["nourriture"]]:
    add(sfx, swish(), t0 - 0.2, 0.5, pan=float(rng.uniform(-0.5, 0.5)))
    add(sfx, boom(), t0, 0.4, send=0.3)
for t0 in [B["karaoke"], B["billard"], B["babyfoot"], B["jeux"]]:
    add(sfx, pop_toon(), t0 - 0.02, 0.4)
add(sfx, water_splash(0.8), B["piscine"], 0.4)
add(sfx, scratch(), B["dj"] - 0.1, 0.5)
add(sfx, scratch(), B["dj"] + 1.1, 0.35)
# Miss Splash : déclic, boom, carillon, boing sur la couronne
add(sfx, riser_fast(0.6), B["miss"] - 0.4, 0.35)
add(sfx, shutter(), B["miss"] + 0.18, 0.6)
add(sfx, chime(), B["miss"] + 0.75, 0.3, send=0.5)
add(sfx, cartoon_boing(), B["miss"] + 1.2, 0.25)
# prix : compteur + caisse enregistreuse
for t0 in np.arange(B["prix"], B["prix"] + 0.9, 0.06):
    add(sfx, tick(), t0, 0.3, pan=-0.2)
add(sfx, ka_ching(), B["prix"] + 0.88, 0.6, send=0.3)
# numéros : un pop par groupe de chiffres
for i, t0 in enumerate(B["nums"]):
    add(sfx, pop_toon(), t0 - 0.05, 0.45)
    add(sfx, ding(1568 + 196 * i), t0, 0.15)
# coupes franches et transitions à bandeaux : swoosh
for b_ in S.INNER_CUTS:
    add(sfx, swish(), b_ - 0.18, 0.45)
for b_ in [CUTS[2], CUTS[3], CUTS[4], CUTS[5], CUTS[6], CUTS[7], CUTS[8]]:
    add(sfx, swish(0.3), b_ - S.XD * 0.6, 0.55, pan=-0.3)
    add(sfx, swish(0.3), b_ - S.XD * 0.1, 0.45, pan=0.3)
# final : montée, plouf, boom, applaudissements et cris de joie
add(sfx, riser_fast(1.2), B["plouf"] - 1.2, 0.4)
add(sfx, water_splash(1.6), B["plouf"] - 0.03, 0.8, send=0.5)
add(sfx, boom(), B["plouf"], 0.8, send=0.5)
add(sfx, applause(DUR - B["plouf"] - 0.2), B["plouf"] + 0.3, 0.32, send=0.2)
add(sfx, cheer(2.5), B["plouf"] + 0.35, 0.2, send=0.3)
add(sfx, boom(), END_HIT, 0.5, send=0.5)

# ---------------------------------------------------------------- réverbération (convolution)
ir_t = tt(2.2)
ir = rng.normal(0, 1, (len(ir_t), 2)) * np.exp(-ir_t * 3.2)[:, None]
ir[:, 0] = lp_fast(ir[:, 0], 6000)
ir[:, 1] = lp_fast(ir[:, 1], 6000)
ir /= np.abs(ir).sum(axis=0) ** 0.5 * 4
L = 1 << int(math.ceil(math.log2(N + len(ir_t))))
rev = np.zeros((N, 2))
for ch in range(2):
    rev[:, ch] = np.fft.irfft(np.fft.rfft(wet[:, ch], L) * np.fft.rfft(ir[:, ch], L), L)[:N]
mix_m = music + rev * 0.5
mix_s = sfx + rev * 0.5


def save(x, name):
    x = x.copy()
    f0 = int((DUR - 0.6) * SR)
    x[f0:] *= np.linspace(1, 0, N - f0)[:, None]
    x /= np.abs(x).max() / 0.85
    with wave.open(str(HERE / "sources" / name), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())


save(mix_m, "musique.wav")
save(mix_s, "bruitages.wav")
json.dump(beats_out, open(HERE / "sources" / "temps-forts.json", "w"))
print("OK", len(beats_out), "temps forts")
