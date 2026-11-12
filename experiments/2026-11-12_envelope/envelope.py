"""Amplitude envelope: signals with a known envelope, two estimators, and the measures (issue #21).

All maths is our own; numpy only.

Signal = a(t) * c(t) + n(t):
  a(t)  the true envelope: rise, decay, burst or constant
  c(t)  a carrier with unit RMS: sine, harmonic tone, or white noise
  n(t)  additive white noise at a given SNR, relative to the carrier at full level

The characteristic time T of each shape is known exactly:
  rise    raised cosine over D seconds; 10-90 % rise time  T = 0.5903 * D
  decay   exp(-t / tau);                90-10 % fall time  T = tau * ln 9
  burst   exp(-t^2 / (2 sigma^2));      full width at half maximum  T = 2.3548 * sigma
  constant  no change (T is not defined)
"""
import numpy as np

SR = 44100
RISE_K = (np.arccos(-0.8) - np.arccos(0.8)) / np.pi      # 10-90 % fraction of a raised-cosine ramp
FWHM_K = 2 * np.sqrt(2 * np.log(2))
SHAPES = ("rise", "decay", "burst", "constant")
# How the noise floor is removed before the times are read. "power" (version 2): the floor adds
# in power, so the envelope is sqrt(e^2 - floor^2). "amplitude" (version 1, kept for the record):
# e - floor, which shortens every time read in additive noise.
FLOOR = "power"


def _remove_floor(e, floor):
    if FLOOR == "amplitude":
        return e - floor
    return np.sqrt(np.maximum(e ** 2 - floor ** 2, 0.0))


# ---------------------------------------------------------------- signals

def true_envelope(shape, T, sr=SR):
    """(time axis, a(t), index of the event start) for a shape with characteristic time T."""
    margin = max(0.2, 3 * T)
    if shape == "rise":
        D = T / RISE_K
        n0, n1 = int(margin * sr), int(D * sr)
        a = np.r_[np.zeros(n0), 0.5 * (1 - np.cos(np.pi * np.arange(n1) / n1)), np.ones(int(margin * sr))]
    elif shape == "decay":
        tau = T / np.log(9)
        n0 = int(margin * sr)
        a = np.r_[np.ones(n0), np.exp(-np.arange(int((margin + 6 * tau) * sr)) / (tau * sr))]
    elif shape == "burst":
        sigma = T / FWHM_K
        n = int((2 * margin + 6 * sigma) * sr)
        t = (np.arange(n) - n / 2) / sr
        a, n0 = np.exp(-t ** 2 / (2 * sigma ** 2)), n // 2
    else:
        n0 = int(0.2 * sr)
        a = np.ones(int(0.6 * sr) + 2 * n0)
    return np.arange(len(a)) / sr, a, n0


def carrier(kind, f0, n, rng, sr=SR):
    t = np.arange(n) / sr
    if kind == "sine":
        c = np.sin(2 * np.pi * f0 * t + rng.uniform(0, 2 * np.pi))
    elif kind == "harmonic":
        c = np.zeros(n)
        for k in range(1, 13):
            if k * f0 >= 0.45 * sr:
                break
            c += np.sin(2 * np.pi * k * f0 * t + rng.uniform(0, 2 * np.pi)) / k
    else:
        c = rng.standard_normal(n)
    return c / np.sqrt(np.mean(c ** 2))


def make(shape, T, kind, f0, snr_db, seed, amp=1.0, sr=SR):
    rng = np.random.default_rng(seed)
    t, a, n0 = true_envelope(shape, T, sr)
    x = amp * a * carrier(kind, f0, len(a), rng, sr)
    if np.isfinite(snr_db):
        x = x + rng.standard_normal(len(x)) * amp * 10 ** (-snr_db / 20)
    return x, a, n0


# ---------------------------------------------------------------- estimators

def _hann(w_s, sr):
    n = max(3, int(round(w_s * sr)) | 1)
    h = np.hanning(n + 2)[1:-1]
    return h / h.sum()


def _smooth(y, h):
    """Zero-phase convolution with a normalised window (FFT, same length as y)."""
    n = len(y) + len(h) - 1
    m = 1 << int(np.ceil(np.log2(n)))
    out = np.fft.irfft(np.fft.rfft(y, m) * np.fft.rfft(h, m), m)[:n]
    k = len(h) // 2
    return out[k:k + len(y)]


