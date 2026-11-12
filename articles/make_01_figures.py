"""Render the table and the tables of article 01 as images, for platforms that cannot show
Markdown tables (X Articles, LinkedIn, Medium import).

The periodic table itself is drawn from the data of table/edition3.html, so the picture always
matches the published table. Run:  python articles/make_01_figures.py  ->  articles/img/01_*.png
"""
import os
import re

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "img")
FONT_DIR = r"C:\Windows\Fonts"
REG, BOLD, MONO, SYM = (os.path.join(FONT_DIR, f) for f in ("segoeui.ttf", "segoeuib.ttf", "consola.ttf", "seguisym.ttf"))

BG, HEAD_BG, ROW_BG, ROW_ALT, GRID = (11, 13, 19), (27, 32, 45), (19, 23, 34), (23, 27, 39), (42, 48, 62)
WHITE, GREY, DIM = (238, 241, 247), (154, 163, 181), (100, 110, 128)
ACCENT = (251, 146, 60)                                   # the Periodicity orange of the table
GROUPS = [("level", "Level", "How strong is it?", (45, 212, 191)),
          ("period", "Periodicity", "What repeats, and how often?", (251, 146, 60)),
          ("irreg", "Irregularity", "How far from regular is it?", (148, 163, 184)),
          ("change", "Change", "Where does it start, end or turn?", (244, 63, 94)),
          ("makeup", "Makeup", "Which components, in what proportions?", (167, 139, 250)),
          ("space", "Space", "Where is it, and how do signals relate?", (56, 189, 248))]
PERIODS = [("Wave", "< 2 ms"), ("Tone", "2–50 ms"), ("Event", "50–250 ms"), ("Beat", "0.25–2 s"),
           ("Bar", "2–8 s"), ("Phrase", "8–32 s"), ("Form", "> 32 s")]
CUTS = (6.0, 10.7, 13.0, 16.0, 18.0, 20.0)
W, PAD = 2000, 100
FOOT = "Periodic Table of Sound  ·  doi:10.5281/zenodo.24161074  ·  github.com/alex-gerek/periodic-table-of-sound"


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, f, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [""]


def header(d, title, subtitle, y=70):
    f1, f2 = F(BOLD, 50), F(REG, 30)
    d.text((W / 2, y), title, font=f1, fill=WHITE, anchor="mt")
    d.text((W / 2, y + 72), subtitle, font=f2, fill=ACCENT, anchor="mt")
    return y + 140


def footer(img, d):
    d.text((W / 2, img.height - 42), FOOT, font=F(REG, 22), fill=DIM, anchor="mm")


def table(name, title, subtitle, head, rows, frac, first_bold=True, note=None, highlight=None):
    """A table image: header row, wrapped cells, alternating rows; highlight = set of row indices."""
    probe = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    fh, fb, fc, fn = F(BOLD, 30), F(BOLD, 29), F(REG, 29), F(REG, 25)
    inner = W - 2 * PAD
    cols = [int(inner * c) for c in frac]
    cols[-1] = inner - sum(cols[:-1])
    pad, lh = 26, 41

    def lines_of(cells, fonts):
        return [wrap(probe, c, f, cw - 2 * pad) for c, f, cw in zip(cells, fonts, cols)]

    hl = lines_of(head, [fh] * len(head))
    body = [lines_of(r, [fb if (i == 0 and first_bold) else fc for i in range(len(r))]) for r in rows]
    hh = max(len(x) for x in hl) * lh + 2 * pad
    rh = [max(len(x) for x in r) * lh + 2 * pad for r in body]
    note_lines = wrap(probe, note, fn, inner) if note else []
    H = 230 + hh + sum(rh) + (len(note_lines) * 36 + 40 if note else 0) + 110
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    y = header(d, title, subtitle) + 20
    x0 = PAD
    d.rectangle([x0, y, x0 + inner, y + hh], fill=HEAD_BG)
    x = x0
    for ls, cw in zip(hl, cols):
        for k, l in enumerate(ls):
            d.text((x + pad, y + pad + k * lh), l, font=fh, fill=ACCENT)
        x += cw
    y += hh
    for ri, (r, h) in enumerate(zip(body, rh)):
        bg = (28, 38, 36) if highlight and ri in highlight else (ROW_BG if ri % 2 == 0 else ROW_ALT)
        d.rectangle([x0, y, x0 + inner, y + h], fill=bg)
        x = x0
        for ci, (ls, cw) in enumerate(zip(r, cols)):
            f = fb if (ci == 0 and first_bold) else fc
            col = WHITE if ci == 0 else GREY
            top = y + (h - len(ls) * lh) / 2
            for k, l in enumerate(ls):
                d.text((x + pad, top + k * lh), l, font=f, fill=col)
            x += cw
        y += h
    x = x0
    for cw in cols[:-1]:
        x += cw
        d.line([x, y - sum(rh) - hh, x, y], fill=GRID, width=2)
    d.rectangle([x0, y - sum(rh) - hh, x0 + inner, y], outline=GRID, width=2)
    if note:
        y += 34
        for l in note_lines:
            d.text((x0, y), l, font=fn, fill=GREY)
            y += 36
    footer(img, d)
    img.save(os.path.join(OUT, name))
    return name


