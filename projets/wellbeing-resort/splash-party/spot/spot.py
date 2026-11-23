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
INTRO = 8.0  # ouverture : montage nerveux sur les vidéos de la fête de la mousse au WBR
W, H, FPS, DUR = 1080, 1920, 30, 60.0 + INTRO
N = int(DUR * FPS)
V = INTRO + 2.0  # la voix démarre après l'ouverture et 2 s sur les yeux
FRAMES_DIR = HERE / ".images" / "frames"          # images extraites des vidéos (régénérées si absentes)


def _extract(src, dst, extra=""):
    if dst.exists() and any(dst.iterdir()):
        return
    dst.mkdir(parents=True, exist_ok=True)
    vf = "scale=1080:1920:flags=lanczos" + extra
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vf", vf, "-q:v", "2", str(dst / "f%04d.jpg")],
                   check=True)


_extract(HERE / "sources" / "video-piscine-wbr.mov", FRAMES_DIR)
_extract(HERE / "sources" / "video-foule-mousse-wbr.mp4", FRAMES_DIR.parent / "frames2", ",unsharp=5:5:0.6")
_extract(HERE / "sources" / "video-fete-mousse-wbr-2.mp4", FRAMES_DIR.parent / "frames3", ",unsharp=5:5:0.8")

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


# ---------------------------------------------------------------- vidéos réelles du Wellbeing Resort
FRAMES2_DIR = FRAMES_DIR.parent / "frames2"   # sources/video-foule-mousse-wbr.mp4 (273 images)
VIDS = {"piscine": (FRAMES_DIR, 230), "foule": (FRAMES2_DIR, 273), "fete": (FRAMES_DIR.parent / "frames3", 839)}
_VCACHE = {}


def _vframe(name, i):
    key = (name, i)
    if key not in _VCACHE:
        if len(_VCACHE) > 40:
            _VCACHE.pop(next(iter(_VCACHE)))
        d, n = VIDS[name]
        _VCACHE[key] = grade(Image.open(d / f"f{int(clamp(i, 1, n)):04d}.jpg"), contrast=1.15, sat=1.12)
    return _VCACHE[key]


def vid(name, ts):
    """Image de la vidéo `name` à ts secondes ; fondu entre images voisines (ralentis fluides)."""
    f = ts * 30 + 1
    i = int(math.floor(f))
    a = f - i
    im = _vframe(name, i)
    if a > 0.2:
        im = Image.blend(im, _vframe(name, i + 1), a)
    return im.convert("RGBA")


def ramp(t, t0, segs):
    """Rampe de vitesse : segs = [(durée vidéo-montage, vitesse), ...] -> temps source depuis 0."""
    lt, src = t - t0, 0.0
    for d, sp in segs:
        if lt <= d:
            return src + lt * sp
        src += d * sp
        lt -= d
    return src + lt * segs[-1][1]


def zoomed(im, z, cx=0.5, cy=0.5):
    if z <= 1.001:
        return im
    big = im.resize((int(W * z), int(H * z)), Image.BILINEAR)
    ox, oy = int((big.width - W) * cx), int((big.height - H) * cy)
    return big.crop((ox, oy, ox + W, oy + H))


# ---------------------------------------------------------------- typographie cinétique
_GLYPHS = {}


def glyphs(text, font_size, gold=False, tracking=4, face=WHITE):
    key = (text, font_size, gold, tracking, face)
    if key in _GLYPHS:
        return _GLYPHS[key]
    font = F_A(font_size)
    out, x = [], 0.0
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    for ch in text:
        w = d.textlength(ch, font=font)
        lay = None if ch == " " else bloom(tl(ch, font, gold=gold, fill=face), 12, 0.35)
        out.append((lay, x + w / 2))
        x += w + tracking
    res = (out, x - tracking)
    _GLYPHS[key] = res
    return res


