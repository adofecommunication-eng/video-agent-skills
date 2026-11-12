#!/usr/bin/env python3
"""Refait uniquement le mixage audio d'un rendu existant (sans recalculer l'image).
Usage : python3 remix.py rendu/well-brunch-reel-18s.mp4 [...]"""
import sys
from pathlib import Path

sys.argv = [sys.argv[0]] + sys.argv[1:]
import render  # noqa: E402

for f in sys.argv[1:]:
    src = Path(f)
    tmp = src.with_name("." + src.name)
    src.rename(tmp)
    render.mux_audio(tmp, src)
    tmp.unlink()
    print("OK", src)
