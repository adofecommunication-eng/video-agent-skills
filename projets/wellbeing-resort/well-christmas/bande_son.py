#!/usr/bin/env python3
"""Monte le son fourni par le client (sources/son-montage-client.mp3, 24,8 s, ~123 BPM)
sous le spot de 30 s, en calant sa reprise (coupure 5,88 -> 7,29 s, retour à 7,29 s)
deux fois sur le montage :
  - partie A : la reprise tombe sur « PISCINE ! »   (vidéo = morceau - 4,62)
  - partie B : la reprise tombe sur « GRATUITE !!! » (vidéo = morceau + 18,58)
Raccord A -> B vers 19,1 s (fondu court), fondu de sortie à la fin.
Sorties : sources/musique-montage.wav + sources/temps-forts.json (temps forts du morceau
dans le temps de la vidéo, pour les pulsations d'image).
"""
import json
import subprocess
from pathlib import Path

import numpy as np

import spot as S

HERE = Path(__file__).resolve().parent
SRC = HERE / "sources" / "son-montage-client.mp3"
SR = 48000
DUR = S.DUR
DROP = 7.29                                   # reprise du morceau (s)
OFF_A = S.CUE["piscine"] - DROP               # vidéo = morceau + OFF_A
OFF_B = S.CUE["gratuite"] - DROP
JOIN = 0.5 + OFF_B                            # début de B (on saute le silence initial du morceau)
XF = 0.12


def load():
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(SRC), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype="<f4").reshape(-1, 2).astype(np.float64)


def segment(x, off, v0, v1):
    """Échantillons du morceau qui tombent sur la vidéo entre v0 et v1."""
    out = np.zeros((int(round((v1 - v0) * SR)), 2))
    t0 = v0 - off
    i0 = int(round(t0 * SR))
    n = len(out)
    src_a, dst_a = max(0, i0), max(0, -i0)
    m = min(n - dst_a, len(x) - src_a)
    if m > 0:
        out[dst_a:dst_a + m] = x[src_a:src_a + m]
    return out


def beats(x):
    """Temps forts (grosse caisse) : pics de l'enveloppe des graves."""
    mono = x.mean(axis=1)
    k = int(SR * 0.01)
    # passe-bas simple (moyenne glissante ~ 150 Hz) puis énergie par tranche de 10 ms
    low = np.convolve(mono, np.ones(160) / 160, mode="same")
    e = np.array([np.sqrt(np.mean(low[i:i + k] ** 2)) for i in range(0, len(low) - k, k)])
    e = e / (e.max() + 1e-9)
    on = np.maximum(0, np.diff(e, prepend=0))
    thr = np.percentile(on, 97)
    times, last = [], -1
    for i, v in enumerate(on):
        t = i * 0.01
        if v > thr and t - last > 0.3 and e[i] > 0.25:
            times.append(t)
            last = t
    return times


def main():
    x = load()
    a = segment(x, OFF_A, 0.0, JOIN + XF)
    b = segment(x, OFF_B, JOIN, DUR)
    n = int(round(DUR * SR))
    bed = np.zeros((n, 2))
    bed[:len(a)] += a
    j = int(round(JOIN * SR))
    f = int(XF * SR)
    fade_out = np.linspace(1, 0, f)[:, None]
    bed[j:j + f] *= fade_out                 # fin de A en fondu
    fade_in = np.ones((len(b), 1))
    fade_in[:f, 0] = np.linspace(0, 1, f)
    bed[j:j + len(b)] += b * fade_in
    end = int((DUR - 1.3) * SR)
    bed[end:] *= np.linspace(1, 0, n - end)[:, None] ** 1.5
    bed /= np.abs(bed).max() / 0.85

    tb = beats(x)
    vt = sorted({round(t + OFF_A, 3) for t in tb if 0 <= t + OFF_A < JOIN}
                | {round(t + OFF_B, 3) for t in tb if JOIN <= t + OFF_B < DUR - 1.0})
    json.dump(vt, open(HERE / "sources" / "temps-forts.json", "w"))

    pcm = (np.clip(bed, -1, 1) * 32767).astype("<i2")
    import wave
    with wave.open(str(HERE / "sources" / "musique-montage.wav"), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"OK : A décalé de {OFF_A:+.2f} s, B de {OFF_B:+.2f} s, raccord à {JOIN:.2f} s, {len(vt)} temps forts")


if __name__ == "__main__":
    main()
