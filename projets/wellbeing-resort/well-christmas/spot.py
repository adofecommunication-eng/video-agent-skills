#!/usr/bin/env python3
"""Spot motion design « WELL CHRISTMAS » (v2, esprit de Noël) — Wellbeing Resort — 30 s, 9:16, 30 i/s.

Palette demandée par le client pour Noël : rouge, blanc, or (le noir ne sert plus que
d'ombre). Polices de la charte WBR : Anton (titres, chiffres), Helvetica Neue (infos,
sous-titres ; TeX Gyre Heros tant que le fichier n'est pas fourni).

Idées signature :
  - un paquet cadeau rouge au ruban d'or s'ouvre sur « NOËL » ; un autre explose sur « GRATUITE !!! »
  - guirlande lumineuse qui scintille, flocons en 3 profondeurs, velours rouge / blanc neige
  - titres en or en relief traversés d'un reflet brillant
  - bonnet de Père Noël sur « PISCINE », page de calendrier de l'Avent pour la date,
    étiquettes cadeau suspendues pour le programme, rideau de velours pour Miss Wellbeing
  - transitions en ruban d'or

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

WHITE = (255, 255, 255)
CREAM = (255, 250, 242)
RED = (190, 18, 30)
RED_DEEP = (110, 6, 14)
RED_DARK = (70, 4, 10)
GOLD = R.GOLD
GOLD_DARK = (120, 82, 20)
INK = (40, 10, 12)          # « noir » de Noël : bordeaux très sombre

# ---------------------------------------------------------------- calage voix (s, délai inclus)
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
CUTS = [2.15, 3.62, 8.40, 11.50, 14.32, 16.45, 21.15, 25.12, 26.55]
IMPACTS = [CUE["noel"], CUE["piscine"], CUE["wellchristmas"] + 0.22, CUE["date"], CUE["prix_fin"],
           CUE["miss"], CUE["gratuite"]]

clamp, prog, ease_out, ease_in_out, back_out = R.clamp, R.prog, R.ease_out, R.ease_in_out, R.back_out
yy, xx = np.mgrid[0:H, 0:W]


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


def slide(c, layer, cx, cy, t, t0, dx=0, dy=0, dur=0.35, alpha=1.0):
    if t < t0:
        return
    p = prog(t, t0, dur)
    e = back_out(p, 1.2)
    place(c, layer, cx + dx * (1 - e), cy + dy * (1 - e), alpha=clamp(p * 3) * alpha)


def pop(c, layer, cx, cy, t, t0, dur=0.3, alpha=1.0):
    if t < t0:
        return
    p = prog(t, t0, dur)
    place(c, layer, cx, cy, alpha=clamp(p * 4) * alpha, scale=back_out(p, 2.2))


def rrect_mask(size, radius):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    return m


def gold_fill(size, mask=None):
    g = R.gradient_fill(size, R.GOLD_STOPS).convert("RGBA")
    if mask is not None:
        g.putalpha(mask)
    return g


def shadowed(layer, blur=18, off=14, opacity=150, color=(30, 0, 4)):
    pad = blur * 2
    out = Image.new("RGBA", (layer.width + 2 * pad, layer.height + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", layer.size, color + (0,))
    sh.putalpha(layer.getchannel("A").point(lambda v: v * opacity // 255))
    out.alpha_composite(sh, (pad, pad + off))
    out = out.filter(ImageFilter.GaussianBlur(blur))
    out.alpha_composite(layer, (pad, pad))
    return out


# ---------------------------------------------------------------- typo en relief + reflet
def text3d(text, font, face="gold", side=GOLD_DARK, depth=12, tracking=0, outline=None):
    """Lettres en relief : extrusion vers le bas, face or / blanche / rouge, ombre douce."""
    m = tl(text, font, fill=WHITE, shadow=False, tracking=tracking).getchannel("A")
    pad = depth + 30
    w, h = m.width + 2 * pad, m.height + 2 * pad
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sh.paste(Image.new("RGBA", m.size, (30, 0, 4, 150)), (pad + 6, pad + depth + 14), m)
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    for i in range(depth, 0, -1):
        k = 0.55 + 0.45 * (1 - i / depth)
        col = tuple(int(v * k) for v in side) + (255,)
        out.paste(Image.new("RGBA", m.size, col), (pad, pad + i), m)
    if outline:
        ol = m.filter(ImageFilter.MaxFilter(7))
        out.paste(Image.new("RGBA", m.size, outline + (255,)), (pad, pad), ol)
    if face == "gold":
        bb = m.getbbox() or (0, 0, m.width, m.height)
        f = Image.new("RGBA", m.size, (0, 0, 0, 0))
        f.paste(R.gradient_fill((m.width, bb[3] - bb[1]), R.GOLD_STOPS).convert("RGBA"), (0, bb[1]))
    else:
        f = Image.new("RGBA", m.size, face + (255,))
    f.putalpha(m)
    out.alpha_composite(f, (pad, pad))
    return out


def shine(layer, p, width=0.10, strength=0.85):
    """Reflet diagonal qui traverse le calque (p de 0 à 1)."""
    if not 0 < p < 1:
        return layer
    w, h = layer.size
    gx = np.arange(w)[None, :] / w + np.arange(h)[:, None] / h * 0.35
    pos = -0.25 + 1.6 * p
    band = np.exp(-((gx - pos) / width) ** 2) * strength
    a = np.asarray(layer.getchannel("A")).astype(np.float32) / 255 * band * 255
    hl = Image.new("RGBA", (w, h), (255, 252, 235, 0))
    hl.putalpha(Image.fromarray(a.astype(np.uint8), "L"))
    out = layer.copy()
    out.alpha_composite(hl)
    return out


def shining(layer, t, t0, period=2.6):
    """Reflet qui repasse régulièrement après l'apparition."""
    if t < t0 + 0.1:
        return layer
    p = ((t - t0 - 0.1) % period) / 0.9
    return shine(layer, p) if p < 1 else layer


# ---------------------------------------------------------------- éléments du flyer
ANIM = Image.open(HERE / "elements" / "animateur.png").convert("RGBA")
ANIM = ANIM.resize((int(ANIM.width * 1.25), int(ANIM.height * 1.25)), Image.LANCZOS)


def sticker_outline(im, width=14, color=WHITE):
    a = im.getchannel("A").point(lambda v: 255 if v > 40 else 0)
    big = a.filter(ImageFilter.MaxFilter(width * 2 + 1)).filter(ImageFilter.GaussianBlur(1.5))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.paste(Image.new("RGBA", im.size, color + (255,)), (0, 0), big)
    out.alpha_composite(im)
    return out


