#!/usr/bin/env python3
"""One-step, guarded production activation. Run manually by an authorised administrator.

Never invoked automatically, and never prints credentials or private enquiry data.
Requires sudo/root, an existing provisioned bcrypt hash staged on the server,
a running production frontend, and a verified immutable PHP image.
"""
from __future__ import annotations
import argparse
import hashlib
import os
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys
import time
from urllib.request import urlopen

BASE = Path("/home/auto-ops/sites/mattsidnell-production")
STAGED = BASE / "php-admin-20261103"
DATA = BASE / "contact-data"
FRONT_CONFIG = BASE / "config/nginx.conf"
CANDIDATE = STAGED / "nginx.admin-candidate.conf"
HASH_STAGED = STAGED / "admin-password.hash.staging"
HASH_ACTIVE = DATA / "portfolio-admin-password.hash"
BACKUP = BASE / "config/nginx.before-admin-20261103.conf"
CONTAINER = "mattsidnell-php-admin"
IMAGE = "mattsidnell-portfolio-php:20261103-admin1"
NETWORK = "pw-service-f1c1a569-de48-4d53-895e-b708f47635cd"
NGINX_IMAGE = "nginx@sha256:a8b39bd9cf0f83869a2162827a0caf6137ddf759d50a171451b335cecc87d236"


def run(*args: str, quiet: bool = False) -> str:
    result = subprocess.run(args, text=True, check=True, capture_output=True)
    if not quiet and result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    return result.stdout.strip()


def verify_configs() -> None:
    current = FRONT_CONFIG.read_text()
    candidate = CANDIDATE.read_text()
    start = candidate.index("  # Private read-only dashboard")
    end = candidate.index("  location = /healthz {", start)
    if candidate[:start] + candidate[end:] != current:
        raise RuntimeError(
            "Frontend configuration changed since review. Refusing to override unrelated routes."
        )
    if "fastcgi_pass mattsidnell-php-prod:9000;" not in current:
        raise RuntimeError("Existing production contact API route was not found.")
    if "fastcgi_pass mattsidnell-php-admin:9000;" not in candidate:
        raise RuntimeError("Candidate does not reference the private dashboard service.")
    if "fastcgi_param HTTP_COOKIE $http_cookie;" not in candidate:
        raise RuntimeError("Candidate does not forward secure session cookies.")


def preflight() -> None:
    for item in (FRONT_CONFIG, CANDIDATE, HASH_STAGED):
        if not item.is_file():
            raise RuntimeError("Missing release prerequisite: " + str(item))
    data = HASH_STAGED.read_text().strip()
    if not re.fullmatch(r"\$2y\$12\$[./A-Za-z0-9]{53}", data):
        raise RuntimeError("Invalid password hash staging file.")
    if os.geteuid() == 0 and HASH_ACTIVE.exists():
        raise RuntimeError("Admin access is already provisioned; manual review is required.")
    if BACKUP.exists():
        raise RuntimeError("An existing admin rollback file is present; refusing to overwrite it.")
    verify_configs()
    # In an unprivileged dry run the private data directory is intentionally
    # inaccessible. The real activation always runs as root and verifies it.
    if os.geteuid() == 0:
        with sqlite3.connect("file:" + str(DATA / "enquiries.sqlite") + "?mode=ro", uri=True) as db:
            if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise RuntimeError("Private enquiry database integrity check failed.")
        print("Preflight OK: configuration, credentials and private database verified.")
    else:
        print("Preflight OK: config and staged credential verified; private database check reserved for activation.")


def activate() -> None:
    if os.geteuid() != 0:
        raise PermissionError("Activation requires an authorised sudo session.")
    preflight()
    run("docker", "image", "inspect", IMAGE, quiet=True)
    exists = subprocess.run(
        ["docker", "container", "inspect", CONTAINER],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    ).returncode == 0
    if exists:
        raise RuntimeError("Admin service container already exists; manual review required.")
    # Write only the bcrypt hash, never the plaintext password.
    fd = os.open(str(HASH_ACTIVE), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(HASH_STAGED.read_text().strip() + "\n")
    os.chown(HASH_ACTIVE, 10001, 10001)
    os.chmod(HASH_ACTIVE, 0o600)
    run(
        "docker", "run", "-d", "--name", CONTAINER,
        "--network", NETWORK, "--restart", "unless-stopped",
        "--read-only", "--user", "10001:10001",
        "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
        "--memory", "128m", "--pids-limit", "64",
        "--tmpfs", "/tmp:rw,nosuid,noexec,size=8m",
        "--mount", "type=bind,src=" + str(DATA) + ",dst=/data",
        IMAGE, quiet=True
    )
    time.sleep(2)
    status = run("docker", "inspect", "--format", "{{.State.Status}}", CONTAINER, quiet=True)
    if status != "running":
        raise RuntimeError("Admin PHP-FPM service did not start successfully.")
    run(
        "docker", "run", "--rm", "--network", NETWORK,
        "--mount", "type=bind,src=" + str(CANDIDATE) +
        ",dst=/etc/nginx/conf.d/default.conf,readonly",
        "--entrypoint", "nginx", NGINX_IMAGE, "-t", quiet=True
    )
    with BACKUP.open("x") as f:
        f.write(FRONT_CONFIG.read_text())
    os.chmod(BACKUP, 0o600)
    try:
        # Overwrite the original bind-mounted inode so the live Nginx
        # container sees the new configuration without recreation.
        shutil.copyfile(CANDIDATE, FRONT_CONFIG)
        run("docker", "exec", "mattsidnell-portfolio-prod", "nginx", "-t", quiet=True)
        run("docker", "exec", "mattsidnell-portfolio-prod", "nginx", "-s", "reload", quiet=True)
        time.sleep(1)
        with urlopen("https://mattsidnell.co.uk/admin", timeout=12) as r:
            html = r.read(10000).decode("utf-8", "replace")
            if r.status != 200 or "Portfolio admin" not in html or "Sign in" not in html:
                raise RuntimeError("Live login page did not pass the HTTPS acceptance check.")
        with urlopen("https://mattsidnell.co.uk/", timeout=12) as r:
            if r.status != 200:
                raise RuntimeError("Portfolio homepage unavailable after activation.")
        print("Admin dashboard activated at https://mattsidnell.co.uk/admin")
        print("Login password is saved privately on your Mac, not in this terminal output.")
    except Exception:
        shutil.copyfile(BACKUP, FRONT_CONFIG)
        run("docker", "exec", "mattsidnell-portfolio-prod", "nginx", "-t", quiet=True)
        run("docker", "exec", "mattsidnell-portfolio-prod", "nginx", "-s", "reload", quiet=True)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                        help="Check release prerequisites without modifying production")
    args = parser.parse_args()
    try:
        if args.check:
            preflight()
        else:
            activate()
    except Exception as exc:
        print(f"Activation not completed: {exc}", file=sys.stderr)
        raise SystemExit(1)
