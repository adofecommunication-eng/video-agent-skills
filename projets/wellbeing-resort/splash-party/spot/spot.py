#!/usr/bin/env python3
"""Spot cinématographique « SPLASH PARTY » — Wellbeing Resort — 60 s, 9:16, 1080x1920, 30 i/s.

Construit uniquement à partir d'images RÉELLES du client (aucune image générée) :
  - sources/photo-enfants-mousse.jpg : photo HD prise à la piscine du Wellbeing Resort
  - sources/video-piscine-wbr.mov    : vidéo tournée au Wellbeing Resort (fête de la mousse)
  - sources/voix-off-lola.mp3        : voix off (prise 2)
Écriture « bande-annonce » : ouverture à froid en format cinéma 2.39 sur les yeux,
compte à rebours, transformation (explosion de mousse qui ouvre le cadre), travelling
en profondeur sur la photo (premier plan détouré, arrière-plan flou), révélation
émotionnelle (mise au point), transitions en bulles, final avec applaudissements.
Étalonnage cinéma (ombres sarcelle, peaux chaudes, halation), grain argentique.
Polices de la charte WBR : Anton (titres, chiffres), Helvetica Neue (infos ; TeX Gyre Heros).

Usage : python3 spot.py [--subs] [--stills]   (musique : python3 son.py)
"""
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "well-brunch-reel"))
import render as R  # noqa: E402

OUT = HERE / "rendu"
OUT.mkdir(exist_ok=True)
W, H, FPS, DUR = 1080, 1920, 30, 60.0
N = int(DUR * FPS)
V = 2.0  # la voix démarre après 2 s d'ouverture à froid
FRAMES_DIR = Path("/tmp/claude-0/-home-user-video-agent-skills/f000ac99-c2ab-59e9-bb38-e2dfc59cda23/scratchpad/sp/frames")

WHITE = (255, 255, 255)
INK = (8, 10, 14)
GOLD = R.GOLD
WATER = (40, 170, 230)
clamp, prog, ease_out, ease_in_out, back_out = R.clamp, R.prog, R.ease_out, R.ease_in_out, R.back_out

# ---------------------------------------------------------------- calage voix (délai inclus)
CUE = {
    "trois": 0.06 + V, "deux": 0.88 + V, "un": 1.86 + V, "splash": 2.46 + V,
    "samedi": 3.80 + V, "wbr": 5.10 + V, "party": 7.20 + V,
    "heures": 8.36 + V, "petits": 11.4 + V,
    "auprog": 13.16 + V, "piscine": 14.11 + V, "miss": 15.79 + V, "danses": 17.75 + V, "karaoke": 19.2 + V,
    "billard": 20.17 + V, "babyfoot": 20.9 + V, "jeux": 21.6 + V, "dj": 22.36 + V,
    "entree": 24.54 + V, "prix": 25.4 + V, "enfant": 26.6 + V, "rafr": 28.0 + V, "acces": 29.4 + V,
    "faims": 30.84 + V, "nourriture": 31.98 + V,
    "famille": 34.08 + V, "adorer": 35.90 + V,
    "resa": 37.72 + V, "nums": [38.72 + V, 39.66 + V, 40.2 + V, 40.9 + V, 41.95 + V],
    "fin": 44.04 + V, "attend": 50.25 + V, "plouf": 51.96 + V,
}
CUTS = [CUE["trois"], CUE["splash"], CUE["heures"] - 0.05, CUE["auprog"] - 0.05, CUE["entree"] - 0.05,
        CUE["faims"] - 0.05, CUE["famille"] - 0.05, CUE["resa"] - 0.05, CUE["fin"] - 0.05, CUE["plouf"]]
IMPACTS = [CUE["splash"], CUE["party"], CUE["miss"], CUE["prix"], CUE["plouf"]]


# ---------------------------------------------------------------- utilitaires
def tl(text, font, **kw):
    return R.text_layer(text, font, **kw)


def place(c, layer, cx, cy, alpha=1.0, scale=1.0, angle=0.0):
    if alpha <= 0.002 or scale <= 0.01:
        return
    if angle:
        layer = layer.rotate(angle, resample=Image.BICUBIC, expand=True)
    R.place(c, layer, cx, cy, alpha=alpha, scale=scale)


def slam(c, layer, cx, cy, t, t0, big=1.6, dur=0.14, alpha=1.0):
    R.slam(c, layer, cx, cy, t, t0, big=big, dur=dur, alpha=alpha)


def reveal(c, layer, cx, cy, t, t0, dur=0.6, alpha=1.0, rise=40):
    """Apparition cinéma : fondu + flou qui se dissipe + légère montée."""
    if t < t0:
        return
    p = prog(t, t0, dur)
    e = ease_out(p)
    lay = layer
    if p < 1:
        lay = layer.filter(ImageFilter.GaussianBlur(10 * (1 - e)))
    place(c, lay, cx, cy + rise * (1 - e), alpha=e * alpha)


def fade_out_after(t, t1, d=0.3):
    return 1 - prog(t, t1, d)


def rrect_mask(size, r):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=r, fill=255)
    return m


def gold_fill(size, mask=None):
    g = R.gradient_fill(size, R.GOLD_STOPS).convert("RGBA")
    if mask is not None:
        g.putalpha(mask)
    return g


def bloom(layer, radius=18, strength=0.6):
    """Halo lumineux autour d'un titre (rendu « cinéma »)."""
    pad = radius * 2
    out = Image.new("RGBA", (layer.width + 2 * pad, layer.height + 2 * pad), (0, 0, 0, 0))
    glow = Image.new("RGBA", out.size, (0, 0, 0, 0))
    glow.alpha_composite(layer, (pad, pad))
    glow = glow.filter(ImageFilter.GaussianBlur(radius))
    glow.putalpha(glow.getchannel("A").point(lambda v: int(v * strength)))
    out.alpha_composite(glow)
    out.alpha_composite(layer, (pad, pad))
    return out


def text3d(text, font, face="gold", side=(110, 76, 18), depth=12, tracking=0):
    m = tl(text, font, fill=WHITE, shadow=False, tracking=tracking).getchannel("A")
    pad = depth + 30
    w, h = m.width + 2 * pad, m.height + 2 * pad
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sh.paste(Image.new("RGBA", m.size, (0, 0, 0, 160)), (pad + 6, pad + depth + 14), m)
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    for i in range(depth, 0, -1):
        k = 0.55 + 0.45 * (1 - i / depth)
        out.paste(Image.new("RGBA", m.size, tuple(int(v * k) for v in side) + (255,)), (pad, pad + i), m)
    if face == "gold":
        bb = m.getbbox() or (0, 0, m.width, m.height)
        f = Image.new("RGBA", m.size, (0, 0, 0, 0))
        f.paste(R.gradient_fill((m.width, bb[3] - bb[1]), R.GOLD_STOPS).convert("RGBA"), (0, bb[1]))
    else:
        f = Image.new("RGBA", m.size, face + (255,))
    f.putalpha(m)
    out.alpha_composite(f, (pad, pad))
    return out


