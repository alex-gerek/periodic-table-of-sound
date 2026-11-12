# Research journal: the journey

This is the chronological index of the project's research journey. Keep how we reached a result: the question, expectation, attempts, failures, surprises, corrections and decisions. Successful findings inform the Sound Collider, the periodic table and the measuring code; unsuccessful findings remain available for future research.

## Recording rules

1. **Start before the attempt.** Every step belongs to a GitHub issue, opened before development or any change to the project starts (see CONTRIBUTING.md). Give each research step a unique ID, for example `2026-11-12-pulse-001`, and add an entry here linking to its dated experiment folder and step record. State the hypothesis, expected outcome and planned check before execution. Small exploratory attempts may share a step record, but each distinct trial needs its own run ID, configuration and outcome.
2. **Record every outcome.** Include successes, failures, null results, regressions, rejected features, abandoned prototypes, parameter sweeps, crashes and interrupted runs. Preserve commands or runnable scripts, code revision and local diff where relevant, parameters, seeds, input provenance, dataset split and evaluation definitions. Log automated sweeps in a machine-readable trial table rather than manually narrating each iteration. Routine file browsing need not have a separate entry.
3. **Preserve evidence.** Give each run a fresh location, such as `experiments/<study>/runs/<run-id>/`, for its configuration, stdout/stderr and complete per-case results. Record aggregate metrics alongside failures and changed cases. Preserve failed prototypes in runnable form or as a recoverable revision or patch. A seed alone is insufficient without its generator version and configuration. Do not keep the only copy of evidence in temporary storage or an ignored output folder. An artifact that is regenerated exactly by a recorded command at a recorded revision (for example a feature cache computed from seeds) may stay out of git; the record must name the command and the revision. Outputs committed before this journal existed are preserved by the git history, which counts as a recoverable revision. New runs use `experiments/runlog.py`, which gives each run its own folder under `runs/` with its ID, revision, command, environment and console output.
4. **Append corrections.** Never silently replace old outputs or rewrite an initial hypothesis to match the outcome. Add a correction explaining what was wrong, which results are affected and which new run supersedes them. Mark invalid evidence as invalid and retain it; do not use it to support a claim. Cosmetic fixes are allowed if they do not change meaning. A report that a script regenerates in place (`results.md`) is a summary: before it is regenerated, its previous version must be committed, so that the history keeps it.
5. **Explain the next turn.** After every attempt, record the observation, interpretation, remaining uncertainty and reason for the next action. Distinguish a measured fact from a hypothesis. An approach that is not used today remains discoverable, with the reason it was set aside.
6. **Keep evaluation history honest.** Record which data informed each decision. Once a held-out set is inspected to guide changes, mark it as development data and retain its earlier status and results in history. Keep omissions, exclusions, expected failures and unavailable data explicit, with counts and reasons. Do not relabel or remove hard cases to improve scores.
7. **Connect research to the product.** Every adopted change to the Collider, table or `pts/` links back to its motivating step and validation runs. The step links forward to the implementation revision or PR and states where the finding is used. A successful experiment may still be unsuitable for adoption; record that decision too.
8. **Separate retention from publication.** Internal research can remain internal. Audio stays outside git. Large or restricted artifacts may live in a persistent external archive, with location, provenance and hashes recorded in an appropriately private manifest. Preserve a recoverable copy, including the relevant code and generator versions. Checkpoint and back up records with their artifacts; do not publish or push automatically. There are two journals. This one is public and covers what is published. The internal journal, `docs/research_journal_internal.md`, is excluded from the public export. It holds steps on restricted material (for example data whose terms are unclear), internal prototypes, and notes on what could be used in PHARMAKON.

Use [the step template](research_step_template.md). For a small step, the *Minimum entry* at the top of the template is enough; automated sweeps write their own run ledger.

**Where each record goes:**
- **This journal:** the whole path, step by step, including what was set aside.
- **The experiment README:** the current state of one experiment.
- **`ROADMAP.md`:** short milestones and the plan; it links here for detail.
- **Pull request descriptions:** what changed in the code and the evidence for it; they link to the steps.

An experiment README is the current overview; step records and preserved runs provide the chronological evidence behind it. Summary documents may change as knowledge changes, while their supporting history remains accessible.

## Entries

### 2026-11-12-recordkeeping-001: establish the journal