def kinetic(c, text, size, cx, cy, t, t0, stagger=0.035, gold=False, tracking=4, alpha=1.0, mode="drop"):
    """Lettres qui arrivent une à une (chute avec rebond, ou zoom depuis la caméra)."""
    if t < t0 - 0.02:
        return
    gl, total = glyphs(text, size, gold, tracking)
    x0 = cx - total / 2
    for k, (lay, xc) in enumerate(gl):
        if lay is None:
            continue
        p = prog(t, t0 + k * stagger, 0.32)
        if p <= 0:
            continue
        if mode == "drop":
            e = back_out(p, 1.8)
            place(c, lay, x0 + xc, cy - 160 * (1 - e), alpha=clamp(p * 3) * alpha, angle=(1 - e) * (-18 if k % 2 else 18))
        else:
            place(c, lay, x0 + xc, cy, alpha=clamp(p * 3) * alpha, scale=1 + 2.2 * (1 - ease_out(p)))


def rgb_split(c, amount):
    s = int(round(amount))
    if s < 1:
        return c
    a = np.asarray(c.convert("RGB"))
    out = a.copy()
    out[:, s:, 0] = a[:, :-s, 0]
    out[:, :-s, 2] = a[:, s:, 2]
    return Image.fromarray(out).convert("RGBA")


def outline(im, width=10, color=WHITE):
    a = im.getchannel("A").point(lambda v: 255 if v > 60 else 0)
    big = a.filter(ImageFilter.MaxFilter(width * 2 + 1)).filter(ImageFilter.GaussianBlur(1.2))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.paste(Image.new("RGBA", im.size, color + (255,)), (0, 0), big)
    out.alpha_composite(im)
    return out


MISS_BG = grade(Image.open(HERE / "elements" / "miss-freeze-fond.jpg"))
MISS_FG = outline(Image.open(HERE / "elements" / "miss-freeze.png").convert("RGBA"), 9)
MISS_HEAD = (322, 590)

# ---------------------------------------------------------------- séquences
def s0_cold(c, t):
    """0 – 2,06 : ouverture à froid. Format cinéma, les yeux de la fillette, lente avancée."""
    p = prog(t, INTRO, CUTS[0] - INTRO)
    c.alpha_composite(crop_fill(PHOTO, view(1180, 965, 2000 / 260 * (1 + 0.08 * p))).convert("RGBA"))
    veil(c, int(255 * (1 - prog(t, INTRO + 0.15, 0.9))))
    letterbox(c, 1)


def s1_count(c, t):
    """2,06 – 4,46 : TROIS (la foule) · DEUX (les pieds dans l'eau) · UN (les yeux)."""
    k = 0 if t < CUE["deux"] else 1 if t < CUE["un"] else 2
    t0 = [CUE["trois"], CUE["deux"], CUE["un"]][k]
    p = prog(t, t0, 1.0)
    if k == 0:
        img = zoomed(vid("foule", 1.6 + (t - t0) * 0.35), 1.35 + 0.08 * p, 0.45, 0.55)
    elif k == 1:
        img = zoomed(vid("piscine", 6.3 + (t - t0) * 0.4), 1.5 + 0.08 * p, 0.75, 0.85)
    else:
        img = crop_fill(PHOTO, view(1180, 962, 2000 / 230 * (1 + 0.05 * p))).convert("RGBA")
    c.alpha_composite(img)
    veil(c, 80)
    slam(c, T[str(3 - k)], W / 2, H / 2, t, t0, big=1.5, dur=0.16)
    flash(c, t, t0, 0.18, 0.5)
    letterbox(c, 1 - ease_in_out(prog(t, CUE["splash"] - 0.25, 0.25)))
    foam_burst(c, t, CUE["splash"] - 0.18, seed=11)


def text_behind(t, t0, dur, title_alpha=1.0, z0=1.02, z1=1.2, y_title=880, **kw):
    """Travelling sur la photo avec le titre glissé DERRIÈRE les fillettes."""
    p = ease_in_out(prog(t, t0, dur))
    z = z0 + (z1 - z0) * p
    cx, cy = kw.get("x0", 700) + (kw.get("x1", 820) - kw.get("x0", 700)) * p, kw.get("y0", 1080) + (kw.get("y1", 1000) - kw.get("y0", 1080)) * p
    bg = crop_fill(PHOTO_BLUR, view(cx, cy, 1 + (z - 1) * 0.65)).convert("RGBA")
    fg = FG.resize((W, H), Image.LANCZOS, box=view(cx, cy, z))
    return bg, fg


