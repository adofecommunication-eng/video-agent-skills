#!/usr/bin/env python3
"""Refait uniquement le mixage audio des vidéos déjà rendues (image conservée).
Usage : python3 remix.py rendu/well-christmas-30s.mp4 rendu/well-christmas-30s-sous-titres.mp4"""
import sys
from pathlib import Path

import spot

for f in sys.argv[1:]:
    src = Path(f)
    tmp = src.with_name("." + src.name)
    src.rename(tmp)
    spot.mux(tmp, src)
    tmp.unlink()
    print("OK", src)
