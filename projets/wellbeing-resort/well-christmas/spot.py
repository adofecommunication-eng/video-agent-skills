#!/usr/bin/env python3
"""Spot motion design « WELL CHRISTMAS » — Wellbeing Resort — 30 s, 9:16, 1080x1920, 30 i/s.

Construit à partir du flyer (sources/flyer-well-christmas.webp) et de la voix off
(sources/voix-off-lola.mp3), dans l'esprit des références du client : personnage détouré
sur fond de couleur, objets qui flottent, transitions « éclaboussure », typographie
cinétique sur fond noir à particules, cartes qui glissent, carte logo finale.
Charte WBR : Anton (titres, chiffres), Helvetica Neue (infos, sous-titres ; TeX Gyre
Heros tant que le fichier n'est pas fourni), noir chaud + or, touches de rouge Noël.

Usage :
  python3 decoupe.py          # une fois : détourage des éléments du flyer
  python3 musique.py          # musique originale + bruitages calés sur CUE
  python3 spot.py [--subs] [--stills]
"""
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "well-brunch-reel"))
import render as R  # noqa: E402  (polices Anton/Helvetica, dégradé or, logo WBR, calques texte)

OUT = HERE / "rendu"
OUT.mkdir(exist_ok=True)
W, H, FPS, DUR = 1080, 1920, 30, 30.0
N = int(DUR * FPS)
VOICE_DELAY = 0.25

INK = R.INK
WHITE = (255, 255, 255)
RED = (178, 16, 26)
RED_DARK = (92, 6, 12)
BLUE = (0, 120, 205)
BLUE_DARK = (0, 52, 120)
GOLD = R.GOLD

# ---------------------------------------------------------------- calage voix (s, délai inclus)
# Mesuré sur l'enveloppe de la voix off ; chaque texte clé apparaît sur son mot.
V = VOICE_DELAY
CUE = {
    "cette": 0.14 + V, "noel": 0.72 + V, "fete": 1.20 + V,
    "aubord": 1.95 + V, "piscine": 2.42 + V,
    "wbr": 3.47 + V, "wellchristmas": 5.16 + V, "pourtous": 6.41 + V,
    "date": 8.27 + V, "heures": 9.14 + V,
    "prog": [11.36 + V, 12.02 + V, 12.40 + V, 12.70 + V],
    "tombola": 14.20 + V, "prix": 15.04 + V, "prix_fin": 15.95 + V,
    "agagner": 16.34 + V, "nuitee": 17.09 + V, "natation": 19.24 + V,
    "etqui": 21.08 + V, "miss": 21.58 + V, "an2027": 23.66 + V,
    "entree": 25.00 + V, "gratuite": 25.62 + V,
    "adresse": 26.44 + V,
}
# coupes : juste avant la phrase qui ouvre la séquence suivante
CUTS = [2.15, 3.62, 8.40, 11.50, 14.32, 16.45, 21.15, 25.12, 26.55]
IMPACTS = [CUE["noel"], CUE["piscine"], CUE["wellchristmas"], CUE["date"], CUE["prix_fin"],
           CUE["miss"], CUE["gratuite"]]

clamp, prog, ease_out, ease_in_out, back_out = R.clamp, R.prog, R.ease_out, R.ease_in_out, R.back_out


# ---------------------------------------------------------------- utilitaires
def tl(text, font, **kw):
    return R.text_layer(text, font, **kw)


def place(c, layer, cx, cy, alpha=1.0, scale=1.0, angle=0.0):
    if alpha <= 0.002:
        return
    if angle:
        layer = layer.rotate(angle, resample=Image.BICUBIC, expand=True)
    R.place(c, layer, cx, cy, alpha=alpha, scale=scale)


def slam(c, layer, cx, cy, t, t0, big=1.6, dur=0.14, alpha=1.0):
    R.slam(c, layer, cx, cy, t, t0, big=big, dur=dur, alpha=alpha)


def slide(c, layer, cx, cy, t, t0, dx=0, dy=0, dur=0.35, alpha=1.0):
    """Glisse depuis (dx, dy) avec un léger dépassement."""
    if t < t0:
        return
    p = prog(t, t0, dur)
    e = back_out(p, 1.2)
    place(c, layer, cx + dx * (1 - e), cy + dy * (1 - e), alpha=clamp(p * 3) * alpha)


def pop(c, layer, cx, cy, t, t0, dur=0.3, alpha=1.0):
    if t < t0:
        return
    p = prog(t, t0, dur)
    place(c, layer, cx, cy, alpha=clamp(p * 4) * alpha, scale=max(0.01, back_out(p, 2.2)))


def rrect(size, fill, radius=24):
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=fill)
    return im


def gold_rrect(size, radius=24):
    g = R.gradient_fill(size, R.GOLD_STOPS).convert("RGBA")
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    g.putalpha(m)
    return g