def s2_hero(c, t):
    """4,46 – 10,3 : chute ! Canon à mousse au ralenti puis accéléré, date, invitation ;
    puis zoom traversant vers la photo, titre SPLASH PARTY derrière les fillettes."""
    if t < CUE["party"] - 0.35:
        ts = ramp(t, CUE["splash"], [(0.9, 0.3), (1.2, 1.6), (9, 1.0)])
        c.alpha_composite(zoomed(vid("foule", ts), 1.12 - 0.08 * prog(t, CUE["splash"], 1.0)))
        grad_bottom(c, 900, 200)
        foam_burst(c, t, CUE["splash"] - 0.18, seed=11)
        a1 = fade_out_after(t, CUE["samedi"] - 0.3)
        kinetic(c, "SPLASH !", 250, W / 2, 760, t, CUE["splash"] + 0.02, stagger=0.03, mode="zoom", alpha=a1)
        droplets(c, t, CUE["splash"] + 0.05, W / 2, 860, n=90, seed=3)
        kinetic(c, "SAMEDI 05 DÉC. 2026", 104, W / 2, 1150, t, CUE["samedi"], stagger=0.03)
        reveal(c, T["wbr"], W / 2, 1290, t, CUE["wbr"])
    else:
        bg, fg = text_behind(t, CUE["party"] - 0.35, CUTS[2] - CUE["party"] + 0.35)
        c.alpha_composite(bg)
        veil(c, 35)
        slam(c, shining(T["titre1"], t, CUE["party"]), W / 2, 300, t, CUE["party"], big=1.8, dur=0.16)
        slam(c, shining(T["titre2"], t, CUE["party"] + 0.25), W / 2, 495, t, CUE["party"] + 0.25, big=1.8, dur=0.16)
        c.alpha_composite(fg)
        light_leak(c, t, CUE["party"] + 0.2, 1.4)


def s3_footage(c, t):
    """10,3 – 15,1 : la vraie piscine du WBR ; ralenti sur les pieds qui éclaboussent."""
    ts = ramp(t, CUTS[2], [(3.0, 1.0), (9, 0.45)])
    img = vid("piscine", 1.6 + ts)
    c.alpha_composite(zoomed(img, 1.02 + 0.06 * prog(t, CUTS[2], 4.8)))
    grad_bottom(c, 900, 190)
    kinetic(c, "08H – 18H", 170, W / 2, 1140, t, CUE["heures"] + 0.15, stagger=0.04)
    reveal(c, T["journee"], W / 2, 1290, t, CUE["heures"] + 1.2)
    kinetic(c, "POUR PETITS ET GRANDS", 84, W / 2, 1400, t, CUE["petits"], stagger=0.025)


