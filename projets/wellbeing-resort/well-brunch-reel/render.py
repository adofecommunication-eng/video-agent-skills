#!/usr/bin/env python3
"""Reel « Well Brunch » — Wellbeing Resort (WBR) — 18 s, 9:16, 1080x1920, 30 i/s.

Version motion design construite à partir du flyer officiel (sources/flyer-well-brunch.png).
Usage :  python3 render.py            -> rendu/well-brunch-reel-18s.mp4
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


def script(size):
    return ImageFont.truetype(str(F / "KaushanScript-Regular.ttf"), size)


def mont(size, weight=600):
    f = ImageFont.truetype(str(F / "Montserrat.ttf"), size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


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


# ---------------------------------------------------------------- textes pré-calculés
T = {
    "samedi": text_layer("SAMEDI,", anton(150)),
    "question": text_layer("UNE SEULE QUESTION :", mont(46, 700), tracking=6),
    "parquoi": text_layer("PAR QUOI", anton(230)),
    "commencer": text_layer("commencer ?", script(190), gold=True),
    "buffet": text_layer("BUFFET À VOLONTÉ", anton(150)),
    "horaire": text_layer("SAMEDI  ·  12H – 18H30", mont(52, 700), gold=True, tracking=4),
    "trinque": text_layer("on trinque, on partage", script(96), gold=True),
    "apres": text_layer("ET APRÈS LE BUFFET ?", mont(44, 700), gold=True, tracking=8),
    "amis": text_layer("ENTRE AMIS", anton(140)),
    "famille": text_layer("ou en famille", script(120), gold=True),
    "wellbrunch": text_layer("Well Brunch", script(190), gold=True),
    "ecrivez": text_layer("ÉCRIVEZ « BRUNCH »", anton(118)),
    "au": text_layer("AU", mont(40, 700), tracking=8),
    "tel1": text_layer("07 47 79 95 07", anton(130), gold=True),
    "tel2": text_layer("05 66 92 33 91", mont(48, 600)),
    "adresse": text_layer("COCODY RIVIERA 3  ·  ROUTE M'BADON", mont(34, 600), tracking=3),
    "tous": text_layer("TOUS LES SAMEDIS  ·  12H – 18H30", mont(34, 700), gold=True, tracking=3),
}
ACTIVITES = ["PISCINE", "BABY-FOOT", "BILLARD", "KARAOKÉ", "DJ MIXTE"]
T_ACT = [text_layer(a, anton(150)) for a in ACTIVITES]
T_ACT_GOLD = [text_layer(a, anton(150), gold=True) for a in ACTIVITES]


def pass_badge():
    lab = text_layer("PASS : 10.000", anton(110), fill=INK, shadow=False)
    cur = text_layer("FCFA", anton(56), fill=INK, shadow=False)
    w, h = lab.width + cur.width - 40, 170
    b = gradient_fill((w, h), GOLD_STOPS).convert("RGBA")
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius=18, fill=255)
    b.putalpha(m)
    b.alpha_composite(lab, (0, (h - lab.height) // 2 + 4))
    b.alpha_composite(cur, (lab.width - 70, (h - lab.height) // 2 - 14))
    return b


T["pass"] = pass_badge()
DECO = deco_pattern(W + 180)


# ---------------------------------------------------------------- séquences
def s_hook(c, t):
    """0 – 2,4 s : accroche. Table en plan large, question en typographie."""
    c.alpha_composite(BG["table"])
    p = prog(t, 0, 2.6)
    ph = framed(kb_crop("table", p, 1.0, 1.18, dx=0.04))
    place(c, ph, W / 2, 1290, alpha=ease_out(prog(t, 0, 0.35)))
    wipe_up(c, T["samedi"], W / 2, 380, prog(t, 0.05, 0.4))
    place(c, T["question"], W / 2, 510, alpha=ease_out(prog(t, 0.35, 0.35)))
    wipe_up(c, T["parquoi"], W / 2, 680, prog(t, 0.65, 0.4))
    k = prog(t, 0.95, 0.45)
    place(c, T["commencer"], W / 2, 880, alpha=k, scale=0.85 + 0.15 * back_out(k) if k > 0 else 1)
    gold_rule(c, W / 2, 1030, 420, prog(t, 0.8, 0.5))


def s_buffet(c, t):
    """2,4 – 6 s : gros plan buffet puis verres qui trinquent."""
    lt = t - 2.4
    if lt < 1.9:
        c.alpha_composite(BG["buffet"])
        ph = framed(kb_crop("buffet", prog(lt, 0, 1.9), 1.05, 1.25, dy=-0.1))
    else:
        c.alpha_composite(BG["toast"])
        ph = framed(kb_crop("toast", prog(lt, 1.9, 1.7), 1.15, 1.0, dx=0.08))
    place(c, ph, W / 2, 1010)
    wipe_up(c, T["buffet"], W / 2, 560, prog(lt, 0.1, 0.45))
    gold_rule(c, W / 2, 680, 560, prog(lt, 0.4, 0.5))
    place(c, T["horaire"], W / 2, 750, alpha=ease_out(prog(lt, 0.5, 0.4)))
    k = prog(lt, 2.1, 0.5)
    place(c, T["trinque"], W / 2, 1400, alpha=k, scale=0.9 + 0.1 * ease_out(k))
    light_leak(c, lt, 1.75)


def s_activites(c, t):
    """6 – 12 s : les activités tombent une à une et forment la liste."""
    lt = t - 6.0
    c.alpha_composite(BG["group"])
    c.alpha_composite(Image.new("RGBA", (W, H), INK + (120,)))
    place(c, T["apres"], W / 2, 380, alpha=ease_out(prog(lt, 0.0, 0.4)))
    gold_rule(c, W / 2, 440, 300, prog(lt, 0.15, 0.5))
    y0, step = 640, 190
    for i in range(5):
        ti = 0.35 + i * 1.0
        p = prog(lt, ti, 0.45)
        if p <= 0:
            continue
        active = ti <= lt < ti + 1.0 or (i == 4 and lt >= ti)
        lay = T_ACT_GOLD[i] if active and lt < 5.4 else T_ACT[i]
        sc = 1.0 + 0.12 * (1 - ease_out(prog(lt, ti, 0.35)))
        if p < 1:
            wipe_up(c, lay, W / 2, y0 + i * step, p)
        else:
            place(c, lay, W / 2, y0 + i * step, scale=sc)
    # final : la liste entière passe en or et pulse
    if lt >= 5.4:
        k = prog(lt, 5.4, 0.4)
        for i in range(5):
            place(c, T_ACT_GOLD[i], W / 2, y0 + i * step, alpha=k)
    light_leak(c, lt, 0.0, 0.3)


def s_groupe(c, t):
    """12 – 15 s : groupe d'amis qui rit + pass."""
    lt = t - 12.0
    c.alpha_composite(BG["group"])
    ph = framed(kb_crop("group", prog(lt, 0, 3.0), 1.0, 1.14, dx=0.06, out_w=1040))
    place(c, ph, W / 2, 990)
    wipe_up(c, T["amis"], W / 2, 470, prog(lt, 0.1, 0.45))
    place(c, T["famille"], W / 2, 610, alpha=ease_out(prog(lt, 0.45, 0.4)))
    k = prog(lt, 0.9, 0.5)
    if k > 0:
        place(c, T["pass"], W / 2, 1390, alpha=clamp(k * 2), scale=0.7 + 0.3 * back_out(k))
    light_leak(c, lt, 0.0, 0.3)


