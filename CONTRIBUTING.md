# Contributing

Thank you for your interest. The project follows a few firm rules.

## The rules

- **Measure, don't guess.** A new element or detector comes with a ground-truth test on a synthetic signal with a known answer, a control in which the detector must find nothing, and a result on real material. Listening is welcome for exploring, but it is never the deciding argument.
- **Our own mathematics.** Methods from papers may be re-derived and implemented from scratch. Do not add third-party code or pretrained models to `pts/`. numpy is the only dependency of the measuring code.
- **No audio in git.** Recordings and stems stay out of the repository. Describe the material and its licence in a `SOURCES.txt` file instead.
- **English only.** Code, comments, docs and commit messages are written in English.
- **Honest records.** If something fails, keep the failure in the experiment's README together with what it teaches.

## How to contribute

1. Open an issue that describes the element, the question it asks, and the test that would prove it.
2. Add code to `pts/` and a test to `tests/`. `python -m pytest tests` must pass.
3. Put real-material runs into a dated folder under `experiments/` with a `README.md` and the results.
4. Open a pull request.

By contributing you agree that your contribution is released under the project's MIT licence.
