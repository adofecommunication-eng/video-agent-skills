#!/usr/bin/env python3
"""Visuels de stories Well Brunch (1080x1920), même charte que le Reel.

Zones de sécurité story : rien d'important au-dessus de y=250 ni sous y=1580
(barre de progression, nom du compte, champ de réponse).
Usage : python3 stories/stories.py -> stories/*.jpg / *.png
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import render as R  # noqa: E402

W, H = R.W, R.H


def base(bg, dark=110, glow_y=(360, 960)):
    c = R.BG[bg].copy()
    c.alpha_composite(Image.new("RGBA", (W, H), R.INK + (dark,)))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((W / 2 - 560, glow_y[0], W / 2 + 560, glow_y[1]), fill=(140, 98, 24, 110))
    c.alpha_composite(glow.filter(ImageFilter.GaussianBlur(130)))
    return c


def dashed_box(c, box, label):
    """Emplacement réservé à un sticker (sondage / lien), en pointillés or discrets."""
    d = ImageDraw.Draw(c)
    x0, y0, x1, y1 = box
    for x in range(x0, x1, 28):
        d.line((x, y0, min(x + 14, x1), y0), fill=R.GOLD + (150,), width=2)
        d.line((x, y1, min(x + 14, x1), y1), fill=R.GOLD + (150,), width=2)
    for y in range(y0, y1, 28):
        d.line((x0, y, x0, min(y + 14, y1)), fill=R.GOLD + (150,), width=2)
        d.line((x1, y, x1, min(y + 14, y1)), fill=R.GOLD + (150,), width=2)
    R.place(c, R.text_layer(label, R.helv(30, bold=True), fill=(225, 205, 160), shadow=False, tracking=2),
            (x0 + x1) / 2, (y0 + y1) / 2)


def story_vendredi():
    """Vendredi 12h–13h30 : rappel + sondage « par quoi commencer ? » + lien vers le Reel."""
    c = base("buffet")
    R.place(c, R.LOGO, W / 2, 315, scale=0.42)
    R.place(c, R.text_layer("DEMAIN,", R.anton(150)), W / 2, 495)
    R.place(c, R.text_layer("PAR QUOI", R.anton(200)), W / 2, 690)
    R.place(c, R.text_layer("COMMENCER ?", R.anton(150), gold=True), W / 2, 885)
    photo = R.framed(R.kb_crop("buffet", 0.0, 1.05, 1.05, out_w=900))
    R.place(c, photo, W / 2, 1170)
    R.place(c, R.text_layer("SAMEDI  ·  12H – 18H30  ·  PASS 10.000 FCFA", R.helv(34, bold=True), tracking=1),
            W / 2, 1395)
    # y 1440–1580 laissé libre pour le sticker sondage / lien
    return c


def story_samedi_matin():
    """Samedi 9h–10h : dernier appel avec les numéros."""
    c = base("group", glow_y=(300, 900))
    R.place(c, R.LOGO, W / 2, 315, scale=0.42)
    R.place(c, R.text_layer("AUJOURD'HUI", R.anton(100), gold=True, tracking=4), W / 2, 485)
    R.place(c, R.text_layer("ON VOUS ATTEND", R.anton(140)), W / 2, 615)
    R.place(c, R.text_layer("DÈS 12H !", R.anton(210), gold=True), W / 2, 800)
    photo = R.framed(R.kb_crop("group", 0.0, 1.0, 1.0, out_w=940))
    R.place(c, photo, W / 2, 1135)
    R.place(c, R.text_layer("RÉSERVEZ  :", R.helv(34, bold=True), tracking=4), W / 2, 1400)
    R.place(c, R.text_layer("07 47 79 95 07  ·  05 66 92 33 91", R.anton(78), gold=True), W / 2, 1470)
    R.place(c, R.text_layer("COCODY RIVIERA 3  ·  ROUTE M'BADON", R.helv(30, bold=True), tracking=2),
            W / 2, 1550)
    return c


def sticker_en_direct():
    """Sticker PNG transparent à poser sur les stories en direct du brunch."""
    lab = R.text_layer("WELL BRUNCH", R.anton(64), fill=R.INK, shadow=False, tracking=3)
    sub = R.text_layer("EN CE MOMENT AU WELLBEING RESORT", R.helv(22, bold=True), fill=R.INK, shadow=False,
                       tracking=2)
    w = max(lab.width, sub.width) + 90
    h = 170
    face = R.gradient_fill((w, h), R.GOLD_STOPS).convert("RGBA")
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius=26, fill=255)
    face.putalpha(m)
    # point « en direct »
    ImageDraw.Draw(face).ellipse((34, 52, 60, 78), fill=(200, 30, 30, 255))
    face.alpha_composite(lab, ((w - lab.width) // 2 + 20, -18))
    face.alpha_composite(sub, ((w - sub.width) // 2 + 20, 76))
    out = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    sh.paste(Image.new("RGBA", (w, h), (0, 0, 0, 140)), (20, 28), m)
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    out.alpha_composite(face, (20, 20))
    return out


if __name__ == "__main__":
    for name, fn in [("story-vendredi-rappel", story_vendredi), ("story-samedi-matin", story_samedi_matin)]:
        Image.fromarray(R.finish(fn())).save(HERE / f"{name}.jpg", quality=94)
    sticker_en_direct().save(HERE / "sticker-en-direct.png")
    print("OK")