def s4_programme(c, t):
    """15,1 – 26,5 : le programme, en coupes rapides sur les vraies images."""
    if t < CUE["piscine"] - 0.05:
        c.alpha_composite(zoomed(vid("foule", 0.6 + (t - CUTS[3]) * 0.5), 1.3).filter(ImageFilter.GaussianBlur(8)))
        veil(c, 110, (0, 20, 40))
        kinetic(c, "AU PROGRAMME", 140, W / 2, H / 2, t, CUE["auprog"], stagger=0.03, mode="zoom")
    elif t < CUE["miss"] - 0.05:
        c.alpha_composite(zoomed(vid("foule", 3.4 + (t - CUE["piscine"]) * 0.8), 1.08))
        grad_bottom(c, 900, 220)
        kinetic(c, "PISCINE", 190, W / 2, 1220, t, CUE["piscine"], stagger=0.04)
        kinetic(c, "& BAIN DE MOUSSE", 96, W / 2, 1380, t, CUE["piscine"] + 0.4, stagger=0.025, gold=True)
    elif t < CUE["danses"] - 0.05:
        miss_scene(c, t)
    elif t < CUE["karaoke"] - 0.05:
        c.alpha_composite(zoomed(vid("foule", 1.5 + (t - CUE["danses"]) * 1.0), 1.15, 0.3, 0.5))
        grad_bottom(c, 900, 200)
        kinetic(c, "CONCOURS", 170, W / 2, 1180, t, CUE["danses"], stagger=0.035)
        kinetic(c, "DE DANSES", 170, W / 2, 1360, t, CUE["danses"] + 0.3, stagger=0.035, gold=True)
    elif t < CUE["billard"] - 0.05:
        c.alpha_composite(zoomed(vid("foule", 6.0 + (t - CUE["karaoke"]) * 0.9), 1.1))
        veil(c, 70, (0, 10, 30))
        kinetic(c, "KARAOKÉ", 210, W / 2, 1000, t, CUE["karaoke"], stagger=0.04, gold=True, mode="zoom")
        eq_bars(c, t, beat_pulse(t), cy=1450, hmax=220 * clamp((t - CUE["karaoke"]) * 3))
    elif t < CUE["dj"] - 0.05:
        words = [("BILLARD", CUE["billard"]), ("BABY-FOOT", CUE["babyfoot"]), ("JEUX", CUE["jeux"])]
        shots = [lambda: crop_fill(PHOTO, view(1300, 600, 2.2)).convert("RGBA"),
                 lambda: zoomed(vid("foule", 4.4 + (t - CUE["babyfoot"]) * 1.2), 1.4, 0.7, 0.4),
                 lambda: crop_fill(PHOTO, view(700, 650, 1.9)).convert("RGBA")]
        for i, (wd, t0) in enumerate(words):
            nxt = words[i + 1][1] if i + 1 < len(words) else 99
            if t0 - 0.05 <= t < nxt - 0.05 or (i == 0 and t < t0):
                c.alpha_composite(shots[i]())
                veil(c, 90, (0, 15, 35))
                kinetic(c, wd, 190, W / 2, H / 2, t, t0, stagger=0.03, mode="zoom")
                flash(c, t, t0, 0.15, 0.4)
    else:
        bp = beat_pulse(t)
        c.alpha_composite(zoomed(vid("foule", 0.2 + (t - CUE["dj"]) * 1.1), 1.08 + 0.03 * bp))
        veil(c, 90, (0, 10, 30))
        if bp > 0.7:  # stroboscope sur les temps forts
            c.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(110 * bp))))
        place(c, VINYL.rotate(-t * 220 % 360, resample=Image.BICUBIC), W / 2, 700, scale=0.75 + 0.03 * bp)
        slam(c, T["dj"], W / 2, 1150, t, CUE["dj"] + 0.4, big=1.5)
        reveal(c, T["toutjour"], W / 2, 1290, t, CUE["dj"] + 1.0)
        eq_bars(c, t, bp, cy=1600, hmax=220)


MISS_Z, MISS_C = 1.6, (480, 900)          # cadrage serré sur la jeune femme


def _miss_view(im, z):
    """Recadre l'image arrêtée sur la jeune femme (zoom z autour de MISS_C)."""
    w, h = W / z, H / z
    x0 = clamp(MISS_C[0] - w / 2, 0, W - w)
    y0 = clamp(MISS_C[1] - h / 2, 0, H - h)
    return im.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + w, y0 + h)), (x0, y0)


