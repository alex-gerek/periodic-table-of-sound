"""Is the vibrato detector blind, or do these AI vocals have no vibrato?

Known vibrato is written into the real lead vocal stems: a delay line whose delay swings
as A*sin(2*pi*f*t) shifts the pitch by the factor 1 - 2*pi*f*A*cos(2*pi*f*t). The rate f
and the depth in cents are therefore known exactly, on a real voice. The detector must find
1/f where the depth is large enough, and nothing where there is none.

Writes vibrato_injection.md next to this file.
"""
import os
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
from pts import periodicity as P  # noqa: E402

TRACKS = {
    "GRAVITY": os.path.join(ROOT, "data", "stems", "gravity"),
    "Metro": os.environ.get("PTS_METRO_STEMS", os.path.join(ROOT, "data", "stems", "metro")),
    "Pure voltage": os.path.join(ROOT, "data", "stems", "pure_voltage"),
}
CASES = [(0, 5.5), (15, 5.5), (30, 5.5), (60, 5.5), (60, 4.5), (60, 7.0)]   # (depth in cents, rate in Hz)


def add_vibrato(x, sr, cents, rate):
    if cents == 0:
        return x
    peak_ratio = 2 ** (cents / 1200) - 1             # largest relative pitch change
    amp = peak_ratio / (2 * np.pi * rate)            # delay swing in seconds
    t = np.arange(len(x)) / sr
    src = (t - amp * (1 + np.sin(2 * np.pi * rate * t))) * sr
    return np.interp(src, np.arange(len(x)), x)


def main():
    rows = []
    for name, folder in TRACKS.items():
        f = next(f for f in os.listdir(folder) if "lead vocal" in f.lower())
        x, sr = sf.read(os.path.join(folder, f), always_2d=True)
        x = P.mono(x)
        for cents, rate in CASES:
            per, runs = P.vibrato(add_vibrato(x, sr, cents, rate), sr, tau_lo=0.03, tau_hi=1.0)
            found = None if per.tau is None else 1 / per.tau
            ok = (cents == 0 and (per.tau is None or per.strength < 0.3)) or \
                 (cents > 0 and found is not None and abs(found / rate - 1) < 0.05)
            rows.append((name, cents, rate, found, per.strength, runs, ok))
            print(rows[-1], flush=True)
    L = ["# Known vibrato written into the real lead vocals", "",
         "Free search over 30 ms – 1 s of the pitch track. Pass: the rate is found within 5%; with no vibrato added, no peak stronger than r = 0.3.", "",
         "| Track | Depth | Rate written | Rate found | r | Long voiced runs | Pass |", "|---|---|---|---|---|---|---|"]
    for name, cents, rate, found, r, runs, ok in rows:
        L.append(f"| {name} | {cents} cents | {'none' if cents == 0 else f'{rate} Hz'} | "
                 f"{'–' if found is None else f'{found:.2f} Hz'} | {r:.2f} | {runs} | {'✓' if ok else '✗'} |")
    with open(os.path.join(HERE, "vibrato_injection.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
