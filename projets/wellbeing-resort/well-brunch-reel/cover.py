#!/usr/bin/env python3
"""Couverture du Reel « Well Brunch » (1080x1920).

Tout l'essentiel tient dans la zone centrale 3:4 (1080x1440, de y=240 à y=1680),
celle que la grille du profil Instagram affiche.
Usage : python3 cover.py  -> rendu/couverture-reel.jpg + rendu/couverture-apercu-grille.jpg
"""
from PIL import Image, ImageDraw, ImageFilter

import render as R

W, H = R.W, R.H
GRID_TOP, GRID_BOT = (H - 1440) // 2, (H + 1440) // 2  # 240 -> 1680


def cover():
    c = R.BG["table"].copy()
    c.alpha_composite(Image.new("RGBA", (W, H), R.INK + (110,)))
    # halo doré derrière la question
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((W / 2 - 560, 380, W / 2 + 560, 980), fill=(140, 98, 24, 110))
    c.alpha_composite(glow.filter(ImageFilter.GaussianBlur(130)))

    R.place(c, R.LOGO, W / 2, 360, scale=0.62)
    R.place(c, R.text_layer("PAR QUOI", R.anton(250)), W / 2, 640)
    R.place(c, R.text_layer("COMMENCER ?", R.anton(176), gold=True), W / 2, 850)
    R.gold_rule(c, W / 2, 985, 520, 1.0)

    photo = R.framed(R.kb_crop("table", 0.0, 1.0, 1.0, out_w=1000))
    R.place(c, photo, W / 2, 1215)

    R.place(c, R.text_layer("WELL BRUNCH", R.anton(124), gold=True, tracking=4), W / 2, 1510)
    R.place(c, R.text_layer("TOUS LES SAMEDIS  ·  12H – 18H30", R.helv(38, bold=True), tracking=2),
            W / 2, 1610)
    # motif art déco hors zone grille, visible seulement dans le Reel plein écran
    c.alpha_composite(R.DECO, (-90, H - R.DECO.height - 40))
    return Image.fromarray(R.finish(c))


if __name__ == "__main__":
    img = cover()
    img.save(R.OUT / "couverture-reel.jpg", quality=94)
    # aperçu : couverture plein écran + recadrage grille 3:4, côte à côte
    grid = img.crop((0, GRID_TOP, W, GRID_BOT))
    s = 0.5
    prev = Image.new("RGB", (int(W * s) * 2 + 40, int(H * s)), (245, 245, 245))
    prev.paste(img.resize((int(W * s), int(H * s))), (0, 0))
    prev.paste(grid.resize((int(W * s), int(1440 * s))), (int(W * s) + 40, int((H - 1440) * s / 2)))
    prev.save(R.OUT / "couverture-apercu-grille.jpg", quality=88)
    print("OK", R.OUT / "couverture-reel.jpg")