def shadowed(layer, blur=18, off=14, opacity=150):
    pad = blur * 2
    out = Image.new("RGBA", (layer.width + 2 * pad, layer.height + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", layer.size, (0, 0, 0, opacity))
    sh.putalpha(layer.getchannel("A").point(lambda v: v * opacity // 255))
    out.alpha_composite(sh, (pad, pad + off))
    out = out.filter(ImageFilter.GaussianBlur(blur))
    out.alpha_composite(layer, (pad, pad))
    return out


# ---------------------------------------------------------------- éléments du flyer
ANIM = Image.open(HERE / "elements" / "animateur.png").convert("RGBA")
ANIM = ANIM.resize((int(ANIM.width * 1.25), int(ANIM.height * 1.25)), Image.LANCZOS)
BOULE = Image.open(HERE / "elements" / "boule.png").convert("RGBA")
LOGO = R.LOGO


def boule(scale=1.0, angle=0.0):
    b = BOULE.resize((int(BOULE.width * scale), int(BOULE.height * scale)), Image.LANCZOS)
    return b.rotate(angle, resample=Image.BICUBIC, expand=True) if angle else b


# ---------------------------------------------------------------- fonds animés
rng = np.random.default_rng(11)
yy, xx = np.mgrid[0:H, 0:W]


def radial(c_in, c_out, cy=0.42, power=1.4):
    d = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * cy) / H) ** 2) / 0.75
    d = np.clip(d, 0, 1) ** power
    a = np.empty((H, W, 3), np.float32)
    for k in range(3):
        a[..., k] = c_in[k] * (1 - d) + c_out[k] * d
    return Image.fromarray(a.astype(np.uint8)).convert("RGBA")


BG_BLACK = radial((40, 30, 16), INK)
BG_RED = radial((205, 32, 40), RED_DARK)
BG_BLUE = radial((40, 170, 235), BLUE_DARK, cy=0.5)

# guirlande de bokeh dorés (3 plans de profondeur)
BOKEH = []
for depth, (n, rmin, rmax, blur) in enumerate([(26, 30, 70, 18), (34, 14, 30, 8), (50, 5, 12, 2)]):
    pts = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(rmin, rmax), rng.uniform(0, 6.28),
            rng.uniform(0.6, 1.8)) for _ in range(n)]
    BOKEH.append((pts, blur, depth))


