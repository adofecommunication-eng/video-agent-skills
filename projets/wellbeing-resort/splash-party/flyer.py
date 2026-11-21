#!/usr/bin/env python3
"""Flyer « Splash Party » (1500x1500), samedi 21 novembre 2026.

Mise en page dans le style demandé par le client (références Robert's Hôtel) :
fond blanc chaud, photo qui bord à droite et se fond en blanc vers la gauche,
titre fort à gauche, filet or, bouton or, bandeau sombre d'infos en bas.
Charte Wellbeing Resort conservée : Anton (titres, prix, numéros), Helvetica Neue
(infos ; TeX Gyre Heros tant que le fichier n'est pas fourni), noir chaud + or.
Usage : python3 flyer.py -> rendu/flyer-splash-party-21-novembre-2026.jpg
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "well-brunch-reel"))
import render as R  # noqa: E402  (polices, dégradé or, logo, calques texte)

OUT = HERE / "rendu"
OUT.mkdir(exist_ok=True)
SRC = Image.open(HERE / "sources" / "flyer-splash-party-original.jpg").convert("RGB")
W = H = 1500
PAPER = (250, 248, 244)
INK = (30, 24, 18)          # noir chaud lisible sur fond clair
GREY = (70, 62, 54)
LIGHT = (245, 240, 230)
FOOT = 1325                 # haut du bandeau d'infos

# zone de la photo d'origine sans aucun texte ni badge : l'enfant au bonnet + les deux enfants
PHOTO = (360, 700, 1084, 1560)


def tl(text, font, **kw):
    kw.setdefault("shadow", False)
    return R.text_layer(text, font, **kw)


def put_left(c, layer, x, cy):
    """Aligne à gauche (le calque a 40 px de marge interne)."""
    c.alpha_composite(layer, (int(x - 40), int(cy - layer.height / 2)))


def photo_layer():
    x0 = 380
    w, h = W - x0, FOOT
    full_h = int(w * (PHOTO[3] - PHOTO[1]) / (PHOTO[2] - PHOTO[0]))
    ph = SRC.resize((w, full_h), Image.LANCZOS, box=PHOTO)
    ph = ph.crop((0, full_h - h, w, full_h))  # garder le bas (les enfants)
    ph = ImageEnhance.Sharpness(ph).enhance(1.25).convert("RGBA")
    # fondu vers le blanc : large à gauche, léger en haut
    ax = np.clip((np.linspace(0, 1, w) - 0.05) / 0.45, 0, 1) ** 1.6
    ay = np.clip(np.linspace(0, 1, h) / 0.12, 0, 1)
    ph.putalpha(Image.fromarray((np.outer(ay, ax) * 255).astype(np.uint8), "L"))
    return ph, x0


def gold_button(text, font, h=112, pad=44, radius=14):
    lab = tl(text, font, fill=INK)
    w = lab.width - 80 + 2 * pad
    b = R.gradient_fill((w, h), R.GOLD_STOPS).convert("RGBA")
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius=radius, fill=255)
    b.putalpha(m)
    b.alpha_composite(lab, ((w - lab.width) // 2, (h - lab.height) // 2 + 3))
    out = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    out.paste(Image.new("RGBA", (w, h), (80, 56, 10, 90)), (20, 30), m)
    out = out.filter(ImageFilter.GaussianBlur(10))
    out.alpha_composite(b, (20, 20))
    return out


def gold_icon(mask):
    f = R.gradient_fill(mask.size, R.GOLD_STOPS).convert("RGBA")
    f.putalpha(mask)
    return f


def icon_pin(size=46):
    s = size * 4
    m = Image.new("L", (s, int(s * 1.35)), 0)
    d = ImageDraw.Draw(m)
    d.ellipse((0, 0, s, s), fill=255)
    d.polygon([(s * 0.13, s * 0.72), (s * 0.87, s * 0.72), (s / 2, s * 1.35)], fill=255)
    d.ellipse((s * 0.32, s * 0.32, s * 0.68, s * 0.68), fill=0)
    return gold_icon(m.resize((size, int(size * 1.35)), Image.LANCZOS))


def flyer():
    c = Image.new("RGBA", (W, H), PAPER + (255,))
    ph, x0 = photo_layer()
    c.alpha_composite(ph, (x0, 0))
    veil = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(veil).rectangle((0, 0, 600, FOOT), fill=PAPER + (190,))
    c.alpha_composite(veil.filter(ImageFilter.GaussianBlur(60)))
    d = ImageDraw.Draw(c)

    X = 75
    # logo + signature
    logo = R.LOGO.resize((int(R.LOGO.width * 0.42), int(R.LOGO.height * 0.42)), Image.LANCZOS)
    c.alpha_composite(logo, (X - 22, 40))
    put_left(c, tl("WELLBEING RESORT ORGANISE", R.helv(24, bold=True), fill=GREY, tracking=7), X, 228)

    # titre
    put_left(c, tl("SPLASH", R.anton(205), fill=INK), X, 375)
    put_left(c, tl("PARTY", R.anton(205), gold=True, tracking=4), X, 580)
    d.rectangle((X, 705, X + 120, 709), fill=R.GOLD + (255,))

    # date
    put_left(c, tl("SAMEDI 21 NOVEMBRE 2026", R.anton(62), fill=INK), X, 775)
    put_left(c, tl("DE 08H À 18H", R.helv(30, bold=True), gold=True, tracking=8), X, 842)

    # animations (capitales espacées, comme les références)
    for i, line in enumerate(["PISCINE, MISS SPLASH, KARAOKÉ,", "CONCOURS DE DANSES, BILLARD,",
                              "BABY-FOOT, AMBIANCE DJ ET JEUX."]):
        put_left(c, tl(line, R.helv(25, bold=True), fill=GREY, tracking=4), X, 912 + i * 40)

    # tarif
    c.alpha_composite(gold_button("ENTRÉE 5.000 F  ·  ENFANT & ADULTE", R.anton(50)), (X - 20, 1045))
    put_left(c, tl("+ 01 RAFRAÎCHISSEMENT, ACCÈS PISCINE INCLUS", R.helv(22, bold=True), fill=INK, tracking=3),
             X, 1192)
    put_left(c, tl("COCKTAIL 1.000 F  ·  POPCORN 500 F", R.anton(44), fill=INK, tracking=1), X, 1244)
    put_left(c, tl("NOURRITURE À COMMANDER SUR PLACE", R.helv(20, bold=True), fill=GREY, tracking=3), X, 1291)

    # bandeau d'infos
    d.rectangle((0, FOOT, W, H), fill=(26, 22, 17, 255))
    d.rectangle((0, FOOT, W, FOOT + 4), fill=R.GOLD + (255,))
    cy = FOOT + (H - FOOT) // 2 + 2
    p = icon_pin(46)
    c.alpha_composite(p, (X, cy - p.height // 2))
    put_left(c, tl("Cocody Riviera 3,", R.helv(30, bold=True), fill=LIGHT), X + 72, cy - 21)
    put_left(c, tl("route M'Badon, Abidjan", R.helv(30, bold=True), fill=LIGHT), X + 72, cy + 21)
    d.rectangle((640, cy - 48, 642, cy + 48), fill=R.GOLD + (200,))
    put_left(c, tl("RÉSERVATION", R.helv(20, bold=True), gold=True, tracking=6), 700, cy - 30)
    put_left(c, tl("07 47 79 95 07  /  05 66 92 33 91", R.anton(56), fill=LIGHT), 700, cy + 16)
    return c


if __name__ == "__main__":
    flyer().convert("RGB").save(OUT / "flyer-splash-party-21-novembre-2026.jpg", quality=94)
    print("OK")
