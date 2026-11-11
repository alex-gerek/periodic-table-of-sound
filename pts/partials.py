"""Partial tracks: follow single spectral lines through time.

A waveform pitch tracker needs one voice. In a mix (a violin over a piano) it locks onto
neither. A spectral line, however, belongs to one source: a vibrating string moves all its
harmonics together, a piano string keeps them straight. So the lines are tracked one by
one and each line's own movement is measured.

Per frame: local maxima of the log spectrum, frequency refined by a parabola through
three bins. Peaks are linked frame to frame to the nearest open track within
`max_step_cents`; a track may skip one frame. Only numpy is used.
"""
from __future__ import annotations

import numpy as np

from .periodicity import mono, frames, autocorr, pick_period, running_median


def partial_tracks(x, sr, size=4096, hop_s=0.01, fmin=150.0, fmax=5000.0, rel_db=-45.0,
                   max_step_cents=40.0, min_len_s=0.6, chunk=2048):
    """Return a list of (start_frame, freqs in Hz, levels in dB) and the frame rate."""
    x = mono(x)
    hop = int(round(hop_s * sr))
    fs = sr / hop
    freqs_bin = sr / size
    lo, hi = int(fmin / freqs_bin), int(fmax / freqs_bin)
    win = np.hanning(size)
    xp = np.pad(x, (size // 2, size // 2))
    n_frames = 1 + (len(xp) - size) // hop
    open_tracks, done = [], []          # track: [start, [f...], [db...], last_seen]
    gmax = None
    for c0 in range(0, n_frames, chunk):
        idx = np.arange(c0, min(n_frames, c0 + chunk))
        F = xp[(idx * hop)[:, None] + np.arange(size)[None, :]] * win
        L = 20 * np.log10(np.abs(np.fft.rfft(F, axis=1)) + 1e-12)
        if gmax is None:
            gmax = L.max()
        gmax = max(gmax, L.max())
        for row, fi in zip(L, idx):
            seg = row[lo - 1:hi + 2]
            m = (seg[1:-1] > seg[:-2]) & (seg[1:-1] >= seg[2:]) & (seg[1:-1] > max(row.max() + rel_db, gmax - 80))
            k = np.where(m)[0] + lo
            if len(k):
                a, b, c = row[k - 1], row[k], row[k + 1]
                den = a - 2 * b + c
                sh = np.where(den < 0, 0.5 * (a - c) / np.where(den < 0, den, -1), 0.0)
                pf, pdb = (k + sh) * freqs_bin, b - 0.25 * (a - c) * sh
                order = np.argsort(pdb)[::-1]
                pf, pdb = pf[order], pdb[order]
            else:
                pf, pdb = np.array([]), np.array([])
            used = np.zeros(len(pf), bool)
            for tr in open_tracks:
                if len(pf) == 0:
                    break
                d = np.abs(1200 * np.log2(pf / tr[1][-1]))
                d[used] = np.inf
                j = int(np.argmin(d))
                if d[j] <= max_step_cents:
                    if tr[3] < fi - 1:                       # bridge one missed frame
                        tr[1].append(0.5 * (tr[1][-1] + pf[j])); tr[2].append(tr[2][-1])
                    tr[1].append(pf[j]); tr[2].append(pdb[j]); tr[3] = fi; used[j] = True
            still = []
            for tr in open_tracks:
                (still if tr[3] >= fi - 1 else done).append(tr)
            open_tracks = still + [[fi, [pf[j]], [pdb[j]], fi] for j in np.where(~used)[0]]
    done += open_tracks
    min_len = int(min_len_s * fs)
    return [(t[0], np.array(t[1]), np.array(t[2])) for t in done if len(t[1]) >= min_len], fs


def track_modulation(freqs, fs, detrend_s=0.5, tau_lo=0.1, tau_hi=0.35):
    """Rate, strength and depth (cents) of the periodic swing of one partial track."""
    cents = 1200 * np.log2(freqs / np.median(freqs))
    k = int(detrend_s * fs) | 1
    hp = (cents - running_median(cents, k))[k // 2: len(cents) - k // 2]
    if len(hp) < int(2 * tau_hi * fs):
        return None
    p = pick_period(autocorr(hp, int(1.2 * tau_hi * fs) + 2), fs, tau_lo, tau_hi)
    return {"rate": None if p.tau is None else 1 / p.tau, "r": p.strength,
            "depth": float(np.sqrt(2) * hp.std()), "dur": len(freqs) / fs}