def miss_scene(c, t):
    """Image arrêtée : la scène se fige, la jeune femme se détache (contour blanc),
    MISS SPLASH passe derrière elle façon couverture de magazine, la couronne descend sur sa tête."""
    t0 = CUE["miss"]
    if t < t0 + 0.2:   # quelques images de mouvement avant le gel
        c.alpha_composite(vid("foule", 7.75 + (t - (t0 - 0.05))))
        flash(c, t, t0 + 0.15, 0.25, 0.8)
        return
    k = ease_out(prog(t, t0 + 0.2, 0.5))
    z = 1 + (MISS_Z - 1) * k + 0.04 * prog(t, t0 + 0.7, 1.3)
    bg, (x0, y0) = _miss_view(MISS_BG.convert("RGBA"), z)
    c.alpha_composite(bg.filter(ImageFilter.GaussianBlur(9 * k)))
    veil(c, int(150 * k), (0, 10, 25))
    hx, hy = (MISS_HEAD[0] - x0) * z, (MISS_HEAD[1] - y0) * z
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).polygon([(hx - 70, 0), (hx + 70, 0), (hx + 480, 1700), (hx - 480, 1700)],
                                 fill=(255, 220, 150, int(110 * k)))
    c.alpha_composite(glow.filter(ImageFilter.GaussianBlur(50)))
    kinetic(c, "MISS", 280, 800, 760, t, t0 + 0.35, stagger=0.05, gold=True)
    kinetic(c, "SPLASH", 190, 800, 990, t, t0 + 0.6, stagger=0.04)
    fg, _ = _miss_view(MISS_FG, z)
    c.alpha_composite(fg)
    kc = prog(t, t0 + 0.75, 0.5)
    if kc > 0:
        place(c, CROWN, hx + 10, -200 + (hy - 120 + 200) * ease_out(kc), scale=0.75, angle=6 * (1 - kc) * math.sin(t * 9))
    sparkle_y = hy - 120
    droplets(c, t, t0 + 1.25, hx, sparkle_y, n=50, seed=41)


def s5_prix(c, t):
    """26,5 – 32,8 : le ticket or ENTRÉE 5.000 F sur la foule au ralenti."""
    c.alpha_composite(zoomed(vid("foule", 2.0 + (t - CUTS[4]) * 0.3), 1.2).filter(ImageFilter.GaussianBlur(7)))
    veil(c, 140, (0, 12, 28))
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
    kinetic(c, "ENFANT & ADULTE", 96, W / 2, 1110, t, CUE["enfant"], stagger=0.025)
    reveal(c, T["rafr"], W / 2, 1240, t, CUE["rafr"])
    kinetic(c, "ACCÈS À LA PISCINE", 84, W / 2, 1350, t, CUE["acces"], stagger=0.025, gold=True)


def s6_food(c, t):
    """32,8 – 36,0 : nourriture à commander sur place."""
    c.alpha_composite(vid("piscine", 0.3 + (t - CUTS[5]) * 0.5).filter(ImageFilter.GaussianBlur(10)))
    veil(c, 130, (10, 8, 4))
    reveal(c, T["faims"], W / 2, 820, t, CUE["faims"])
    kinetic(c, "NOURRITURE", 170, W / 2, 980, t, CUE["nourriture"], stagger=0.035)
    kinetic(c, "À COMMANDER SUR PLACE", 86, W / 2, 1130, t, CUE["nourriture"] + 0.6, stagger=0.02, gold=True)
    light_leak(c, t, CUE["nourriture"], 1.6, color=(255, 190, 110), alpha=110)


def s7_emotion(c, t):
    """36,0 – 39,6 : révélation émotionnelle. La mise au point se fait sur les sourires."""
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
    """39,6 – 45,9 : réservation sur la foule au ralenti ; les chiffres tombent dans l'eau."""
    c.alpha_composite(zoomed(vid("foule", 5.0 + (t - CUTS[7]) * 0.35), 1.15))
    veil(c, 150, (0, 14, 32))
    bubbles(c, t, n=30, seed=16, alpha=0.6)
    reveal(c, T["resa"], W / 2, 520, t, CUE["resa"], dur=0.5)
    xs = [210, 365, 540, 715, 870]
    for i, t0 in enumerate(CUE["nums"]):
        if t < t0 - 0.05:
            continue
        p = prog(t, t0 - 0.05, 0.3)
        place(c, T_NUM[i], xs[i], 820 - 500 * (1 - back_out(p, 1.6)), alpha=clamp(p * 3), scale=0.62)
        if p > 0.9 and t < t0 + 0.6:
            rr = (t - t0) * 300
            ImageDraw.Draw(c).ellipse((xs[i] - rr, 920 - rr * 0.25, xs[i] + rr, 920 + rr * 0.25),
                                      outline=(230, 250, 255, int(200 * clamp(1 - rr / 180))), width=4)
    reveal(c, T["tel2"], W / 2, 1060, t, CUE["nums"][-1] + 0.8)


