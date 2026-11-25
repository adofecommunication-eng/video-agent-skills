#!/usr/bin/env python3
"""Publicité « SPLASH PARTY » (20 s) — flyer animé, même écriture motion design que la référence
fournie par le client (flyer animé de resort) : apparition du titre avec flou, mot écrit à la main
(ici en Anton, révélé de gauche à droite), date qui monte, bandeau qui se déroule, bloc qui remonte,
infos qui s'inscrivent ligne à ligne, pastille, macaron qui se décolle, flous de mouvement réguliers sur le titre.
Contenu : uniquement les informations du flyer Splash Party. Charte : textes blancs, beige doré #C39E6E,
Anton + Helvetica, logo WBR blanc. Rendu 1080x1920 puis livraison 4K.
Usage : python3 musique.py && python3 pub.py [--stills t1 t2 ...]
"""
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "well-brunch-reel"))
import render as R  # noqa: E402  (Anton, Helvetica, logo, calques texte)
sys.path.insert(0, str(HERE.parent / "spot"))

OUT = HERE / "rendu"
OUT.mkdir(exist_ok=True)
W, H, FPS = 1080, 1920, 30
DUR = 20.1                       # même durée que la vidéo de référence
N = int(round(DUR * FPS))
WHITE = (255, 255, 255)
SAND = (195, 158, 110)
clamp, prog, ease_out, ease_in_out, back_out = R.clamp, R.prog, R.ease_out, R.ease_in_out, R.back_out


def tl(text, font, **kw):
    kw.setdefault("shadow", True)
    return R.text_layer(text, font, **kw)


def place(c, lay, cx, cy, alpha=1.0, scale=1.0, angle=0.0):
    if alpha <= 0.003:
        return
    if angle:
        lay = lay.rotate(angle, resample=Image.BICUBIC, expand=True)
    R.place(c, lay, cx, cy, alpha=alpha, scale=scale)


def put_left(c, lay, x, cy, alpha=1.0):
    if alpha <= 0.003:
        return
    if alpha < 1:
        lay = lay.copy()
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * alpha)))
    c.alpha_composite(lay, (int(x - 40), int(cy - lay.height / 2)))


def blur_in(c, lay, cx, cy, t, t0, dur=0.5):
    """Apparition avec flou qui se dissipe (comme le titre de la référence)."""
    p = prog(t, t0, dur)
    if p <= 0:
        return
    e = ease_out(p)
    l2 = lay.filter(ImageFilter.GaussianBlur(14 * (1 - e))) if p < 1 else lay
    place(c, l2, cx, cy, alpha=e, scale=1.06 - 0.06 * e)


def wipe_lr(c, lay, cx, cy, t, t0, dur=0.8):
    """Révélation de gauche à droite (équivalent du mot écrit à la main)."""
    p = prog(t, t0, dur)
    if p <= 0:
        return
    w = max(1, int(lay.width * ease_in_out(p)))
    part = lay.crop((0, 0, w, lay.height))
    c.alpha_composite(part, (int(cx - lay.width / 2), int(cy - lay.height / 2)))


def rise(c, lay, cx, cy, t, t0, dur=0.35, dy=40, left=False):
    p = prog(t, t0, dur)
    if p <= 0:
        return
    e = ease_out(p)
    if left:
        put_left(c, lay, cx, cy + dy * (1 - e), alpha=e)
    else:
        place(c, lay, cx, cy + dy * (1 - e), alpha=e)


def typed(c, text, font, x, cy, t, t0, cps=38, fill=WHITE):
    """Texte qui s'inscrit lettre par lettre."""
    n = int((t - t0) * cps)
    if n <= 0:
        return
    put_left(c, tl(text[:n], font, fill=fill, shadow=True), x, cy)


# ---------------------------------------------------------------- fond : la photo du flyer
def background():
    im = Image.open(HERE.parent / "spot" / "sources" / "photo-enfants-mousse.jpg").convert("RGB")
    im = im.crop((270, 0, 1395, 2000)).resize((W, H), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32)
    y = np.arange(H)[:, None, None] / H
    top = np.clip(1 - y / 0.32, 0, 1) ** 1.4 * 0.62           # haut assombri (titre lisible)
    bot = np.clip((y - 0.5) / 0.38, 0, 1) ** 1.2 * 0.86        # bas très sombre (infos lisibles)
    a = a * (1 - np.maximum(top, bot)) + np.array([8, 12, 20]) * np.maximum(top, bot)
    lum = a.mean(axis=2, keepdims=True)
    a = lum + (a - lum) * 1.08
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


BG = background()
LOGO = R.LOGO.copy()
LOGO.paste(Image.new("RGBA", LOGO.size, WHITE + (255,)), (0, 0), LOGO.getchannel("A"))
LOGO = LOGO.resize((int(LOGO.width * 0.42), int(LOGO.height * 0.42)), Image.LANCZOS)

