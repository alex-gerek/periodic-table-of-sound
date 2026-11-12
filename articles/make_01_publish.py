"""Build the copy-ready page of article 01 for X Articles (and other editors that take rich text).

Every Markdown table becomes an image slot [IMAGE n], the images are copied next to the page,
and a "Copy article text" button copies headings, bold, italics, lists and links.
Run after make_01_figures.py:  python articles/make_01_publish.py  ->  _publish/01/index.html
"""
import html
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(HERE, "01_the_periodic_table_of_sound.md")
OUT = os.path.join(ROOT, "_publish", "01")
SITE = "https://alex-gerek.github.io/periodic-table-of-sound/"
REPO = "https://github.com/alex-gerek/periodic-table-of-sound"

# image for each Markdown table, in order of appearance; None = covered by the previous image
TABLE_IMAGES = ["01_time_octave.png", "01_six_questions.png", "01_what_we_measured.png", "01_beat_level.png",
                "01_space_compounds.png", None]
ALT = {"01_periodic_table.png": "The Periodic Table of Sound: 70 elements by group and time octave",
       "01_time_octave.png": "The time octave Z and its landmarks", "01_six_questions.png": "The six groups and their questions",
       "01_what_we_measured.png": "What we measured", "01_beat_level.png": "Is the pulse the beat? The strict benchmark",
       "01_space_compounds.png": "How large is the space of compounds"}
HERO_BEFORE = "## 1."
LINKS = [("Open the table", SITE + "table/standalone/Periodic_Table_of_Sound_edition3.html"),
         ("Open the Sound Collider", SITE + "lab/collider.html"), ("Source code and data", REPO),
         ("Archived version (DOI)", "https://doi.org/10.5281/zenodo.24161074")]


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"`([^`]+)`", r'<code class="notranslate">\1</code>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![*\w])\*([^*]+)\*(?![*\w])", r"<em>\1</em>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    return t


def convert(md):
    out, slots, n_table, i = [], [], 0, 0
    lines = md.splitlines()

    def slot(img):
        slots.append(img)
        k = len(slots)
        return (f'<div class="slot"><p class="marker"><strong>[IMAGE {k}]</strong> {html.escape(ALT[img])} '
                f'<span class="file">({img})</span></p><img src="{img}" alt="{html.escape(ALT[img])}"></div>')

    while i < len(lines):
        l = lines[i]
        if l.startswith(HERO_BEFORE) and "01_periodic_table.png" not in slots:
            out.append(slot("01_periodic_table.png"))
        if l.startswith("|"):
            while i < len(lines) and lines[i].startswith("|"):
                i += 1
            img = TABLE_IMAGES[n_table]
            n_table += 1
            if img:
                out.append(slot(img))
            continue
        if l.startswith("# "):
            out.append(f"<h1>{inline(l[2:])}</h1>")
        elif l.startswith("## "):
            out.append(f"<h2>{inline(l[3:])}</h2>")
        elif l.startswith("### "):
            out.append(f"<h3>{inline(l[4:])}</h3>")
        elif re.match(r"^\s*[-*] ", l) or re.match(r"^\s*\d+\. ", l):
            ordered = bool(re.match(r"^\s*\d+\. ", l))
            tag = "ol" if ordered else "ul"
            items = []
            while i < len(lines) and (re.match(r"^\s*[-*] ", lines[i]) or re.match(r"^\s*\d+\. ", lines[i])):
                items.append(re.sub(r"^\s*([-*]|\d+\.) ", "", lines[i]))
                i += 1
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
            continue
        elif l.strip():
            para = [l.strip()]
            while i + 1 < len(lines) and lines[i + 1].strip() and not re.match(r"^(#|\||\s*[-*] |\s*\d+\. )", lines[i + 1]):
                i += 1
                para.append(lines[i].strip())
            out.append(f"<p>{inline(' '.join(para))}</p>")
        i += 1
    out.append("<hr>" + "".join(f'<p><strong>{html.escape(t)}:</strong> <a href="{u}">{u}</a></p>' for t, u in LINKS))
    return "\n".join(out), slots


PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Article 01 - copy-ready</title>
<style>
:root{--ink:#111827;--muted:#6b7280;--line:#e5e7eb;--accent:#c2410c;--bg:#ffffff}
body{margin:0;background:#f3f4f6;color:var(--ink);font:17px/1.65 "Segoe UI",system-ui,sans-serif}
.bar{position:sticky;top:0;z-index:5;background:#0b0d13;color:#fff;padding:12px 16px;display:flex;gap:12px;align-items:center;flex-wrap:wrap}
.bar button{background:#fb923c;color:#111;border:0;border-radius:6px;padding:9px 16px;font-weight:700;cursor:pointer}
.bar span{color:#a0aaba;font-size:14px}
main{max-width:760px;margin:24px auto;background:var(--bg);padding:40px 48px;border-radius:10px;box-shadow:0 1px 3px rgba(0,0,0,.08)}
h1{font-size:30px;line-height:1.25;margin:0 0 14px}h2{font-size:24px;margin:36px 0 10px}h3{font-size:20px;margin:28px 0 8px}
hr{border:0;border-top:1px solid var(--line);margin:28px 0}
code{background:#f3f4f6;padding:1px 5px;border-radius:4px;font-size:15px}
.slot{margin:22px 0;padding:12px;border:2px dashed #fb923c;border-radius:8px;background:#fff7ed}
.slot .marker{margin:0 0 8px;color:var(--accent)}.slot .file{color:var(--muted);font-size:13px}.slot img{width:100%;display:block;border-radius:4px}
@media (max-width:640px){main{padding:24px 16px;margin:0;border-radius:0}}
</style></head><body>
<div class="bar"><button id="copy">Copy article text</button><span id="msg">Copies headings, bold, italics, lists and links. Images are marked [IMAGE n]: upload each file at its marker.</span></div>
<main id="article">
__BODY__
</main>
<script>
document.getElementById('copy').onclick = async () => {
  const src = document.getElementById('article').cloneNode(true);
  src.querySelectorAll('.slot').forEach(s => { const p = document.createElement('p'); p.textContent = s.querySelector('.marker strong').textContent; s.replaceWith(p); });
  const html = src.innerHTML, text = src.innerText;
  try {
    await navigator.clipboard.write([new ClipboardItem({'text/html': new Blob([html], {type: 'text/html'}), 'text/plain': new Blob([text], {type: 'text/plain'})})]);
    document.getElementById('msg').textContent = 'Copied. Paste into the editor, then upload IMAGE 1 to __N__ at their markers.';
  } catch (e) {
    const r = document.createRange(); r.selectNodeContents(document.getElementById('article'));
    const s = getSelection(); s.removeAllRanges(); s.addRange(r);
    document.getElementById('msg').textContent = 'Text selected: press Ctrl+C.';
  }
};
</script></body></html>
"""


def main():
    body, slots = convert(open(SRC, encoding="utf-8").read())
    os.makedirs(OUT, exist_ok=True)
    for k, img in enumerate(slots, 1):
        shutil.copy(os.path.join(HERE, "img", img), os.path.join(OUT, f"{k:02d}_{img}"))
        body = body.replace(f'src="{img}"', f'src="{k:02d}_{img}"').replace(f"({img})", f"({k:02d}_{img})")
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(PAGE.replace("__BODY__", body).replace("__N__", str(len(slots))))
    print(len(slots), "images:", [f"{k:02d}_{s}" for k, s in enumerate(slots, 1)])


if __name__ == "__main__":
    main()
