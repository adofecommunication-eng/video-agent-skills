#!/usr/bin/env python3
"""Reel « Well Brunch » — Wellbeing Resort (WBR) — 18 s, 9:16, 1080x1920, 30 i/s.

Version motion design construite à partir du flyer officiel (sources/flyer-well-brunch.png).
Usage :  python3 music.py puis
         python3 render.py            -> rendu/well-brunch-reel-18s.mp4 (voix off + musique)
         python3 render.py --subs     -> rendu/well-brunch-reel-18s-sous-titres.mp4
         python3 render.py --stills   -> rendu/apercu-*.png (une image par séquence)
"""
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "rendu"
OUT.mkdir(exist_ok=True)

W, H, FPS, DUR = 1080, 1920, 30, 18.0
N = int(DUR * FPS)

# ---------------------------------------------------------------- palette
INK = (11, 9, 6)
WHITE = (255, 255, 255)
GOLD = (214, 168, 62)
GOLD_STOPS = [(0.0, (252, 232, 160)), (0.42, (226, 181, 74)),
              (0.72, (176, 128, 36)), (1.0, (240, 207, 122))]

# ---------------------------------------------------------------- fonts
F = ROOT / "fonts"


def anton(size):
    return ImageFont.truetype(str(F / "Anton-Regular.ttf"), size)


def helv(size, bold=False):
    """Police secondaire : Helvetica Neue si le fichier est fourni, sinon TeX Gyre Heros (clone libre)."""
    for name in (["HelveticaNeue-Bold.otf", "HelveticaNeue-Bold.ttf", "texgyreheros-bold.otf"] if bold
                 else ["HelveticaNeue.otf", "HelveticaNeue.ttf", "texgyreheros-regular.otf"]):
        if (F / name).exists():
            return ImageFont.truetype(str(F / name), size)
    raise FileNotFoundError("police secondaire introuvable dans fonts/")


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def prog(t, t0, d):
    return clamp((t - t0) / d)


def ease_out(x):
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def back_out(x, s=1.6):
    x -= 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


# ---------------------------------------------------------------- layers
def gradient_fill(size, stops):
    w, h = size
    ys = np.linspace(0, 1, h)
    col = np.zeros((h, 3))
    for c in range(3):
        col[:, c] = np.interp(ys, [s[0] for s in stops], [s[1][c] for s in stops])
    arr = np.repeat(col[:, None, :], w, axis=1).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def text_layer(text, font, fill=WHITE, gold=False, shadow=True, tracking=0, stroke=0):
    """Texte sur calque RGBA serré, avec ombre portée douce."""
    pad = 40
    dummy = ImageDraw.Draw(Image.new("L", (1, 1)))
    if tracking:
        widths = [dummy.textlength(ch, font=font) for ch in text]
        tw = int(sum(widths) + tracking * (len(text) - 1))
    else:
        tw = int(dummy.textlength(text, font=font))
    asc, desc = font.getmetrics()
    th = asc + desc
    w, h = tw + 2 * pad, th + 2 * pad
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    if tracking:
        x = pad
        for ch, cw in zip(text, widths):
            d.text((x, pad), ch, font=font, fill=255, stroke_width=stroke, stroke_fill=255)
            x += cw + tracking
    else:
        d.text((pad, pad), text, font=font, fill=255, stroke_width=stroke, stroke_fill=255)
    if gold:
        bb = mask.getbbox() or (0, 0, w, h)
        face = Image.new("RGB", (w, h))
        g = gradient_fill((w, bb[3] - bb[1]), GOLD_STOPS)
        face.paste(g, (0, bb[1]))
    else:
        face = Image.new("RGB", (w, h), fill)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if shadow:
        sh = mask.filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.75))
        out.paste(Image.new("RGBA", (w, h), (0, 0, 0, 255)), (0, 6), sh)
    out.paste(face.convert("RGBA"), (0, 0), mask)
    return out