def bokeh_layer(t, strength=1.0, warm=(255, 205, 110)):
    lay = Image.new("RGBA", (W // 2, H // 2), (0, 0, 0, 0))
    for pts, blur, depth in BOKEH:
        sub = Image.new("RGBA", lay.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(sub)
        drift = t * (8 + depth * 10)
        for x, y, r, ph, sp in pts:
            a = (0.45 + 0.55 * math.sin(ph + t * sp * 2.2)) * 120 * strength
            yy_ = (y - drift) % H
            d.ellipse(((x - r) / 2, (yy_ - r) / 2, (x + r) / 2, (yy_ + r) / 2), fill=warm + (int(a),))
        lay.alpha_composite(sub.filter(ImageFilter.GaussianBlur(blur / 2)) if blur > 2 else sub)
    return lay.resize((W, H), Image.BILINEAR)


SNOW = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(2, 6), rng.uniform(40, 120), rng.uniform(0, 6.28))
        for _ in range(90)]


def snow(c, t, color=(255, 240, 200), alpha=200):
    d = ImageDraw.Draw(c)
    for x, y, r, v, ph in SNOW:
        yy_ = (y + v * t) % H
        xx_ = x + 18 * math.sin(ph + t * 1.3)
        d.ellipse((xx_ - r, yy_ - r, xx_ + r, yy_ + r), fill=color + (alpha,))


RAYS = None


def rays_layer(angle):
    global RAYS
    if RAYS is None:
        s = 2400
        im = Image.new("L", (s, s), 0)
        d = ImageDraw.Draw(im)
        for k in range(18):
            a0 = k * 20
            d.pieslice((0, 0, s, s), a0, a0 + 8, fill=40)
        RAYS = im.filter(ImageFilter.GaussianBlur(6))
    r = RAYS.rotate(angle, resample=Image.BILINEAR)
    r = r.crop(((2400 - W) // 2, (2400 - H) // 2, (2400 + W) // 2, (2400 + H) // 2))
    lay = Image.new("RGBA", (W, H), (255, 214, 120, 0))
    lay.putalpha(r)
    return lay


def bg_black(c, t):
    c.alpha_composite(BG_BLACK)
    c.alpha_composite(bokeh_layer(t, 0.9))
    snow(c, t, alpha=140)


def bg_red(c, t, rays=True):
    c.alpha_composite(BG_RED)
    if rays:
        c.alpha_composite(rays_layer(t * 6))
    c.alpha_composite(bokeh_layer(t, 0.55))
    snow(c, t, color=(255, 255, 255), alpha=150)


def bg_blue(c, t):
    c.alpha_composite(BG_BLUE)
    # reflets d'eau (caustiques) calculés en basse résolution
    sx, sy = np.meshgrid(np.linspace(0, 6, W // 6), np.linspace(0, 10, H // 6))
    v = (np.sin(sx * 2.1 + t * 2.0 + np.sin(sy * 1.7 + t)) + np.sin(sy * 2.6 - t * 1.6 + np.sin(sx * 1.3))) / 2
    v = np.clip((v - 0.55) * 4, 0, 1) * 70
    caust = Image.fromarray(v.astype(np.uint8), "L").resize((W, H), Image.BICUBIC)
    lay = Image.new("RGBA", (W, H), (210, 245, 255, 0))
    lay.putalpha(caust)
    c.alpha_composite(lay)


# ---------------------------------------------------------------- effets
def confetti(c, t, t0, cx, cy, n=90, seed=1, spread=1.0):
    if t < t0 or t > t0 + 2.2:
        return
    r = np.random.default_rng(seed)
    d = ImageDraw.Draw(c)
    dt = t - t0
    cols = [(240, 200, 90), (255, 230, 150), (200, 20, 30), (255, 255, 255), (190, 140, 40)]
    for _ in range(n):
        ang = r.uniform(0, 2 * math.pi)
        sp = r.uniform(500, 1400) * spread
        vx, vy = math.cos(ang) * sp, math.sin(ang) * sp - 500
        x = cx + vx * dt * 0.9
        y = cy + vy * dt * 0.9 + 900 * dt * dt
        w, h = r.uniform(8, 16), r.uniform(14, 26)
        rot = r.uniform(0, 6.28) + dt * r.uniform(4, 12)
        col = cols[int(r.integers(0, len(cols)))]
        a = int(255 * clamp(1.6 - dt / 1.4))
        cw, sw = abs(math.cos(rot)) * w + 2, h
        d.rectangle((x - cw / 2, y - sw / 2, x + cw / 2, y + sw / 2), fill=col + (a,))


def splash(c, t, t0, cx, cy, n=60, seed=3):
    """Gerbe d'eau (gouttes blanches/bleues) pour « piscine »."""
    if t < t0 or t > t0 + 1.4:
        return
    r = np.random.default_rng(seed)
    d = ImageDraw.Draw(c)
    dt = t - t0
    for _ in range(n):
        ang = r.uniform(math.pi * 1.05, math.pi * 1.95)
        sp = r.uniform(600, 1500)
        x = cx + math.cos(ang) * sp * dt
        y = cy + math.sin(ang) * sp * dt + 1600 * dt * dt
        rad = r.uniform(5, 14) * (1 - dt / 1.6)
        a = int(230 * clamp(1.4 - dt))
        d.ellipse((x - rad, y - rad, x + rad, y + rad), fill=(230, 248, 255, a))


def flash(c, t, t0, dur=0.3, strength=0.6, color=(255, 226, 160)):
    p = (t - t0) / dur
    if 0 <= p <= 1:
        c.alpha_composite(Image.new("RGBA", (W, H), color + (int(255 * strength * math.sin(p * math.pi)),)))


def blob_mask(p, cx, cy, seed=0):
    """Masque « éclaboussure » qui grandit de 0 à plein écran (p de 0 à 1)."""
    if p <= 0:
        return None
    r = np.random.default_rng(seed)
    harm = [(k, r.uniform(0.05, 0.16) / (1 + k * 0.3), r.uniform(0, 6.28)) for k in range(3, 9)]
    small = 4
    gy, gx = np.mgrid[0:H // small, 0:W // small]
    dx, dy = gx * small - cx, gy * small - cy
    ang = np.arctan2(dy, dx)
    rad = np.sqrt(dx ** 2 + dy ** 2)
    edge = 1 + sum(a * np.sin(k * ang + ph + p * 3) for k, a, ph in harm)
    R0 = ease_in_out(p) * 2400
    m = (rad < R0 * edge).astype(np.uint8) * 255
    return Image.fromarray(m, "L").resize((W, H), Image.BILINEAR)


# ---------------------------------------------------------------- textes
T = {
    "cette": tl("CETTE ANNÉE,", R.anton(110), tracking=4),
    "noel": tl("NOËL", R.anton(330), gold=True),
    "fete": tl("SE FÊTE…", R.anton(120), tracking=4),
    "aubord": tl("AU BORD DE LA", R.anton(110), tracking=4),
    "piscine": tl("PISCINE !", R.anton(250)),
    "organise": tl("WELLBEING RESORT ORGANISE", R.helv(36, bold=True), tracking=6),
    "well": tl("WELL", R.anton(210), gold=True, tracking=6),
    "christmas": tl("CHRISTMAS", R.anton(210), gold=True, tracking=4),
    "pourtous": tl("LA FÊTE DE NOËL POUR TOUS", R.helv(40, bold=True), fill=INK, shadow=False, tracking=3),
    "24": tl("24", R.anton(520), gold=True),
    "dec": tl("DÉC. 2026", R.anton(170)),
    "heures": tl("10H00 – 18H00", R.anton(96), fill=INK, shadow=False, tracking=2),
    "auprog": tl("AU PROGRAMME", R.helv(40, bold=True), gold=True, tracking=10),
    "atelier": tl("ATELIER TOMBOLA", R.anton(110), tracking=3),
    "agagner": tl("À GAGNER", R.anton(150), gold=True, tracking=6),
    "ou": tl("OU", R.anton(90), gold=True),
    "etqui": tl("ET QUI SERA…", R.anton(100), tracking=4),
    "miss": tl("MISS", R.anton(230), gold=True, tracking=8),
    "wellbeing": tl("WELLBEING", R.anton(190), gold=True, tracking=4),
    "ambass": tl("AMBASSADRICE", R.anton(90), tracking=4),
    "an2027": tl("2027", R.anton(200)),
    "bonus": tl("COURS DE NATATION, GRANDE PIZZA", R.helv(34, bold=True), fill=(235, 225, 200), tracking=2),
    "bonus2": tl("ET PLEIN D'AUTRES GADGETS", R.helv(34, bold=True), fill=(235, 225, 200), tracking=2),
    "lentree": tl("L'ENTRÉE EST", R.anton(130), tracking=4),
    "gratuite": tl("GRATUITE !!!", R.anton(220), gold=True),
    "fin_titre": tl("WELL CHRISTMAS", R.anton(150), gold=True, tracking=4),
    "fin_date": tl("24 DÉC. 2026  ·  10H – 18H", R.helv(42, bold=True), tracking=3),
    "fin_gratuit": tl("ENTRÉE GRATUITE", R.anton(90), fill=INK, shadow=False, tracking=3),
    "fin_adr": tl("COCODY RIVIERA 3, ROUTE M'BADON", R.helv(36, bold=True), tracking=2),
    "fin_tel1": tl("07 47 79 95 07", R.anton(120), gold=True),
    "fin_tel2": tl("05 66 92 33 91", R.anton(84)),
}
PROG = ["PISCINE", "JEUX", "STANDS", "DON DE CADEAUX"]


def chip(text):
    lab = tl(text, R.anton(96), fill=RED, shadow=False, tracking=2)
    w = lab.width - 80 + 110
    b = rrect((w, 150), (255, 255, 255, 255), radius=75)
    ImageDraw.Draw(b).ellipse((34, 57, 70, 93), fill=GOLD + (255,))
    b.alpha_composite(lab, (70 + (w - 70 - lab.width) // 2 - 10, (150 - lab.height) // 2 + 4))
    return shadowed(b, blur=14, off=10, opacity=110)


CHIPS = [chip(p) for p in PROG]


def prize_card(big, small):
    a = tl(big, R.anton(130), fill=INK, shadow=False, tracking=2)
    b = tl(small, R.helv(34, bold=True), fill=(70, 20, 20), shadow=False, tracking=2)
    w = max(a.width, b.width) - 80 + 120
    card = gold_rrect((w, 290), radius=30)
    card.alpha_composite(a, ((w - a.width) // 2, 10))
    card.alpha_composite(b, ((w - b.width) // 2, 190))
    return shadowed(card)


CARD1 = prize_card("1 NUITÉE", "DANS NOTRE RÉSIDENCE HÔTELIÈRE")
CARD2 = prize_card("1 MOIS", "DE COURS DE NATATION")
_TICKETS = {}


def ticket(value):
    if value in _TICKETS:
        return _TICKETS[value]
    w, h = 860, 400
    tk = gold_rrect((w, h), radius=34)
    m = tk.getchannel("A")
    d = ImageDraw.Draw(m)
    for y in (h // 2,):  # encoches latérales
        d.ellipse((-50, y - 50, 50, y + 50), fill=0)
        d.ellipse((w - 50, y - 50, w + 50, y + 50), fill=0)
    tk.putalpha(m)
    dd = ImageDraw.Draw(tk)
    for x in range(90, w - 90, 26):  # pointillés
        dd.line((x, 92, x + 12, 92), fill=INK + (120,), width=3)
    lab = tl("TOMBOLA", R.helv(40, bold=True), fill=INK, shadow=False, tracking=14)
    tk.alpha_composite(lab, ((w - lab.width) // 2, 2))
    val = tl(f"{value} F", R.anton(200), fill=INK, shadow=False)
    tk.alpha_composite(val, ((w - val.width) // 2, 90))
    out = shadowed(tk)
    _TICKETS[value] = out
    return out


def crown(size=260):
    s = size
    m = Image.new("L", (s * 2, int(s * 1.5)), 0)
    d = ImageDraw.Draw(m)
    S = 2 * s
    pts = [(0.05, 0.9), (0.05, 0.3), (0.28, 0.6), (0.5, 0.1), (0.72, 0.6), (0.95, 0.3), (0.95, 0.9)]
    d.polygon([(x * S, y * S * 0.75) for x, y in pts], fill=255)
    for x, y in [(0.05, 0.3), (0.5, 0.1), (0.95, 0.3)]:
        d.ellipse((x * S - 22, y * S * 0.75 - 22, x * S + 22, y * S * 0.75 + 22), fill=255)
    m = m.resize((s, int(s * 0.75)), Image.LANCZOS)
    g = R.gradient_fill(m.size, R.GOLD_STOPS).convert("RGBA")
    g.putalpha(m)
    return shadowed(g, blur=10, off=8)


CROWN = crown()
DECO = R.deco_pattern(W + 180)


# ---------------------------------------------------------------- séquences
def s1_hook(c, t):
    """0 – 2,15 : CETTE ANNÉE, / NOËL / SE FÊTE…"""
    bg_black(c, t)
    # boule qui descend au bout de son fil et se balance
    p = ease_out(prog(t, 0.0, 0.9))
    bx = W / 2 + 70 * math.sin(t * 2.4) * (1 - 0.5 * p)
    by = -200 + 560 * p
    ImageDraw.Draw(c).line((W / 2, 0, bx, by - 110), fill=GOLD + (200,), width=3)
    place(c, boule(1.25, angle=-12 * math.sin(t * 2.4)), bx, by)
    slide(c, T["cette"], W / 2, 690, t, CUE["cette"], dx=-700)
    slam(c, T["noel"], W / 2, 930, t, CUE["noel"], big=1.9, dur=0.16)
    confetti(c, t, CUE["noel"], W / 2, 930, n=60, seed=2, spread=0.8)
    slide(c, T["fete"], W / 2, 1175, t, CUE["fete"], dx=700)


def s2_piscine(c, t):
    """2,15 – 3,62 : AU BORD DE LA / PISCINE ! (la boule plonge)"""
    bg_blue(c, t)
    slide(c, T["aubord"], W / 2, 720, t, CUE["aubord"], dy=-200)
    # la boule tombe et plonge dans l'eau sur « piscine »
    tp = CUE["piscine"]
    if t < tp:
        p = prog(t, CUE["aubord"], tp - CUE["aubord"])
        place(c, boule(1.1, angle=200 * p), W / 2, -150 + (1300 - -150) * p ** 2)
    splash(c, t, tp, W / 2, 1300, n=70, seed=5)
    slam(c, T["piscine"], W / 2, 960, t, tp, big=1.8)
    # vaguelettes concentriques
    if t > tp:
        d = ImageDraw.Draw(c)
        for k in range(3):
            rr = (t - tp - k * 0.18) * 520
            if rr > 0:
                a = int(200 * clamp(1 - rr / 700))
                d.ellipse((W / 2 - rr, 1300 - rr * 0.28, W / 2 + rr, 1300 + rr * 0.28), outline=(230, 250, 255, a),
                          width=6)


def s3_invite(c, t):
    """3,62 – 8,4 : animateur + WELL CHRISTMAS + LA FÊTE DE NOËL POUR TOUS"""
    bg_red(c, t)
    t0 = CUTS[1]
    # boules qui flottent autour (comme les icônes des références)
    for i, (bx, by, sc, ph) in enumerate([(150, 1060, 0.9, 0), (940, 1010, 0.75, 1.7), (130, 1470, 0.6, 3.1),
                                          (960, 1420, 0.85, 4.2)]):
        k = prog(t, t0 + 0.25 + i * 0.12, 0.4)
        if k > 0:
            place(c, boule(sc, angle=15 * math.sin(t * 1.5 + ph)), bx, by + 20 * math.sin(t * 2 + ph),
                  alpha=k, scale=back_out(k, 2))
    # animateur qui surgit par le bas
    k = prog(t, t0 + 0.05, 0.5)
    if k > 0:
        y = 1920 - ANIM.height / 2 + (1 - back_out(k, 1.4)) * 900
        place(c, ANIM, W / 2, y + 6 * math.sin(t * 3))
    slide(c, T["organise"], W / 2, 330, t, CUE["wbr"], dy=-120)
    slam(c, T["well"], W / 2, 520, t, CUE["wellchristmas"], big=1.7)
    slam(c, T["christmas"], W / 2, 700, t, CUE["wellchristmas"] + 0.22, big=1.7)
    confetti(c, t, CUE["wellchristmas"] + 0.22, W / 2, 620, n=110, seed=7)
    # bandeau or « la fête de Noël pour tous »
    k = prog(t, CUE["pourtous"], 0.3)
    if k > 0:
        lab = T["pourtous"]
        band = gold_rrect((lab.width - 80 + 90, 96), radius=48)
        band.alpha_composite(lab, ((band.width - lab.width) // 2, (96 - lab.height) // 2 + 2))
        place(c, shadowed(band, blur=10, off=8), W / 2, 870, alpha=clamp(k * 3), scale=0.6 + 0.4 * back_out(k))


def s4_date(c, t):
    """8,4 – 11,5 : 24 DÉC. 2026 / 10H00 – 18H00"""
    bg_black(c, t)
    slam(c, T["24"], W / 2, 760, t, CUE["date"], big=2.0, dur=0.16)
    confetti(c, t, CUE["date"], W / 2, 760, n=70, seed=9, spread=0.9)
    slide(c, T["dec"], W / 2, 1060, t, CUE["date"] + 0.35, dy=250)
    k = prog(t, CUE["heures"], 0.3)
    if k > 0:
        lab = T["heures"]
        pill = gold_rrect((lab.width - 80 + 100, 150), radius=75)
        pill.alpha_composite(lab, ((pill.width - lab.width) // 2, (150 - lab.height) // 2 + 4))
        place(c, shadowed(pill, blur=12, off=10), W / 2, 1290, alpha=clamp(k * 3), scale=0.5 + 0.5 * back_out(k))


def s5_programme(c, t):
    """11,5 – 14,32 : PISCINE · JEUX · STANDS · DON DE CADEAUX (une carte par mot)"""
    bg_red(c, t, rays=False)
    slide(c, T["auprog"], W / 2, 470, t, CUTS[3] + 0.02, dy=-120)
    for i, ti in enumerate(CUE["prog"]):
        x_from = -900 if i % 2 == 0 else 900
        slide(c, CHIPS[i], W / 2, 680 + i * 200, t, ti - 0.04, dx=x_from, dur=0.32)


def s6_tombola(c, t):
    """14,32 – 16,45 : ATELIER TOMBOLA + ticket 2.000 F qui défile"""
    bg_black(c, t)
    slide(c, T["atelier"], W / 2, 640, t, CUE["tombola"], dy=-160)
    k = prog(t, CUE["tombola"] + 0.25, 0.45)
    if k > 0:
        cp = prog(t, CUE["prix"], CUE["prix_fin"] - CUE["prix"])
        val = int(round(2000 * ease_out(cp) / 100) * 100)
        txt = f"{val // 1000}.{val % 1000:03d}" if val >= 1000 else str(val)
        tk = ticket(txt)
        flip = abs(math.cos((1 - ease_out(k)) * math.pi * 1.5)) if k < 1 else 1.0
        tk = tk.resize((max(2, int(tk.width * flip)), tk.height), Image.BILINEAR)
        pulse = 1 + 0.08 * math.sin(math.pi * prog(t, CUE["prix_fin"], 0.25))
        place(c, tk, W / 2, 1010 + 10 * math.sin(t * 2.5), alpha=clamp(k * 3), scale=pulse, angle=-4)
    flash(c, t, CUE["prix_fin"], 0.3, 0.45)


def s7_gains(c, t):
    """16,45 – 21,15 : À GAGNER / 1 NUITÉE / OU / 1 MOIS DE COURS DE NATATION"""
    bg_red(c, t)
    slam(c, T["agagner"], W / 2, 470, t, CUE["agagner"], big=1.6)
    slide(c, CARD1, W / 2, 790, t, CUE["nuitee"], dx=-1000, dur=0.4)
    pop(c, T["ou"], W / 2, 1010, t, CUE["natation"] - 0.25)
    slide(c, CARD2, W / 2, 1230, t, CUE["natation"], dx=1000, dur=0.4)


def s8_miss(c, t):
    """21,15 – 25,12 : ET QUI SERA… MISS WELLBEING · AMBASSADRICE 2027"""
    bg_black(c, t)
    # projecteur doré
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    a = int(110 * clamp((t - CUE["miss"]) * 3))
    ImageDraw.Draw(glow).polygon([(W / 2 - 80, 0), (W / 2 + 80, 0), (W / 2 + 520, 1250), (W / 2 - 520, 1250)],
                                 fill=(255, 215, 130, a))
    c.alpha_composite(glow.filter(ImageFilter.GaussianBlur(50)))
    slide(c, T["etqui"], W / 2, 420, t, CUE["etqui"], dy=-120)
    k = prog(t, CUE["miss"] - 0.1, 0.45)
    if k > 0:
        place(c, CROWN, W / 2, -200 + (610 + 200) * ease_out(k), angle=8 * (1 - k) * math.sin(t * 8))
    slam(c, T["miss"], W / 2, 830, t, CUE["miss"], big=1.8)
    slam(c, T["wellbeing"], W / 2, 1020, t, CUE["miss"] + 0.25, big=1.6)
    confetti(c, t, CUE["miss"] + 0.2, W / 2, 830, n=90, seed=13)
    slide(c, T["ambass"], W / 2, 1220, t, CUE["an2027"] - 0.55, dx=-800)
    slam(c, T["an2027"], W / 2, 1385, t, CUE["an2027"] + 0.25, big=1.7)
    place(c, T["bonus"], W / 2, 1515, alpha=ease_out(prog(t, CUE["an2027"] + 0.6, 0.3)))
    place(c, T["bonus2"], W / 2, 1560, alpha=ease_out(prog(t, CUE["an2027"] + 0.75, 0.3)))


def s9_gratuit(c, t):
    """25,12 – 26,55 : L'ENTRÉE EST / GRATUITE !!!"""
    bg_red(c, t)
    slide(c, T["lentree"], W / 2, 800, t, CUE["entree"], dy=-200)
    slam(c, T["gratuite"], W / 2, 1010, t, CUE["gratuite"], big=2.1, dur=0.16)
    confetti(c, t, CUE["gratuite"], W / 2, 1010, n=160, seed=17, spread=1.2)
    flash(c, t, CUE["gratuite"], 0.35, 0.6)


def s10_fin(c, t):
    """26,55 – 30 : carte finale."""
    bg_black(c, t)
    lt = t - CUTS[-1]
    c.alpha_composite(DECO, (-90 - int(40 * lt) % 90, H - DECO.height - 40))
    for i, (bx, sc, ph) in enumerate([(150, 0.8, 0.3), (930, 0.95, 1.9)]):
        k = ease_out(prog(lt, 0.1 * i, 0.7))
        by = -150 + 420 * k
        ImageDraw.Draw(c).line((bx, 0, bx, by - 90), fill=GOLD + (190,), width=3)
        place(c, boule(sc, angle=10 * math.sin(t * 2 + ph)), bx, by)
    pop(c, LOGO.resize((int(LOGO.width * 0.6), int(LOGO.height * 0.6)), Image.LANCZOS), W / 2, 330, t,
        CUTS[-1] + 0.05, dur=0.4)
    slam(c, T["fin_titre"], W / 2, 560, t, CUTS[-1] + 0.15, big=1.4)
    place(c, T["fin_date"], W / 2, 675, alpha=ease_out(prog(lt, 0.35, 0.3)))
    k = prog(lt, 0.5, 0.3)
    if k > 0:
        lab = T["fin_gratuit"]
        pill = gold_rrect((lab.width - 80 + 90, 130), radius=65)
        pill.alpha_composite(lab, ((pill.width - lab.width) // 2, (130 - lab.height) // 2 + 4))
        place(c, shadowed(pill, blur=10, off=8), W / 2, 820, alpha=clamp(k * 3), scale=0.6 + 0.4 * back_out(k))
    slide(c, T["fin_adr"], W / 2, 980, t, CUE["adresse"] + 0.6, dy=80)
    t1 = CUE["adresse"] + 0.9
    if t < t1 + 0.5:
        slam(c, T["fin_tel1"], W / 2, 1110, t, t1, big=1.4)
    else:
        place(c, T["fin_tel1"], W / 2, 1110, scale=1 + 0.025 * math.sin((t - t1) * 6))
    place(c, T["fin_tel2"], W / 2, 1230, alpha=ease_out(prog(t, t1 + 0.3, 0.3)))


SCENES = [s1_hook, s2_piscine, s3_invite, s4_date, s5_programme, s6_tombola, s7_gains, s8_miss, s9_gratuit,
          s10_fin]
BOUNDS = [0.0] + CUTS + [DUR]
# transitions entrantes : « blob » = éclaboussure de la couleur de la séquence suivante
TRANS = {1: ("blob", (W / 2, 1300)), 2: ("blob", (W / 2, 1900)), 4: ("blob", (0, 0)), 6: ("blob", (W, 300)),
         8: ("blob", (W / 2, 960))}
XD = 0.32  # durée d'une transition


def scene_frame(i, t):
    c = Image.new("RGBA", (W, H), INK + (255,))
    SCENES[i](c, t)
    return c


def shake(c, t):
    for ti in IMPACTS:
        p = (t - ti) / 0.2
        if 0 <= p <= 1:
            amp = 16 * (1 - p)
            dx, dy = amp * math.sin(p * 37), amp * math.cos(p * 29)
            big = c.resize((int(W * 1.03), int(H * 1.03)), Image.BILINEAR)
            ox, oy = (big.width - W) / 2 + dx, (big.height - H) / 2 + dy
            return big.crop((int(ox), int(oy), int(ox) + W, int(oy) + H))
    return c


# ---------------------------------------------------------------- sous-titres
SUBS_ON = "--subs" in sys.argv
SUBS = [
    (0.39, 2.0, "Cette année, Noël se fête…"), (2.2, 3.4, "au bord de la piscine !"),
    (3.72, 6.5, "Wellbeing Resort vous invite au Well Christmas,"), (6.66, 8.2, "la fête de Noël pour tous."),
    (8.52, 11.4, "Le 24 décembre, de 10h à 18h :"), (11.62, 14.1, "piscine, jeux, stands et don de cadeaux."),
    (14.45, 16.25, "Atelier tombola à 2.000 francs."),
    (16.59, 19.3, "À gagner : une nuitée dans notre résidence hôtelière,"),
    (19.3, 20.95, "ou un mois de cours de natation."), (21.33, 22.4, "Et qui sera Miss Wellbeing,"),
    (22.4, 24.96, "notre ambassadrice pour l'année 2027 ?"), (25.25, 26.31, "L'entrée est gratuite !"),
    (26.69, 29.2, "Wellbeing Resort, Cocody Riviera 3."),
]
_SUB = {}


def draw_sub(c, t):
    for a, b, text in SUBS:
        if a <= t < b:
            if text not in _SUB:
                _SUB[text] = R.sub_layer(text)
            k = min(prog(t, a, 0.1), 1.0 if t < b - 0.1 else prog(b, t, 0.1))
            place(c, _SUB[text], W / 2, 1640, alpha=k)
            return


def write_srt(path):
    def ts(x):
        ms = int(round(x * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    with open(path, "w", encoding="utf-8") as f:
        for i, (a, b, text) in enumerate(SUBS, 1):
            f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{text}\n\n")


# ---------------------------------------------------------------- rendu
def frame(t):
    i = max(k for k in range(len(SCENES)) if BOUNDS[k] <= t) if t < DUR else len(SCENES) - 1
    c = scene_frame(i, t)
    # transition sortante vers la séquence suivante
    nxt = i + 1
    if nxt < len(SCENES) and t > BOUNDS[nxt] - XD:
        p = (t - (BOUNDS[nxt] - XD)) / XD
        kind, center = TRANS.get(nxt, ("cut", None))
        if kind == "blob":
            m = blob_mask(p, *center, seed=nxt)
            if m is not None:
                c.paste(scene_frame(nxt, t), (0, 0), m)
    c = shake(c, t)
    if SUBS_ON:
        draw_sub(c, t)
    a = np.asarray(c.convert("RGB")).astype(np.float32)
    a += np.random.default_rng(int(t * FPS)).normal(0, 2.0, (H // 2, W // 2, 1)).repeat(2, 0).repeat(2, 1)
    if t > DUR - 0.25:
        a *= clamp((DUR - t) / 0.25)
    return np.clip(a, 0, 255).astype(np.uint8)


def mux(video, dst):
    voice = HERE / "sources" / "voix-off-lola.mp3"
    music = HERE / "sources" / "musique-et-bruitages.wav"
    d = int(VOICE_DELAY * 1000)
    fc = (f"[1:a]adelay={d}|{d},highpass=f=90,equalizer=f=3500:t=q:w=1.2:g=2,"
          "acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=2,"
          f"pan=stereo|c0=c0|c1=c0,apad=whole_dur={DUR},asplit=2[v][key];"
          "[2:a]volume=0.55[m];"
          "[m][key]sidechaincompress=threshold=0.03:ratio=3:attack=20:release=300[md];"
          "[v][md]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(voice), "-i", str(music),
                    "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "192k", "-t", str(DUR), "-movflags", "+faststart", str(dst)], check=True)


def main():
    if "--stills" in sys.argv:
        for t in [1.3, 3.0, 6.0, 7.5, 9.9, 13.6, 16.3, 20.5, 24.6, 26.2, 29.0]:
            Image.fromarray(frame(t)).save(OUT / f"apercu-{t:04.1f}s.png")
        return
    write_srt(OUT / "well-christmas-30s.srt")
    name = "well-christmas-30s-sous-titres" if SUBS_ON else "well-christmas-30s"
    silent = OUT / f".{name}-video.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           str(silent)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for n in range(N):
        proc.stdin.write(frame(n / FPS).tobytes())
        if n % 90 == 0:
            print(f"{n}/{N}", flush=True)
    proc.stdin.close()
    proc.wait()
    mux(silent, OUT / f"{name}.mp4")
    silent.unlink()
    print("OK", OUT / f"{name}.mp4")


if __name__ == "__main__":
    main()