def load_table():
    s = open(os.path.join(ROOT, "table", "edition3.html"), encoding="utf-8").read()
    rows = re.findall(r'^\s*\["([A-Za-z0-9]+)","([^"]+)","(level|period|irreg|change|makeup|space)",([0-9.e-]+),[0-9.e-]+,[0-9.e-]+,"[mpn]",([01]),', s, re.M)
    checked = set(re.findall(r'^\s{2}([A-Za-z0-9]+): \[', s[s.index("const CHECK"):s.index("const METRIC")], re.M))
    out = []
    for sym, name, grp, tau, unstable in rows:
        z = np.log2(float(tau)) + 15
        row = int(np.searchsorted(CUTS, z, side="right"))
        out.append((sym, name, grp, row, unstable == "1", sym in checked))
    return out


def periodic_table():
    els = load_table()
    img = Image.new("RGB", (W, 1800), BG)
    d = ImageDraw.Draw(img)
    y0 = header(d, "THE PERIODIC TABLE OF SOUND", "70 ELEMENTS  //  ORDERED BY TIME OCTAVE  Z = log₂(τ / 1 s) + 15", 56)
    lab_w = 250
    cw = (W - 2 * PAD - lab_w) / 6
    top = y0 + 10
    fhead, fq = F(BOLD, 30), F(REG, 19)
    for i, (key, gname, q, col) in enumerate(GROUPS):
        x = PAD + lab_w + i * cw
        d.rectangle([x + 4, top, x + cw - 4, top + 112], fill=HEAD_BG)
        d.rectangle([x + 4, top, x + cw - 4, top + 7], fill=col)
        d.text((x + cw / 2, top + 22), gname, font=fhead, fill=col, anchor="mt")
        for k, l in enumerate(wrap(d, q, fq, cw - 28)):
            d.text((x + cw / 2, top + 54 + k * 24), l, font=fq, fill=GREY, anchor="mt")
    rh, gy = 150, top + 124
    fchip, fp, fr, fsym = F(BOLD, 27), F(BOLD, 30), F(REG, 22), F(SYM, 25)
    for r, (pname, prange) in enumerate(PERIODS):
        y = gy + r * rh
        d.rectangle([PAD, y + 4, PAD + lab_w - 10, y + rh - 4], fill=HEAD_BG)
        d.text((PAD + 22, y + rh / 2 - 18), f"{r + 1}  {pname}", font=fp, fill=WHITE, anchor="lm")
        d.text((PAD + 22, y + rh / 2 + 22), prange, font=fr, fill=GREY, anchor="lm")
        for i, (key, gname, q, col) in enumerate(GROUPS):
            x = PAD + lab_w + i * cw
            d.rectangle([x + 4, y + 4, x + cw - 4, y + rh - 4], fill=ROW_BG if r % 2 == 0 else ROW_ALT)
            cell = [e for e in els if e[2] == key and e[3] == r]
            cx, cy, chip_h = x + 16, y + 16, 46
            for sym, name, grp, row, unstable, ok in cell:
                tw = d.textlength(sym, font=fchip) + 26 + (d.textlength(" ✓", font=fsym) if ok else 0)
                if cx + tw > x + cw - 12:
                    cx, cy = x + 16, cy + chip_h + 10
                ink = col if unstable else BG
                if unstable:
                    d.rounded_rectangle([cx, cy, cx + tw, cy + chip_h], radius=10, outline=col, width=3)
                else:
                    d.rounded_rectangle([cx, cy, cx + tw, cy + chip_h], radius=10, fill=col)
                d.text((cx + 13, cy + chip_h / 2), sym, font=fchip, fill=ink, anchor="lm")
                if ok:
                    d.text((cx + 13 + d.textlength(sym, font=fchip), cy + chip_h / 2), " ✓", font=fsym, fill=ink, anchor="lm")
                cx += tw + 10
    ly = gy + 7 * rh + 28
    fl = F(REG, 25)
    d.rounded_rectangle([PAD + lab_w, ly, PAD + lab_w + 70, ly + 40], radius=9, fill=ACCENT)
    d.text((PAD + lab_w + 35, ly + 20), "Pu", font=F(BOLD, 22), fill=BG, anchor="mm")
    d.text((PAD + lab_w + 86, ly + 20), "stable element", font=fl, fill=GREY, anchor="lm")
    x2 = PAD + lab_w + 330
    d.rounded_rectangle([x2, ly, x2 + 70, ly + 40], radius=9, outline=ACCENT, width=3)
    d.text((x2 + 35, ly + 20), "Cl", font=F(BOLD, 22), fill=ACCENT, anchor="mm")
    d.text((x2 + 86, ly + 20), "defect (an unstable form)", font=fl, fill=GREY, anchor="lm")
    x3 = x2 + 470
    d.text((x3, ly + 20), "✓", font=F(SYM, 27), fill=WHITE, anchor="lm")
    d.text((x3 + 34, ly + 20), "measured in this project", font=fl, fill=GREY, anchor="lm")
    d.text((PAD + lab_w, ly + 72), "Rows are cut at the borders of hearing. An element sits in the row of its typical time τ.", font=fl, fill=GREY, anchor="lm")
    img = img.crop((0, 0, W, ly + 170))
    footer(img, ImageDraw.Draw(img))
    img.save(os.path.join(OUT, "01_periodic_table.png"))