def place(canvas, layer, cx, cy, alpha=1.0, scale=1.0):
    """Compose `layer` centré en (cx, cy)."""
    if alpha <= 0.002:
        return
    if abs(scale - 1) > 1e-3:
        layer = layer.resize((max(1, int(layer.width * scale)), max(1, int(layer.height * scale))),
                             Image.LANCZOS)
    if alpha < 0.999:
        a = layer.getchannel("A").point(lambda v: int(v * alpha))
        layer = layer.copy()
        layer.putalpha(a)
    canvas.alpha_composite(layer, (int(cx - layer.width / 2), int(cy - layer.height / 2)))


def wipe_up(canvas, layer, cx, cy, p, rise=None):
    """Révélation « masque » : le texte monte depuis une ligne invisible."""
    if p <= 0:
        return
    rise = rise or layer.height * 0.7
    e = ease_out(p)
    box = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    box.alpha_composite(layer, (0, int((1 - e) * rise)))
    place(canvas, box, cx, cy, alpha=clamp(p * 2.5))


# ---------------------------------------------------------------- sources
FLYER = Image.open(ROOT / "sources" / "flyer-well-brunch.png").convert("RGB")


def gold_logo():
    """Logo WBR détouré du flyer puis recoloré en or (fond clair -> transparent)."""
    crop = FLYER.crop((50, 30, 225, 150))
    a = np.asarray(crop).astype(np.float32)
    alpha = np.clip((240 - a[..., 2]) / (240 - 60), 0, 1)
    alpha = (alpha ** 0.9 * 255).astype(np.uint8)
    big = (crop.width * 3, crop.height * 3)
    m = Image.fromarray(alpha, "L").resize(big, Image.LANCZOS)
    face = gradient_fill(big, GOLD_STOPS).convert("RGBA")
    face.putalpha(m)
    return face


LOGO = gold_logo()

# cadrages cinéma 2.35:1 extraits du flyer (zones sans texte)
CROPS = {
    "table": (100, 560, 1000, 943),   # table entière, buffet + verres
    "buffet": (250, 712, 810, 940),   # plats, gros plan
    "toast": (170, 505, 740, 748),    # verres de jus qui trinquent
    "group": (0, 400, 1080, 860),     # groupe qui rit
}


def kb_crop(name, p, z0=1.0, z1=1.12, dx=0.0, dy=0.0, out_w=1000):
    """Ken Burns dans un cadrage : zoom de z0 à z1, dérive dx/dy (fraction)."""
    x0, y0, x1, y1 = CROPS[name]
    cw, ch = x1 - x0, y1 - y0
    z = z0 + (z1 - z0) * p
    w, h = cw / z, ch / z
    cx = x0 + cw / 2 + dx * cw * (p - 0.5)
    cy = y0 + ch / 2 + dy * ch * (p - 0.5)
    cx = clamp(cx, w / 2, FLYER.width - w / 2)
    cy = clamp(cy, h / 2, FLYER.height - h / 2)
    box = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    out_h = int(out_w * ch / cw)
    return FLYER.resize((out_w, out_h), Image.LANCZOS, box=box)


