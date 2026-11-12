# Research history

Read [the research journal](docs/research_journal.md) before research work and follow its recording rules. Use [the step template](docs/research_step_template.md).

- Record every research step, including unsuccessful tests, rejected approaches, parameter trials, implementation errors, interrupted runs and inconclusive findings. Record the path to a result, not only the final result.
- Open or take a GitHub issue before any development or project change, and name it in the journal entry.
- Create a dated journal entry before running an experiment. Append the outcome, evidence and next decision afterward; retain the initial hypothesis and expectations.
- Preserve earlier entries, runnable variants, configurations and outputs. Give each run a unique ID and a fresh output location; do not overwrite previous research results. Link corrections and superseding runs to their predecessors.
- Keep failures and known limitations visible. A rejected approach remains research evidence; an expected failure is not a passing test. Never remove a case merely to improve reported scores.
- Link changes to the Sound Collider, periodic table and measuring code to the journal steps that motivated and validated them.
- Research records may be internal. Retaining a record does not require publishing it. Keep audio and large or restricted artifacts outside git, with provenance and hashes in the appropriate local manifest.
- Two journals: the public [research journal](docs/research_journal.md) and the internal `docs/research_journal_internal.md` (excluded from the public export) for restricted material, internal prototypes and notes for PHARMAKON.
- Start runs through `experiments/runlog.py`, which gives each run an ID and its own folder.
- Research decisions on the table and the Sound Collider rest with Claude as research lead; Lex Gerek owns the project and merges.
- Write repository records in English. Preserve unrelated work and follow CONTRIBUTING.md for publishing changes.