def analytic(x):
    """The analytic signal x + i H(x), by zeroing the negative frequencies."""
    n = len(x)
    X = np.fft.fft(x)
    g = np.zeros(n)
    g[0] = 1
    if n % 2 == 0:
        g[1:n // 2] = 2
        g[n // 2] = 1
    else:
        g[1:(n + 1) // 2] = 2
    return np.fft.ifft(X * g)


def envelope(x, method, w_s, sr=SR):
    """Envelope on the scale of the carrier's RMS. method: 'rms' or 'analytic'; w_s: Hann window in s."""
    h = _hann(w_s, sr)
    if method == "rms":
        return np.sqrt(np.maximum(_smooth(x ** 2, h), 0.0))
    return _smooth(np.abs(analytic(x)), h) / np.sqrt(2.0)


# ---------------------------------------------------------------- measures

def _cross(e, level, i_from, step):
    """First sample index (fractional, linear interpolation) from i_from where e crosses level."""
    i = i_from
    n = len(e)
    while 0 < i < n - 1:
        j = i + step
        if (e[i] - level) * (e[j] - level) <= 0 and e[i] != e[j]:
            return i + step * (level - e[i]) / (e[j] - e[i])
        i = j
    return None


def characteristic_time(e, shape, n0, T, sr=SR, scale=1.0):
    """Measured T, the floor and the top used, from an envelope e. None if it cannot be read.

    scale multiplies the fixed analysis margins (guard and the floor and top segments), so that a
    signal played k times faster or slower is read with margins scaled by the same k.
    """
    guard = max(1, int(0.05 * scale * sr))
    if shape == "rise":
        floor = np.median(e[guard:max(guard + 1, n0 - int(T * sr))])
        top = np.median(e[-int(0.15 * scale * sr):-guard])
        e, d = _remove_floor(e, floor), float(_remove_floor(np.array([top]), floor)[0])
        floor0, floor = floor, 0.0
        i90 = _cross(e, floor + 0.9 * d, n0, 1)
        if i90 is None:
            return None, floor, top
        i10 = _cross(e, floor + 0.1 * d, int(i90), -1)
        return (None if i10 is None else (i90 - i10) / sr), floor0, top
    if shape == "decay":
        top = np.median(e[guard:max(guard + 1, n0 - int(0.05 * scale * sr))])
        floor = np.median(e[-int(0.1 * scale * sr):-guard])
        e, d = _remove_floor(e, floor), float(_remove_floor(np.array([top]), floor)[0])
        floor0, floor = floor, 0.0
        i10 = _cross(e, floor + 0.1 * d, n0, 1)
        if i10 is None:
            return None, floor, top
        i90 = _cross(e, floor + 0.9 * d, int(i10), -1)
        return (None if i90 is None else (i10 - i90) / sr), floor0, top
    if shape == "burst":
        floor = np.median(np.r_[e[guard:int(0.15 * scale * sr)], e[-int(0.15 * scale * sr):-guard]])
        ip = int(np.argmax(e[guard:-guard])) + guard
        top = e[ip]
        floor0 = floor
        e = _remove_floor(e, floor)
        floor, half = 0.0, 0.5 * float(_remove_floor(np.array([top]), floor0)[0])
        a, b = _cross(e, half, ip, -1), _cross(e, half, ip, 1)
        return (None if a is None or b is None else (b - a) / sr), floor0, top
    return None, None, None


def shape_error(e, a, floor, top, n0, T, shape, sr=SR):
    """RMS difference between the normalised measured and the true envelope over the event."""
    if top is None or top == floor:
        return None
    d = float(_remove_floor(np.array([top]), floor)[0])
    if d <= 0:
        return None
    en = _remove_floor(e, floor) / d
    if shape == "burst":
        sigma = T / FWHM_K
        lo, hi = n0 - int(3 * sigma * sr), n0 + int(3 * sigma * sr)
    elif shape == "rise":
        lo, hi = n0 - int(T * sr), n0 + int((T / RISE_K + T) * sr)
    else:
        lo, hi = n0 - int(T * sr), n0 + int(2.5 * T * sr)
    lo, hi = max(0, lo), min(len(e), hi)
    return float(np.sqrt(np.mean((en[lo:hi] - a[lo:hi]) ** 2)))


def false_change_db(e, w_s, sr=SR):
    """Constant level: the spread of the reading inside the steady part, max over min, in dB."""
    g = int(max(0.25, 2 * w_s) * sr)
    seg = e[g:-g]
    return float(20 * np.log10(seg.max() / max(seg.min(), 1e-12)))


# ---------------------------------------------------------------- time scaling (tape speed)

def stretch(x, k):
    """Play k times slower (integer k): the spectrum is interpolated by zero padding."""
    X = np.fft.rfft(x)
    n = len(x) * k
    Y = np.zeros(n // 2 + 1, dtype=complex)
    Y[:len(X)] = X
    return np.fft.irfft(Y, n) * k
