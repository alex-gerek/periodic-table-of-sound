"""Local server for the beat-tapping page (issue #15, journal step 2026-11-13-tapping-001).

  PTS_TAPPING_DIR=<folder with audio/track_NN.wav> python tap_server.py [port]

Serves tap.html, the blinded excerpts and the saved taps. Every finished pass is stored at once
in <PTS_TAPPING_DIR>/taps.json (raw tap times, never overwritten: each save also writes a
timestamped copy under history/). The blinding key stays in key.json and is never served.
"""
import datetime
import json
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("PTS_TAPPING_DIR")
if not DATA or not os.path.isdir(os.path.join(DATA, "audio")):
    raise SystemExit("set PTS_TAPPING_DIR to the folder that holds audio/track_NN.wav")
TAPS = os.path.join(DATA, "taps.json")


def load():
    return json.load(open(TAPS, encoding="utf-8")) if os.path.exists(TAPS) else {}


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self.path = self.path.split("?", 1)[0]          # ignore query strings (cache busting)
        if self.path in ("/", "/index.html"):
            body = open(os.path.join(HERE, "tap.html"), "rb").read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/tracks":
            ids = sorted(f[:-4] for f in os.listdir(os.path.join(DATA, "audio")) if f.startswith("track_") and f.endswith(".wav"))
            self._json({"tracks": ids, "taps": load()})
        elif self.path.startswith("/audio/track_") and self.path.endswith(".wav") and "/" not in self.path[7:] and ".." not in self.path:
            p = os.path.join(DATA, "audio", self.path[7:])
            if not os.path.exists(p):
                return self._json({"error": "not found"}, 404)
            body = open(p, "rb").read()
            self.send_response(200)
            self.send_header("Content-Type", "audio/wav")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self):
        if self.path.split("?", 1)[0] != "/save":
            return self._json({"error": "not found"}, 404)
        rec = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
        tid, key = str(rec.get("id")), str(rec.get("pass"))
        if not tid.startswith("track_") or key not in ("1", "2", "3", "4"):
            return self._json({"error": "bad record"}, 400)
        taps = load()
        taps.setdefault(tid, {})[key] = {"taps_s": rec.get("taps_s", []), "no_steady_beat": bool(rec.get("no_steady_beat")),
                                         "saved_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()}
        json.dump(taps, open(TAPS, "w", encoding="utf-8"), indent=1)
        os.makedirs(os.path.join(DATA, "history"), exist_ok=True)
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        json.dump(taps, open(os.path.join(DATA, "history", f"taps_{stamp}.json"), "w", encoding="utf-8"), indent=1)
        self._json({"ok": True})


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8770
    print(f"tapping page on http://127.0.0.1:{port}/", flush=True)
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()