def finale_card(c, t, t0):
    c.alpha_composite(zoomed(vid("foule", 0.4 + (t - t0) * 0.3), 1.25).filter(ImageFilter.GaussianBlur(12)))
    veil(c, 175, (0, 10, 24))
    bubbles(c, t, n=40, seed=21, alpha=0.6)
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
    """45,9 – 60 : titre derrière les fillettes (travelling), « PLOUF ! », carte finale."""
    if t < CUE["plouf"]:
        bg, fg = text_behind(t, CUTS[8], CUE["plouf"] - CUTS[8], z0=1.25, z1=1.02, x0=820, x1=740, y0=980, y1=1060)
        c.alpha_composite(bg)
        veil(c, 30)
        slam(c, shining(T["titre1"], t, CUTS[8] + 0.2), W / 2, 300, t, CUTS[8], big=1.6)
        slam(c, shining(T["titre2"], t, CUTS[8] + 0.4), W / 2, 495, t, CUTS[8] + 0.2, big=1.6)
        c.alpha_composite(fg)
        grad_bottom(c, 650, 220)
        reveal(c, T["fin_date"], W / 2, 1500, t, CUE["fin"] + 1.1)
        reveal(c, T["fin_adr"], W / 2, 1570, t, CUE["fin"] + 3.0)
        foam_burst(c, t, CUE["plouf"] - 0.12, cy=H * 0.55, dur=0.5, seed=31)
    else:
        finale_card(c, t, CUE["plouf"] + 0.35)
        foam_burst(c, t, CUE["plouf"] - 0.12, cy=H * 0.55, dur=0.5, seed=31)
        a = 1 - prog(t, CUE["plouf"] + 0.9, 0.4)
        kinetic(c, "PLOUF !", 300, W / 2, H / 2, t, CUE["plouf"] + 0.03, stagger=0.03, mode="zoom", alpha=a)
        droplets(c, t, CUE["plouf"] + 0.05, W / 2, 1000, n=140, seed=33)


# ---------------------------------------------------------------- ouverture : la fête de la mousse au WBR
BEAT0 = V + 2.46 - 8 * 0.5 * 4          # grille à 120 BPM alignée sur « SPLASH »
INTRO_BEATS = [round(BEAT0 + 0.5 * k, 3) for k in range(40) if 0 < BEAT0 + 0.5 * k < INTRO]
# (temps source dans video-fete-mousse-wbr-2.mp4, vitesse, zoom) ; une entrée par coupe, coupes sur les temps
INTRO_SHOTS = [(25.2, 0.45, 1.05), (3.5, 1.0, 1.08), (0.0, 1.0, 1.12), (13.6, 1.0, 1.0), (18.4, 1.0, 1.06),
               (14.5, 0.8, 1.1), (5.5, 1.0, 1.0), (8.0, 0.45, 1.12), (21.4, 1.0, 1.05), (16.5, 1.0, 1.1),
               (19.5, 1.0, 1.05), (25.0, 0.3, 1.0)]
INTRO_CUTS = [0.0] + [b for i, b in enumerate(INTRO_BEATS) if i in (1, 3, 4, 5, 7, 8, 9, 11, 12, 13, 14)]


def s_intro(c, t):
    """0 – 8 s : montage nerveux, une coupe par temps fort, ralentis sur la mousse ; sortie au blanc puis noir."""
    i = max(k for k, b in enumerate(INTRO_CUTS) if b <= t)
    src, sp, z = INTRO_SHOTS[min(i, len(INTRO_SHOTS) - 1)]
    lt = t - INTRO_CUTS[i]
    c.alpha_composite(zoomed(vid("fete", src + lt * sp), z + 0.05 * lt))
    if i == 0:
        veil(c, int(255 * (1 - prog(t, 0.0, 0.35))))
    flash(c, t, INTRO_CUTS[i], 0.1, 0.35)
    grad_bottom(c, 700, 150)
    kinetic(c, "WELLBEING RESORT", 120, W / 2, 1300, t, INTRO_BEATS[1], stagger=0.03, gold=True,
            alpha=1 - prog(t, INTRO_BEATS[7], 0.2))
    kinetic(c, "ORGANISE", 96, W / 2, 1440, t, INTRO_BEATS[3], stagger=0.04, alpha=1 - prog(t, INTRO_BEATS[7], 0.2))
    if t > INTRO_BEATS[-1] - 0.1:  # coup de blanc puis noir avant les yeux
        k = prog(t, INTRO_BEATS[-1] - 0.1, 0.12)
        c.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * k))))
        if t > INTRO_BEATS[-1] + 0.05:
            c.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 255)))


