#!/usr/bin/env python3
"""Flyer « Splash Party » aux couleurs de la charte Wellbeing Resort.

Charte (brand/wellbeing-resort/README.md) : noir chaud + or, Anton en principale,
Helvetica Neue en secondaire (TeX Gyre Heros tant que le fichier n'est pas fourni),
photo cerclée d'un filet or sur fond flou assombri, motif art déco.
Source photo : sources/flyer-splash-party-original.jpg (zones sans texte uniquement).
Usage : python3 flyer.py -> rendu/flyer-splash-party-21-novembre-2026.jpg (1410x2000) + version 4:5
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "well-brunch-reel"))
import render as R  # noqa: E402  (polices, dégradé or, logo, calques texte)

OUT = HERE / "rendu"
OUT.mkdir(exist_ok=True)
SRC = Image.open(HERE / "sources" / "flyer-splash-party-original.jpg").convert("RGB")
W, H = 1410, 2000

# zones photo du flyer d'origine sans aucun texte ni badge
PANO = (40, 700, 1330, 1085)     # les deux adultes + l'enfant au bonnet
KIDS = (315, 1100, 1115, 1560)   # les deux enfants aux lunettes


def tl(text, font, **kw):
    return R.text_layer(text, font, **kw)


def place(c, layer, cx, cy, scale=1.0):
    R.place(c, layer, cx, cy, scale=scale)


def framed(box, out_w):
    x0, y0, x1, y1 = box
    out_h = int(out_w * (y1 - y0) / (x1 - x0))
    ph = SRC.resize((out_w, out_h), Image.LANCZOS, box=box)
    return R.framed(ph)


def gold_badge(text, font, pad_x=46, h=150, radius=20):
    lab = tl(text, font, fill=R.INK, shadow=False)
    w = lab.width - 80 + 2 * pad_x
    b = R.gradient_fill((w, h), R.GOLD_STOPS).convert("RGBA")
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius=radius, fill=255)
    b.putalpha(m)
    b.alpha_composite(lab, ((w - lab.width) // 2, (h - lab.height) // 2 + 4))
    return b


def rule(c, cx, cy, width, thick=3):
    ImageDraw.Draw(c).rectangle((cx - width // 2, cy - thick // 2, cx + width // 2, cy + thick // 2),
                                fill=R.GOLD + (255,))


def pin(size=46):
    """Pictogramme de localisation, en or."""
    s = size * 4
    m = Image.new("L", (s, int(s * 1.35)), 0)
    d = ImageDraw.Draw(m)
    d.ellipse((0, 0, s, s), fill=255)
    d.polygon([(s * 0.13, s * 0.72), (s * 0.87, s * 0.72), (s / 2, s * 1.35)], fill=255)
    d.ellipse((s * 0.32, s * 0.32, s * 0.68, s * 0.68), fill=0)
    m = m.resize((size, int(size * 1.35)), Image.LANCZOS)
    face = R.gradient_fill(m.size, R.GOLD_STOPS).convert("RGBA")
    face.putalpha(m)
    return face


def background():
    bg = SRC.crop((0, 640, 1410, 1600)).resize((W // 4, H // 4))
    bg = bg.filter(ImageFilter.GaussianBlur(16)).resize((W, H), Image.BICUBIC)
    c = Image.blend(Image.new("RGB", (W, H), R.INK), bg, 0.30).convert("RGBA")
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((W / 2 - 700, 180, W / 2 + 700, 900), fill=(140, 98, 24, 120))
    c.alpha_composite(glow.filter(ImageFilter.GaussianBlur(160)))
    return c


def finish(c):
    yy, xx = np.mgrid[0:H, 0:W]
    vig = 1 - 0.45 * np.clip(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2, 0, 1)
    a = np.asarray(c.convert("RGB")).astype(np.float32) * vig[..., None]
    a += np.random.default_rng(7).normal(0, 2.0, (H, W, 1))
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def flyer():
    c = background()

    # en-tête
    place(c, R.LOGO, W / 2, 125, scale=0.48)
    place(c, tl("WELLBEING RESORT  ORGANISE", R.helv(30, bold=True), gold=True, tracking=10), W / 2, 262)

    # titre
    place(c, tl("SPLASH", R.anton(225)), W / 2, 395)
    place(c, tl("PARTY", R.anton(225), gold=True, tracking=6), W / 2, 595)

    # date
    rule(c, W / 2, 735, 900, 2)
    place(c, tl("SAMEDI 21 NOVEMBRE 2026", R.anton(90)), W / 2, 795)
    place(c, tl("DE 08H À 18H", R.helv(36, bold=True), gold=True, tracking=8), W / 2, 880)

    # photos
    place(c, framed(PANO, 1310), W / 2, 1125)
    place(c, framed(KIDS, 560), W - 330, 1405)

    # tarif (colonne gauche, à côté des enfants)
    cx = 370
    place(c, tl("ENFANT & ADULTE", R.anton(54), gold=True, tracking=3), cx, 1360)
    place(c, gold_badge("ENTRÉE 5.000 F", R.anton(88), h=132), cx, 1458)
    place(c, tl("+ 01 RAFRAÎCHISSEMENT", R.anton(50)), cx, 1555)

    # infos pratiques
    rule(c, W / 2, 1612, 1200, 2)
    place(c, tl("CE TARIF VOUS DONNE DROIT À LA PISCINE", R.helv(32, bold=True), tracking=2), W / 2, 1652)
    place(c, tl("COCKTAIL 1.000 F   ·   POPCORN 500 F", R.anton(66), gold=True, tracking=2), W / 2, 1716)
    place(c, tl("POSSIBILITÉ DE COMMANDER LA NOURRITURE SUR PLACE", R.helv(26, bold=True), tracking=2),
          W / 2, 1775)

    # activités
    act = dict(fill=(240, 228, 200), tracking=1)
    place(c, tl("PISCINE  ·  MISS SPLASH  ·  KARAOKÉ  ·  CONCOURS DE DANSES", R.helv(30, bold=True), **act),
          W / 2, 1818)
    place(c, tl("BILLARD  ·  BABY-FOOT  ·  AMBIANCE DJ  ·  JEUX", R.helv(30, bold=True), **act), W / 2, 1856)

    # bandeau bas : adresse + réservation
    top = 1888
    c.alpha_composite(Image.new("RGBA", (W, H - top), R.INK + (255,)), (0, top))
    rule(c, W / 2, top, W, 4)
    c.alpha_composite(pin(40), (64, 1918))
    addr = tl("COCODY RIVIERA 3, ROUTE M'BADON", R.helv(28, bold=True), tracking=1)
    c.alpha_composite(addr, (118 - 40, 1946 - addr.height // 2))
    tel = tl("07 47 79 95 07  /  05 66 92 33 91", R.anton(50), gold=True)
    tx = W - 64 - (tel.width - 80) / 2
    place(c, tl("RÉSERVATION", R.helv(22, bold=True), tracking=6), tx, 1920)
    place(c, tel, tx, 1960)
    return c


if __name__ == "__main__":
    img = finish(flyer())
    img.save(OUT / "flyer-splash-party-21-novembre-2026.jpg", quality=94)
    print("OK")