- **Request:** preserve every step of research, including unsuccessful tests and discarded branches, so that future work can revisit the full journey.
- **Change:** added the recording rules, a reusable step template and repository instructions; linked the policy from CONTRIBUTING.md.
- **Outcome:** future research must preserve both the evidence and the decisions connecting it to the Collider, table and measuring code.
- **Historical scope:** earlier experiments already contain scripts, reports and results under `experiments/`. This entry does not claim their full trial histories have been recovered. When revisiting them, link the available evidence and mark missing history as unavailable; do not invent entries or dates.
- **Next:** start the next research step with a record before running it, and append each attempted variant and outcome as work proceeds.

### 2026-11-12-recordkeeping-002: amendments by the research lead (Claude)

- **Change:**
  - committed outputs from before this journal are preserved by the git history;
  - regenerated reports are committed before they are regenerated;
  - regenerable caches may stay out of git, together with their command and revision;
  - new runs get their own folder through `experiments/runlog.py`;
  - two journals, public and internal;
  - the roles of the journal, the experiment README, the roadmap and pull requests;
  - a minimum entry for small steps;
  - the README rule "keep the failure with what it teaches" is restored in CONTRIBUTING.md;
  - `CLAUDE.md` points to `AGENTS.md`, so that Claude reads these rules in every session.
- **Why:** the first version required that no result ever be overwritten, but every `run.py` regenerates its report in place. It also forbade ignored copies, although caches are exact functions of seeds and code. And it would have sent internal steps to the public export.
- **Found while applying it:** the exploratory scripts of 2026-11-12 existed only in a temporary folder. They are now kept unchanged in `experiments/_prototypes_internal/2026-11-12/` (internal), with an index and hashes.

### 2026-11-12-recordkeeping-003: citable snapshot (issue #17)

- **Before:** Codex opened issue #17 through the maintainer account: record the studies, publish the band-split result and the journal, check the article, prepare citation metadata, and release a version for Zenodo. Most of it was already done locally, so with the owner's approval Claude took the issue over, and Codex reviews.
- **Changes:**
  - the band-split conclusion is narrowed to the tested features, classifiers and generator;
  - the rules now require an issue before any development;
  - `CITATION.cff` is set to version 0.4.0 of 2026-11-12, with an abstract of this version. Lex Gerek is the author, and the development with Claude is stated in the abstract.
- **Article:** its numbers were checked against the stored results before PR #16. It does not mention the band split.
- **Not a legal step:** a DOI records a version and its date. It does not register a patent or a copyright.
- **Next:** a pull request for the journal, the rules and the band split; after the merge, and with the owner's confirmation, the release that Zenodo archives.

---

The entries below were **reconstructed on 2026-11-12** from commits, experiment READMEs and the working session, after the steps had run. Times are not given, because they were not recorded. Hypotheses are stated as they were written in the issues before the runs.

### 2026-11-12-confirm-001: is a best peak a period? (issue #7)

- **Before:** the peak rule always returns a candidate. *Hypothesis:* a test against the noise level of the autocorrelation separates real periods from chance peaks. *Check:* train the thresholds on one set, then apply them unchanged to other generators and to real stems.
- **Runs:**
  - first version, rejected: the stems were downsampled, which stretched time by ×1.088;
  - second version, rejected: the shuffle control cut pieces of one fixed length (120 ms), which built a 120 ms grid;
  - final version: native sample rate, and pieces of random length with fades.
- **Outcome:** 0% false and 0% missed periods on the held-out sets, against 100% false with the bare rule. Earlier claims were corrected: the harmonic rhythm is confirmed on 4 of 7 tracks, and Loop and Repetition are never confirmed.
- **Use:** `confirm_period()` in `pts/`. PR #9.

### 2026-11-12-collider-001: runs racing the recipe; random controls (issue #8)

- **Outcome:** each run works on a snapshot of the recipe and its version, and the noise is seeded. Two renders agreed to 1.2·10⁻⁷. Checked by moving a slider in the middle of a run. PR #11.

### 2026-11-12-collider-002: false Variation at 150 BPM in 3/4 (issue #10)

- **Before:** the issue blamed the synthesis.
- **What happened:** four causes, found one after another:
  1. **The same hit rendered differently** depending on its place in a 128-frame block. Snapping the start to a whole sample did not help; removing the pitch sweep did. Fix: each hit is rendered once and copied.
  2. **The bar grid drifted.** After fix 1 the bars were equal sample for sample, but Variation was still reported. Fix: a Theil–Sen fit.
  3. **The pulse rule picked the bar** on the new sound, because the onset curve was spiky. Fix: a ±15 ms triangle.
  4. **The meter median took the upper middle value.** Fix: a true median.
