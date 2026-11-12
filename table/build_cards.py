"""Build the element cards (issue #24) into both copies of the third edition.

  python table/build_cards.py           inject table/cards.json between the CARDS markers
  python table/build_cards.py --install add the card styles, the dialog and the renderer once

The card data lives in table/cards.json. The two pages (table/edition3.html and
table/standalone/Periodic_Table_of_Sound_edition3.html) carry the same code; this script keeps
them equal.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PAGES = [os.path.join(HERE, "edition3.html"), os.path.join(HERE, "standalone", "Periodic_Table_of_Sound_edition3.html")]
BEGIN, END = "// CARDS:BEGIN", "// CARDS:END"
PBEGIN, PEND = "// PREDICTIONS:BEGIN", "// PREDICTIONS:END"

CSS = """
/* element cards (issue #24) */
.cardbg { position: fixed; inset: 0; z-index: 50; background: color-mix(in srgb, #000 55%, transparent); display: flex; align-items: flex-start; justify-content: center; overflow-y: auto; padding: 32px 16px; }
.cardbg[hidden] { display: none; }
.card { width: min(860px, 100%); background: var(--panel); color: var(--ink); border: 1px solid var(--line); border-top: 6px solid var(--fam); border-radius: 14px; padding: 22px 26px 26px; position: relative; box-shadow: 0 20px 60px rgba(0,0,0,.35); }
.card .x { position: absolute; top: 12px; right: 12px; border: 1px solid var(--line); background: var(--panel); color: var(--ink); border-radius: 8px; width: 36px; height: 36px; font-size: 18px; cursor: pointer; }
.card .hd { display: flex; gap: 18px; align-items: center; margin: 0 40px 12px 0; }
.card .sym { font-family: var(--font-display); font-size: 44px; font-weight: 800; color: var(--fam); min-width: 86px; }
.card h2 { margin: 0; font-family: var(--font-display); font-size: 24px; letter-spacing: .03em; }
.card .meta { color: var(--muted); font-size: 13.5px; margin-top: 4px; }
.card .badge { display: inline-block; font-size: 12.5px; padding: 2px 9px; border-radius: 99px; border: 1px solid var(--fam); color: var(--fam); margin-right: 6px; }
.card .one { font-size: 18px; margin: 6px 0 4px; }
.card h4 { font-family: var(--font-display); font-size: 12.5px; letter-spacing: .1em; text-transform: uppercase; color: var(--fam); margin: 22px 0 8px; }
.card ul { margin: 0; padding-left: 20px; } .card li { margin: 3px 0; }
.card .typ { color: var(--muted); font-size: 12.5px; margin: -4px 0 6px; }
.card .listen { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
.card .btn { display: inline-block; background: var(--fam); color: var(--panel); text-decoration: none; font-weight: 700; padding: 9px 16px; border-radius: 8px; }
.card .chart { width: 100%; height: auto; display: block; margin: 6px 0 4px; }
.card .pred { border: 1px solid var(--line); border-radius: 10px; padding: 10px 14px; margin: 8px 0; }
.card .pred b { margin-right: 6px; } .card .pred small { display: block; color: var(--muted); margin-top: 3px; }
.card a { color: var(--fam); }
@media (max-width: 640px) { .card { padding: 18px 16px 20px; } .card .sym { font-size: 34px; min-width: 60px; } }
/* prediction scoreboard (issue #24) */
.score { background: var(--panel); border: 1px solid var(--line); border-radius: 10px; margin: 0 0 14px; }
.score summary { cursor: pointer; padding: 12px 16px; display: flex; flex-wrap: wrap; gap: 6px 18px; align-items: baseline; list-style: none; }
.score summary::-webkit-details-marker { display: none; }
.score summary b { font-family: var(--font-display); font-size: 13px; letter-spacing: .08em; text-transform: uppercase; }
.score .n { font-variant-numeric: tabular-nums; margin-right: 14px; white-space: nowrap; }
.score .hint { color: var(--muted); font-size: 12.5px; flex-basis: 100%; }
.score ol { margin: 0; padding: 4px 18px 14px 40px; } .score li { margin: 7px 0; }
.score li small { display: block; color: var(--muted); }
.score .chip { border: 1px solid var(--line); background: var(--band); color: var(--ink); border-radius: 6px; padding: 0 7px; font: inherit; font-size: 12.5px; cursor: pointer; margin-left: 6px; }
"""

DIALOG = '<div class="cardbg" id="cardbg" hidden><article class="card" id="card" role="dialog" aria-modal="true" aria-labelledby="cardname"></article></div>\n'

JS = r"""
// element cards (issue #24): the data is injected by table/build_cards.py
// CARDS:BEGIN
const CARDS = {};
// CARDS:END
const REPO = "https://github.com/alex-gerek/periodic-table-of-sound/blob/main/";
const LAB = location.pathname.includes("/standalone/") ? "../../lab/" : "../lab/";
const STATUS_ICON = {true: "✓ came true", partly: "✓ partly", false: "✗ did not come true", waiting: "🔮 waiting for a test"};
function cardChart(c) {
  const W = 760, rowH = 34, top = c.band ? 44 : 30, left = 250, right = 120, H = top + c.rows.length * rowH + 34;
  const x = v => left + (v - c.lo) / (c.hi - c.lo) * (W - left - right);
  let s = `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="${c.title}"><text x="0" y="16" font-size="13" fill="var(--muted)">${c.title}</text>`;
  const step = c.step || 1, dec = c.dec == null ? 2 : c.dec;
  for (let v = c.lo; v <= c.hi + 1e-9; v += step) s += `<line x1="${x(v)}" x2="${x(v)}" y1="${top - 6}" y2="${H - 28}" stroke="var(--line)"/><text x="${x(v)}" y="${H - 10}" font-size="12" text-anchor="middle" fill="var(--muted)">${+v.toFixed(3)}${Math.abs(v - c.hi) < 1e-9 ? " " + c.unit : ""}</text>`;
  if (c.band) s += `<rect x="${x(c.band[0])}" y="${top - 6}" width="${x(c.band[1]) - x(c.band[0])}" height="${H - 22 - top}" fill="var(--fam)" opacity="0.08"/><text x="${x((c.band[0] + c.band[1]) / 2)}" y="${top - 10}" font-size="11.5" text-anchor="middle" fill="var(--fam)">${c.band[2] || ""}</text>`;
  c.rows.forEach((r, i) => {
    const y = top + i * rowH + rowH / 2;
    s += `<text x="0" y="${y + 4}" font-size="13" fill="var(--ink)">${r.label}</text>`;
    if (r.median == null) { s += `<text x="${left}" y="${y + 4}" font-size="13" fill="var(--muted)">${r.note || "none"}</text>`; return; }
    const a = r.p10 == null ? r.median : r.p10, b = r.p90 == null ? r.median : r.p90, dim = r.control || r.open;
    if (b > a) s += `<line x1="${x(a)}" x2="${x(b)}" y1="${y}" y2="${y}" stroke="var(--fam)" stroke-width="8" stroke-linecap="round" opacity="${dim ? 0.45 : 0.85}"${dim ? ' stroke-dasharray="3 5"' : ""}/>`;
    s += `<circle cx="${x(r.median)}" cy="${y}" r="7" fill="${r.open ? "var(--panel)" : "var(--fam)"}" stroke="var(--fam)" stroke-width="3"/><text x="${x(b) + 12}" y="${y + 4}" font-size="12.5" fill="var(--muted)">${r.text || r.median.toFixed(dec) + " " + c.unit}</text>`;
  });
  return s + "</svg>";
}
function openGapCard(name) {
  const g = GAPS.find(x => x[0] === name);
  if (!g || !CARDS["gap:" + name]) return false;
  return openCard({ s: "?", name: g[0], g: g[1], p: g[2], gap: true, key: "gap:" + name });
}
function openCard(e) {
  const k = CARDS[e.key || e.s], bg = document.getElementById("cardbg"), C = document.getElementById("card");
  if (!k) return false;
  const P = PERIODS[e.p - 1];
  C.style.setProperty("--fam", gv(e.g));
  const chk = !e.gap && CHECK[e.s];
  const links = (k.found && k.found.links || []).map(([t, u]) => `<a href="${REPO}${u}" target="_blank" rel="noopener">${t}</a>`).join(" · ");
  C.innerHTML = `<button class="x" id="cardx" aria-label="Close">✕</button>
    <div class="hd"><div class="sym">${e.s}</div><div><h2 id="cardname">${e.name}</h2>
      <div class="meta">${e.gap ? `Predicted cell · ${GRP[e.g][0]} · Period ${e.p} (${P[0]}, ${P[1]}, ${P[2]})` : `${GRP[e.g][0]} · Period ${e.p} (${P[0]}, ${P[1]}) · Z ${fmtZ(e.z)}, range ${fmtZ(zOf(e.tmin))} – ${fmtZ(zOf(e.tmax))}`}</div>
      <div style="margin-top:6px">${e.gap ? `<span class="badge">🔮 predicted cell</span>` : chk ? `<span class="badge">✓ measured in this project</span>` : `<span class="badge">not measured yet</span>`}${e.of && byS[e.of] ? `<span class="badge">built on ${byS[e.of].name}</span>` : ""}</div></div></div>
    <p class="one">${k.sentence}</p>
    <h4>Where you hear it</h4><p class="typ">Typical examples, a description rather than a measurement.</p><ul>${k.where.map(w => `<li>${w}</li>`).join("")}</ul>
    <h4>Its place in the table</h4><ul>${k.place.map(w => `<li>${w}</li>`).join("")}</ul>
    ${k.listen ? `<h4>Listen</h4><div class="listen">${k.listen.recipe ? `<a class="btn" href="${LAB}collider.html?recipe=${k.listen.recipe}" target="_blank" rel="noopener">▶ Open in the collider</a>` : ""}<span>${k.listen.label}</span></div>` : ""}
    ${k.found ? `<h4>How we found it</h4><p>${k.found.summary}</p>${k.found.chart ? cardChart(k.found.chart) : ""}<ul>${k.found.numbers.map(w => `<li>${w}</li>`).join("")}</ul>
      ${k.found.limits && k.found.limits.length ? `<p style="margin:10px 0 4px"><b>Where it does not work yet</b></p><ul>${k.found.limits.map(w => `<li>${w}</li>`).join("")}</ul>` : ""}<p>${links}</p>` : ""}
    ${k.predictions ? `<h4>Our predictions</h4>${k.predictions.map(p => `<div class="pred"><b>${STATUS_ICON[p.status]}</b>${p.text}<small>Would fail if: ${p.fail}</small><small>${p.evidence}${p.link ? ` <a href="${REPO}${p.link}" target="_blank" rel="noopener">evidence</a>` : ""}</small></div>`).join("")}` : ""}
    <h4>In PHARMAKON</h4><p>${k.pharmakon}</p>`;
  bg.hidden = false;
  document.getElementById("cardx").onclick = closeCard;
  document.getElementById("cardx").focus();
  return true;
}
function closeCard() { document.getElementById("cardbg").hidden = true; }
document.getElementById("cardbg").addEventListener("click", ev => { if (ev.target.id === "cardbg") closeCard(); });
document.addEventListener("keydown", ev => { if (ev.key === "Escape") closeCard(); });
"""


def inject_predictions(s, preds):
    a, b = s.index(PBEGIN), s.index(PEND)
    return s[:a] + PBEGIN + "\nconst PREDICTIONS = " + json.dumps(preds["list"], ensure_ascii=False, indent=1) + ";\n" + s[b:]


SCORE_JS = r"""
// prediction scoreboard (issue #24): the data is injected by table/build_cards.py
// PREDICTIONS:BEGIN
const PREDICTIONS = [];
// PREDICTIONS:END
(function () {
  const box = document.getElementById("score"); if (!box) return;
  const n = st => PREDICTIONS.filter(p => p.status === st).length;
  const ICON = { true: "✓", partly: "◐", false: "✗", waiting: "🔮" };
  const name = k => k.startsWith("gap:") ? k.slice(4) : (byS[k] ? byS[k].name : k);
  box.innerHTML = `<details class="score"><summary><b>Predictions</b>
      <span class="n">${PREDICTIONS.length} made</span><span class="n">✓ ${n("true")} came true</span><span class="n">◐ ${n("partly")} partly</span>
      <span class="n">✗ ${n("false")} did not</span><span class="n">🔮 ${n("waiting")} waiting</span>
      <span class="hint">Only predictions written down before their test are counted. Click to see each one and its evidence.</span></summary>
    <ol>${PREDICTIONS.map(p => `<li>${ICON[p.status]} ${p.text}<button class="chip" data-el="${p.el}">${name(p.el)}</button>
      <small>${p.evidence}${p.link ? ` <a href="${REPO}${p.link}" target="_blank" rel="noopener">evidence</a>` : ""}</small></li>`).join("")}</ol></details>`;
  box.addEventListener("click", ev => {
    const c = ev.target.closest(".chip"); if (!c) return;
    const k = c.dataset.el, el = k.startsWith("gap:") ? T.querySelector(`.el[data-gap="${k.slice(4)}"]`) : T.querySelector(`.el[data-s="${k}"]`);
    if (el) { el.click(); el.scrollIntoView({ block: "center" }); }
  });
})();
"""


def install_score(s):
    if PBEGIN in s:
        return s
    anchor = '  <div class="status">'
    assert s.count(anchor) == 1
    s = s.replace(anchor, '  <div id="score"></div>\n' + anchor)
    a = "// column chains"
    return s.replace(a, SCORE_JS.strip() + "\n\n" + a)


def replace_score(s):
    a = s.index("// prediction scoreboard (issue #24)")
    b = s.index("// column chains")
    return s[:a] + SCORE_JS.strip() + "\n\n" + s[b:]


def inject(s, cards):
    a, b = s.index(BEGIN), s.index(END)
    data = json.dumps({k: v for k, v in cards.items() if not k.startswith("_")}, ensure_ascii=False, indent=1)
    return s[:a] + BEGIN + "\nconst CARDS = " + data + ";\n" + s[b:]


def install(s):
    if BEGIN in s:
        return s
    s = s.replace("</style>", CSS + "</style>", 1)
    s = s.replace('<script>', DIALOG + '<script>', 1) if s.count("<script>") == 1 else s
    anchor = "// column chains"
    assert s.count(anchor) == 1
    s = s.replace(anchor, JS.strip() + "\n\n" + anchor)
    old = "else { press(`[data-s=\"${b.dataset.s}\"]`); showEl(byS[b.dataset.s]); }"
    new = "else { press(`[data-s=\"${b.dataset.s}\"]`); showEl(byS[b.dataset.s]); openCard(byS[b.dataset.s]); }"
    assert s.count(old) == 1
    return s.replace(old, new)


def hook_gaps(s):
    old = "if (b.dataset.gap) { press(`[data-gap=\"${b.dataset.gap}\"]`); showGap(b.dataset.gap); }"
    new = "if (b.dataset.gap) { press(`[data-gap=\"${b.dataset.gap}\"]`); showGap(b.dataset.gap); openGapCard(b.dataset.gap); }"
    return s.replace(old, new) if old in s else s


def replace_renderer(s):
    """Replace the installed renderer with the current one (keeps the injected data)."""
    a = s.index("// element cards (issue #24)")
    b = s.index("// prediction scoreboard (issue #24)") if "// prediction scoreboard (issue #24)" in s else s.index("// column chains")
    return s[:a] + JS.strip() + "\n\n" + s[b:]


def replace_css(s):
    """Keep the installed card and scoreboard styles equal to CSS (from its first line to </style>)."""
    a = s.index("/* element cards (issue #24) */")
    b = s.index("</style>", a)
    return s[:a] + CSS.strip() + "\n" + s[b:]


def main():
    cards = json.load(open(os.path.join(HERE, "cards.json"), encoding="utf-8"))
    preds = json.load(open(os.path.join(HERE, "predictions.json"), encoding="utf-8"))
    for p in PAGES:
        s = open(p, encoding="utf-8").read()
        if "--install" in sys.argv:
            s = install(s)
        else:
            s = replace_renderer(s)
        s = hook_gaps(s)
        s = replace_css(s)
        s = install_score(s)
        s = replace_score(s)
        s = inject(s, cards)
        s = inject_predictions(s, preds)
        open(p, "w", encoding="utf-8", newline="").write(s)
        print("built", os.path.relpath(p, HERE), "cards:", [k for k in cards if not k.startswith("_")])


if __name__ == "__main__":
    main()