def blurred_bg(name, dark=0.32):
    x0, y0, x1, y1 = CROPS[name]
    ch = y1 - y0
    cw = ch * W / H
    cx = (x0 + x1) / 2
    img = FLYER.crop((int(cx - cw / 2), y0, int(cx + cw / 2), y1)).resize((W // 4, H // 4))
    img = img.filter(ImageFilter.GaussianBlur(14)).resize((W, H), Image.BICUBIC)
    return Image.blend(Image.new("RGB", (W, H), INK), img, dark).convert("RGBA")


BG = {k: blurred_bg(k) for k in CROPS}


def framed(photo):
    """Fil d'or autour du plan."""
    f = Image.new("RGBA", (photo.width + 8, photo.height + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(f)
    d.rectangle((0, 0, f.width - 1, f.height - 1), outline=GOLD + (255,), width=3)
    f.paste(photo, (4, 4))
    return f


# vignette + grain
yy, xx = np.mgrid[0:H, 0:W]
VIG = 1 - 0.55 * np.clip(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2, 0, 1)
VIG = VIG[..., None].astype(np.float32)
RNG = np.random.default_rng(7)


def finish(canvas):
    a = np.asarray(canvas.convert("RGB")).astype(np.float32) * VIG
    a += RNG.normal(0, 2.5, (H // 2, W // 2, 1)).repeat(2, 0).repeat(2, 1)
    return np.clip(a, 0, 255).astype(np.uint8)


def gold_rule(canvas, cx, cy, width, p, thick=3):
    if p <= 0:
        return
    w = int(width * ease_out(p))
    d = ImageDraw.Draw(canvas)
    d.rectangle((cx - w // 2, cy - thick // 2, cx + w // 2, cy + thick // 2), fill=GOLD + (255,))


def light_leak(canvas, t, t_cut, dur=0.35):
    """Éclat doré sur les coupes."""
    p = (t - t_cut) / dur
    if not 0 <= p <= 1:
        return
    a = math.sin(p * math.pi) * 0.55
    leak = Image.new("RGBA", (W, H), (255, 214, 140, int(255 * a)))
    canvas.alpha_composite(leak)


def deco_pattern(width, rows=3, cell=90):
    """Motif art déco (éventails) rappelant le bas du flyer."""
    h = rows * cell // 2 + cell // 2
    img = Image.new("RGBA", (width, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for r in range(rows):
        y = r * cell // 2
        off = (cell // 2) if r % 2 else 0
        for x in range(-cell, width + cell, cell):
            for k in range(1, 4):
                rr = cell // 2 * k // 3
                d.arc((x + off - rr, y + cell // 2 - rr, x + off + rr, y + cell // 2 + rr),
                      180, 360, fill=GOLD + (150,), width=2)
    return img


# ---------------------------------------------------------------- calage sur la voix off
# Instants (s) où chaque mot est prononcé par Lola, décalage de 0,15 s inclus.
# Mesurés sur l'enveloppe de sources/voix-off-lola.mp3. Musique (music.py) et
# animation lisent ces mêmes valeurs : tout tombe sur la voix.
CUE = {
    "samedi": 0.15, "question": 1.49, "suspense": 2.35,
    "par": 2.75, "quoi": 2.99, "commencer": 3.21,
    "buffet": 4.15, "horaires": 4.97,
    "act": [7.17, 7.85, 8.57, 9.45, 10.21],
    "pass": 11.69, "prix": 12.43, "prix_fin": 12.95,
    "amis": 13.59, "famille": 14.47,
    "ecrivez": 15.47, "brunch": 15.83, "reserver": 16.07,
}
CUTS = [4.10, 7.05, 11.60, 15.40]
IMPACTS = [CUE["par"], CUE["quoi"], CUE["commencer"], CUE["buffet"], CUE["brunch"]]


def slam(canvas, layer, cx, cy, t, t0, big=1.55, dur=0.14, alpha=1.0):
    """Mot qui « claque » : arrive en grand et se pose net sur la syllabe prononcée."""
    if t < t0 - 0.02:
        return
    p = prog(t, t0 - 0.02, dur)
    sc = big + (1 - big) * ease_out(p)
    place(canvas, layer, cx, cy, alpha=clamp(p * 3) * alpha, scale=sc)


# ---------------------------------------------------------------- textes pré-calculés
# Anton = police principale (titres, accroches, prix, numéros)
# Helvetica Neue (ici TeX Gyre Heros, clone libre) = infos pratiques, horaires, adresse, sous-titres
T = {
    "samedi": text_layer("SAMEDI,", anton(170)),
    "question": text_layer("UNE SEULE QUESTION :", anton(76), tracking=4),
    "par": text_layer("PAR", anton(270)),
    "quoi": text_layer("QUOI", anton(270)),
    "commencer": text_layer("COMMENCER ?", anton(190), gold=True),
    "buffet": text_layer("BUFFET À VOLONTÉ", anton(150)),
    "horaire": text_layer("SAMEDI  ·  12H – 18H30", helv(54, bold=True), gold=True, tracking=3),
    "apres": text_layer("ET APRÈS LE BUFFET ?", anton(66), gold=True, tracking=6),
    "amis": text_layer("ENTRE AMIS", anton(150)),
    "famille": text_layer("OU EN FAMILLE", anton(110), gold=True, tracking=2),
    "wellbrunch": text_layer("WELL BRUNCH", anton(170), gold=True, tracking=4),
    "tous": text_layer("TOUS LES SAMEDIS  ·  12H – 18H30", helv(36, bold=True), gold=True, tracking=2),
    "ecrivez": text_layer("ÉCRIVEZ", anton(120)),
    "brunch": text_layer("« BRUNCH »", anton(190), gold=True),
    "reserver": text_layer("POUR RÉSERVER", helv(40, bold=True), tracking=6),
    "tel1": text_layer("07 47 79 95 07", anton(130), gold=True),
    "tel2": text_layer("05 66 92 33 91", anton(80)),
    "adresse": text_layer("COCODY RIVIERA 3  ·  ROUTE M'BADON", helv(36, bold=True), tracking=2),
}
ACTIVITES = ["PISCINE", "BABY-FOOT", "BILLARD", "KARAOKÉ", "DJ MIXTE"]
T_ACT = [text_layer(a, anton(150)) for a in ACTIVITES]
T_ACT_GOLD = [text_layer(a, anton(150), gold=True) for a in ACTIVITES]

_BADGES = {}


def pass_badge(value, fcfa=True):
    """Badge or « PASS : 10.000 FCFA » ; largeur fixe pour que le compteur ne tremble pas."""
    key = (value, fcfa)
    if key in _BADGES:
        return _BADGES[key]
    ref = text_layer("PASS : 10.000", anton(110), fill=INK, shadow=False)
    lab = text_layer(f"PASS : {value}", anton(110), fill=INK, shadow=False)
    cur = text_layer("FCFA", anton(56), fill=INK, shadow=False)
    w, h = ref.width + cur.width - 40, 170
    b = gradient_fill((w, h), GOLD_STOPS).convert("RGBA")
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius=18, fill=255)
    b.putalpha(m)
    b.alpha_composite(lab, (0, (h - lab.height) // 2 + 4))
    if fcfa:
        b.alpha_composite(cur, (ref.width - 70, (h - ref.height) // 2 - 14))
    _BADGES[key] = b
    return b


DECO = deco_pattern(W + 180)


# ---------------------------------------------------------------- séquences
def s_hook(c, t):
    """0 – 4,1 s : « Samedi, … une seule question : » puis PAR / QUOI / COMMENCER ? sur chaque mot."""
    c.alpha_composite(BG["table"])
    # suspense : la première partie s'efface pendant le silence de la voix (2,35 -> 2,67)
    out = 1 - ease_in_out(prog(t, CUE["suspense"], 0.32))
    if out > 0:
        ph = framed(kb_crop("table", prog(t, 0, 2.7), 1.0, 1.18, dx=0.04))
        place(c, ph, W / 2, 1230, alpha=ease_out(prog(t, 0, 0.35)) * out, scale=1 - 0.06 * (1 - out))
        slam(c, T["samedi"], W / 2, 470, t, CUE["samedi"], alpha=out)
        if out >= 1:
            wipe_up(c, T["question"], W / 2, 640, prog(t, CUE["question"], 0.3))
        else:
            place(c, T["question"], W / 2, 640, alpha=out)
    c.alpha_composite(Image.new("RGBA", (W, H), INK + (int(190 * (1 - out)),)))
    # la question, mot à mot, sur la voix
    slam(c, T["par"], W / 2, 600, t, CUE["par"])
    slam(c, T["quoi"], W / 2, 880, t, CUE["quoi"])
    slam(c, T["commencer"], W / 2, 1140, t, CUE["commencer"], big=1.8, dur=0.16)
    gold_rule(c, W / 2, 1280, 520, prog(t, CUE["commencer"] + 0.1, 0.4))
    light_leak(c, t, CUE["commencer"] - 0.05, 0.4)


def s_buffet(c, t):
    """4,1 – 7,05 s : « Buffet à volonté de 12h à 18h30 »."""
    lt = t - CUTS[0]
    if t < 5.6:
        c.alpha_composite(BG["buffet"])
        ph = framed(kb_crop("buffet", prog(t, CUTS[0], 1.5), 1.05, 1.25, dy=-0.1))
    else:
        c.alpha_composite(BG["toast"])
        ph = framed(kb_crop("toast", prog(t, 5.6, 1.5), 1.15, 1.0, dx=0.08))
    place(c, ph, W / 2, 1060)
    slam(c, T["buffet"], W / 2, 560, t, CUE["buffet"], big=1.35)
    gold_rule(c, W / 2, 680, 560, prog(t, CUE["buffet"] + 0.15, 0.5))
    wipe_up(c, T["horaire"], W / 2, 755, prog(t, CUE["horaires"], 0.35))
    light_leak(c, t, 5.6, 0.3)
    light_leak(c, lt, 0.0, 0.25)


def s_activites(c, t):
    """7,05 – 11,6 s : chaque activité apparaît quand Lola la prononce."""
    c.alpha_composite(BG["group"])
    c.alpha_composite(Image.new("RGBA", (W, H), INK + (120,)))
    place(c, T["apres"], W / 2, 400, alpha=ease_out(prog(t, CUTS[1], 0.3)))
    gold_rule(c, W / 2, 470, 300, prog(t, CUTS[1] + 0.1, 0.4))
    y0, step = 640, 190
    acts = CUE["act"]
    all_gold = t >= 10.95
    for i, ti in enumerate(acts):
        if t < ti - 0.02:
            continue
        nxt = acts[i + 1] if i + 1 < len(acts) else 99
        lay = T_ACT_GOLD[i] if (ti <= t < nxt or all_gold) else T_ACT[i]
        slam(c, lay, W / 2, y0 + i * step, t, ti, big=1.4, dur=0.13)
    light_leak(c, t, CUTS[1], 0.25)


def s_groupe(c, t):
    """11,6 – 15,4 s : « Le pass : 10.000 francs. Venez entre amis ou en famille. »"""
    c.alpha_composite(BG["group"])
    ph = framed(kb_crop("group", prog(t, CUTS[2], 3.8), 1.0, 1.14, dx=0.06, out_w=1040))
    place(c, ph, W / 2, 990)
    # badge : arrive sur « Le pass », le prix défile sur « 10.000 francs »
    k = prog(t, CUE["pass"], 0.3)
    if k > 0:
        cp = prog(t, CUE["prix"], CUE["prix_fin"] - CUE["prix"])
        val = int(round(10000 * ease_out(cp) / 500) * 500)
        txt = f"{val // 1000}.{val % 1000:03d}" if val >= 1000 else str(val)
        badge = pass_badge(txt, fcfa=cp >= 1)
        pop = 1 + 0.08 * math.sin(math.pi * prog(t, CUE["prix_fin"], 0.25))
        place(c, badge, W / 2, 1400, alpha=clamp(k * 2), scale=(0.7 + 0.3 * back_out(k)) * pop)
    light_leak(c, t, CUE["prix_fin"], 0.3)
    slam(c, T["amis"], W / 2, 470, t, CUE["amis"], big=1.35)
    slam(c, T["famille"], W / 2, 620, t, CUE["famille"], big=1.35)
    light_leak(c, t, CUTS[2], 0.25)


def s_final(c, t):
    """15,4 – 18 s : « Écrivez “BRUNCH” pour réserver. »"""
    lt = t - CUTS[3]
    c.alpha_composite(Image.new("RGBA", (W, H), INK + (255,)))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((W / 2 - 520, 120, W / 2 + 520, 960), fill=(120, 84, 20, 90))
    c.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    drift = int(60 * lt)
    c.alpha_composite(DECO, (-90 - drift % 90, H - DECO.height - 40))
    place(c, LOGO, W / 2, 270, alpha=ease_out(prog(lt, 0.0, 0.4)), scale=0.78 + 0.07 * ease_out(prog(lt, 0, 0.8)))
    place(c, T["wellbrunch"], W / 2, 545, alpha=ease_out(prog(lt, 0.0, 0.35)))
    place(c, T["tous"], W / 2, 660, alpha=ease_out(prog(lt, 0.15, 0.35)))
    gold_rule(c, W / 2, 715, 640, prog(lt, 0.15, 0.4), thick=2)
    slam(c, T["ecrivez"], W / 2, 825, t, CUE["ecrivez"], big=1.3)
    slam(c, T["brunch"], W / 2, 990, t, CUE["brunch"], big=1.8, dur=0.16)
    light_leak(c, t, CUE["brunch"] - 0.03, 0.35)
    wipe_up(c, T["reserver"], W / 2, 1125, prog(t, CUE["reserver"], 0.3))
    t1 = CUE["reserver"] + 0.25
    if t < t1 + 0.5:
        slam(c, T["tel1"], W / 2, 1230, t, t1, big=1.3)
    else:  # le numéro respire doucement jusqu'à la fin
        place(c, T["tel1"], W / 2, 1230, scale=1 + 0.025 * math.sin((t - t1 - 0.5) * 6))
    place(c, T["tel2"], W / 2, 1335, alpha=ease_out(prog(t, CUE["reserver"] + 0.5, 0.35)))
    place(c, T["adresse"], W / 2, 1420, alpha=ease_out(prog(t, CUE["reserver"] + 0.7, 0.35)))


# ---------------------------------------------------------------- sous-titres (voix off)
SUBS_ON = "--subs" in sys.argv
SUB_Y = 1610  # au-dessus de la zone de légende Instagram / Facebook
SUB_FONT = helv(42, bold=True)


def load_srt(path):
    def ts(x):
        h, m, rest = x.strip().split(":")
        sec, ms = rest.split(",")
        return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000
    subs = []
    for block in path.read_text(encoding="utf-8").strip().split("\n\n"):
        lines = block.strip().splitlines()
        a, b = lines[1].split("-->")
        subs.append((ts(a), ts(b), " ".join(lines[2:])))
    return subs


SUBS = load_srt(OUT / "voix-off.srt")
_SUB_CACHE = {}


def sub_layer(text):
    if text in _SUB_CACHE:
        return _SUB_CACHE[text]
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    words, lines, cur = text.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if d.textlength(trial, font=SUB_FONT) > 960 and cur:
            lines.append(cur)
            cur = wd
        else:
            cur = trial
    lines.append(cur)
    lh = 54
    tw = int(max(d.textlength(li, font=SUB_FONT) for li in lines))
    w, h = tw + 56, lh * len(lines) + 30
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dd = ImageDraw.Draw(lay)
    dd.rounded_rectangle((0, 0, w - 1, h - 1), radius=16, fill=(11, 9, 6, 170))
    dd.rectangle((0, 12, 4, h - 12), fill=GOLD + (255,))
    for i, li in enumerate(lines):
        lw = d.textlength(li, font=SUB_FONT)
        dd.text(((w - lw) / 2, 12 + i * lh), li, font=SUB_FONT, fill=WHITE)
    _SUB_CACHE[text] = lay
    return lay


def draw_sub(c, t):
    for a, b, text in SUBS:
        if a <= t < b:
            k = min(prog(t, a, 0.12), prog(b, t, 0.12) if t > b - 0.12 else 1.0)
            place(c, sub_layer(text), W / 2, SUB_Y, alpha=k)
            return

SCENES = [(0.0, CUTS[0], s_hook), (CUTS[0], CUTS[1], s_buffet), (CUTS[1], CUTS[2], s_activites),
          (CUTS[2], CUTS[3], s_groupe), (CUTS[3], DUR, s_final)]
XF = 0.12  # fondu très court : les coupes restent franches


def shake(c, t):
    """Secousse brève (0,18 s) sur les mots qui claquent."""
    for ti in IMPACTS:
        p = (t - ti) / 0.18
        if 0 <= p <= 1:
            amp = 14 * (1 - p)
            dx, dy = amp * math.sin(p * 37), amp * math.cos(p * 29)
            z = 1.025
            big = c.resize((int(W * z), int(H * z)), Image.BILINEAR)
            ox, oy = (big.width - W) / 2 + dx, (big.height - H) / 2 + dy
            return big.crop((int(ox), int(oy), int(ox) + W, int(oy) + H))
    return c


def frame(t):
    c = Image.new("RGBA", (W, H), INK + (255,))
    for i, (a, b, fn) in enumerate(SCENES):
        if a <= t < b or (i == len(SCENES) - 1 and t >= a):
            fn(c, t)
            # fondu vers la séquence suivante
            if i + 1 < len(SCENES) and t > b - XF:
                nxt = Image.new("RGBA", (W, H), INK + (255,))
                SCENES[i + 1][2](nxt, b)
                k = (t - (b - XF)) / XF
                c = Image.blend(c, nxt, ease_in_out(k))
            break
    c = shake(c, t)
    if SUBS_ON:
        draw_sub(c, t)
    # fondu au noir des 6 dernières images pour la boucle
    out = finish(c)
    if t > DUR - 0.2:
        out = (out * clamp((DUR - t) / 0.2)).astype(np.uint8)
    return out


def main():
    if "--stills" in sys.argv:
        for t in [1.9, 3.7, 5.3, 9.0, 12.6, 14.9, 17.2]:
            Image.fromarray(frame(t)).save(OUT / f"apercu-{t:04.1f}s.png")
        return
    name = "well-brunch-reel-18s-sous-titres" if SUBS_ON else "well-brunch-reel-18s"
    dst = OUT / f"{name}.mp4"
    silent = OUT / f".{name}-video.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "slow", "-crf", "21", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", str(silent)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for n in range(N):
        proc.stdin.write(frame(n / FPS).tobytes())
        if n % 60 == 0:
            print(f"{n}/{N}", flush=True)
    proc.stdin.close()
    proc.wait()
    mux_audio(silent, dst)
    silent.unlink()
    print("OK", dst)


VOICE = ROOT / "sources" / "voix-off-lola.mp3"
MUSIC = ROOT / "sources" / "musique-legere.wav"  # généré par music.py
VOICE_DELAY_MS = 150


def mux_audio(video, dst):
    """Voix off traitée + musique légère qui s'efface sous la voix (ducking), -14 LUFS."""
    fc = (
        f"[1:a]adelay={VOICE_DELAY_MS}|{VOICE_DELAY_MS},highpass=f=90,"
        "equalizer=f=3500:t=q:w=1.2:g=2,"
        "acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=2,"
        "pan=stereo|c0=c0|c1=c0,apad=whole_dur=18,asplit=2[v][key];"
        "[2:a]volume=0.5[m];"
        "[m][key]sidechaincompress=threshold=0.03:ratio=3:attack=25:release=350[md];"
        "[v][md]amix=inputs=2:duration=first:normalize=0,"
        "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]"
    )
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(VOICE),
                    "-i", str(MUSIC), "-filter_complex", fc, "-map", "0:v", "-map", "[a]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", str(DUR),
                    "-movflags", "+faststart", str(dst)], check=True)


if __name__ == "__main__":
    main()
