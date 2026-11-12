"""The valid region of the envelope reading, fixed on the development grid (v2) before the held-out run.

A case (true time T, window w, carrier, f0, SNR) is inside the region when:
  tonal carrier (sine or harmonic):  w <= T/4  and  w * f0 >= 2  and
                                     (SNR = infinity, or SNR >= 20 dB with w >= T/50 and w >= 2 ms)
  noise carrier:                     w <= T/4  and  w >= 10 ms  and  SNR >= 20 dB
Additive noise below 20 dB SNR is outside the region.
"""
import numpy as np


def inside(T, w, carrier, f0, snr):
    if np.isfinite(snr) and snr < 20:
        return False
    if carrier == "noise":
        return w <= T / 4 and w >= 0.01
    if not (w <= T / 4 and w * f0 >= 2):
        return False
    return (not np.isfinite(snr)) or (w >= T / 50 and w >= 0.002)


def inside_constant(w, carrier, f0, snr):
    if np.isfinite(snr) and snr < 20:
        return False
    if carrier == "noise":
        return w >= 0.01
    return w * f0 >= 2 and ((not np.isfinite(snr)) or w >= 0.002)