pad_im = Image.new("RGBA", (ANIM.width + 40, ANIM.height + 20), (0, 0, 0, 0))
pad_im.alpha_composite(ANIM, (20, 20))
ANIM_ST = shadowed(sticker_outline(pad_im, 12), blur=20, off=16, opacity=140)
BOULE = Image.open(HERE / "elements" / "boule.png").convert("RGBA")
LOGO = R.LOGO


def boule(scale=1.0, angle=0.0):
    b = BOULE.resize((int(BOULE.width * scale), int(BOULE.height * scale)), Image.LANCZOS)
    return b.rotate(angle, resample=Image.BICUBIC, expand=True) if angle else b


# ---------------------------------------------------------------- décors de Noël dessinés
def radial(c_in, c_out, cy=0.42, power=1.4):
    d = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * cy) / H) ** 2) / 0.75
    d = np.clip(d, 0, 1) ** power
    a = np.empty((H, W, 3), np.float32)
    for k in range(3):
        a[..., k] = c_in[k] * (1 - d) + c_out[k] * d
    return Image.fromarray(a.astype(np.uint8)).convert("RGBA")


def snowflake(size, color=WHITE, alpha=255, width=None):
    s = size * 2
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    w = width or max(2, size // 9)
    c = s / 2
    for k in range(6):
        a = math.radians(k * 60)
        x1, y1 = c + math.cos(a) * size * 0.9, c + math.sin(a) * size * 0.9
        d.line((c, c, x1, y1), fill=color + (alpha,), width=w)
        for f in (0.45, 0.7):
            bx, by = c + math.cos(a) * size * f, c + math.sin(a) * size * f
            for sgn in (-1, 1):
                b = a + sgn * math.radians(45)
                d.line((bx, by, bx + math.cos(b) * size * 0.25, by + math.sin(b) * size * 0.25),
                       fill=color + (alpha,), width=w)
    return im


def velvet_bg():
    base = radial((214, 36, 46), RED_DARK, cy=0.40)
    # motif damassé discret de flocons
    pat = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fl = snowflake(46, (255, 220, 200), 26, width=4)
    for j, y in enumerate(range(-60, H + 120, 230)):
        for x in range(-60 + (115 if j % 2 else 0), W + 120, 230):
            pat.alpha_composite(fl, (x, y))
    base.alpha_composite(pat)
    return base


BG_VELVET = velvet_bg()
BG_SNOW = radial(CREAM, (232, 218, 198), cy=0.45, power=1.8)
BG_BLUE = radial((50, 175, 238), (0, 52, 120), cy=0.5)

rng = np.random.default_rng(11)
FLAKES = []
for depth, (n, smin, smax, blur, speed) in enumerate([(14, 40, 70, 6, 260), (26, 16, 30, 1, 150), (60, 4, 9, 0, 80)]):
    for _ in range(n):
        size = int(rng.uniform(smin, smax))
        FLAKES.append((depth, rng.uniform(0, W), rng.uniform(0, H), speed * rng.uniform(0.8, 1.2),
                       rng.uniform(0, 6.28), size, blur))
FLAKE_SPRITES = {}


def flake_sprite(size, blur, color):
    key = (size, blur, color)
    if key not in FLAKE_SPRITES:
        sp = snowflake(size, color, 230) if size > 12 else None
        if sp is None:
            sp = Image.new("RGBA", (size * 2, size * 2), (0, 0, 0, 0))
            ImageDraw.Draw(sp).ellipse((size / 2, size / 2, size * 1.5, size * 1.5), fill=color + (230,))
        if blur:
            sp = sp.filter(ImageFilter.GaussianBlur(blur))
        FLAKE_SPRITES[key] = sp
    return FLAKE_SPRITES[key]


def snowfall(c, t, color=WHITE, layers=(0, 1, 2), alpha=1.0):
    for depth, x, y, sp, ph, size, blur in FLAKES:
        if depth not in layers:
            continue
        yy_ = (y + sp * t) % (H + 200) - 100
        xx_ = x + 30 * math.sin(ph + t * 1.2)
        spr = flake_sprite(size, blur, color)
        if depth == 0:
            spr = spr.rotate((t * 40 + ph * 50) % 360, resample=Image.BILINEAR)
        if alpha < 1:
            spr = spr.copy()
            spr.putalpha(spr.getchannel("A").point(lambda v: int(v * alpha)))
        c.alpha_composite(spr, (int(xx_ - spr.width / 2), int(yy_ - spr.height / 2)))


# guirlande lumineuse (fil or en chaînette, ampoules rouge / or / blanc qui scintillent)
def build_garland():
    wire = Image.new("RGBA", (W, 300), (0, 0, 0, 0))
    d = ImageDraw.Draw(wire)
    pts = [(x, 40 + 120 * (1 - ((x - W / 2) / (W / 2 + 60)) ** 2)) for x in range(-60, W + 61, 6)]
    d.line(pts, fill=(170, 125, 40, 255), width=4)
    bulbs = []
    cols = [(255, 60, 60), (255, 210, 110), (255, 250, 235)]
    for i, x in enumerate(range(-20, W + 40, 78)):
        y = 40 + 120 * (1 - ((x - W / 2) / (W / 2 + 60)) ** 2)
        bulbs.append((x, y + 26, cols[i % 3], i))
    return wire, bulbs


GARLAND_WIRE, BULBS = build_garland()


def garland(c, t, y0=0):
    glow = Image.new("RGBA", (W // 2, 160), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    c.alpha_composite(GARLAND_WIRE, (0, y0))
    d = ImageDraw.Draw(c)
    for x, y, col, i in BULBS:
        tw = 0.55 + 0.45 * math.sin(t * 5 + i * 1.7)
        gd.ellipse(((x - 34) / 2, (y - 34) / 2, (x + 34) / 2, (y + 34) / 2), fill=col + (int(170 * tw),))
        d.rectangle((x - 6, y0 + y - 24, x + 6, y0 + y - 14), fill=(190, 150, 60, 255))
        d.ellipse((x - 11, y0 + y - 16, x + 11, y0 + y + 16), fill=tuple(int(v * (0.75 + 0.25 * tw)) for v in col) + (255,))
    c.alpha_composite(glow.filter(ImageFilter.GaussianBlur(9)).resize((W, 320), Image.BILINEAR), (0, y0))


def bokeh(c, t, color=(255, 210, 120), n=26, alpha=110, seed=4):
    r = np.random.default_rng(seed)
    lay = Image.new("RGBA", (W // 3, H // 3), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for _ in range(n):
        x, y, rad, ph = r.uniform(0, W), r.uniform(0, H), r.uniform(18, 60), r.uniform(0, 6.28)
        a = (0.5 + 0.5 * math.sin(ph + t * 2)) * alpha
        y = (y - t * 25) % H
        d.ellipse(((x - rad) / 3, (y - rad) / 3, (x + rad) / 3, (y + rad) / 3), fill=color + (int(a),))
    c.alpha_composite(lay.filter(ImageFilter.GaussianBlur(5)).resize((W, H), Image.BILINEAR))


def bg_velvet(c, t, lights=True):
    c.alpha_composite(BG_VELVET)
    bokeh(c, t)
    snowfall(c, t, layers=(1, 2))
    if lights:
        garland(c, t)


def bg_snow(c, t, lights=True):
    c.alpha_composite(BG_SNOW)
    bokeh(c, t, color=(230, 170, 60), alpha=70, seed=8)
    snowfall(c, t, color=(220, 175, 90), layers=(1, 2), alpha=0.8)
    if lights:
        garland(c, t)


def front_snow(c, t, color=WHITE):
    snowfall(c, t, color=color, layers=(0,), alpha=0.9)


# paquet cadeau rouge au ruban d'or
def gift_parts(w=560, h=460):
    body = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    a = np.zeros((h, w, 4), np.uint8)
    shade = np.linspace(1.0, 0.72, w)[None, :] * np.linspace(1.0, 0.85, h)[:, None]
    for k, v in enumerate((200, 22, 34)):
        a[..., k] = (v * shade).astype(np.uint8)
    a[..., 3] = 255
    body = Image.fromarray(a, "RGBA")
    rib = gold_fill((90, h))
    body.alpha_composite(rib, (w // 2 - 45, 0))
    lw, lh = w + 60, 130
    lid = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    la = np.zeros((lh, lw, 4), np.uint8)
    shade = np.linspace(1.0, 0.75, lw)[None, :]
    for k, v in enumerate((214, 28, 40)):
        la[..., k] = (v * shade).astype(np.uint8)
    la[..., 3] = 255
    lid = Image.fromarray(la, "RGBA")
    lid.alpha_composite(gold_fill((90, lh)), (lw // 2 - 45, 0))
    # nœud
    bow = Image.new("RGBA", (360, 200), (0, 0, 0, 0))
    bm = Image.new("L", bow.size, 0)
    bd = ImageDraw.Draw(bm)
    bd.ellipse((10, 30, 175, 190), fill=255)
    bd.ellipse((185, 30, 350, 190), fill=255)
    bd.ellipse((60, 75, 140, 150), fill=0)
    bd.ellipse((220, 75, 300, 150), fill=0)
    bd.ellipse((145, 70, 215, 170), fill=255)
    bow = gold_fill(bow.size, bm)
    lid_full = Image.new("RGBA", (lw, lh + 160), (0, 0, 0, 0))
    lid_full.alpha_composite(lid, (0, 160))
    lid_full.alpha_composite(bow, (lw // 2 - 180, 0))
    return shadowed(body, blur=16, off=18, opacity=120), lid_full


GIFT_BODY, GIFT_LID = gift_parts()


def draw_gift(c, cx, cy, t, t_open=None, shake_from=None, scale=1.0, burst=False):
    """Cadeau qui tremble puis s'ouvre (couvercle projeté, rayons de lumière)."""
    jit = 0.0
    if shake_from is not None and t_open is not None and shake_from <= t < t_open:
        jit = 10 * math.sin(t * 60) * prog(t, shake_from, t_open - shake_from)
    body = GIFT_BODY if scale == 1 else GIFT_BODY.resize((int(GIFT_BODY.width * scale),
                                                           int(GIFT_BODY.height * scale)), Image.LANCZOS)
    lid = GIFT_LID if scale == 1 else GIFT_LID.resize((int(GIFT_LID.width * scale),
                                                        int(GIFT_LID.height * scale)), Image.LANCZOS)
    opened = t_open is not None and t >= t_open
    if opened:
        p = prog(t, t_open, 0.6)
        rays(c, cx, cy - 230 * scale, t, alpha=clamp(p * 2) * (0.9 if not burst else 1.2))
    if not (burst and opened):
        place(c, body, cx + jit, cy, angle=jit * 0.3)
    if not opened:
        place(c, lid, cx + jit * 1.2, cy - (GIFT_BODY.height / 2 + 40) * scale, angle=-jit * 0.6)
    else:
        p = prog(t, t_open, 0.7)
        place(c, lid, cx - 420 * p * scale, cy - (GIFT_BODY.height / 2 + 40 + 900 * p - 500 * p * p) * scale,
              angle=-70 * p, alpha=clamp(1.4 - p))


def rays(c, cx, cy, t, alpha=1.0, color=(255, 236, 170)):
    if alpha <= 0:
        return
    s = 1800
    im = Image.new("L", (s // 2, s // 2), 0)
    d = ImageDraw.Draw(im)
    rot = t * 25
    for k in range(16):
        a0 = rot + k * 22.5
        d.pieslice((0, 0, s // 2, s // 2), a0, a0 + 9, fill=int(120 * alpha))
    d.ellipse((s // 4 - 120, s // 4 - 120, s // 4 + 120, s // 4 + 120), fill=int(200 * min(1, alpha)))
    im = im.filter(ImageFilter.GaussianBlur(10)).resize((s, s), Image.BILINEAR)
    lay = Image.new("RGBA", (s, s), color + (0,))
    lay.putalpha(im)
    c.alpha_composite(lay, (int(cx - s / 2), int(cy - s / 2)))


def santa_hat(w=300):
    h = int(w * 0.9)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(w * 0.08, h * 0.78), (w * 0.55, h * 0.05), (w * 0.88, h * 0.30), (w * 0.95, h * 0.78)],
              fill=(205, 24, 36, 255))
    d.polygon([(w * 0.55, h * 0.05), (w * 0.88, h * 0.30), (w * 0.80, h * 0.36)], fill=(150, 12, 22, 255))
    d.rounded_rectangle((0, h * 0.68, w, h * 0.92), radius=int(h * 0.12), fill=WHITE + (255,))
    d.ellipse((w * 0.78, h * 0.18, w * 0.98, h * 0.40), fill=WHITE + (255,))
    return shadowed(im, blur=8, off=6, opacity=110)


HAT = santa_hat(250)


def calendar(n_text="24"):
    w, h = 720, 800
    card = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    m = rrect_mask((w, h), 40)
    face = Image.new("RGBA", (w, h), CREAM + (255,))
    head = Image.new("RGBA", (w, 210), RED + (255,))
    face.alpha_composite(head)
    face.putalpha(m)
    card.alpha_composite(face)
    dd = ImageDraw.Draw(card)
    for x in (190, w - 190):  # anneaux
        dd.rounded_rectangle((x - 16, -10, x + 16, 60), radius=14, fill=(180, 140, 50, 255))
    mon = tl("DÉCEMBRE", R.anton(110), fill=WHITE, shadow=False, tracking=6)
    card.alpha_composite(mon, ((w - mon.width) // 2, 105 - mon.height // 2))
    num = text3d(n_text, R.anton(430), face=RED, side=(120, 8, 16), depth=14)
    card.alpha_composite(num, ((w - num.width) // 2, 230 + (470 - num.height) // 2))
    yr = tl("2026", R.helv(54, bold=True), fill=(150, 110, 40), shadow=False, tracking=14)
    card.alpha_composite(yr, ((w - yr.width) // 2, 700 - yr.height // 2))
    return shadowed(card, blur=22, off=20, opacity=130)


def gift_tag(text):
    lab = tl(text, R.anton(88), fill=WHITE, shadow=False, tracking=2)
    w = lab.width - 80 + 190
    h = 140
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    d.polygon([(0, h / 2), (60, 0), (w, 0), (w, h), (60, h)], fill=255)
    d.ellipse((34, h / 2 - 14, 62, h / 2 + 14), fill=0)
    border = m.filter(ImageFilter.MaxFilter(9))
    tag = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0))
    tag.paste(gold_fill((w, h)), (4, 4), border.point(lambda v: v))
    inner = Image.new("RGBA", (w, h), RED + (255,))
    im2 = m.filter(ImageFilter.MinFilter(9))
    tag.paste(inner, (4, 4), im2)
    tag.alpha_composite(lab, (4 + 70 + (w - 70 - lab.width) // 2, 4 + (h - lab.height) // 2 + 4))
    return shadowed(tag, blur=12, off=10, opacity=120)


def curtains(c, p):
    """Rideau de velours rouge à plis, qui s'ouvre (p de 0 à 1)."""
    if p >= 1:
        return
    pw = W // 2 + 80
    xs = np.arange(pw)
    fold = 0.62 + 0.38 * np.abs(np.sin(xs / 46.0))
    a = np.zeros((H, pw, 4), np.uint8)
    for k, v in enumerate((196, 20, 32)):
        a[..., k] = (v * fold)[None, :].astype(np.uint8)
    a[..., 3] = 255
    panel = Image.fromarray(a, "RGBA")
    fr = gold_fill((pw, 40))
    panel.alpha_composite(fr, (0, H - 40))
    e = ease_in_out(p)
    left = panel
    right = panel.transpose(Image.FLIP_LEFT_RIGHT)
    c.alpha_composite(shadowed(left, blur=20, off=0, opacity=120), (int(-60 - e * pw) - 40, -40))
    c.alpha_composite(shadowed(right, blur=20, off=0, opacity=120), (int(W / 2 - 20 + e * pw) - 40, -40))
    # lambrequin or en haut
    val = Image.new("RGBA", (W, 120), RED_DEEP + (255,))
    val.alpha_composite(gold_fill((W, 16)), (0, 104))
    c.alpha_composite(val)


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
    g = gold_fill(m.size, m)
    gd = ImageDraw.Draw(g)
    for x in (0.28, 0.5, 0.72):  # pierres rouges
        gd.ellipse((x * s - 14, s * 0.55 - 14, x * s + 14, s * 0.55 + 14), fill=RED + (255,))
    return shadowed(g, blur=10, off=8)


CROWN = crown()


# ---------------------------------------------------------------- effets
def confetti(c, t, t0, cx, cy, n=90, seed=1, spread=1.0):
    if t < t0 or t > t0 + 2.4:
        return
    r = np.random.default_rng(seed)
    d = ImageDraw.Draw(c)
    dt = t - t0
    cols = [(240, 200, 90), (255, 232, 160), (210, 24, 36), (255, 255, 255), (190, 140, 40)]
    for _ in range(n):
        ang = r.uniform(0, 2 * math.pi)
        sp = r.uniform(500, 1400) * spread
        x = cx + math.cos(ang) * sp * dt * 0.9
        y = cy + (math.sin(ang) * sp - 500) * dt * 0.9 + 900 * dt * dt
        w, h = r.uniform(8, 16), r.uniform(14, 26)
        rot = r.uniform(0, 6.28) + dt * r.uniform(4, 12)
        col = cols[int(r.integers(0, len(cols)))]
        a = int(255 * clamp(1.7 - dt / 1.4))
        cw = abs(math.cos(rot)) * w + 2
        d.rectangle((x - cw / 2, y - h / 2, x + cw / 2, y + h / 2), fill=col + (a,))


def sparkles(c, t, cx, cy, rx, ry, n=14, seed=2, color=(255, 240, 190)):
    """Étoiles scintillantes (croix lumineuses) autour d'un point."""
    r = np.random.default_rng(seed)
    d = ImageDraw.Draw(c)
    for _ in range(n):
        x, y = cx + r.uniform(-rx, rx), cy + r.uniform(-ry, ry)
        ph, sp = r.uniform(0, 6.28), r.uniform(2, 4)
        k = max(0.0, math.sin(ph + t * sp)) ** 3
        if k < 0.05:
            continue
        L = 26 * k + 4
        a = int(255 * k)
        d.line((x - L, y, x + L, y), fill=color + (a,), width=3)
        d.line((x, y - L, x, y + L), fill=color + (a,), width=3)
        d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(255, 255, 255, a))


def splash(c, t, t0, cx, cy, n=70, seed=3):
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
        d.ellipse((x - rad, y - rad, x + rad, y + rad), fill=(235, 250, 255, int(230 * clamp(1.4 - dt))))


def flash(c, t, t0, dur=0.3, strength=0.6, color=(255, 236, 190)):
    p = (t - t0) / dur
    if 0 <= p <= 1:
        c.alpha_composite(Image.new("RGBA", (W, H), color + (int(255 * strength * math.sin(p * math.pi)),)))


def caustics(c, t):
    sx, sy = np.meshgrid(np.linspace(0, 6, W // 6), np.linspace(0, 10, H // 6))
    v = (np.sin(sx * 2.1 + t * 2.0 + np.sin(sy * 1.7 + t)) + np.sin(sy * 2.6 - t * 1.6 + np.sin(sx * 1.3))) / 2
    v = np.clip((v - 0.55) * 4, 0, 1) * 70
    lay = Image.new("RGBA", (W, H), (215, 248, 255, 0))
    lay.putalpha(Image.fromarray(v.astype(np.uint8), "L").resize((W, H), Image.BICUBIC))
    c.alpha_composite(lay)


# ---------------------------------------------------------------- transitions
def blob_mask(p, cx, cy, seed=0):
    r = np.random.default_rng(seed)
    harm = [(k, r.uniform(0.05, 0.16) / (1 + k * 0.3), r.uniform(0, 6.28)) for k in range(3, 9)]
    s = 4
    gy, gx = np.mgrid[0:H // s, 0:W // s]
    dx, dy = gx * s - cx, gy * s - cy
    ang, rad = np.arctan2(dy, dx), np.sqrt(dx ** 2 + dy ** 2)
    edge = 1 + sum(a * np.sin(k * ang + ph + p * 3) for k, a, ph in harm)
    m = (rad < ease_in_out(p) * 2400 * edge).astype(np.uint8) * 255
    return Image.fromarray(m, "L").resize((W, H), Image.BILINEAR), None


def ribbon_mask(p, direction=1):
    """Ruban d'or diagonal qui balaie l'écran et dévoile la séquence suivante."""
    s = 4
    gy, gx = np.mgrid[0:H // s, 0:W // s]
    u = (gx * s if direction > 0 else (W - gx * s)) + gy * s * 0.45
    u = u / (W + H * 0.45)
    pos = -0.15 + 1.3 * ease_in_out(p)
    m = (u < pos - 0.03).astype(np.uint8) * 255
    band = np.exp(-((u - pos) / 0.035) ** 2)
    mask = Image.fromarray(m, "L").resize((W, H), Image.BILINEAR)
    b = Image.fromarray((band * 255).astype(np.uint8), "L").resize((W, H), Image.BILINEAR)
    rib = gold_fill((W, H))
    rib.putalpha(b)
    return mask, rib


TRANS = {1: ("blob", (W / 2, 1900)), 2: ("ribbon", 1), 3: ("ribbon", -1), 4: ("ribbon", 1), 5: ("ribbon", -1),
         6: ("ribbon", 1), 7: ("cut", None), 8: ("ribbon", -1), 9: ("ribbon", 1)}
XD = 0.34


# ---------------------------------------------------------------- textes
T = {
    "cette": tl("CETTE ANNÉE,", R.anton(110), tracking=4),
    "noel": text3d("NOËL", R.anton(330), depth=16),
    "fete": tl("SE FÊTE…", R.anton(120), tracking=4),
    "aubord": tl("AU BORD DE LA", R.anton(110), tracking=4),
    "piscine": text3d("PISCINE !", R.anton(230), face=WHITE, side=(180, 20, 30), depth=14),
    "organise": tl("WELLBEING RESORT ORGANISE", R.helv(36, bold=True), tracking=6),
    "well": text3d("WELL", R.anton(210), depth=14, tracking=6),
    "christmas": text3d("CHRISTMAS", R.anton(200), depth=14, tracking=4),
    "pourtous": tl("LA FÊTE DE NOËL POUR TOUS", R.helv(40, bold=True), fill=RED_DEEP, shadow=False, tracking=3),
    "heures": tl("10H00 – 18H00", R.anton(96), fill=WHITE, shadow=False, tracking=2),
    "auprog": text3d("AU PROGRAMME", R.anton(110), face=RED, side=(110, 8, 16), depth=10, tracking=4),
    "atelier": text3d("ATELIER TOMBOLA", R.anton(110), face=WHITE, side=(150, 10, 20), depth=10, tracking=3),
    "agagner": text3d("À GAGNER", R.anton(160), face=RED, side=(110, 8, 16), depth=12, tracking=6),
    "ou": tl("OU", R.anton(90), fill=RED, shadow=False),
    "etqui": tl("ET QUI SERA…", R.anton(100), tracking=4),
    "miss": text3d("MISS", R.anton(230), depth=14, tracking=8),
    "wellbeing": text3d("WELLBEING", R.anton(190), depth=14, tracking=4),
    "ambass": tl("AMBASSADRICE", R.anton(90), tracking=4),
    "an2027": text3d("2027", R.anton(200), face=WHITE, side=(150, 10, 20), depth=12),
    "bonus": tl("COURS DE NATATION, GRANDE PIZZA", R.helv(34, bold=True), fill=(255, 235, 210), tracking=2),
    "bonus2": tl("ET PLEIN D'AUTRES GADGETS", R.helv(34, bold=True), fill=(255, 235, 210), tracking=2),
    "lentree": tl("L'ENTRÉE EST", R.anton(130), tracking=4),
    "gratuite": text3d("GRATUITE !!!", R.anton(210), depth=16),
    "fin_titre": text3d("WELL CHRISTMAS", R.anton(140), depth=10, tracking=4),
    "fin_date": tl("24 DÉC. 2026  ·  10H – 18H", R.helv(42, bold=True), tracking=3),
    "fin_gratuit": tl("ENTRÉE GRATUITE", R.anton(84), fill=RED_DEEP, shadow=False, tracking=3),
    "fin_adr": tl("COCODY RIVIERA 3, ROUTE M'BADON", R.helv(36, bold=True), tracking=2),
    "fin_tel1": text3d("07 47 79 95 07", R.anton(118), depth=8),
    "fin_tel2": tl("05 66 92 33 91", R.anton(84)),
}
TAGS = [gift_tag(p) for p in ["PISCINE", "JEUX", "STANDS", "DON DE CADEAUX"]]
CAL = calendar()
_TICKETS = {}


def ticket(value):
    if value in _TICKETS:
        return _TICKETS[value]
    w, h = 860, 400
    m = rrect_mask((w, h), 34)
    d = ImageDraw.Draw(m)
    d.ellipse((-50, h // 2 - 50, 50, h // 2 + 50), fill=0)
    d.ellipse((w - 50, h // 2 - 50, w + 50, h // 2 + 50), fill=0)
    tk = gold_fill((w, h), m)
    dd = ImageDraw.Draw(tk)
    for x in range(90, w - 90, 26):
        dd.line((x, 92, x + 12, 92), fill=(110, 10, 16, 140), width=3)
    lab = tl("TOMBOLA", R.helv(40, bold=True), fill=RED_DEEP, shadow=False, tracking=14)
    tk.alpha_composite(lab, ((w - lab.width) // 2, 2))
    val = tl(f"{value} F", R.anton(200), fill=RED_DEEP, shadow=False)
    tk.alpha_composite(val, ((w - val.width) // 2, 90))
    out = shadowed(tk)
    _TICKETS[value] = out
    return out


def prize_card(big, small):
    a = tl(big, R.anton(130), fill=WHITE, shadow=False, tracking=2)
    b = tl(small, R.helv(34, bold=True), fill=(255, 225, 160), shadow=False, tracking=2)
    w = max(a.width, b.width) - 80 + 140
    h = 300
    card = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0))
    card.paste(gold_fill((w + 16, h + 16)), (0, 0), rrect_mask((w + 16, h + 16), 36))
    inner = Image.new("RGBA", (w, h), RED + (255,))
    inner.putalpha(rrect_mask((w, h), 30))
    card.alpha_composite(inner, (8, 8))
    card.alpha_composite(a, (8 + (w - a.width) // 2, 14))
    card.alpha_composite(b, (8 + (w - b.width) // 2, 196))
    return shadowed(card)


CARD1 = prize_card("1 NUITÉE", "DANS NOTRE RÉSIDENCE HÔTELIÈRE")
CARD2 = prize_card("1 MOIS", "DE COURS DE NATATION")


def gold_pill(lab, h, pad=90):
    pill = gold_fill((lab.width - 80 + pad, h), rrect_mask((lab.width - 80 + pad, h), h // 2))
    pill.alpha_composite(lab, ((pill.width - lab.width) // 2, (h - lab.height) // 2 + 4))
    return shadowed(pill, blur=10, off=8)


def red_pill(lab, h, pad=90):
    w = lab.width - 80 + pad
    out = Image.new("RGBA", (w + 12, h + 12), (0, 0, 0, 0))
    out.paste(gold_fill((w + 12, h + 12)), (0, 0), rrect_mask((w + 12, h + 12), (h + 12) // 2))
    inner = Image.new("RGBA", (w, h), RED + (255,))
    inner.putalpha(rrect_mask((w, h), h // 2))
    out.alpha_composite(inner, (6, 6))
    out.alpha_composite(lab, (6 + (w - lab.width) // 2, 6 + (h - lab.height) // 2 + 4))
    return shadowed(out, blur=10, off=8)


PILL_HEURES = red_pill(T["heures"], 150)
PILL_POURTOUS = gold_pill(T["pourtous"], 96)
PILL_GRATUIT = gold_pill(T["fin_gratuit"], 124)


# ---------------------------------------------------------------- séquences
def s1_hook(c, t):
    """0 – 2,15 : le cadeau tremble, s'ouvre sur « NOËL »."""
    bg_velvet(c, t)
    draw_gift(c, W / 2, 1320, t, t_open=CUE["noel"] - 0.06, shake_from=CUE["cette"] + 0.1)
    slide(c, T["cette"], W / 2, 430, t, CUE["cette"], dx=-700)
    k = prog(t, CUE["noel"] - 0.06, 0.32)
    if k > 0:  # NOËL jaillit du cadeau
        y = 1150 - 400 * back_out(k, 1.5)
        place(c, shining(T["noel"], t, CUE["noel"]), W / 2, y, scale=0.4 + 0.6 * back_out(k, 1.5), alpha=clamp(k * 3))
    confetti(c, t, CUE["noel"], W / 2, 950, n=110, seed=2)
    sparkles(c, t, W / 2, 760, 420, 220, seed=3)
    slide(c, T["fete"], W / 2, 1010, t, CUE["fete"], dx=700)
    front_snow(c, t)


def s2_piscine(c, t):
    """2,15 – 3,62 : la boule plonge ; « PISCINE ! » coiffé d'un bonnet de Père Noël."""
    c.alpha_composite(BG_BLUE)
    caustics(c, t)
    snowfall(c, t, layers=(1, 2), alpha=0.7)
    slide(c, T["aubord"], W / 2, 590, t, CUE["aubord"], dy=-200)
    tp = CUE["piscine"]
    if t < tp:
        p = prog(t, CUE["aubord"], tp - CUE["aubord"])
        place(c, boule(1.1, angle=200 * p), W / 2, -150 + 1450 * p ** 2)
    splash(c, t, tp, W / 2, 1300)
    slam(c, T["piscine"], W / 2, 940, t, tp, big=1.8)
    k = prog(t, tp + 0.15, 0.35)
    if k > 0:  # le bonnet tombe sur le « P »
        place(c, HAT, 205, 800 - 260 * (1 - ease_out(k)), angle=-18 + 6 * math.sin(t * 5), alpha=clamp(k * 3))
    if t > tp:
        d = ImageDraw.Draw(c)
        for kk in range(3):
            rr = (t - tp - kk * 0.18) * 520
            if rr > 0:
                d.ellipse((W / 2 - rr, 1300 - rr * 0.28, W / 2 + rr, 1300 + rr * 0.28),
                          outline=(235, 250, 255, int(200 * clamp(1 - rr / 700))), width=6)


def boule_orbit(c, t, t0):
    for i, (bx, by, sc, ph) in enumerate([(150, 1060, 0.9, 0), (940, 1010, 0.75, 1.7), (130, 1470, 0.6, 3.1),
                                          (960, 1420, 0.85, 4.2)]):
        k = prog(t, t0 + 0.25 + i * 0.12, 0.4)
        if k > 0:
            place(c, boule(sc, angle=15 * math.sin(t * 1.5 + ph)), bx, by + 20 * math.sin(t * 2 + ph),
                  alpha=k, scale=back_out(k, 2))


def s3_invite(c, t):
    """3,62 – 8,4 : l'animateur surgit ; WELL CHRISTMAS en or ; bandeau « pour tous »."""
    bg_velvet(c, t)
    t0 = CUTS[1]
    rays(c, W / 2, 1450, t, alpha=0.55 * prog(t, t0, 0.5))
    boule_orbit(c, t, t0)
    k = prog(t, t0 + 0.05, 0.5)
    if k > 0:
        y = H - ANIM_ST.height / 2 + 30 + (1 - back_out(k, 1.4)) * 900
        place(c, ANIM_ST, W / 2, y + 6 * math.sin(t * 3))
    sparkles(c, t, W / 2, 1300, 480, 320, n=16, seed=5)
    slide(c, T["organise"], W / 2, 330, t, CUE["wbr"], dy=-120)
    slam(c, shining(T["well"], t, CUE["wellchristmas"]), W / 2, 500, t, CUE["wellchristmas"], big=1.7)
    slam(c, shining(T["christmas"], t, CUE["wellchristmas"] + 0.22), W / 2, 690, t, CUE["wellchristmas"] + 0.22,
         big=1.7)
    confetti(c, t, CUE["wellchristmas"] + 0.22, W / 2, 620, n=120, seed=7)
    k = prog(t, CUE["pourtous"], 0.3)
    if k > 0:
        place(c, PILL_POURTOUS, W / 2, 870, alpha=clamp(k * 3), scale=0.6 + 0.4 * back_out(k))
    front_snow(c, t)


def s4_date(c, t):
    """8,4 – 11,5 : la page du calendrier de l'Avent tombe sur « 24 » ; pastille horaires."""
    bg_snow(c, t)
    k = prog(t, CUE["date"] - 0.12, 0.4)
    if k > 0:  # la page bascule vers l'avant (rabat qui se déplie)
        sy = max(0.02, back_out(k, 1.3))
        cal = CAL.resize((CAL.width, max(2, int(CAL.height * sy))), Image.BILINEAR)
        place(c, cal, W / 2, 330 + cal.height / 2, alpha=clamp(k * 3))
    confetti(c, t, CUE["date"] + 0.1, W / 2, 750, n=80, seed=9, spread=0.9)
    sparkles(c, t, W / 2, 760, 460, 420, seed=10, color=(220, 160, 50))
    k = prog(t, CUE["heures"], 0.3)
    if k > 0:
        place(c, PILL_HEURES, W / 2, 1330, alpha=clamp(k * 3), scale=0.5 + 0.5 * back_out(k))


def s5_programme(c, t):
    """11,5 – 14,32 : étiquettes cadeau suspendues à la guirlande, une par mot."""
    bg_snow(c, t)
    slide(c, T["auprog"], W / 2, 400, t, CUTS[3] + 0.02, dy=-150)
    xs = [300, 770, 330, 680]
    ys = [700, 880, 1080, 1290]
    d = ImageDraw.Draw(c)
    for i, ti in enumerate(CUE["prog"]):
        if t < ti - 0.05:
            continue
        p = prog(t, ti - 0.05, 0.35)
        drop = (1 - back_out(p, 1.6)) * -500
        sw = 14 * math.exp(-(t - ti) * 1.8) * math.sin((t - ti) * 9) + 2 * math.sin(t * 1.5 + i)
        x, y = xs[i], ys[i] + drop
        d.line((x - 60, 160, x - (TAGS[i].width / 2 - 70), y), fill=(190, 150, 60, 255), width=3)
        place(c, TAGS[i], x, y, angle=sw, alpha=clamp(p * 3))
    front_snow(c, t, color=(230, 190, 110))


def s6_tombola(c, t):
    """14,32 – 16,45 : ticket doré qui se retourne, prix qui défile jusqu'à 2.000 F."""
    bg_velvet(c, t)
    slide(c, T["atelier"], W / 2, 600, t, CUE["tombola"], dy=-160)
    k = prog(t, CUE["tombola"] + 0.25, 0.45)
    if k > 0:
        rays(c, W / 2, 1010, t, alpha=0.5 * clamp(k * 2))
        cp = prog(t, CUE["prix"], CUE["prix_fin"] - CUE["prix"])
        val = int(round(2000 * ease_out(cp) / 100) * 100)
        txt = f"{val // 1000}.{val % 1000:03d}" if val >= 1000 else str(val)
        tk = shining(ticket(txt), t, CUE["prix_fin"], period=1.3)
        flip = abs(math.cos((1 - ease_out(k)) * math.pi * 1.5)) if k < 1 else 1.0
        tk = tk.resize((max(2, int(tk.width * flip)), tk.height), Image.BILINEAR)
        pulse = 1 + 0.08 * math.sin(math.pi * prog(t, CUE["prix_fin"], 0.25))
        place(c, tk, W / 2, 1010 + 10 * math.sin(t * 2.5), alpha=clamp(k * 3), scale=pulse, angle=-4)
    confetti(c, t, CUE["prix_fin"], W / 2, 1010, n=70, seed=12)
    flash(c, t, CUE["prix_fin"], 0.3, 0.4)
    front_snow(c, t)


def s7_gains(c, t):
    """16,45 – 21,15 : À GAGNER / 1 NUITÉE / OU / 1 MOIS DE COURS DE NATATION (fond neige)."""
    bg_snow(c, t)
    slam(c, shining(T["agagner"], t, CUE["agagner"]), W / 2, 440, t, CUE["agagner"], big=1.6)
    slide(c, CARD1, W / 2, 780, t, CUE["nuitee"], dx=-1000, dur=0.4)
    pop(c, T["ou"], W / 2, 1015, t, CUE["natation"] - 0.25)
    slide(c, CARD2, W / 2, 1250, t, CUE["natation"], dx=1000, dur=0.4)
    sparkles(c, t, W / 2, 1000, 480, 450, seed=14, color=(220, 160, 50))
    front_snow(c, t, color=(230, 190, 110))


def s8_miss(c, t):
    """21,15 – 25,12 : le rideau de velours s'ouvre sur la couronne et MISS WELLBEING."""
    c.alpha_composite(BG_STAGE)
    a = int(130 * clamp((t - CUE["miss"] + 0.3) * 3))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).polygon([(W / 2 - 80, 0), (W / 2 + 80, 0), (W / 2 + 540, 1300), (W / 2 - 540, 1300)],
                                 fill=(255, 220, 140, a))
    c.alpha_composite(glow.filter(ImageFilter.GaussianBlur(50)))
    snowfall(c, t, layers=(1, 2), alpha=0.8)
    k = prog(t, CUE["miss"] - 0.15, 0.45)
    if k > 0:
        place(c, CROWN, W / 2, -200 + (620 + 200) * ease_out(k), angle=8 * (1 - k) * math.sin(t * 8))
    slam(c, shining(T["miss"], t, CUE["miss"]), W / 2, 840, t, CUE["miss"], big=1.8)
    slam(c, shining(T["wellbeing"], t, CUE["miss"] + 0.25), W / 2, 1030, t, CUE["miss"] + 0.25, big=1.6)
    confetti(c, t, CUE["miss"] + 0.2, W / 2, 840, n=100, seed=13)
    sparkles(c, t, W / 2, 900, 460, 330, n=18, seed=15)
    slide(c, T["ambass"], W / 2, 1225, t, CUE["an2027"] - 0.55, dx=-800)
    slam(c, T["an2027"], W / 2, 1385, t, CUE["an2027"] + 0.25, big=1.7)
    place(c, T["bonus"], W / 2, 1520, alpha=ease_out(prog(t, CUE["an2027"] + 0.6, 0.3)))
    place(c, T["bonus2"], W / 2, 1565, alpha=ease_out(prog(t, CUE["an2027"] + 0.75, 0.3)))
    # rideau : fermé à l'arrivée, s'ouvre sur « Et qui sera… », le texte arrive devant
    curtains(c, prog(t, CUE["etqui"] - 0.05, 0.8))
    slide(c, T["etqui"], W / 2, 330, t, CUE["etqui"], dy=-120)


BG_STAGE = radial((150, 22, 30), (45, 2, 8), cy=0.4)


def s9_gratuit(c, t):
    """25,12 – 26,55 : un énorme cadeau tremble puis explose sur « GRATUITE !!! »."""
    bg_velvet(c, t)
    draw_gift(c, W / 2, 1180, t, t_open=CUE["gratuite"] - 0.04, shake_from=CUE["entree"] + 0.1, scale=1.15,
              burst=True)
    slide(c, T["lentree"], W / 2, 520, t, CUE["entree"], dy=-200)
    slam(c, shining(T["gratuite"], t, CUE["gratuite"], period=1.0), W / 2, 900, t, CUE["gratuite"], big=2.1,
         dur=0.16)
    confetti(c, t, CUE["gratuite"], W / 2, 1100, n=200, seed=17, spread=1.3)
    flash(c, t, CUE["gratuite"], 0.35, 0.65)
    front_snow(c, t)


def s10_fin(c, t):
    """26,55 – 30 : carte finale rouge, blanc, or ; l'animateur revient saluer."""
    bg_velvet(c, t)
    lt = t - CUTS[-1]
    rays(c, W / 2, 1700, t, alpha=0.45)
    k = prog(lt, 0.2, 0.5)
    if k > 0:
        sm = ANIM_ST.resize((int(ANIM_ST.width * 0.72), int(ANIM_ST.height * 0.72)), Image.LANCZOS)
        place(c, sm, W / 2, H - sm.height / 2 + 40 + (1 - back_out(k, 1.3)) * 600)
    pop(c, LOGO.resize((int(LOGO.width * 0.55), int(LOGO.height * 0.55)), Image.LANCZOS), W / 2, 330, t,
        CUTS[-1] + 0.05, dur=0.4)
    slam(c, shining(T["fin_titre"], t, CUTS[-1] + 0.15, period=1.6), W / 2, 545, t, CUTS[-1] + 0.15, big=1.4)
    place(c, T["fin_date"], W / 2, 655, alpha=ease_out(prog(lt, 0.35, 0.3)))
    k = prog(lt, 0.5, 0.3)
    if k > 0:
        place(c, PILL_GRATUIT, W / 2, 780, alpha=clamp(k * 3), scale=0.6 + 0.4 * back_out(k))
    slide(c, T["fin_adr"], W / 2, 915, t, CUE["adresse"] + 0.6, dy=80)
    t1 = CUE["adresse"] + 0.9
    if t < t1 + 0.5:
        slam(c, T["fin_tel1"], W / 2, 1035, t, t1, big=1.4)
    else:
        place(c, shining(T["fin_tel1"], t, t1 + 0.5, period=1.8), W / 2, 1035,
              scale=1 + 0.02 * math.sin((t - t1) * 6))
    place(c, T["fin_tel2"], W / 2, 1145, alpha=ease_out(prog(t, t1 + 0.3, 0.3)))
    front_snow(c, t)


SCENES = [s1_hook, s2_piscine, s3_invite, s4_date, s5_programme, s6_tombola, s7_gains, s8_miss, s9_gratuit,
          s10_fin]
BOUNDS = [0.0] + CUTS + [DUR]


def scene_frame(i, t):
    c = Image.new("RGBA", (W, H), RED_DARK + (255,))
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


def push_in(c, t):
    """Légère poussée de caméra continue dans chaque séquence (effet « vivant »)."""
    i = max(k for k in range(len(SCENES)) if BOUNDS[k] <= t) if t < DUR else len(SCENES) - 1
    p = prog(t, BOUNDS[i], BOUNDS[i + 1] - BOUNDS[i])
    z = 1 + 0.035 * p
    big = c.resize((int(W * z), int(H * z)), Image.BILINEAR)
    ox, oy = (big.width - W) // 2, (big.height - H) // 2
    return big.crop((ox, oy, ox + W, oy + H))


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


def sub_layer(text):
    if text in _SUB:
        return _SUB[text]
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
    lay = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0))
    lay.paste(gold_fill((w + 8, h + 8)), (0, 0), rrect_mask((w + 8, h + 8), 22))
    inner = Image.new("RGBA", (w, h), (150, 12, 22, 235))
    inner.putalpha(rrect_mask((w, h), 18).point(lambda v: v * 235 // 255))
    lay.alpha_composite(inner, (4, 4))
    dd = ImageDraw.Draw(lay)
    for i, li in enumerate(lines):
        lw = d.textlength(li, font=font)
        dd.text((4 + (w - lw) / 2, 4 + 12 + i * lh), li, font=font, fill=WHITE)
    _SUB[text] = lay
    return lay


def draw_sub(c, t):
    for a, b, text in SUBS:
        if a <= t < b:
            k = min(prog(t, a, 0.1), 1.0 if t < b - 0.1 else prog(b, t, 0.1))
            place(c, sub_layer(text), W / 2, 1640, alpha=k)
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
    nxt = i + 1
    if nxt < len(SCENES) and t > BOUNDS[nxt] - XD:
        p = (t - (BOUNDS[nxt] - XD)) / XD
        kind, arg = TRANS.get(nxt, ("cut", None))
        if kind in ("blob", "ribbon") and p > 0:
            mask, overlay = blob_mask(p, *arg, seed=nxt) if kind == "blob" else ribbon_mask(p, arg)
            c.paste(scene_frame(nxt, t), (0, 0), mask)
            if overlay is not None:
                c.alpha_composite(overlay)
    c = push_in(c, t)
    c = shake(c, t)
    if SUBS_ON:
        draw_sub(c, t)
    a = np.asarray(c.convert("RGB")).astype(np.float32)
    a += np.random.default_rng(int(t * FPS)).normal(0, 1.6, (H // 2, W // 2, 1)).repeat(2, 0).repeat(2, 1)
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
        for t in [1.4, 3.1, 6.0, 7.6, 9.9, 13.6, 16.2, 20.3, 21.6, 24.7, 26.2, 29.0]:
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