def s_final(c, t):
    """15 – 18 s : carte finale, logo or, appel à l'action, numéro."""
    lt = t - 15.0
    c.alpha_composite(Image.new("RGBA", (W, H), INK + (255,)))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((W / 2 - 520, 120, W / 2 + 520, 960), fill=(120, 84, 20, 90))
    c.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    drift = int(60 * lt)
    c.alpha_composite(DECO, (-90 - drift % 90, H - DECO.height - 40))
    place(c, LOGO, W / 2, 330, alpha=ease_out(prog(lt, 0.0, 0.5)), scale=0.92 + 0.08 * ease_out(prog(lt, 0, 0.8)))
    k = prog(lt, 0.2, 0.5)
    place(c, T["wellbrunch"], W / 2, 620, alpha=k, scale=0.9 + 0.1 * ease_out(k))
    place(c, T["tous"], W / 2, 755, alpha=ease_out(prog(lt, 0.45, 0.4)))
    gold_rule(c, W / 2, 815, 640, prog(lt, 0.5, 0.5), thick=2)
    wipe_up(c, T["ecrivez"], W / 2, 920, prog(lt, 0.7, 0.45))
    place(c, T["au"], W / 2, 1035, alpha=ease_out(prog(lt, 0.95, 0.3)))
    k = prog(lt, 1.05, 0.45)
    pulse = 1 + 0.025 * math.sin(max(0, lt - 1.6) * 6) if lt > 1.6 else 1
    place(c, T["tel1"], W / 2, 1140, alpha=k, scale=(0.85 + 0.15 * back_out(k)) * pulse if k > 0 else 1)
    place(c, T["tel2"], W / 2, 1260, alpha=ease_out(prog(lt, 1.3, 0.4)))
    place(c, T["adresse"], W / 2, 1345, alpha=ease_out(prog(lt, 1.5, 0.4)))


SCENES = [(0.0, 2.4, s_hook), (2.4, 6.0, s_buffet), (6.0, 12.0, s_activites),
          (12.0, 15.0, s_groupe), (15.0, 18.0, s_final)]
XF = 0.2  # fondu enchaîné entre séquences


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
    # fondu au noir des 6 dernières images pour la boucle
    out = finish(c)
    if t > DUR - 0.2:
        out = (out * clamp((DUR - t) / 0.2)).astype(np.uint8)
    return out


def main():
    if "--stills" in sys.argv:
        for t in [1.8, 3.6, 5.2, 8.6, 11.8, 13.8, 17.0]:
            Image.fromarray(frame(t)).save(OUT / f"apercu-{t:04.1f}s.png")
        return
    dst = OUT / "well-brunch-reel-18s.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "slow", "-crf", "21", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", str(dst)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for n in range(N):
        proc.stdin.write(frame(n / FPS).tobytes())
        if n % 60 == 0:
            print(f"{n}/{N}", flush=True)
    proc.stdin.close()
    proc.wait()
    print("OK", dst)


if __name__ == "__main__":
    main()
