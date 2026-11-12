"""Give every research run an ID and a folder of its own (so that no run overwrites another).

    from runlog import run_folder
    with run_folder(__file__, "final2") as run:
        ...                                   # print() goes to the console and to run/console.txt
        save(os.path.join(run.path, "results.json"))

This creates `<experiment>/runs/<run-id>/` with:
  meta.json     run ID, UTC start and end, git revision, whether the tree had local changes
                (and the SHA-256 of `git diff HEAD`), the command line, the Python and numpy
                versions, and the names of the PTS_* variables that were set
  console.txt   everything printed during the run
The run ID is `<UTC time>-<label>-<revision>`, so a rerun never overwrites an earlier run.
An exception is recorded in meta.json and then raised again: a crashed run keeps its folder.

The values of PTS_* variables are not written, because they are local paths; only a hash of
each value is kept, which is enough to tell whether two runs used the same input.
"""
import contextlib
import datetime
import hashlib
import json
import os
import platform
import subprocess
import sys
import traceback


class _Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, s):
        for st in self.streams:
            st.write(s)

    def flush(self):
        for st in self.streams:
            st.flush()


def _git(repo, *args):
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


class Run:
    def __init__(self, path, meta):
        self.path, self.meta = path, meta


@contextlib.contextmanager
def run_folder(script, label):
    here = os.path.dirname(os.path.abspath(script))
    rev = _git(here, "rev-parse", "--short=12", "HEAD") or "norev"
    diff = _git(here, "diff", "HEAD")
    start = datetime.datetime.now(datetime.timezone.utc)
    run_id = f"{start:%Y%m%dT%H%M%SZ}-{label}-{rev}"
    path = os.path.join(here, "runs", run_id)
    os.makedirs(path, exist_ok=False)
    try:
        import numpy
        np_version = numpy.__version__
    except ImportError:
        np_version = None
    meta = {"run_id": run_id, "label": label, "started_utc": start.isoformat(), "revision": rev,
            "local_changes": bool(diff), "diff_sha256": hashlib.sha256(diff.encode()).hexdigest() if diff else None,
            "command": [os.path.basename(sys.argv[0])] + sys.argv[1:], "python": platform.python_version(), "numpy": np_version,
            "pts_env": {k: hashlib.sha256(v.encode()).hexdigest()[:16] for k, v in sorted(os.environ.items()) if k.startswith("PTS_")}}
    console = open(os.path.join(path, "console.txt"), "w", encoding="utf-8")
    old = sys.stdout
    sys.stdout = _Tee(old, console)
    run = Run(path, meta)
    try:
        yield run
        meta["outcome"] = "completed"
    except BaseException as e:
        meta["outcome"] = "crashed"
        meta["error"] = "".join(traceback.format_exception_only(type(e), e)).strip()
        console.write(traceback.format_exc())
        raise
    finally:
        sys.stdout = old
        console.close()
        meta["ended_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with open(os.path.join(path, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=1)
