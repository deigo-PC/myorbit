#!/usr/bin/env python3
"""MyOrbit reference server - one file, standard library only, no pip install.

Serves the client, the manifest, the runtime config, and the task API over a plain
JSON store. It exists so this project can be cloned and run in one command, whether
or not you use the same dashboard the original author mounts it in.

    python3 server/server.py                      # port 8787, ./store.json
    python3 server/server.py --port 9000 --store ~/orbit.json --config config.json

State is a single JSON file. There is no database and no migration step.
"""
import argparse
import json
import re
import threading
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
LOCK = threading.Lock()

TASK_FIELDS = ("title", "domain", "area", "group", "client", "state", "kind",
               "next_action", "due", "estimate", "blocker", "waits_on", "notes",
               "pinned", "priority", "tags", "children", "source", "section")
EDITABLE = set(TASK_FIELDS) | {"moved"}


def read_json(path, default):
    p = Path(path)
    if not p.is_file():
        return default
    try:
        return json.loads(p.read_text())
    except Exception:
        return default


def write_json(path, obj):
    p = Path(path)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False))
    tmp.replace(p)


class Orbit:
    """The whole backend: one JSON store, one config file, four verbs."""

    def __init__(self, store_path, config_path):
        self.store_path = Path(store_path)
        self.config_path = Path(config_path)

    def config(self):
        return read_json(self.config_path, {})

    def tasks(self):
        data = read_json(self.store_path, {"rows": []})
        return data.get("rows", []) if isinstance(data, dict) else data

    def save(self, rows):
        write_json(self.store_path, {"rows": rows})

    def next_id(self, rows):
        n = max([int(r["id"][1:]) for r in rows
                 if re.fullmatch(r"t\d+", str(r.get("id", "")))] or [0])
        return f"t{n + 1:03d}"

    def create(self, body):
        title = (body.get("title") or "").strip()
        if not title:
            raise ValueError("title is required")
        with LOCK:
            rows = self.tasks()
            row = {k: body.get(k) for k in TASK_FIELDS}
            row["id"] = self.next_id(rows)
            row["title"] = title
            row["state"] = body.get("state") or "open"
            row["kind"] = body.get("kind") or "task"
            row["source"] = body.get("source") or "client"
            row["created"] = row["moved"] = date.today().isoformat()
            rows.append(row)
            self.save(rows)
        return row

    def patch(self, task_id, body):
        fields = {k: v for k, v in body.items() if k in EDITABLE}
        if not fields:
            raise ValueError("nothing to update")
        with LOCK:
            rows = self.tasks()
            for r in rows:
                if r.get("id") == task_id:
                    r.update(fields)
                    if body.get("touch", True) and "moved" not in fields:
                        r["moved"] = date.today().isoformat()
                    self.save(rows)
                    return r
        raise KeyError(task_id)

    def bulk(self, body):
        ids = set(body.get("ids") or [])
        if not ids:
            raise ValueError("ids is required")
        with LOCK:
            rows = self.tasks()
            if body.get("delete"):
                kept = [r for r in rows if r.get("id") not in ids]
                self.save(kept)
                return {"deleted": len(rows) - len(kept)}
            fields = {k: v for k, v in (body.get("patch") or {}).items() if k in EDITABLE}
            if not fields:
                raise ValueError("patch is required")
            hit = 0
            for r in rows:
                if r.get("id") in ids:
                    r.update(fields)
                    r["moved"] = date.today().isoformat()
                    hit += 1
            self.save(rows)
            return {"updated": hit}

    def delete(self, task_id):
        with LOCK:
            rows = self.tasks()
            kept = [r for r in rows if r.get("id") != task_id]
            if len(kept) == len(rows):
                raise KeyError(task_id)
            self.save(kept)
            return {"removed": 1}


class Handler(BaseHTTPRequestHandler):
    orbit = None
    server_version = "MyOrbit/0.1"

    def log_message(self, fmt, *a):
        print("  " + (fmt % a))

    def _send(self, code, body, ctype="application/json"):
        raw = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(raw)

    def _file(self, path, ctype):
        p = Path(path)
        if not p.is_file():
            return self._send(404, {"error": "not found"})
        self._send(200, p.read_bytes(), ctype)

    def _body(self):
        try:
            n = int(self.headers.get("Content-Length") or 0)
            return json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return {}

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        path = urlparse(self.path).path
        o = self.orbit
        if path in ("/", "/m.html", "/index.html"):
            return self._file(ROOT / "client" / "m.html", "text/html; charset=utf-8")
        if path == "/app.webmanifest":
            cfg = o.config()
            man = {"name": cfg.get("name", "MyOrbit"), "short_name": cfg.get("short_name", "MyOrbit"),
                   "start_url": "m.html", "scope": "./", "display": "standalone",
                   "background_color": "#07090A", "theme_color": "#07090A",
                   "icons": cfg.get("icons", [])}
            return self._send(200, man, "application/manifest+json")
        if path.startswith("/assets/"):
            name = Path(path).name
            ctype = "image/svg+xml" if name.endswith(".svg") else "image/png"
            return self._file(ROOT / "assets" / name, ctype)
        if path == "/api/config":
            return self._send(200, o.config())
        if path == "/api/tasks":
            rows = o.tasks()
            return self._send(200, {"rows": rows, "count": len(rows)})
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        path = urlparse(self.path).path
        body = self._body()
        try:
            if path == "/api/tasks":
                return self._send(200, {"ok": True, "task": self.orbit.create(body)})
            if path == "/api/tasks/bulk":
                return self._send(200, {"ok": True, **self.orbit.bulk(body)})
        except ValueError as e:
            return self._send(400, {"error": str(e)})
        return self._send(404, {"error": "not found"})

    def do_PATCH(self):
        path = urlparse(self.path).path
        m = re.fullmatch(r"/api/tasks/([A-Za-z0-9_-]+)", path)
        if not m:
            return self._send(404, {"error": "not found"})
        try:
            return self._send(200, {"ok": True, "task": self.orbit.patch(m.group(1), self._body())})
        except ValueError as e:
            return self._send(400, {"error": str(e)})
        except KeyError:
            return self._send(404, {"error": "no such task"})

    def do_DELETE(self):
        path = urlparse(self.path).path
        m = re.fullmatch(r"/api/tasks/([A-Za-z0-9_-]+)", path)
        if not m:
            return self._send(404, {"error": "not found"})
        try:
            return self._send(200, {"ok": True, **self.orbit.delete(m.group(1))})
        except KeyError:
            return self._send(404, {"error": "no such task"})


def main():
    ap = argparse.ArgumentParser(description="MyOrbit reference server")
    ap.add_argument("--port", type=int, default=8787)
    ap.add_argument("--host", default="127.0.0.1",
                    help="use 0.0.0.0 to reach it from other devices on your network")
    ap.add_argument("--store", default=str(HERE / "store.json"))
    ap.add_argument("--config", default=str(HERE / "config.json"))
    a = ap.parse_args()

    if not Path(a.store).exists():
        example = HERE / "store.example.json"
        if example.is_file():
            Path(a.store).write_text(example.read_text())
            print(f"seeded {a.store} from store.example.json")
    if not Path(a.config).exists():
        example = HERE / "config.example.json"
        if example.is_file():
            Path(a.config).write_text(example.read_text())
            print(f"seeded {a.config} from config.example.json")

    Handler.orbit = Orbit(a.store, a.config)
    srv = ThreadingHTTPServer((a.host, a.port), Handler)
    print(f"MyOrbit on http://{a.host}:{a.port}/   store={a.store}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")


if __name__ == "__main__":
    main()
