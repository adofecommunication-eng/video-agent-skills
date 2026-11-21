#!/usr/bin/env python3
"""Détoure les éléments du flyer (animateur, boules, guirlande, cadeaux, sapins) -> elements/*.png
Nécessite : pip install "rembg[cpu]" (modèles téléchargés au premier lancement)."""
from pathlib import Path
from PIL import Image
from rembg import new_session, remove

HERE = Path(__file__).resolve().parent
SRC = Image.open(HERE / "sources" / "flyer-well-christmas.webp").convert("RGB")
OUT = HERE / "elements"
OUT.mkdir(exist_ok=True)

HUMAN = new_session("u2net_human_seg")
GEN = new_session("isnet-general-use")

PIECES = {
    "animateur": ((180, 820, 1300, 1578), HUMAN),
    "boule": ((1130, 230, 1340, 485), GEN),
}

for name, (box, sess) in PIECES.items():
    im = remove(SRC.crop(box), session=sess, post_process_mask=True)
    im = im.crop(im.getbbox())
    im.save(OUT / f"{name}.png")
    print(name, im.size)