def main():
    os.makedirs(OUT, exist_ok=True)
    periodic_table()
    table("01_time_octave.png", "ONE NUMBER FOR ORDER: THE TIME OCTAVE",
          "Z = log₂(τ / 1 s) + 15   //   ONE STEP DOUBLES THE TIME", ["Landmark", "τ", "Z"],
          [["The top of hearing, 20 kHz", "50 µs", "0.6"], ["The note A4, 440 Hz", "2.27 ms", "6.2"],
           ["20 Hz, where repeats turn into pitch", "50 ms", "10.7"], ["A pulse at 120 BPM", "0.5 s", "14"],
           ["A 4/4 bar at 120 BPM", "2 s", "16"], ["A song of four minutes", "240 s", "22.9"]],
          [0.62, 0.2, 0.18], note="The whole of music fits into about 23 steps of Z.")
    table("01_six_questions.png", "SIX QUESTIONS INSTEAD OF EIGHT FAMILIES",
          "THE GROUPS OF THE TABLE  //  THE SAME QUESTION RETURNS AT EVERY TIME SCALE", ["Group", "Question"],
          [[g[1], g[2]] for g in GROUPS], [0.32, 0.68])
    table("01_what_we_measured.png", "WHAT WE MEASURED", "EVERY CLAIM NEEDS A NUMBER, A KNOWN ANSWER AND DATA THE METHOD HAS NOT SEEN",
          ["Claim", "How it was tested", "Result"],
          [["The bar is an element whose Z moves with tempo", "Six Suno tracks in 4/4; the Z values for 80.5 and 100 BPM written down before measuring", "Z 16.58 and 16.26, as predicted. Above about 120 BPM the bar falls below Z 16, into the Beat row"],
           ["Metric levels nest as logarithms of whole numbers", "Chord changes, measured independently of the drums", "ΔZ = log₂ 4 or log₂ 8 within 0.003, on the four of seven tracks where the chord period is confirmed"],
           ["A best peak is not yet a period", "Four tests on every candidate; held-out noise, smooth swells, and real drums with the beat destroyed", "0% false and 0% missed periods held out (the bare rule: 100% false). Smooth swells: 25 of 40 passed before the fourth test, none after"],
           ["No hidden bias towards doubling", "A waltz, and a real 6/8 march", "Three beats per bar in the waltz; three eighths per beat and two beats per bar in the march"],
           ["Natural vibrato lives in the Event row", "Two operatic voices and a historic solo violin, with a piano as a control", "Z 12.3 to 12.5. The piano gave no false alarms; vibrato written into it was found at its rate"],
           ["Envelope is a Level element", "Known rises, decays and bursts on tones and noise; one held-out run; compression and stretching", "Times within 10% (median 0.3%) when a change lasts 8 carrier periods; scales exactly with tape speed. Not for noise at short times"],
           ["The detector can say no", "Two Suno tracks requested in 6/8", "Both came out binary, and the method said so"]],
          [0.25, 0.34, 0.41])
    table("01_beat_level.png", "IS THE PULSE THE BEAT?", "STRICT BENCHMARK  //  ONLY THE BEAT ITSELF COUNTS  //  TWO HELD-OUT SETS",
          ["Rule", "First held-out set", "Second held-out set (new generator)"],
          [["The rule in our core code", "80% of beats exact; the rest are bars and half bars", "76.5% exact"],
           ["Candidate: strong events only, period from its multiples, shortest confirmed level", "95% exact (34 better, 4 worse)", "94% exact (42 better, 7 worse)"]],
          [0.42, 0.29, 0.29], highlight={1},
          note="The candidate's new errors: heavy noise on the first set, and a kick on the \"and\" between beats (rock, boom-bap) on the second, where the old rule is right. It is not in the core code until it passes real recordings with verified beat labels.")
    table("01_space_compounds.png", "HOW LARGE IS THE SPACE?", "59 STABLE ELEMENTS  //  2⁵⁹ ≈ 5.8 × 10¹⁷ POSSIBLE SETS, ABOUT THE SECONDS SINCE THE BIG BANG",
          ["Elements in the compound", "Possible compounds", "Variants with five-position dials", "Listening at 30 s each"],
          [["2", "1,711", "–", "–"], ["3", "32,509", "4,063,625", "about 4 years"], ["5", "5,006,386", "15,644,956,250", "about 15,000 years"],
           ["8", "2,217,471,399", "866,199,765,234,375", "about 800 million years"], ["10", "62,828,356,305", "–", "–"]],
          [0.22, 0.24, 0.3, 0.24], note="With every element on a five-position dial plus \"off\": 6⁵⁹ ≈ 8.1 × 10⁴⁵ formulas. Each formula can be realised by countless melodies.")
    print(sorted(f for f in os.listdir(OUT) if f.startswith("01_")))


if __name__ == "__main__":
    main()