A, Hh = R.anton, (lambda s: R.helv(s, bold=True))
Hr = lambda s: R.helv(s, bold=False)  # noqa: E731
L = {
    "organise": tl("W E L L B E I N G   R E S O R T   O R G A N I S E", Hh(20)),
    "splash": tl("SPLASH", A(250), tracking=2),
    "party": tl("PARTY", A(200), tracking=10),
    "date": tl("SAMEDI 05.12 / 08H – 18H", A(78), tracking=1),
    "lieu": tl("Cocody Riviera 3, Route M'Badon", Hr(32)),
    "prog1": tl("PISCINE / MISS SPLASH / KARAOKÉ", Hh(40)),
    "prog2": tl("CONCOURS DE DANSES", Hh(40)),
    "prog3": tl("BILLARD · BABY-FOOT · DJ · JEUX", Hh(34)),
    "entrees": tl("E N T R É E", Hh(22)),
    "info": tl("Infos et réservations", Hh(27)),
}


def bar_layer(text, size=27):
    lab = R.text_layer(text, Hh(size), fill=WHITE, shadow=False, tracking=3)
    w, h = lab.width - 80 + 60, lab.height - 80 + 20
    b = Image.new("RGBA", (w, h), SAND + (255,))
    b.alpha_composite(lab, ((w - lab.width) // 2, (h - lab.height) // 2 + 2))
    return b


BAR = bar_layer("PISCINE  ·  BAIN DE MOUSSE  ·  AMBIANCE DJ")


def pill(text):
    lab = R.text_layer(text, Hh(20), fill=WHITE, shadow=False, tracking=2)
    w, h = lab.width - 80 + 34, 38
    p = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(p).rounded_rectangle((0, 0, w - 1, h - 1), radius=8, fill=SAND + (255,))
    p.alpha_composite(lab, ((w - lab.width) // 2, (h - lab.height) // 2 + 1))
    return p


PILL = pill("PISCINE INCLUSE")


def sticker():
    """Macaron rond (comme « DRESS CODE ALL WHITE ») : ENTRÉE 5000F = 01 RAFRAÎCHISSEMENT."""
    s = 300
    st = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(st)
    d.ellipse((0, 0, s - 1, s - 1), fill=(248, 246, 242, 255))
    d.ellipse((10, 10, s - 11, s - 11), outline=SAND + (255,), width=4)
    for txt, font, y, col in [("ENTRÉE", Hh(26), 78, SAND), ("5000F", A(96), 148, (30, 26, 22)),
                              ("= 01 RAFRAÎCHISSEMENT", Hh(17), 222, SAND)]:
        lay = R.text_layer(txt, font, fill=col, shadow=False, tracking=1)
        st.alpha_composite(lay, ((s - lay.width) // 2, int(y - lay.height / 2)))
    sh = Image.new("RGBA", (s + 60, s + 60), (0, 0, 0, 0))
    m = Image.new("L", (s, s), 0)
    ImageDraw.Draw(m).ellipse((0, 0, s - 1, s - 1), fill=150)
    sh.paste(Image.new("RGBA", (s, s), (0, 0, 0, 255)), (34, 40), m)
    sh = sh.filter(ImageFilter.GaussianBlur(12))
    sh.alpha_composite(st, (30, 30))
    return sh


STICKER = sticker()
PHONE = Image.new("RGBA", (30, 30), (0, 0, 0, 0))
ImageDraw.Draw(PHONE).ellipse((0, 0, 29, 29), fill=(37, 211, 102, 255))
ImageDraw.Draw(PHONE).arc((8, 7, 22, 23), 100, 300, fill=WHITE + (255,), width=4)

GLITCHES = [5.1, 8.05, 12.55, 15.55, 18.05]   # flous de mouvement réguliers sur le titre (comme la référence)
rng = np.random.default_rng(4)
BUBBLES = [(rng.uniform(60, 1020), rng.uniform(0, H), rng.uniform(6, 20), rng.uniform(20, 55), rng.uniform(0, 6))
           for _ in range(26)]


def title_smear(lay, k):
    if k <= 0:
        return lay
    out = lay.copy()
    for dx in (12, 24, 36):
        sh = Image.new("RGBA", lay.size, (0, 0, 0, 0))
        sh.alpha_composite(lay, (int(dx * k), 0))
        out = Image.blend(out, sh, 0.35)
    return out.filter(ImageFilter.BoxBlur(3 * k))


def frame(t):
    c = BG.copy()
    # bulles qui montent doucement (remplacent le soleil de la référence), à partir de 5 s
    if t > 4.9:
        d = ImageDraw.Draw(c)
        a = clamp((t - 4.9) * 2)
        for x, y, r, sp, ph in BUBBLES:
            yy = (y - sp * t) % H
            if yy < 1000:
                continue
            xx = x + 10 * math.sin(ph + t * 1.5)
            d.ellipse((xx - r, yy - r, xx + r, yy + r), outline=(255, 255, 255, int(120 * a)), width=2)
    # en-tête
    place(c, LOGO, W / 2, 95, alpha=ease_out(prog(t, 0.0, 0.4)))
    place(c, L["organise"], W / 2, 205, alpha=ease_out(prog(t, 0.1, 0.4)))
    # titre
    k = 0.0
    for g in GLITCHES:
        if 0 <= t - g < 0.3:
            k = max(k, math.sin(math.pi * (t - g) / 0.3))
    sp = title_smear(L["splash"], k) if k > 0 else L["splash"]
    blur_in(c, sp, W / 2, 360, t, 0.15, 0.55)
    wipe_lr(c, L["party"], W / 2, 540, t, 0.5, 0.8)
    # bloc central : apparaît plus bas puis remonte (1,5 → 2,2 s) pour laisser la place aux infos
    off = 200 * (1 - ease_in_out(prog(t, 1.5, 0.7)))
    y0 = 1130 + off
    rise(c, L["date"], W / 2, y0, t, 1.0)
    rise(c, L["lieu"], W / 2, y0 + 62, t, 1.1)
    p = prog(t, 1.15, 0.35)
    if p > 0:
        w = max(1, int(BAR.width * ease_out(p)))
        c.alpha_composite(BAR.crop((0, 0, w, BAR.height)), (int(W / 2 - BAR.width / 2), int(y0 + 125 - BAR.height / 2)))
    rise(c, L["prog1"], W / 2, y0 + 195, t, 1.3)
    rise(c, L["prog2"], W / 2, y0 + 245, t, 1.42)
    rise(c, L["prog3"], W / 2, y0 + 295, t, 1.54)
    # infos du bas, ligne par ligne
    x = 64
    rise(c, L["entrees"], x, 1500, t, 2.2, left=True, dy=20)
    typed(c, "Enfant & Adulte : 5.000 F", Hh(32), x, 1548, t, 2.35)
    if t > 3.7:
        pp = prog(t, 3.7, 0.25)
        put_left(c, PILL.resize((max(1, int(PILL.width * back_out(pp, 2))), PILL.height)), x + 470, 1550)
    typed(c, "+ 01 rafraîchissement  ·  accès à la piscine", Hr(26), x, 1594, t, 2.7, cps=55)
    rise(c, L["info"], x, 1660, t, 3.0, left=True, dy=20)
    if t > 3.2:
        c.alpha_composite(PHONE, (x, 1695))
    typed(c, "07 47 79 95 07  /  05 66 92 33 91", Hh(30), x + 42, 1710, t, 3.2, cps=45)
    typed(c, "Commander la nourriture sur place", Hr(24), x, 1772, t, 3.45, cps=50)
    # macaron qui se décolle (5,0 s) puis flotte
    ps = prog(t, 5.0, 0.45)
    if ps > 0:
        sc = 0.3 + 0.7 * back_out(ps, 1.8)
        ang = -35 * (1 - ease_out(ps)) + 6 * math.sin(t * 1.6)
        place(c, STICKER, 880, 1600 + 6 * math.sin(t * 2), alpha=clamp(ps * 3), scale=sc * 0.9, angle=ang)
    return np.asarray(c.convert("RGB"))


def mux(video, dst):
    music = HERE / "musique.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(music),
                    "-filter_complex", "[1:a]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-t", str(DUR),
                    "-movflags", "+faststart", str(dst)], check=True)


def export_4k(src, dst):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
                    "-vf", "scale=2160:3840:flags=lanczos,unsharp=5:5:0.5:5:5:0.0",
                    "-c:v", "libx264", "-preset", "slow", "-profile:v", "high", "-level", "5.2",
                    "-b:v", "20M", "-maxrate", "24M", "-bufsize", "40M", "-pix_fmt", "yuv420p",
                    "-c:a", "copy", "-movflags", "+faststart", str(dst)], check=True)


def main():
    if "--stills" in sys.argv:
        for t in [float(x) for x in sys.argv[sys.argv.index("--stills") + 1:]]:
            Image.fromarray(frame(t)).save(OUT / f"apercu-{t:05.2f}s.png")
        return
    silent = OUT / ".video.mp4"
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                             "-crf", "14", "-pix_fmt", "yuv420p", str(silent)], stdin=subprocess.PIPE)
    for n in range(N):
        proc.stdin.write(frame(n / FPS).tobytes())
    proc.stdin.close()
    proc.wait()
    hd = OUT / ".pub-hd.mp4"
    mux(silent, hd)
    export_4k(hd, OUT / "splash-party-pub-20s-4k.mp4")
    silent.unlink()
    hd.unlink()
    print("OK", OUT / "splash-party-pub-20s-4k.mp4")


if __name__ == "__main__":
    main()
