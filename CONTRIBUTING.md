# Contributing

Thank you for your interest. The project follows a few firm rules.

## The rules

- **Measure, don't guess.** A new element or detector comes with a ground-truth test on a synthetic signal with a known answer, a control in which the detector must find nothing, and a result on real material. Listening is welcome for exploring, but it is never the deciding argument.
- **Our own mathematics.** Methods from papers may be re-derived and implemented from scratch. Do not add third-party code or pretrained models to `pts/`. numpy is the only dependency of the measuring code.
- **No audio in git.** Recordings and stems stay out of the repository. Describe the material and its licence in a `SOURCES.txt` file instead.
- **English only.** Code, comments, docs and commit messages are written in English.
- **Honest records.** If something fails, keep the failure in the experiment's README together with what it teaches.
- **Keep the research journey.** Record every research step, including successful and failed tests, rejected ideas, errors and corrections, in the [research journal](docs/research_journal.md), using the [step template](docs/research_step_template.md). Preserve each run's code, configuration and evidence without overwriting earlier results. Link adopted Collider, table and detector changes to their research history. Internal records need not be published.

## How work is coordinated

Several people work on the project, and Claude (Anthropic) is one of them.

- **Roles.** Lex Gerek owns the project and the idea, and merges pull requests. Claude leads the research on the table and the Sound Collider: it decides methods, validation rules, and what is adopted into `pts/`, and it reviews research changes before they are merged.

Two rules keep people from doing the same task twice or overwriting each other:

- **One task, one issue, one owner.** Every task starts as a GitHub issue. Before you start, assign yourself, or comment "taking this" if you cannot assign. If an issue already has an owner, leave it to them or ask in the issue.
- **Everything reaches `main` through a pull request.** `main` is protected:
  - direct pushes, force-pushes and deletion are blocked;
  - the tests on Python 3.10 and 3.12 must pass before a merge;
  - the maintainer reviews and merges.

## How to contribute

1. Open an issue, or pick an open one and assign yourself. Describe the element, the question it asks, and the test that would prove it.
2. Create a branch named after you and the topic, for example `lex/level-column`.
3. Add code to `pts/` and a test to `tests/`. `python -m pytest tests` must pass.
4. Put real-material runs into a dated folder under `experiments/`, with a `README.md` and the results.
5. Open a pull request that says `Closes #<issue number>`. Push to your branch only, never to `main`.

By contributing you agree that your contribution is released under the project's MIT licence.
