"""Group II, Periodicity: "What repeats, and how often?"

One question, asked with one tool at every time scale: the autocorrelation of a track.
Only the track changes with the scale:

- the waveform itself              -> Frequency, Pitch            (Wave, Tone)
- the pitch track of a voice       -> Vibrato (second-order)      (Event)
- the onset envelope               -> Subdivision, Pulse, Meter   (Event, Beat, Bar)
- the level track                  -> Sidechain pump (second-order) (Beat)
- the sequence of spectral frames  -> Loop, Repetition            (Phrase, Form)

Peak rule, the same everywhere: among the local maxima of the autocorrelation inside the
lag range, take the shortest lag whose score is at least `rule` times the best one.
Multiples of a true period are almost as strong as the period itself, so the shortest
strong lag is the period and its multiples are not. For tracks longer than a few periods
(envelopes, levels, spectral frames) the score is the comb score: the mean over the
first four multiples of the lag, because a true period keeps repeating.

Only numpy is used, for arrays and the FFT.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .zscale import z_of, period_of

RULE = 0.9
# A sequence counts as flat when its variance is below this share of its mean square:
# far below any real signal, well above the rounding noise left after removing the mean.
_FLAT = 1e-20


@dataclass
class Periodicity:
    tau: float | None                 # candidate period in seconds, or None if there is no candidate
    strength: float                   # normalised autocorrelation at that lag, 0..1
    candidates: list = field(default_factory=list)  # [(tau, strength)] strongest local maxima
    confirmed: bool | None = None     # None: not tested; False: the candidate is not proven
    evidence: dict = field(default_factory=dict)    # what the confirmation test measured

    @property
    def z(self):
        return None if self.tau is None else z_of(self.tau)

    @property
    def period(self):
        return None if self.tau is None else period_of(self.z)


# ---------------------------------------------------------------- basic tools

def _require(ok: bool, message: str) -> None:
    """Raise a ValueError that names the parameter and its allowed range."""
    if not ok:
        raise ValueError(message)


def _samples(name: str, seconds: float, sr: float) -> int:
    """A duration in seconds as a whole number of samples, at least one."""
    _require(seconds > 0, f"{name} must be > 0 seconds, got {seconds!r}")
    n = int(round(seconds * sr))
    _require(n >= 1, f"{name} = {seconds!r} s is shorter than one sample at sr = {sr!r}")
    return n


def _check_sr(sr: float) -> None:
    _require(np.isfinite(sr) and sr > 0, f"sr must be a positive sample rate, got {sr!r}")


def mono(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    return x.mean(axis=1) if x.ndim == 2 else x


def autocorr(x: np.ndarray, max_lag: int, unbiased: bool = True) -> np.ndarray:
    """Autocorrelation r[0..max_lag] of a mean-removed sequence, r[0] = 1.

    A sequence with nothing to correlate (fewer than two values, or no variation at all)
    gives zeros: there is no periodicity in it, and dividing by its zero energy would
    only produce noise or NaN.
    """
    x = np.asarray(x, dtype=np.float64).ravel()
    n = len(x)
    if n < 2:
        return np.zeros(1)
    max_lag = max(0, min(max_lag, n - 1))
    ref = np.mean(x ** 2)
    x = x - x.mean()
    if not np.mean(x ** 2) > _FLAT * ref:
        return np.zeros(max_lag + 1)
    nfft = 1 << int(np.ceil(np.log2(2 * n)))
    spec = np.fft.rfft(x, nfft)
    r = np.fft.irfft(spec * np.conj(spec), nfft)[: max_lag + 1]
    if unbiased:
        r = r / (n - np.arange(max_lag + 1))
    return r / r[0] if r[0] > 0 else np.zeros_like(r)


def comb_score(r: np.ndarray, lag: int, n_mult: int) -> float:
    """Mean autocorrelation at lag, 2*lag, ... n_mult*lag (each within +-1 sample).

    A true period repeats: its multiples are strong too. A lag that only links two
    different kinds of events (a kick to the hat after it) is strong once, not at every
    multiple, so its comb score is lower.
    """
    vals = []
    for m in range(1, n_mult + 1):
        c = m * lag
        if c + 1 >= len(r):
            break
        vals.append(r[c - 1:c + 2].max())
    return float(np.mean(vals)) if vals else 0.0


def pick_period(r: np.ndarray, fs: float, tau_lo: float, tau_hi: float, rule: float = RULE,
                n_mult: int = 1) -> Periodicity:
    """Apply the peak rule to an autocorrelation sampled at fs, inside [tau_lo, tau_hi).

    With n_mult > 1 the rule is applied to the comb score instead of the single value.
    """
    lo = max(1, int(np.floor(tau_lo * fs)))
    hi = min(len(r) - 2, int(np.ceil(tau_hi * fs)))
    if hi <= lo:
        return Periodicity(None, 0.0)
    k = np.arange(lo, hi + 1)
    peaks = k[(r[k] > r[k - 1]) & (r[k] >= r[k + 1]) & (r[k] > 0)]
    peaks = peaks[(peaks / fs >= tau_lo) & (peaks / fs < tau_hi)]
    if len(peaks) == 0:
        return Periodicity(None, 0.0)
    score = np.array([comb_score(r, p, n_mult) for p in peaks]) if n_mult > 1 else r[peaks]
    best = score.max()
    if not best > 0:                      # nothing repeats at this scale
        return Periodicity(None, 0.0)
    chosen = peaks[score >= rule * best][0]
    # parabolic interpolation around the chosen lag
    a, b, c = r[chosen - 1], r[chosen], r[chosen + 1]
    den = a - 2 * b + c
    shift = 0.5 * (a - c) / den if den < 0 else 0.0
    order = peaks[np.argsort(r[peaks])[::-1][:5]]
    return Periodicity((chosen + shift) / fs, float(b), [(float(p / fs), float(r[p])) for p in order])


def frames(x: np.ndarray, size: int, hop: int) -> np.ndarray:
    """Overlapping frames of length size, every hop samples. A signal shorter than one
    frame gives no frames (shape (0, size)) rather than a frame that runs past its end."""
    if len(x) < size:
        return np.zeros((0, size), dtype=np.asarray(x).dtype)
    n = 1 + (len(x) - size) // hop
    idx = np.arange(size)[None, :] + hop * np.arange(n)[:, None]
    return x[idx]


# ---------------------------------------------------------------- the five tracks

def pitch_track(x: np.ndarray, sr: int, fmin: float = 30.0, fmax: float = 1000.0,
                frame_s: float = 0.08, hop_s: float = 0.01, voiced: float = 0.7,
                silence_db: float = -50.0, dip: float = 0.15):
    """Waveform period per frame. Returns (times, periods in s, NaN where not periodic).

    For each frame and lag tau the difference d(tau) = sum (x[j] - x[j+tau])^2 is computed
    from the autocorrelation and running energies. It is normalised by its own running
    mean, d'(tau) = d(tau) * tau / sum_{k<=tau} d(k), so that d' is near 1 for noise and
    near 0 at the period. The period is the first dip of d' below `dip`, or else the
    deepest dip if 1 - d' >= `voiced`. Unlike a plain autocorrelation peak this does not
    lose a voice whose level changes inside the frame, which reverberant vocals do.
    """
    _check_sr(sr)
    _require(0 < fmin < fmax, f"need 0 < fmin < fmax, got fmin = {fmin!r}, fmax = {fmax!r}")
    x = mono(x)
    size, hop = int(frame_s * sr), _samples("hop_s", hop_s, sr)
    _require(frame_s > 0 and size >= 2, f"frame_s = {frame_s!r} s must cover at least two samples")
    F = frames(x, size, hop)
    if len(F) == 0:                      # shorter than one frame: no pitch can be measured
        return np.zeros(0), np.zeros(0)
    lo, hi = int(np.floor(sr / fmax)), min(int(np.ceil(sr / fmin)), size // 2)
    nfft = 1 << int(np.ceil(np.log2(2 * size)))
    # The silence gate looks at the energy that can carry a period: the mean is removed
    # first. A constant (DC) frame then has no energy and stays unvoiced; measuring the RMS
    # before removing the mean let it through, and its all-zero difference function read
    # as a perfect period at the shortest lag (fmax).
    rms = np.sqrt(((F - F.mean(axis=1, keepdims=True)) ** 2).mean(axis=1))
    # what is left of a constant frame after removing its mean is rounding noise, about
    # 1e-16 of its raw level; anything below 1e-8 of the raw level counts as no variation
    rms[rms <= 1e-8 * np.sqrt((F ** 2).mean(axis=1))] = 0.0
    floor = rms.max() * 10 ** (silence_db / 20) if rms.max() > 0 else np.inf
    out = np.full(len(F), np.nan)
    good = np.where(rms > floor)[0]
    lags = np.arange(hi + 2)
    for start in range(0, len(good), 512):
        sel = good[start:start + 512]
        X = F[sel] - F[sel].mean(axis=1, keepdims=True)
        S = np.fft.rfft(X, nfft, axis=1)
        R = np.fft.irfft(S * np.conj(S), nfft, axis=1)[:, :hi + 2]
        c = np.concatenate([np.zeros((len(sel), 1)), np.cumsum(X ** 2, axis=1)], axis=1)
        d = c[:, size - lags] + (c[:, size:size + 1] - c[:, lags]) - 2 * R
        d = np.maximum(d, 0.0)
        cm = np.cumsum(d[:, 1:], axis=1)
        dn = np.ones_like(d)
        dn[:, 1:] = d[:, 1:] * lags[1:] / np.maximum(cm, 1e-20)
        for row, i in zip(dn, sel):
            seg = row[lo:hi + 1]
            below = np.where(seg < dip)[0]
            if len(below):
                k = below[0]
                while k + 1 < len(seg) and seg[k + 1] < seg[k]:
                    k += 1
            else:
                k = int(np.argmin(seg))
                if 1 - seg[k] < voiced:
                    continue
            k += lo
            a_, b_, c_ = row[k - 1], row[k], row[min(k + 1, len(row) - 1)]
            den = a_ - 2 * b_ + c_
            shift = 0.5 * (a_ - c_) / den if den > 0 else 0.0
            out[i] = (k + shift) / sr
    times = (np.arange(len(F)) * hop + size / 2) / sr
    return times, out


def clean_cents(cents: np.ndarray, fs: float, max_dev: float = 150.0, med_s: float = 0.3, max_gap: int = 5):
    """Remove octave errors and fill short gaps in a pitch track given in cents.

    A frame further than max_dev cents from the running median of the voiced frames
    around it is dropped. Gaps up to max_gap frames are filled by straight lines.
    """
    c = cents.copy()
    half = max(1, int(med_s * fs / 2))
    ref = np.full_like(c, np.nan)
    for i in range(len(c)):
        w = c[max(0, i - half): i + half + 1]
        w = w[np.isfinite(w)]
        if len(w):
            ref[i] = np.median(w)
    c[np.abs(c - ref) > max_dev] = np.nan
    ok = np.isfinite(c)
    idx = np.where(ok)[0]
    for a, b in zip(idx[:-1], idx[1:]):
        if 1 < b - a <= max_gap + 1:
            c[a:b + 1] = np.linspace(c[a], c[b], b - a + 1)
    return c


def stft_power(x: np.ndarray, sr: int, size: int = 1024, hop_s: float = 0.005):
    _check_sr(sr)
    _require(int(size) >= 2, f"size must be at least 2 samples, got {size!r}")
    x = mono(x)
    hop = _samples("hop_s", hop_s, sr)
    F = frames(np.pad(x, (size // 2, size // 2)), size, hop) * np.hanning(size)
    return np.abs(np.fft.rfft(F, axis=1)) ** 2, sr / hop


def log_bands(P: np.ndarray, sr: int, size: int, n_bands: int = 24, fmin: float = 40.0, fmax: float = 16000.0):
    """Power in logarithmically spaced bands, in dB."""
    freqs = np.fft.rfftfreq(size, 1 / sr)
    edges = np.geomspace(fmin, min(fmax, sr / 2), n_bands + 1)
    B = np.stack([P[:, (freqs >= a) & (freqs < b)].sum(axis=1) for a, b in zip(edges[:-1], edges[1:])], axis=1)
    return 10 * np.log10(B + 1e-12)


def onset_envelope(x: np.ndarray, sr: int, hop_s: float = 0.005):
    """Sum over bands of the rise in band level: where new energy arrives. Returns (env, fs).

    Band power is compressed with the exponent 0.3 instead of taken in dB. In dB every
    hit rises by the same amount out of silence, and a hat would weigh as much as a kick.
    """
    P, fs = stft_power(x, sr, 1024, hop_s)
    L = 10 ** (log_bands(P, sr, 1024, 8) / 10 * 0.3)
    rise = np.maximum(np.diff(L, axis=0, prepend=L[:1]), 0.0)
    return rise.sum(axis=1), fs


def level_track(x: np.ndarray, sr: int, hop_s: float = 0.01, detrend_s: float = 4.0):
    """Level in dB per hop with the slow trend removed. Returns (track, fs).

    The trend is a moving average over detrend_s that averages only the hops that exist.
    A plain zero-padded moving average is pulled towards 0 near both ends, and on a
    steady level it leaves a false slope of up to 60 dB in the first and last seconds.
    """
    _check_sr(sr)
    _require(detrend_s > 0, f"detrend_s must be > 0 seconds, got {detrend_s!r}")
    x = mono(x)
    hop = _samples("hop_s", hop_s, sr)
    fs = sr / hop
    F = frames(x, hop, hop)
    if len(F) == 0:
        return np.zeros(0), fs
    lv = 10 * np.log10((F ** 2).mean(axis=1) + 1e-12)
    lv = np.maximum(lv, lv.max() - 60)
    k = max(1, min(int(round(detrend_s * fs)), len(lv)))   # never longer than the track
    window = np.ones(k)
    trend = np.convolve(lv, window, mode="same") / np.convolve(np.ones_like(lv), window, mode="same")
    return lv - trend, fs


def frame_features(x: np.ndarray, sr: int, hop_s: float = 0.1):
    """Spectral frames for long scales: 24 log bands, each band standardised over time."""
    P, fs = stft_power(x, sr, 4096, hop_s)
    L = log_bands(P, sr, 4096, 24)
    L = (L - L.mean(axis=0)) / (L.std(axis=0) + 1e-9)
    return L, fs


def lag_similarity(F: np.ndarray, max_lag: int) -> np.ndarray:
    """Mean similarity of frame t and frame t+lag, normalised so that lag 0 is 1.

    The multichannel version of the autocorrelation: the sum over bands of each band's
    autocorrelation.
    """
    F = np.asarray(F, dtype=np.float64)
    if F.ndim != 2 or F.shape[0] < 2:
        return np.zeros(1)
    n, d = F.shape
    max_lag = max(0, min(max_lag, n - 1))
    ref = np.mean(F ** 2)
    G = F - F.mean(axis=0)
    if not np.mean(G ** 2) > _FLAT * ref:          # constant frames: nothing repeats
        return np.zeros(max_lag + 1)
    nfft = 1 << int(np.ceil(np.log2(2 * n)))
    S = np.fft.rfft(G, nfft, axis=0)
    r = np.fft.irfft((S * np.conj(S)).sum(axis=1), nfft)[: max_lag + 1]
    r = r / (n - np.arange(max_lag + 1))
    return r / r[0] if r[0] > 0 else np.zeros_like(r)


# ---------------------------------------------------------------- the elements

def pitch(x, sr, fmin=30.0, fmax=1000.0):
    """Pitch: typical waveform period and its spread over voiced frames."""
    _, per = pitch_track(x, sr, fmin, fmax)
    v = per[np.isfinite(per)]
    if len(v) == 0:
        return None
    return {"tau": float(np.median(v)), "tau_p10": float(np.percentile(v, 10)),
            "tau_p90": float(np.percentile(v, 90)), "voiced_share": float(len(v) / len(per))}


def running_median(x: np.ndarray, n: int) -> np.ndarray:
    n = max(1, n | 1)
    pad = np.pad(x, (n // 2, n // 2), mode="edge")
    return np.median(np.lib.stride_tricks.sliding_window_view(pad, n), axis=1)


def vibrato(x, sr, fmin=70.0, fmax=1000.0, min_run_s=0.6, detrend_s=0.3, tau_lo=0.05, tau_hi=0.25):
    """Vibrato: periodicity of the pitch track (in cents) inside long voiced runs.

    Vibrato is a swing inside a held note. The note itself is removed with a running
    median over detrend_s: a median follows the steps from note to note but not a swing
    that is shorter than its window. A moving average would leave the note steps in, and
    a melody that moves on every beat would then look like a 2 Hz vibrato.
    """
    t, per = pitch_track(x, sr, fmin, fmax, frame_s=0.05, hop_s=0.01)
    fs = 100.0
    cents = clean_cents(1200 * np.log2(1 / per / 440.0), fs)
    ok = np.isfinite(cents)
    runs, start = [], None
    for i, flag in enumerate(np.append(ok, False)):
        if flag and start is None:
            start = i
        elif not flag and start is not None:
            if (i - start) / fs >= min_run_s:
                runs.append(cents[start:i])
            start = None
    if not runs:
        return Periodicity(None, 0.0), 0
    k = int(detrend_s * fs)
    max_lag = int(1.2 * tau_hi * fs) + 2
    acc, weight = np.zeros(max_lag + 1), 0.0
    for c in runs:
        hp = c - running_median(c, k)
        hp = hp[k // 2: len(hp) - k // 2]
        if len(hp) <= max_lag + 2:
            continue
        acc += autocorr(hp, max_lag) * len(hp)
        weight += len(hp)
    if weight == 0:
        return Periodicity(None, 0.0), len(runs)
    return pick_period(acc / weight, fs, tau_lo, tau_hi), len(runs)


def compress_time(x: np.ndarray, k: int) -> np.ndarray:
    """Play a signal k times faster at the same sample rate.

    Everything above the new Nyquist frequency is removed in the frequency domain first,
    then every k-th sample is kept. Every time in the signal shrinks by k, so every
    element moves down by log2(k) in Z.
    """
    _require(isinstance(k, (int, np.integer)) and k >= 1, f"k must be a whole number >= 1, got {k!r}")
    x = mono(x)
    n = len(x)
    if n == 0:
        return np.zeros(0)
    X = np.fft.rfft(x)
    X[len(X) // k:] = 0
    return np.fft.irfft(X, n)[::k]


N_MULT = 4


# ---------------------------------------------------------------- confirmation
#
# The peak rule always returns its best candidate, even in pure noise. Whether that
# candidate is a real period is a separate question, answered here with three tests:
#
# 1. Significance. If a track has no periodicity, its autocorrelation at a long lag l is
#    noise with standard deviation (Bartlett's formula for a correlated sequence)
#        sigma(l) = sqrt((1 + 2 * sum_{k=1..K} rho(k)^2) / (n - l)),
#    where rho(k) for k below the search range describes the track's own smoothness.
#    The candidate's peak must stand Z_MIN standard deviations above zero.
# 2. Repetitions. The period must fit into the track at least MIN_REPS times.
# 3. Stability. The same lag must stay significant in each half of the track, at
#    Z_MIN / sqrt(2) (each half has half the data).
#
# The thresholds were chosen on a training set and checked on independent signals:
# experiments/2026-11-12_periodicity_confirmation/.

# Chosen on the training set (largest share of true detections with at most 1% false
# detections): 5 sigma and 4 repetitions. On the test set and on the real drum stems this
# gave 0% false detections and 0% misses. The noisiest negative reached 5.2 sigma once and
# was rejected by the stability test, so the three tests are meant to work together.
Z_MIN = 5.0
MIN_REPS = 4.0


def _bartlett_sigma(r: np.ndarray, n: int, lag: int, k_short: int) -> float:
    k_short = max(1, min(k_short, len(r) - 1))
    s = 1.0 + 2.0 * float(np.sum(r[1:k_short] ** 2))
    return float(np.sqrt(s / max(1, n - lag)))


def _peak_near(r: np.ndarray, lag: float, tol: float = 0.02) -> tuple[int, float]:
    lo, hi = max(1, int(np.floor(lag * (1 - tol)))), min(len(r) - 1, int(np.ceil(lag * (1 + tol))))
    if hi < lo:
        return int(round(lag)), 0.0
    k = lo + int(np.argmax(r[lo:hi + 1]))
    return k, float(r[k])


def confirm_period(track, fs, cand: Periodicity, tau_lo: float, corr=None,
                   z_min: float = None, min_reps: float = None) -> Periodicity:
    """Mark a candidate period as confirmed or not, and record the evidence.

    `track` is the sequence the candidate was found in (1-D envelope or 2-D frames) and
    `corr` the function that autocorrelates it (autocorr or lag_similarity).
    """
    z_min = Z_MIN if z_min is None else z_min
    min_reps = MIN_REPS if min_reps is None else min_reps
    corr = corr or autocorr
    track = np.asarray(track, dtype=np.float64)
    n = len(track)
    if cand.tau is None or n < 4:
        cand.confirmed, cand.evidence = False, {"reason": "no candidate"}
        return cand
    lag = cand.tau * fs
    k_short = int(tau_lo * fs)
    reps = n / lag
    ev = {"repetitions": reps}

    def significance(seq):
        m = len(seq)
        if m <= lag + 2:
            return 0.0
        r = corr(seq, int(lag * 1.05) + 2)
        k, val = _peak_near(r, lag)
        return val / _bartlett_sigma(r, m, k, k_short)

    ev["significance"] = significance(track)
    half = n // 2
    ev["significance_halves"] = (significance(track[:half]), significance(track[half:]))
    reasons = []
    if reps < min_reps:
        reasons.append(f"only {reps:.1f} repetitions (need {min_reps:g})")
    if ev["significance"] < z_min:
        reasons.append(f"peak {ev['significance']:.1f} sigma (need {z_min:g})")
    if min(ev["significance_halves"]) < z_min / np.sqrt(2):
        reasons.append("not stable in both halves")
    cand.confirmed = not reasons
    ev["reason"] = "; ".join(reasons) if reasons else "confirmed"
    cand.evidence = ev
    return cand


def envelope_periodicity(env, fs, tau_lo, tau_hi, n_mult=N_MULT, confirm=True):
    """Best candidate period of an envelope in [tau_lo, tau_hi), with confirmation."""
    r = autocorr(env, int(n_mult * tau_hi * fs) + 2)
    cand = pick_period(r, fs, tau_lo, tau_hi, n_mult=n_mult)
    return confirm_period(env, fs, cand, tau_lo, autocorr) if confirm else cand


def feature_periodicity(F, fs, tau_lo, tau_hi, n_mult=N_MULT, confirm=True):
    """Best candidate period of a sequence of frames in [tau_lo, tau_hi), with confirmation."""
    r = lag_similarity(F, int(n_mult * tau_hi * fs) + 2)
    cand = pick_period(r, fs, tau_lo, tau_hi, n_mult=n_mult)
    return confirm_period(F, fs, cand, tau_lo, lag_similarity) if confirm else cand


# ---------------------------------------------------------------- harmonic change

def chroma_frames(x: np.ndarray, sr: int, hop_s: float = 0.02, size: int = 8192,
                  fmin: float = 55.0, fmax: float = 4000.0):
    """Power per pitch class (12 bins, A = 0) per frame. Returns (C, fs)."""
    Pw, fs = stft_power(x, sr, size, hop_s)
    f = np.fft.rfftfreq(size, 1 / sr)
    band = (f >= fmin) & (f <= fmax)
    pc = np.round(12 * np.log2(f[band] / 440.0)) % 12
    C = np.stack([Pw[:, band][:, pc == k].sum(axis=1) for k in range(12)], axis=1)
    return C, fs


def harmonic_change(x: np.ndarray, sr: int, side_s: float = 0.2):
    """How much the pitch-class content changes at each moment. Returns (curve, fs).

    The mean pitch-class profile of side_s before a frame is compared with the one after
    it (1 - cosine similarity). The curve peaks where the chord changes. A bar is marked
    by when chords change, not by what they are, so its period is a periodicity of this
    curve, not of the chord frames themselves.
    """
    C, fs = chroma_frames(x, sr)
    C = C / (np.linalg.norm(C, axis=1, keepdims=True) + 1e-12)
    k = max(1, int(side_s * fs))
    cs = np.concatenate([np.zeros((1, 12)), np.cumsum(C, axis=0)])
    i = np.arange(k, len(C) - k)
    before, after = cs[i] - cs[i - k], cs[i + k] - cs[i]
    cos = (before * after).sum(1) / (np.linalg.norm(before, axis=1) * np.linalg.norm(after, axis=1) + 1e-12)
    out = np.zeros(len(C))
    out[i] = 1 - cos
    return out, fs