- **Threshold:** a one-beat fill fell below the threshold of 0.1. The new floor (0.0035) and the weakest fill (0.081) were measured, and the threshold was set to 0.02.
- **Interrupted:** one comparison run timed out in the browser. It was repeated in the background, with its state kept in the page.
- **Outcome:** 359 of 360 settings pass, up from 304. The one failure is kept as a known limit. PR #12.

### 2026-11-12-confirm-002: a single smooth burst confirmed as a period (issue #13, review)

- **Before:** review reported three problems:
  - one swell in 100 s was confirmed at 14 σ;
  - reports ignored `confirmed=False`;
  - the wrong-period rate on real stems defaulted to "right".
- **Runs:**
  - return test with the valley searched from lag 0: 3 of 40 smooth signals were still confirmed, with 5% false detections on the test set (**rejected**);
  - valley searched from lag/2 to the lag: 0 of 40 (adopted).
- **Implementation error found:** the meter script crashed on `meter_6-8_real`, a folder without a drum stem. The input checks of issue #5 now reject that case, and the script skips such folders.
- **Outcome:** smooth signals confirmed went from 25 of 40 to 0. The thresholds came out the same. Two verdicts changed, and both are documented. PR #14.

### 2026-11-12-pulse-001: are the remaining wrong periods a defect? (issue #15)

- **Before:** one wrong period in 60 test positives. *Question:* doubling, halving, the bar, or something else?
- **What happened:**
  - there were **three** wrong periods, not one: 5 beats twice, and a beat 3.2% off;
  - the metric counted any multiple as right, which hid bar-instead-of-beat: the beat itself was chosen in only 47 and 37 of 60;
  - candidate rules were tried on synthetic and on real stems.
- **Set aside, with reasons:**
  - the shortest confirmed level returns the eighths on 6 real tracks;
  - the exact comb flips the 80 BPM retake to the eighths;
  - the old rule plus a descent to T/q was tuned on the same real tracks it would be judged on.
- **Decision (Lex):** a strict benchmark first.

### 2026-11-12-pulse-002: strict beat-level benchmark, candidate v1 (issue #15)

- **Runs:**
  - on the development set of 320 signals: rules A, B and C, the band edge, and the share ρ (the sweeps are in the internal prototypes);
  - v1 fixed at ρ = 0.5 and 2.5 kHz, then the first final set, run once.
- **Implementation error:** a prototype produced a negative period, and `confirm_period()` raised on it. The first prototype comparison crashed for this reason and was rerun. A guard was added to `pts/`, with a test.
- **Outcome:** on the final set the old rule got 160 and v1 190 of 200, with 4 worsened. Real stems are not scored, because no label is verified. Commit `babad3f`.

### 2026-11-12-pulse-003: four worsened signals, v2, second held-out set (issue #15)

- **Status change:** the first final set became development data once it was inspected.
- **Runs:**
  - occupancy check, κ from 0.6 to 0.9: it cost 31 to 72 beats (**rejected**);
  - ratio r(T)/r(2T): the classes overlap (**rejected**);
  - support by a confirmed multiple: 505 → 510 of 520 (adopted as v2);
  - a new generator (`holdout_b.py`), committed together with v2 before either was run, then run once.
- **Outcome:** old 153, v1 188, v2 188 of 200. v2 gives nothing over v1 on independent data. The known errors are kept as strict xfail tests. Tag `beat-level-comparison-2026-11-12`.

### 2026-11-12-bands-001: does splitting events by band tell the beat from its half? (issue #15)

- **Before:** *hypothesis:* low, mid and high envelopes and their joint pattern carry beat information that the full envelope lacks. *Rule set by Lex:* if they do, make a candidate and test it on a new set; if they do not, keep the negative result.
- **Runs:**
  - hats with an accent on the beat: bands 98.1%, full 93.4%;
  - hats all at one level: 97.8% against 95.1%;
  - hats at one level and at the same physical step under both labels: 95.7% against 95.5%, McNemar χ² = 0.1.
- **Interrupted:** the first analysis crashed at the very end (`HERE` undefined), after computing every feature. It was rerun with a feature cache.
- **Outcome:** negative, within its scope (these features, two classifiers, one generator). The gain came from conventions in the generator, not from the beat. No candidate was made. Commit `ccbd8b4`.
- **Correction (issue #17):** the first wording, "the bands carry no information about the beat", was wider than the evidence. It was narrowed to the tested features, classifiers and generator.
