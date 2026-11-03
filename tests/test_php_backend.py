#!/usr/bin/env python3
"""Black-box compatibility tests against the PHP replacement API."""
from __future__ import annotations
import json, os, pathlib, sqlite3, subprocess, tempfile, time, urllib.error, urllib.request, uuid

ROOT = pathlib.Path(__file__).resolve().parents[1]
PHP = ROOT / "deploy/production/php/index.php"
PORT = 18931
BASE = f"http://127.0.0.1:{PORT}"
ORIGIN = "https://mattsidnell.co.uk"

def request(path, data=None, headers=None, method=None):
    raw = None if data is None else json.dumps(data).encode()
    h = {"Origin": ORIGIN, "Content-Type": "application/json", "Sec-Fetch-Site": "same-origin"}
    h.update(headers or {})
    req = urllib.request.Request(BASE + path, data=raw, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=4) as res:
            return res.status, res.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()

def run():
    with tempfile.TemporaryDirectory() as d:
        db = pathlib.Path(d) / "existing-enquiries.sqlite"
        with sqlite3.connect(db) as c:
            c.execute("""CREATE TABLE enquiries(
                id TEXT PRIMARY KEY, created_at TEXT NOT NULL,
                sender_name TEXT NOT NULL, sender_email TEXT NOT NULL,
                company TEXT NOT NULL, enquiry_type TEXT NOT NULL,
                message TEXT NOT NULL, email_hash TEXT NOT NULL,
                notification_status TEXT NOT NULL DEFAULT 'not_configured')""")
            c.execute("""INSERT INTO enquiries
                (id,created_at,sender_name,sender_email,company,enquiry_type,message,email_hash)
                VALUES(?,?,?,?,?,?,?,?)""",
                ("old-legacy-record", "2026-11-01T10:00:00+00:00",
                 "Existing User", "previous@example.org", "Example", "General enquiry",
                 "An existing message", "hashed-placeholder"))
        env = {**os.environ, "CONTACT_DB": str(db), "CONTACT_RATE_SALT": "local-test-salt"}
        proc = subprocess.Popen(["php", "-S", f"127.0.0.1:{PORT}", "-t", str(PHP.parent),
                                 str(PHP)], cwd=ROOT, env=env, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        try:
            for i in range(40):
                try:
                    status, _ = request("/healthz", method="GET")
                    if status == 200: break
                except Exception:
                    time.sleep(.08)
            else: raise AssertionError("PHP HTTP service did not start")
            assert request("/api/analytics", {"kind":"pageview","target":"home","source":"direct"})[0] == 204
            assert request("/api/analytics", {"kind":"pageview","target":"home","source":"direct"})[0] == 204
            assert request("/api/analytics", {"kind":"pageview","target":"unknown","source":"direct"})[0] == 422
            assert request("/api/analytics", {"kind":"pageview","target":"home","source":"direct"},
                           {"Origin":"https://attacker.example"})[0] == 403
            sample = {"name":"Sample Tester","email":"test@example.org","company":"Example",
                      "enquiry_type":"Agency overflow",
                      "message":"Please help with a custom project development task.",
                      "company_url":""}
            key = str(uuid.uuid4())
            headers = {"Idempotency-Key":key}
            assert request("/api/contact", sample, headers)[0] == 202
            assert request("/api/contact", sample, headers)[0] == 202
            assert request("/api/contact", {**sample,"company_url":"https://spam.example"},
                           {"Idempotency-Key":str(uuid.uuid4())})[0] == 202
            assert request("/api/contact", {**sample,"enquiry_type":"Unknown"},
                           {"Idempotency-Key":str(uuid.uuid4())})[0] == 422
            assert request("/api/contact", sample,
                           {"Idempotency-Key":str(uuid.uuid4()),"Origin":"https://evil.example"})[0] == 403
            assert request("/api/contact", sample)[0] == 400
            with sqlite3.connect(db) as c:
                assert c.execute("SELECT COUNT(*) FROM enquiries").fetchone()[0] == 2
                assert c.execute("SELECT COUNT(*) FROM enquiries WHERE id='old-legacy-record'").fetchone()[0] == 1
                assert c.execute("SELECT count FROM analytics_daily WHERE target='home'").fetchone()[0] == 2
            result = subprocess.run(["php", str(PHP), "stats", "1"], env=env, capture_output=True, text=True, check=True)
            assert json.loads(result.stdout)["counts"][0]["count"] == 2
            print("PASS: same-site API, existing SQLite, idempotency, anti-spam, analytics, CLI statistics, origin checks")
        finally:
            proc.terminate()
            try:proc.wait(timeout=3)
            except subprocess.TimeoutExpired:proc.kill()
if __name__ == '__main__': run()