SCENES = [s_intro, s0_cold, s1_count, s2_hero, s3_footage, s4_programme, s5_prix, s6_food, s7_emotion, s8_resa, s9_final]
BOUNDS = [0.0, INTRO] + CUTS[:-1] + [DUR]
TRANS = {4: "zoom", 5: "whip", 6: "zoom", 7: "bubbles", 8: "bubbles", 9: "zoom", 10: "whip"}
XD = 0.34
# coupes rapides internes au programme : zoom traversant aussi
INNER_CUTS = [CUE["piscine"] - 0.05, CUE["danses"] - 0.05, CUE["karaoke"] - 0.05, CUE["billard"] - 0.05,
              CUE["dj"] - 0.05]


def scene_frame(i, t):
    c = Image.new("RGBA", (W, H), INK + (255,))
    SCENES[i](c, t)
    return c


def zoom_through(cur, nxt, p):
    """Zoom traversant : on fonce dans l'image, la suivante arrive depuis l'avant."""
    if p < 0.5:
        q = ease_in_out(p * 2)
        im = zoomed(cur, 1 + 1.6 * q)
        acc = Image.blend(im, zoomed(cur, 1 + 1.9 * q), 0.5)
    else:
        q = ease_in_out((p - 0.5) * 2)
        im = zoomed(nxt, 1 + 0.8 * (1 - q))
        acc = Image.blend(im, zoomed(nxt, 1 + 1.0 * (1 - q)), 0.5)
    return acc


def whip(c, nxt, p):
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


GLITCH = IMPACTS + [CUE["auprog"], CUE["piscine"], CUE["danses"], CUE["karaoke"], CUE["billard"], CUE["babyfoot"],
                    CUE["jeux"], CUE["dj"] + 0.4]


def glitch_amount(t):
    a = 0.0
    for g in GLITCH:
        if 0 <= t - g < 0.15:
            a = max(a, 14 * (1 - (t - g) / 0.15))
    return a


def pulse(c, t):
    bp = beat_pulse(t) if t < INTRO - 0.05 or CUE["splash"] < t < CUTS[6] or CUTS[7] < t else 0
    if bp < 0.05:
        return c
    c = zoomed(c, 1 + 0.02 * bp)
    c.alpha_composite(Image.new("RGBA", (W, H), (255, 235, 200, int(26 * bp))))
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
        kind = TRANS[nxt]
        if kind == "bubbles":
            c.paste(nf, (0, 0), bubble_mask(p, seed=nxt))
        elif kind == "zoom":
            c = zoom_through(c, nf, p)
        else:
            c = whip(c, nf, p)
    for ic in INNER_CUTS:  # zooms traversants entre les activités du programme
        if ic - 0.18 <= t < ic:
            p = (t - ic + 0.18) / 0.36
            c = zoomed(c, 1 + 1.4 * ease_in_out(p * 2) * 0.5)
        elif ic <= t < ic + 0.18:
            p = (t - ic) / 0.18
            c = zoomed(c, 1 + 0.6 * (1 - ease_out(p)))
    c = pulse(c, t)
    c = shake(c, t)
    c = rgb_split(c, glitch_amount(t))
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
    write_srt(OUT / "splash-party-spot.srt")
    name = "splash-party-spot-sous-titres" if SUBS_ON else "splash-party-spot"
    silent = OUT / f".{name}-video.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-b:v", "8M", "-maxrate", "10M", "-bufsize", "16M", "-pix_fmt", "yuv420p",
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
