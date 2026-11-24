#!/usr/bin/env python3
"""Détourages pour le spot (rembg) :
  - elements/fillettes-brut.png : les fillettes de la photo HD (premier plan du travelling, titre derrière elles)
  - elements/miss-freeze.png    : image arrêtée de sources/video-foule-mousse-wbr.mp4 à 8,0 s, femme au centre détourée
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image
from rembg import new_session, remove

HERE = Path(__file__).resolve().parent
SEG = new_session("u2net_human_seg")

im = Image.open(HERE / "sources" / "photo-enfants-mousse.jpg").convert("RGB")
remove(im, session=SEG, post_process_mask=True).save(HERE / "elements" / "fillettes-brut.png")

t = float(sys.argv[1]) if len(sys.argv) > 1 else 8.0
raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(HERE / "sources" / "video-foule-mousse-wbr.mp4"),
                      "-frames:v", "1", "-vf", "scale=1080:1920:flags=lanczos", "-f", "image2pipe", "-vcodec", "png", "-"],
                     capture_output=True, check=True).stdout
import io  # noqa: E402
fr = Image.open(io.BytesIO(raw)).convert("RGB")
fr.save(HERE / "elements" / "miss-freeze-fond.jpg", quality=95)
box = (165, 520, 525, 1280)                      # la femme au bikini vert, face caméra
cut = remove(fr.crop(box), session=SEG, post_process_mask=True)
full = Image.new("RGBA", fr.size, (0, 0, 0, 0))
full.paste(cut, box[:2])
import numpy as np  # noqa: E402
a = np.asarray(full).copy()
a[720:1250, :220, 3] = 0       # personne derrière, à gauche
a[860:1130, 476:, 3] = 0       # bouée rouge, à droite
full = Image.fromarray(a, "RGBA")
full.save(HERE / "elements" / "miss-freeze.png")
print("OK")
