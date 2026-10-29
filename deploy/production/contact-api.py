#!/usr/bin/env python3
"""Private, same-origin contact intake for mattsidnell.co.uk.

Stores validated enquiries in a durable SQLite database. No email credentials or
public admin routes. The site must never claim a notification was sent unless a
separate verified mail transport has accepted delivery.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import json
import os
import re
import secrets
import sqlite3
import sys
import threading
import time
from urllib.parse import urlsplit

DB = Path(os.environ.get("CONTACT_DB", "/data/enquiries.sqlite"))
ALLOWED_ORIGINS = {"https://mattsidnell.co.uk", "https://www.mattsidnell.co.uk"}
ALLOWED_TYPES = {
    "Contract opportunity", "Agency overflow", "Website project",
    "Custom software", "General enquiry"
}
EMAIL = re.compile(r"^[^\s@<>\x00-\x1f]{1,100}@[^\s@<>\x00-\x1f]{3,150}$")
IDENTITY = re.compile(r"^[A-Za-z0-9._:-]{8,128}$")
MAX_BODY = 16 * 1024
RETAIN_DAYS = 180


def connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(DB), timeout=10)
    db.execute("PRAGMA busy_timeout=10000")
    db.execute("PRAGMA journal_mode=WAL")
    db.execute(
        """CREATE TABLE IF NOT EXISTS enquiries (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            sender_name TEXT NOT NULL,
            sender_email TEXT NOT NULL,
            company TEXT NOT NULL,
            enquiry_type TEXT NOT NULL,
            message TEXT NOT NULL,
            email_hash TEXT NOT NULL,
            notification_status TEXT NOT NULL DEFAULT 'not_configured'
        )"""
    )
    db.execute("CREATE INDEX IF NOT EXISTS enquiry_time ON enquiries(created_at)")
    db.execute("CREATE INDEX IF NOT EXISTS enquiry_email_hash ON enquiries(email_hash,created_at)")
    db.commit()
    return db


def clean(value, limit, required=False):
    if not isinstance(value, str):
        raise ValueError("Invalid field")
    value = value.strip()
    if len(value) > limit or (required and not value):
        raise ValueError("Invalid field length")
    if any(ord(c) < 32 and c not in "\n\r\t" for c in value):
        raise ValueError("Invalid characters")
    return value


class Handler(BaseHTTPRequestHandler):
    server_version = "PortfolioContact/1.0"
    sys_version = ""

    def log_message(self, format, *args):
        # No personal form content or email/IP is ever logged.
        sys.stderr.write("contact-api %s\n" % (format % args))

    def respond(self, status, payload):
        body = json.dumps(payload, separators=(",", ":")).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Robots-Tag", "noindex")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if urlsplit(self.path).path == "/healthz":
            self.respond(200, {"ok": True})
        else:
            self.respond(404, {"error": "not_found"})

    def do_POST(self):
        if urlsplit(self.path).path != "/api/contact":
            return self.respond(404, {"error": "not_found"})
        if self.headers.get("Origin") not in ALLOWED_ORIGINS:
            return self.respond(403, {"error": "origin_not_allowed"})
        if self.headers.get("Content-Type", "").split(";")[0].strip().lower() != "application/json":
            return self.respond(415, {"error": "unsupported_media_type"})
        if self.headers.get("Sec-Fetch-Site") not in (None, "same-origin"):
            return self.respond(403, {"error": "cross_site"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_BODY:
            return self.respond(413, {"error": "invalid_size"})
        key = self.headers.get("Idempotency-Key", "")
        if not IDENTITY.fullmatch(key):
            return self.respond(400, {"error": "missing_request_identity"})
        try:
            raw = json.loads(self.rfile.read(length))
            if not isinstance(raw, dict):
                raise ValueError("Not an object")
            if set(raw) - {
                "name", "email", "company", "enquiry_type", "message", "company_url"
            }:
                raise ValueError("Unknown fields")
            name = clean(raw.get("name", ""), 120, True)
            email = clean(raw.get("email", ""), 254, True).lower()
            company = clean(raw.get("company", ""), 160)
            kind = clean(raw.get("enquiry_type", ""), 60, True)
            message = clean(raw.get("message", ""), 5000, True)
            trap = clean(raw.get("company_url", ""), 200)
            if not EMAIL.fullmatch(email) or kind not in ALLOWED_TYPES or len(message) < 10:
                raise ValueError("Invalid content")
        except (UnicodeDecodeError, ValueError, TypeError, json.JSONDecodeError):
            return self.respond(422, {"error": "invalid_submission"})
        # Do not disclose the honeypot to automated senders.
        if trap:
            return self.respond(202, {"accepted": True})
        now = datetime.now(timezone.utc)
        hashed = sha256((os.environ.get("CONTACT_RATE_SALT", "portfolio") + ":" + email).encode()).hexdigest()
        try:
            with connect() as db:
                previous = db.execute("SELECT 1 FROM enquiries WHERE id = ?", (key,)).fetchone()
                if previous:
                    return self.respond(202, {"accepted": True})
                since = (now - timedelta(hours=2)).isoformat()
                per_sender = db.execute(
                    "SELECT COUNT(*) FROM enquiries WHERE email_hash = ? AND created_at >= ?",
                    (hashed, since)
                ).fetchone()[0]
                total = db.execute(
                    "SELECT COUNT(*) FROM enquiries WHERE created_at >= ?", (since,)
                ).fetchone()[0]
                if per_sender >= 4 or total >= 70:
                    return self.respond(429, {"error": "too_many_requests"})
                db.execute(
                    """INSERT INTO enquiries
                    (id,created_at,sender_name,sender_email,company,enquiry_type,message,email_hash)
                    VALUES(?,?,?,?,?,?,?,?)""",
                    (key, now.isoformat(), name, email, company, kind, message, hashed)
                )
                db.execute(
                    "DELETE FROM enquiries WHERE created_at < ?",
                    ((now - timedelta(days=RETAIN_DAYS)).isoformat(),)
                )
                db.commit()
            return self.respond(202, {"accepted": True})
        except (OSError, sqlite3.Error) as error:
            self.log_message("store failed: %s", type(error).__name__)
            return self.respond(503, {"error": "temporarily_unavailable"})


def retention_worker():
    # Delete expired enquiries even if no further visitor submits a form.
    while True:
        try:
            cutoff = (datetime.now(timezone.utc) - timedelta(days=RETAIN_DAYS)).isoformat()
            with connect() as db:
                db.execute("DELETE FROM enquiries WHERE created_at < ?", (cutoff,))
                db.commit()
        except (OSError, sqlite3.Error) as error:
            sys.stderr.write("contact-api retention failed: %s\n" % type(error).__name__)
        time.sleep(6 * 60 * 60)


def admin_list(show_id=None):
    if not DB.is_file():
        print("No enquiries have been received.")
        return
    with connect() as db:
        if show_id:
            rows = db.execute(
                "SELECT id,created_at,sender_name,sender_email,company,enquiry_type,message,notification_status FROM enquiries WHERE id = ?",
                (show_id,)
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT id,created_at,sender_name,sender_email,company,enquiry_type,notification_status FROM enquiries ORDER BY created_at DESC LIMIT 30"
            ).fetchall()
        for row in rows:
            print(json.dumps(row, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", nargs="?", choices=["serve", "list", "show"], default="serve")
    parser.add_argument("identity", nargs="?")
    args = parser.parse_args()
    if args.mode in ("list", "show"):
        if args.mode == "show" and not args.identity:
            parser.error("show requires an enquiry id")
        return admin_list(args.identity if args.mode == "show" else None)
    connect().close()
    threading.Thread(target=retention_worker, daemon=True).start()
    server = ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", "8080"))), Handler)
    print("portfolio contact intake listening", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