def shine(layer, p, width=0.10, strength=0.8):
    if not 0 < p < 1:
        return layer
    w, h = layer.size
    gx = np.arange(w)[None, :] / w + np.arange(h)[:, None] / h * 0.35
    band = np.exp(-((gx - (-0.25 + 1.6 * p)) / width) ** 2) * strength
    a = np.asarray(layer.getchannel("A")).astype(np.float32) / 255 * band * 255
    hl = Image.new("RGBA", (w, h), (255, 252, 235, 0))
    hl.putalpha(Image.fromarray(a.astype(np.uint8), "L"))
    out = layer.copy()
    out.alpha_composite(hl)
    return out


def shining(layer, t, t0, period=2.4):
    if t < t0 + 0.1:
        return layer
    p = ((t - t0 - 0.1) % period) / 0.9
    return shine(layer, p) if p < 1 else layer


# ---------------------------------------------------------------- étalonnage cinéma
def grade(img, warm=1.0, teal=1.0, contrast=1.12, sat=1.08, halation=True):
    a = np.asarray(img.convert("RGB")).astype(np.float32) / 255
    lum = (0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2])[..., None]
    a = (a - 0.5) * contrast + 0.5                                       # contraste
    a = lum + (a - lum) * sat                                            # saturation
    a += (1 - lum) ** 2 * np.array([-0.025, 0.018, 0.04]) * teal         # ombres sarcelle
    a += lum ** 2 * np.array([0.045, 0.018, -0.03]) * warm               # hautes lumières chaudes
    a = np.clip(a, 0, 1)
    out = Image.fromarray((a * 255).astype(np.uint8))
    if halation:
        hl = np.clip((lum[..., 0] - 0.82) * 5, 0, 1)
        glow = Image.fromarray((hl * 255).astype(np.uint8), "L").resize((img.width // 4, img.height // 4))
        glow = glow.filter(ImageFilter.GaussianBlur(10)).resize(img.size, Image.BILINEAR)
        g = np.asarray(glow).astype(np.float32)[..., None] / 255
        b = np.asarray(out).astype(np.float32) / 255
        b = 1 - (1 - b) * (1 - g * np.array([0.35, 0.16, 0.08]))
        out = Image.fromarray((np.clip(b, 0, 1) * 255).astype(np.uint8))
    return out


# ---------------------------------------------------------------- sources
PHOTO = grade(Image.open(HERE / "sources" / "photo-enfants-mousse.jpg").convert("RGB"))  # 1500x2000
PH_W, PH_H = PHOTO.size
PHOTO_BLUR = PHOTO.filter(ImageFilter.GaussianBlur(9))
_m = Image.open(HERE / "elements" / "fillettes-brut.png").getchannel("A")
_mm = np.asarray(_m).copy()
_mm[:810, 1080:] = 0                      # retire le garçon de l'arrière-plan
_mm[:600, :] = 0
FG_MASK = Image.fromarray(_mm, "L").filter(ImageFilter.GaussianBlur(2))
FG = PHOTO.convert("RGBA")
FG.putalpha(FG_MASK)


def frame_video(t_src):
    """Image de la vidéo du Wellbeing Resort à l'instant t_src (s), étalonnée."""
    i = int(clamp(t_src * 30, 0, 229)) + 1
    return grade(Image.open(FRAMES_DIR / f"f{i:04d}.jpg"))


def crop_fill(img, box, out=(W, H)):
    """Recadre img sur box (à l'aspect de out) et redimensionne."""
    return img.resize(out, Image.LANCZOS, box=box)


def view(cx, cy, zoom, img=PHOTO, aspect=W / H):
    """Fenêtre centrée (cx, cy) dans la photo ; zoom 1 = hauteur entière."""
    h = img.height / zoom
    w = h * aspect
    cx = clamp(cx, w / 2, img.width - w / 2)
    cy = clamp(cy, h / 2, img.height - h / 2)
    return (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)


def parallax(t, t0, dur, z0=1.0, z1=1.18, x0=750, x1=820, y0=1050, y1=1000, depth=0.35):
    """Travelling en profondeur : l'arrière-plan (flou) bouge moins que les fillettes (nettes)."""
    p = ease_in_out(prog(t, t0, dur))
    z = z0 + (z1 - z0) * p
    cx, cy = x0 + (x1 - x0) * p, y0 + (y1 - y0) * p
    bz = 1 + (z - 1) * (1 - depth)
    bg = crop_fill(PHOTO_BLUR, view(cx, cy, bz))
    fgv = view(cx, cy, z)
    fg = FG.resize((W, H), Image.LANCZOS, box=fgv)
    c = bg.convert("RGBA")
    c.alpha_composite(fg)
    return c


# ---------------------------------------------------------------- effets
def letterbox(c, amount):
    """Bandes noires format cinéma 2.39 (amount 0 → 1)."""
    if amount <= 0:
        return
    bar = int((H - W / 2.39) / 2 * amount)
    d = ImageDraw.Draw(c)
    d.rectangle((0, 0, W, bar), fill=(0, 0, 0, 255))
    d.rectangle((0, H - bar, W, H), fill=(0, 0, 0, 255))


def light_leak(c, t, t0, dur=1.2, color=(255, 170, 90), x0=-300, x1=1400, alpha=150):
    p = prog(t, t0, dur)
    if p <= 0 or p >= 1:
        return
    lay = Image.new("RGBA", (W // 4, H // 4), (0, 0, 0, 0))
    x = (x0 + (x1 - x0) * p) / 4
    ImageDraw.Draw(lay).ellipse((x - 90, -40, x + 90, H // 4 + 40), fill=color + (int(alpha * math.sin(p * math.pi)),))
    c.alpha_composite(lay.filter(ImageFilter.GaussianBlur(30)).resize((W, H), Image.BILINEAR))


def bubbles(c, t, n=40, seed=3, alpha=0.8, speed=1.0):
    r = np.random.default_rng(seed)
    d = ImageDraw.Draw(c)
    for _ in range(n):
        x0, y0, rad, sp, ph = r.uniform(0, W), r.uniform(0, H), r.uniform(4, 22), r.uniform(80, 260), r.uniform(0, 6)
        y = (y0 - sp * speed * t) % (H + 60) - 30
        x = x0 + 14 * math.sin(ph + t * 2)
        a = int(170 * alpha)
        d.ellipse((x - rad, y - rad, x + rad, y + rad), outline=(230, 248, 255, a), width=2)
        d.ellipse((x - rad * 0.45, y - rad * 0.6, x - rad * 0.1, y - rad * 0.25), fill=(255, 255, 255, a))


_src = PHOTO.crop((380, 1300, 1120, 2000))             # zone de mousse pure, agrandie sans déformation
_k = (H + 260) / _src.height
FOAM_TEX = _src.resize((int(_src.width * _k), H + 260), Image.LANCZOS)
FOAM_TEX = FOAM_TEX.crop(((FOAM_TEX.width - W) // 2, 0, (FOAM_TEX.width - W) // 2 + W, H + 260))
_ft = np.asarray(FOAM_TEX).astype(np.float32)
_lum = _ft.mean(axis=2, keepdims=True)
_ft = _lum + (_ft - _lum) * 0.55                    # mousse plus blanche (moins de bleu d'eau)
FOAM_TEX = Image.fromarray(np.clip(_ft * 1.12 + 18, 0, 255).astype(np.uint8)).convert("RGBA")


def foam_burst(c, t, t0, cx=W / 2, cy=H / 2, dur=0.6, seed=5):
    """Transformation : une vague de VRAIE mousse (texture de la photo) envahit l'écran puis se dissipe."""
    p = (t - t0) / dur
    if p < -0.3 or p > 1.6:
        return
    r = np.random.default_rng(seed)
    m = Image.new("L", (W // 4, H // 4), 0)
    d = ImageDraw.Draw(m)
    grow = ease_out(clamp((p + 0.3) / 0.7))
    fade = 1 - clamp((p - 0.6) / 1.0)
    for _ in range(260):
        ang, dist = r.uniform(0, 6.283), r.uniform(0, 1.15) ** 0.7
        rad = r.uniform(70, 220) * (0.4 + grow)
        x = cx + math.cos(ang) * dist * 1300 * grow
        y = cy + math.sin(ang) * dist * 1800 * grow
        d.ellipse(((x - rad) / 4, (y - rad) / 4, (x + rad) / 4, (y + rad) / 4), fill=int(255 * fade))
    m = m.filter(ImageFilter.GaussianBlur(4)).resize((W, H), Image.BILINEAR)
    shift = int(160 * clamp(p, 0, 1.6))
    tex = FOAM_TEX.crop((0, shift, W, shift + H))
    c.paste(tex, (0, 0), m)


def bubble_mask(p, seed=0):
    """Transition magique : des bulles grossissent et dévoilent la séquence suivante."""
    r = np.random.default_rng(seed)
    m = Image.new("L", (W // 4, H // 4), 0)
    d = ImageDraw.Draw(m)
    e = ease_in_out(p)
    for _ in range(70):
        x, y, s, dl = r.uniform(0, W / 4), r.uniform(0, H / 4), r.uniform(0.6, 1.4), r.uniform(0, 0.45)
        k = clamp((e - dl) / (1 - dl))
        rad = k * 160 * s
        d.ellipse((x - rad, y - rad, x + rad, y + rad), fill=255)
    return m.filter(ImageFilter.GaussianBlur(2)).resize((W, H), Image.BILINEAR)


def flash(c, t, t0, dur=0.25, strength=0.7, color=(255, 255, 255)):
    p = (t - t0) / dur
    if 0 <= p <= 1:
        c.alpha_composite(Image.new("RGBA", (W, H), color + (int(255 * strength * (1 - p) ** 2),)))


def droplets(c, t, t0, cx, cy, n=80, seed=7):
    if t < t0 or t > t0 + 1.4:
        return
    r = np.random.default_rng(seed)
    d = ImageDraw.Draw(c)
    dt = t - t0
    for _ in range(n):
        ang = r.uniform(math.pi * 1.02, math.pi * 1.98)
        sp = r.uniform(700, 1700)
        x = cx + math.cos(ang) * sp * dt
        y = cy + math.sin(ang) * sp * dt + 1700 * dt * dt
        rad = r.uniform(4, 13) * (1 - dt / 1.6)
        d.ellipse((x - rad, y - rad, x + rad, y + rad), fill=(235, 250, 255, int(230 * clamp(1.4 - dt))))


def caustics_bg(t, base=(0, 70, 120)):
    sx, sy = np.meshgrid(np.linspace(0, 6, W // 6), np.linspace(0, 10, H // 6))
    v = (np.sin(sx * 2.1 + t * 1.6 + np.sin(sy * 1.7 + t)) + np.sin(sy * 2.6 - t * 1.3 + np.sin(sx * 1.3))) / 2
    v = np.clip((v - 0.5) * 3, 0, 1)
    d = np.sqrt(((np.arange(H // 6)[:, None] - H / 12) / (H / 6)) ** 2 + ((np.arange(W // 6)[None, :] - W / 12) / (W / 6)) ** 2)
    a = np.empty((H // 6, W // 6, 3), np.float32)
    for k, cc in enumerate(base):
        a[..., k] = cc * (1.2 - d) + v * (60 if k else 20) * (1.1 - d)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC).convert("RGBA")


def veil(c, a=120, color=(0, 0, 0)):
    c.alpha_composite(Image.new("RGBA", (W, H), color + (a,)))


def grad_bottom(c, h=900, a=210):
    g = np.linspace(0, 1, h) ** 1.6 * a
    lay = Image.new("RGBA", (W, h), (0, 0, 0, 0))
    lay.putalpha(Image.fromarray(np.repeat(g[:, None], W, 1).astype(np.uint8), "L"))
    c.alpha_composite(lay, (0, H - h))


# ---------------------------------------------------------------- textes
F_A = R.anton
F_H = lambda s: R.helv(s, bold=True)  # noqa: E731
T = {
    "3": bloom(tl("3", F_A(560))), "2": bloom(tl("2", F_A(560))), "1": bloom(tl("1", F_A(560))),
    "splash": bloom(text3d("SPLASH !", F_A(250), face=WHITE, side=(20, 110, 170), depth=16), 22, 0.5),
    "samedi": tl("SAMEDI 05 DÉC. 2026", F_A(96), tracking=6),
    "wbr": tl("WELLBEING RESORT PRÉSENTE", F_H(38), tracking=10),
    "titre1": bloom(text3d("SPLASH", F_A(270), depth=16, tracking=6), 24, 0.55),
    "titre2": bloom(text3d("PARTY", F_A(270), face=WHITE, side=(20, 110, 170), depth=16, tracking=10), 24, 0.45),
    "heures": tl("08H – 18H", F_A(150), tracking=6),
    "journee": tl("UNE JOURNÉE DE FUN", F_H(42), tracking=10),
    "petits": tl("POUR PETITS ET GRANDS", F_A(84), tracking=4),
    "auprog": bloom(tl("AU PROGRAMME", F_A(130), tracking=10), 16, 0.4),
    "piscine": tl("PISCINE", F_A(190), tracking=4),
    "mousse": tl("& BAIN DE MOUSSE", F_A(96), tracking=4),
    "miss": bloom(text3d("MISS SPLASH", F_A(170), depth=14, tracking=4), 20, 0.5),
    "election": tl("L'ÉLECTION", F_H(40), tracking=14),
    "danses": tl("CONCOURS DE DANSES", F_A(120), tracking=3),
    "karaoke": tl("KARAOKÉ", F_A(190), gold=True, tracking=6),
    "billard": tl("BILLARD", F_A(170), tracking=6),
    "babyfoot": tl("BABY-FOOT", F_A(170), tracking=6),
    "jeux": tl("JEUX", F_A(170), tracking=6),
    "dj": bloom(text3d("AMBIANCE DJ", F_A(160), depth=12, tracking=4), 20, 0.5),
    "toutjour": tl("TOUTE LA JOURNÉE", F_H(40), tracking=12),
    "enfadu": tl("ENFANT & ADULTE", F_A(90), tracking=6),
    "rafr": tl("+ 01 RAFRAÎCHISSEMENT OFFERT", F_H(40), tracking=4),
    "acces": tl("ACCÈS À LA PISCINE", F_A(80), gold=True, tracking=6),
    "faims": tl("POUR LES PETITES FAIMS", F_H(40), tracking=10),
    "nourr": tl("NOURRITURE", F_A(170), tracking=6),
    "surplace": tl("À COMMANDER SUR PLACE", F_A(86), gold=True, tracking=4),
    "famille": tl("EN FAMILLE OU ENTRE AMIS", F_H(44), tracking=8),
    "adorer": bloom(tl("LES ENFANTS VONT ADORER", F_A(86), tracking=3), 16, 0.45),
    "resa": tl("RÉSERVATION", F_H(46), gold=True, tracking=16),
    "tel2": tl("05 66 92 33 91", F_A(110)),
    "fin_date": tl("SAMEDI 05 DÉC. 2026  ·  08H – 18H", F_H(40), tracking=4),
    "fin_adr": tl("COCODY RIVIERA 3, ROUTE M'BADON", F_H(36), tracking=3),
    "fin_tel": tl("07 47 79 95 07  ·  05 66 92 33 91", F_A(70), gold=True),
    "fin_prix": tl("ENTRÉE 5.000 F  ·  ENFANT & ADULTE", F_H(38), tracking=3),
    "plouf": bloom(text3d("PLOUF !", F_A(300), face=WHITE, side=(20, 110, 170), depth=18), 26, 0.55),
}
NUM_GROUPS = ["07", "47", "79", "95", "07"]
T_NUM = [bloom(text3d(g, F_A(220), depth=12), 16, 0.45) for g in NUM_GROUPS]
LOGO = R.LOGO
_TK = {}


def ticket(value):
    if value in _TK:
        return _TK[value]
    w, h = 880, 420
    m = rrect_mask((w, h), 36)
    d = ImageDraw.Draw(m)
    d.ellipse((-50, h // 2 - 50, 50, h // 2 + 50), fill=0)
    d.ellipse((w - 50, h // 2 - 50, w + 50, h // 2 + 50), fill=0)
    tk = gold_fill((w, h), m)
    dd = ImageDraw.Draw(tk)
    for x in range(90, w - 90, 26):
        dd.line((x, 100, x + 12, 100), fill=(60, 40, 10, 140), width=3)
    lab = tl("ENTRÉE", F_H(44), fill=INK, shadow=False, tracking=16)
    tk.alpha_composite(lab, ((w - lab.width) // 2, 6))
    val = tl(f"{value} F", F_A(210), fill=INK, shadow=False)
    tk.alpha_composite(val, ((w - val.width) // 2, 100))
    out = Image.new("RGBA", (w + 80, h + 80), (0, 0, 0, 0))
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sh.paste(Image.new("RGBA", (w, h), (0, 0, 0, 170)), (0, 0), m)
    out.alpha_composite(sh, (40, 60))
    out = out.filter(ImageFilter.GaussianBlur(16))
    out.alpha_composite(tk, (40, 40))
    _TK[value] = out
    return out


def crown(size=280):
    s = size
    m = Image.new("L", (s * 2, int(s * 1.5)), 0)
    d = ImageDraw.Draw(m)
    S2 = 2 * s
    pts = [(0.05, 0.9), (0.05, 0.3), (0.28, 0.6), (0.5, 0.1), (0.72, 0.6), (0.95, 0.3), (0.95, 0.9)]
    d.polygon([(x * S2, y * S2 * 0.75) for x, y in pts], fill=255)
    for x, y in [(0.05, 0.3), (0.5, 0.1), (0.95, 0.3)]:
        d.ellipse((x * S2 - 22, y * S2 * 0.75 - 22, x * S2 + 22, y * S2 * 0.75 + 22), fill=255)
    m = m.resize((s, int(s * 0.75)), Image.LANCZOS)
    g = gold_fill(m.size, m)
    gd = ImageDraw.Draw(g)
    for x in (0.28, 0.5, 0.72):
        gd.ellipse((x * s - 14, s * 0.55 - 14, x * s + 14, s * 0.55 + 14), fill=WATER + (255,))
    return bloom(g, 18, 0.5)


CROWN = crown()


def eq_bars(c, t, beat, cy=1350, n=24, w=26, gap=12, hmax=260):
    d = ImageDraw.Draw(c)
    x0 = (W - n * (w + gap)) / 2
    for i in range(n):
        h = hmax * (0.25 + 0.75 * abs(math.sin(t * 7 + i * 0.6)) * (0.5 + 0.5 * beat)) * (1 - abs(i - n / 2) / n)
        x = x0 + i * (w + gap)
        d.rounded_rectangle((x, cy - h, x + w, cy), radius=8, fill=GOLD + (230,))


def vinyl(size=520, angle=0):
    s = size
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, s, s), fill=(14, 14, 16, 255))
    for r in range(30, s // 2 - 10, 9):
        d.ellipse((s / 2 - r, s / 2 - r, s / 2 + r, s / 2 + r), outline=(40, 40, 46, 255), width=1)
    lab = gold_fill((int(s * 0.36), int(s * 0.36)), Image.new("L", (int(s * 0.36), int(s * 0.36)), 0))
    lm = Image.new("L", lab.size, 0)
    ImageDraw.Draw(lm).ellipse((0, 0, lab.width, lab.height), fill=255)
    lab.putalpha(lm)
    im.alpha_composite(lab, ((s - lab.width) // 2, (s - lab.height) // 2))
    d.ellipse((s / 2 - 10, s / 2 - 10, s / 2 + 10, s / 2 + 10), fill=(10, 10, 10, 255))
    d.line((s / 2, s / 2 - s * 0.45, s / 2 + 8, s / 2 - s * 0.2), fill=(255, 255, 255, 60), width=6)  # reflet
    return im.rotate(angle, resample=Image.BICUBIC)


VINYL = vinyl()

# ---------------------------------------------------------------- temps forts de la musique (pulsations)
BEATS_FILE = HERE / "sources" / "temps-forts.json"
BEATS = json.load(open(BEATS_FILE)) if BEATS_FILE.exists() else []


def beat_pulse(t):
    k = 0.0
    for b in BEATS:
        if b <= t < b + 0.25:
            k = max(k, math.exp(-(t - b) / 0.07))
    return k


# ---------------------------------------------------------------- séquences
def s0_cold(c, t):
    """0 – 2,06 : ouverture à froid. Format cinéma, les yeux de la fillette, lente avancée."""
    p = prog(t, 0, CUTS[0])
    box = view(1180, 965, 2000 / 260 * (1 + 0.08 * p), aspect=W / H)
    img = crop_fill(PHOTO, box)
    c.alpha_composite(img.convert("RGBA"))
    veil(c, int(255 * (1 - prog(t, 0.15, 0.9))))
    letterbox(c, 1)


def s1_count(c, t):
    """2,06 – 4,46 : TROIS (sourire) · DEUX (mains dans la mousse) · UN (les yeux)."""
    k = 0 if t < CUE["deux"] else 1 if t < CUE["un"] else 2
    t0 = [CUE["trois"], CUE["deux"], CUE["un"]][k]
    p = prog(t, t0, 1.0)
    if k == 0:
        img = crop_fill(PHOTO, view(530, 800, 2000 / 420 * (1 + 0.06 * p)))
    elif k == 1:
        img = crop_fill(PHOTO, view(480, 990, 2000 / 560 * (1 + 0.06 * p)))
    else:
        img = crop_fill(PHOTO, view(1180, 962, 2000 / 230 * (1 + 0.05 * p)))
    c.alpha_composite(img.convert("RGBA"))
    veil(c, 90)
    slam(c, T[str(3 - k)], W / 2, H / 2, t, t0, big=1.5, dur=0.16)
    flash(c, t, t0, 0.18, 0.5)
    letterbox(c, 1 - ease_in_out(prog(t, CUE["splash"] - 0.25, 0.25)))
    foam_burst(c, t, CUE["splash"] - 0.18, seed=11)


def s2_hero(c, t):
    """4,46 – 10,3 : transformation terminée, travelling Nolan sur la photo ; SPLASH ! puis le titre."""
    img = parallax(t, CUTS[1], CUTS[2] - CUTS[1], z0=1.02, z1=1.22, x0=700, x1=820, y0=1080, y1=1000)
    c.alpha_composite(img)
    grad_bottom(c, 1000, 200)
    veil(c, 40)
    foam_burst(c, t, CUE["splash"] - 0.18, seed=11)
    a1 = fade_out_after(t, CUE["samedi"] - 0.3)
    slam(c, T["splash"], W / 2, 780, t, CUE["splash"] + 0.05, big=2.0, dur=0.18, alpha=a1)
    droplets(c, t, CUE["splash"] + 0.05, W / 2, 900, n=90, seed=3)
    a2 = fade_out_after(t, CUE["party"] - 0.4)
    reveal(c, T["samedi"], W / 2, 1180, t, CUE["samedi"], alpha=a2)
    reveal(c, T["wbr"], W / 2, 1290, t, CUE["wbr"], alpha=a2)
    slam(c, shining(T["titre1"], t, CUE["party"]), W / 2, 1060, t, CUE["party"], big=1.8, dur=0.16)
    slam(c, shining(T["titre2"], t, CUE["party"] + 0.25), W / 2, 1290, t, CUE["party"] + 0.25, big=1.8, dur=0.16)
    droplets(c, t, CUE["party"] + 0.25, W / 2, 1300, n=90, seed=4)
    light_leak(c, t, CUE["party"] + 0.2, 1.4)


def s3_footage(c, t):
    """10,3 – 15,1 : la vraie fête au Wellbeing Resort, 08H – 18H, pour petits et grands."""
    lt = t - CUTS[2]
    img = frame_video(2.0 + lt * 1.0)
    z = 1.0 + 0.04 * prog(t, CUTS[2], 5)
    img = img.resize((int(W * z), int(H * z)), Image.BILINEAR).crop((int(W * (z - 1) / 2), int(H * (z - 1) / 2),
                                                                     int(W * (z - 1) / 2) + W, int(H * (z - 1) / 2) + H))
    c.alpha_composite(img.convert("RGBA"))
    grad_bottom(c, 900, 190)
    reveal(c, T["heures"], W / 2, 1140, t, CUE["heures"] + 0.2)
    reveal(c, T["journee"], W / 2, 1270, t, CUE["heures"] + 1.2)
    a = 1 - prog(t, CUE["petits"] - 0.4, 0.3)
    if a < 1:
        pass
    reveal(c, T["petits"], W / 2, 1380, t, CUE["petits"])


def s4_programme(c, t):
    """15,1 – 26,5 : le programme, une coupe par activité."""
    if t < CUE["piscine"] - 0.05:  # AU PROGRAMME sur l'eau
        c.alpha_composite(caustics_bg(t))
        bubbles(c, t, n=50, seed=8)
        slam(c, T["auprog"], W / 2, H / 2, t, CUE["auprog"], big=1.4)
    elif t < CUE["miss"] - 0.05:  # piscine & mousse
        p = prog(t, CUE["piscine"], 1.8)
        c.alpha_composite(crop_fill(PHOTO, view(760, 1250 - 120 * p, 1.35 + 0.15 * p)).convert("RGBA"))
        grad_bottom(c, 1000, 235)
        slam(c, T["piscine"], W / 2, 1250, t, CUE["piscine"], big=1.5)
        reveal(c, T["mousse"], W / 2, 1400, t, CUE["piscine"] + 0.45, dur=0.4)
        bubbles(c, t, n=30, seed=9)
    elif t < CUE["danses"] - 0.05:  # Miss Splash
        c.alpha_composite(caustics_bg(t, base=(4, 30, 60)))
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        a = int(140 * clamp((t - CUE["miss"]) * 3))
        ImageDraw.Draw(glow).polygon([(W / 2 - 70, 0), (W / 2 + 70, 0), (W / 2 + 520, 1350), (W / 2 - 520, 1350)],
                                     fill=(255, 220, 150, a))
        c.alpha_composite(glow.filter(ImageFilter.GaussianBlur(50)))
        k = prog(t, CUE["miss"] - 0.15, 0.5)
        if k > 0:
            place(c, CROWN, W / 2, -200 + (720 + 200) * ease_out(k), angle=6 * (1 - k) * math.sin(t * 9))
        reveal(c, T["election"], W / 2, 900, t, CUE["miss"] - 0.1, dur=0.35)
        slam(c, shining(T["miss"], t, CUE["miss"] + 0.1), W / 2, 1040, t, CUE["miss"] + 0.1, big=1.7)
        droplets(c, t, CUE["miss"] + 0.1, W / 2, 1050, n=60, seed=5)
    elif t < CUE["billard"] - 0.05:  # danses + karaoké : la vraie foule, floutée
        img = frame_video(5.4 + (t - CUE["danses"]) * 0.6).filter(ImageFilter.GaussianBlur(6))
        c.alpha_composite(img.convert("RGBA"))
        veil(c, 120, (4, 20, 40))
        slam(c, T["danses"], W / 2, 860, t, CUE["danses"], big=1.4)
        slam(c, T["karaoke"], W / 2, 1060, t, CUE["karaoke"], big=1.6)
        eq_bars(c, t, beat_pulse(t), cy=1420, hmax=200 * clamp((t - CUE["karaoke"]) * 3))
    elif t < CUE["dj"] - 0.05:  # billard, baby-foot, jeux : un mot par temps
        img = crop_fill(PHOTO_BLUR, view(750, 700, 1.0))
        c.alpha_composite(img.convert("RGBA"))
        veil(c, 140, (2, 20, 40))
        words = [("billard", CUE["billard"]), ("babyfoot", CUE["babyfoot"]), ("jeux", CUE["jeux"])]
        for i, (k, t0) in enumerate(words):
            nxt = words[i + 1][1] if i + 1 < len(words) else 99
            if t0 - 0.05 <= t < nxt - 0.05:
                slam(c, T[k], W / 2, H / 2, t, t0, big=1.7)
        bubbles(c, t, n=24, seed=12)
    else:  # ambiance DJ : vinyle qui tourne, égaliseur sur la musique
        c.alpha_composite(caustics_bg(t, base=(2, 18, 40)))
        bp = beat_pulse(t)
        place(c, VINYL.rotate(-t * 220 % 360, resample=Image.BICUBIC), W / 2, 760, scale=1 + 0.04 * bp)
        slam(c, T["dj"], W / 2, 1150, t, CUE["dj"] + 0.4, big=1.5)
        reveal(c, T["toutjour"], W / 2, 1290, t, CUE["dj"] + 1.0)
        eq_bars(c, t, bp, cy=1600, hmax=220)


def s5_prix(c, t):
    """26,5 – 32,8 : le ticket or ENTRÉE 5.000 F, enfant & adulte, rafraîchissement, accès piscine."""
    c.alpha_composite(crop_fill(PHOTO_BLUR, view(760, 1350, 1.2)).convert("RGBA"))
    veil(c, 150, (2, 16, 30))
    bubbles(c, t, n=30, seed=14, alpha=0.6)
    k = prog(t, CUE["entree"] + 0.1, 0.5)
    if k > 0:
        cp = prog(t, CUE["prix"], 0.9)
        val = int(round(5000 * ease_out(cp) / 250) * 250)
        txt = f"{val // 1000}.{val % 1000:03d}" if val >= 1000 else str(val)
        tk = shining(ticket(txt), t, CUE["prix"] + 0.9, 1.6)
        flip = abs(math.cos((1 - ease_out(k)) * math.pi * 1.5)) if k < 1 else 1.0
        tk = tk.resize((max(2, int(tk.width * flip)), tk.height), Image.BILINEAR)
        place(c, tk, W / 2, 760 + 10 * math.sin(t * 2.2), alpha=clamp(k * 3), angle=-3)
    flash(c, t, CUE["prix"] + 0.9, 0.3, 0.35, (255, 230, 170))
    slam(c, T["enfadu"], W / 2, 1110, t, CUE["enfant"], big=1.4)
    reveal(c, T["rafr"], W / 2, 1240, t, CUE["rafr"])
    reveal(c, T["acces"], W / 2, 1350, t, CUE["acces"])


def s6_food(c, t):
    """32,8 – 36,0 : nourriture à commander sur place (la vraie piscine en fond)."""
    img = frame_video(0.3 + (t - CUTS[5]) * 0.5).filter(ImageFilter.GaussianBlur(10))
    c.alpha_composite(img.convert("RGBA"))
    veil(c, 130, (10, 8, 4))
    reveal(c, T["faims"], W / 2, 820, t, CUE["faims"])
    slam(c, T["nourr"], W / 2, 980, t, CUE["nourriture"], big=1.4)
    reveal(c, T["surplace"], W / 2, 1130, t, CUE["nourriture"] + 0.6)
    light_leak(c, t, CUE["nourriture"], 1.6, color=(255, 190, 110), alpha=110)


def s7_emotion(c, t):
    """36,0 – 39,6 : révélation émotionnelle. Mise au point qui se fait sur les sourires."""
    p = prog(t, CUTS[6], CUTS[7] - CUTS[6])
    box = view(800, 1000, 1.25 + 0.12 * p)
    sharp = crop_fill(PHOTO, box)
    blur = crop_fill(PHOTO_BLUR.filter(ImageFilter.GaussianBlur(8)), box)
    focus = ease_in_out(prog(t, CUTS[6] + 0.2, 1.4))
    c.alpha_composite(Image.blend(blur, sharp, focus).convert("RGBA"))
    grad_bottom(c, 800, 170)
    light_leak(c, t, CUTS[6] + 0.3, 2.6, color=(255, 175, 95), alpha=170)
    letterbox(c, 0.75 * (1 - prog(t, CUTS[7] - 0.3, 0.3)))
    reveal(c, T["famille"], W / 2, 1180, t, CUE["famille"], dur=0.8)
    reveal(c, T["adorer"], W / 2, 1300, t, CUE["adorer"], dur=0.7)


def s8_resa(c, t):
    """39,6 – 45,9 : réservation. Chaque groupe de chiffres tombe dans l'eau."""
    c.alpha_composite(caustics_bg(t))
    bubbles(c, t, n=40, seed=16)
    reveal(c, T["resa"], W / 2, 520, t, CUE["resa"], dur=0.5)
    xs = [190, 390, 540, 690, 890]
    for i, t0 in enumerate(CUE["nums"]):
        if t < t0 - 0.05:
            continue
        p = prog(t, t0 - 0.05, 0.3)
        y = 820 - 500 * (1 - back_out(p, 1.6))
        place(c, T_NUM[i], [210, 365, 540, 715, 870][i], y, alpha=clamp(p * 3), scale=0.62)
        if p > 0.9 and t < t0 + 0.6:  # ondes à l'impact
            rr = (t - t0) * 300
            ImageDraw.Draw(c).ellipse(([210, 365, 540, 715, 870][i] - rr, 920 - rr * 0.25,
                                       [210, 365, 540, 715, 870][i] + rr, 920 + rr * 0.25),
                                      outline=(230, 250, 255, int(200 * clamp(1 - rr / 180))), width=4)
    reveal(c, T["tel2"], W / 2, 1060, t, CUE["nums"][-1] + 0.8)
    del xs


def finale_card(c, t, t0):
    c.alpha_composite(caustics_bg(t, base=(2, 14, 30)))
    bubbles(c, t, n=50, seed=21, alpha=0.7)
    pop = prog(t, t0, 0.5)
    place(c, LOGO.resize((int(LOGO.width * 0.55), int(LOGO.height * 0.55)), Image.LANCZOS), W / 2, 330,
          alpha=pop, scale=0.8 + 0.2 * back_out(pop))
    slam(c, shining(T["titre1"], t, t0 + 0.2, 1.8), W / 2, 590, t, t0 + 0.15, big=1.6)
    slam(c, shining(T["titre2"], t, t0 + 0.4, 1.8), W / 2, 810, t, t0 + 0.35, big=1.6)
    reveal(c, T["fin_date"], W / 2, 980, t, t0 + 0.7)
    reveal(c, T["fin_prix"], W / 2, 1050, t, t0 + 0.9)
    reveal(c, T["fin_adr"], W / 2, 1120, t, t0 + 1.1)
    reveal(c, T["fin_tel"], W / 2, 1240, t, t0 + 1.3)


def s9_final(c, t):
    """45,9 – 60 : travelling final sur la photo puis « PLOUF ! » et la carte finale."""
    if t < CUE["plouf"]:
        img = parallax(t, CUTS[8], CUE["plouf"] - CUTS[8], z0=1.25, z1=1.0, x0=820, x1=750, y0=980, y1=1060)
        c.alpha_composite(img)
        grad_bottom(c, 1100, 225)
        veil(c, 30)
        slam(c, shining(T["titre1"], t, CUTS[8] + 0.2), W / 2, 1000, t, CUTS[8], big=1.6)
        slam(c, shining(T["titre2"], t, CUTS[8] + 0.4), W / 2, 1220, t, CUTS[8] + 0.2, big=1.6)
        reveal(c, T["fin_date"], W / 2, 1400, t, CUE["fin"] + 1.1)
        reveal(c, T["fin_adr"], W / 2, 1470, t, CUE["fin"] + 3.0)
        foam_burst(c, t, CUE["plouf"] - 0.12, cy=H * 0.55, dur=0.5, seed=31)
    else:
        finale_card(c, t, CUE["plouf"] + 0.35)
        foam_burst(c, t, CUE["plouf"] - 0.12, cy=H * 0.55, dur=0.5, seed=31)
        a = 1 - prog(t, CUE["plouf"] + 0.9, 0.4)
        slam(c, T["plouf"], W / 2, H / 2, t, CUE["plouf"] + 0.05, big=2.2, dur=0.16, alpha=a)
        droplets(c, t, CUE["plouf"] + 0.05, W / 2, 1000, n=140, seed=33)


SCENES = [s0_cold, s1_count, s2_hero, s3_footage, s4_programme, s5_prix, s6_food, s7_emotion, s8_resa, s9_final]
BOUNDS = [0.0] + CUTS[:-1] + [DUR]
TRANS = {3: "bubbles", 5: "bubbles", 7: "bubbles", 9: "bubbles", 4: "whip", 6: "whip", 8: "whip"}
XD = 0.36


def scene_frame(i, t):
    c = Image.new("RGBA", (W, H), INK + (255,))
    SCENES[i](c, t)
    return c


def whip(c, nxt, p):
    """Panoramique filé : flou de bougé horizontal entre deux plans."""
    e = ease_in_out(p)
    src = c if e < 0.5 else nxt
    shift = int((e if e < 0.5 else e - 1) * W * 0.9)
    base = Image.new("RGBA", (W, H), INK + (255,))
    acc = None
    for k in range(6):
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        im.alpha_composite(src, (shift + k * 22 - 55, 0))
        acc = im if acc is None else Image.blend(acc, im, 1 / (k + 1))
    base.alpha_composite(acc)
    return base


def shake(c, t):
    for ti in IMPACTS:
        p = (t - ti) / 0.22
        if 0 <= p <= 1:
            amp = 14 * (1 - p)
            dx, dy = amp * math.sin(p * 37), amp * math.cos(p * 29)
            big = c.resize((int(W * 1.03), int(H * 1.03)), Image.BILINEAR)
            ox, oy = (big.width - W) / 2 + dx, (big.height - H) / 2 + dy
            return big.crop((int(ox), int(oy), int(ox) + W, int(oy) + H))
    return c


def pulse(c, t):
    bp = beat_pulse(t) if CUE["splash"] < t < CUTS[6] or CUTS[7] < t else 0
    if bp < 0.05:
        return c
    z = 1 + 0.018 * bp
    big = c.resize((int(W * z), int(H * z)), Image.BILINEAR)
    ox, oy = (big.width - W) // 2, (big.height - H) // 2
    c = big.crop((ox, oy, ox + W, oy + H))
    c.alpha_composite(Image.new("RGBA", (W, H), (255, 235, 200, int(28 * bp))))
    return c


# ---------------------------------------------------------------- sous-titres
SUBS_ON = "--subs" in sys.argv
_S = [
    (0.0, 2.4, "Trois… deux… un…"), (2.4, 3.5, "SPLASH !"),
    (3.8, 8.0, "Samedi 5 décembre, Wellbeing Resort vous invite à la Splash Party !"),
    (8.36, 12.8, "De 8h à 18h, on plonge dans une journée de fun pour petits et grands."),
    (13.16, 15.5, "Au programme : piscine et bain de mousse…"), (15.79, 17.46, "l'élection de Miss Splash…"),
    (17.75, 19.95, "un concours de danses, du karaoké…"),
    (20.17, 24.16, "billard, baby-foot, jeux, et une ambiance DJ toute la journée !"),
    (24.54, 27.5, "L'entrée est à 5.000 francs, enfant comme adulte,"),
    (27.5, 30.53, "avec un rafraîchissement offert et l'accès à la piscine."),
    (30.84, 33.75, "Et pour les petites faims, la nourriture se commande sur place."),
    (34.08, 37.37, "Venez en famille ou entre amis : les enfants vont adorer !"),
    (37.72, 43.72, "Réservez dès maintenant au 07 47 79 95 07."),
    (44.04, 49.91, "Splash Party, samedi 5 décembre, au Wellbeing Resort, Cocody Riviera 3, route M'Badon."),
    (50.25, 52.6, "On vous attend… pour un grand plouf !"),
]
SUBS = [(a + V, b + V, s) for a, b, s in _S]
_SUBC = {}


def sub_layer(text):
    if text in _SUBC:
        return _SUBC[text]
    font = R.helv(40, bold=True)
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    words, lines, cur = text.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if d.textlength(trial, font=font) > 900 and cur:
            lines.append(cur)
            cur = wd
        else:
            cur = trial
    lines.append(cur)
    lh = 52
    tw = int(max(d.textlength(li, font=font) for li in lines))
    w, h = tw + 60, lh * len(lines) + 30
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    lay.paste(Image.new("RGBA", (w, h), (6, 12, 20, 190)), (0, 0), rrect_mask((w, h), 18))
    dd = ImageDraw.Draw(lay)
    dd.rectangle((0, 14, 4, h - 14), fill=GOLD + (255,))
    for i, li in enumerate(lines):
        lw = d.textlength(li, font=font)
        dd.text(((w - lw) / 2, 12 + i * lh), li, font=font, fill=WHITE)
    _SUBC[text] = lay
    return lay


def draw_sub(c, t):
    for a, b, text in SUBS:
        if a <= t < b:
            k = min(prog(t, a, 0.1), 1.0 if t < b - 0.1 else prog(b, t, 0.1))
            place(c, sub_layer(text), W / 2, 1650, alpha=k)
            return


def write_srt(path):
    def ts(x):
        ms = int(round(x * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    with open(path, "w", encoding="utf-8") as f:
        for i, (a, b, text) in enumerate(SUBS, 1):
            f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{text}\n\n")


# ---------------------------------------------------------------- rendu
GRAIN = [np.random.default_rng(k).normal(0, 3.2, (H // 2, W // 2, 1)).astype(np.float32) for k in range(8)]
yy, xx = np.mgrid[0:H, 0:W]
VIG = (1 - 0.42 * np.clip(((xx - W / 2) / (W * 0.72)) ** 2 + ((yy - H / 2) / (H * 0.6)) ** 2, 0, 1))[..., None]
VIG = VIG.astype(np.float32)


def frame(t):
    i = max(k for k in range(len(SCENES)) if BOUNDS[k] <= t) if t < DUR else len(SCENES) - 1
    c = scene_frame(i, t)
    nxt = i + 1
    if nxt < len(SCENES) and t > BOUNDS[nxt] - XD and nxt in TRANS:
        p = (t - (BOUNDS[nxt] - XD)) / XD
        nf = scene_frame(nxt, t)
        if TRANS[nxt] == "bubbles":
            c.paste(nf, (0, 0), bubble_mask(p, seed=nxt))
        else:
            c = whip(c, nf, p)
    c = pulse(c, t)
    c = shake(c, t)
    if SUBS_ON:
        draw_sub(c, t)
    a = np.asarray(c.convert("RGB")).astype(np.float32) * VIG
    a += GRAIN[int(t * FPS) % 8].repeat(2, 0).repeat(2, 1)
    if t > DUR - 0.5:
        a *= clamp((DUR - t) / 0.5)
    return np.clip(a, 0, 255).astype(np.uint8)


def mux(video, dst):
    voice = HERE / "sources" / "voix-off-lola.mp3"
    bed = HERE / "sources" / "musique.wav"
    sfx = HERE / "sources" / "bruitages.wav"
    d = int(V * 1000)
    fc = (f"[1:a]adelay={d}|{d},highpass=f=90,equalizer=f=250:t=q:w=1:g=-1.5,equalizer=f=3500:t=q:w=1.2:g=2,"
          "acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=2,"
          "aecho=0.8:0.5:28|41:0.10|0.07,"                       # légère pièce : la voix ne sonne pas « sèche »
          f"pan=stereo|c0=c0|c1=c0,apad=whole_dur={DUR},asplit=2[v][key];"
          "[2:a]volume=0.45[m];"
          "[m][key]sidechaincompress=threshold=0.03:ratio=3.5:attack=20:release=300[md];"
          "[3:a]volume=0.5[fx];"
          "[v][md][fx]amix=inputs=3:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(voice), "-i", str(bed),
                    "-i", str(sfx), "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-t", str(DUR), "-movflags", "+faststart", str(dst)], check=True)


def main():
    if "--stills" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--stills") + 1:]] if len(sys.argv) > 2 else \
            [1.2, 2.5, 3.3, 4.2, 5.0, 8.2, 10.0, 12.0, 16.0, 17.0, 18.6, 20.6, 22.8, 25.4, 28.6, 31.6, 34.4,
             37.2, 38.6, 44.6, 48.0, 54.3, 57.0]
        for t in ts:
            Image.fromarray(frame(t)).save(OUT / f"apercu-{t:04.1f}s.png")
        return
    write_srt(OUT / "splash-party-60s.srt")
    name = "splash-party-60s-sous-titres" if SUBS_ON else "splash-party-60s"
    silent = OUT / f".{name}-video.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
           str(silent)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for n in range(N):
        proc.stdin.write(frame(n / FPS).tobytes())
        if n % 150 == 0:
            print(f"{n}/{N}", flush=True)
    proc.stdin.close()
    proc.wait()
    mux(silent, OUT / f"{name}.mp4")
    silent.unlink()
    print("OK", OUT / f"{name}.mp4")


if __name__ == "__main__":
    main()
