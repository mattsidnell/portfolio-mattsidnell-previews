#!/usr/bin/env python3
"""Exercise the private PHP dashboard, authentication and session protections."""
import http.cookiejar
import os
import pathlib
import re
import sqlite3
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
APP = ROOT / "deploy/production/php"
PORT = 18938
BASE = f"http://127.0.0.1:{PORT}"
ORIGIN = "https://mattsidnell.co.uk"

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def exercise():
    with tempfile.TemporaryDirectory() as d:
        db = pathlib.Path(d) / "enquiries.sqlite"
        secret = pathlib.Path(d) / "dashboard.hash"
        env = {**os.environ, "CONTACT_DB": str(db),
               "PORTFOLIO_ADMIN_PASSWORD_FILE": str(secret)}
        cookiejar = http.cookiejar.CookieJar()
        browser = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(cookiejar), NoRedirect())
        def fetch(path, data=None, origin=True):
            raw = None if data is None else urllib.parse.urlencode(data).encode()
            headers = {"Origin": ORIGIN} if raw is not None and origin else {}
            cookies = [c.name + "=" + c.value for c in cookiejar if c.name == "__Host-PortfolioAdmin"]
            if cookies:
                # Browser Secure cookies require HTTPS; force locally over the test-only HTTP loopback.
                headers["Cookie"] = "; ".join(cookies)
            request = urllib.request.Request(BASE + path, data=raw, headers=headers)
            try:
                with browser.open(request, timeout=4) as res:
                    return res.status, res.read().decode(), res.headers
            except urllib.error.HTTPError as exc:
                return exc.code, exc.read().decode(), exc.headers

        process = subprocess.Popen(
            ["php", "-S", f"127.0.0.1:{PORT}", "-t", str(APP), str(APP / "index.php")],
            env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            for _ in range(40):
                try:
                    assert fetch("/admin")[0] == 503
                    break
                except Exception:
                    time.sleep(.1)
            else:
                raise AssertionError("PHP development server not available")
            created = subprocess.run(
                ["php", str(APP / "admin.php"), "provision"],
                env=env, capture_output=True, text=True, check=True)
            password = created.stdout.split("shown only once):\n")[1].splitlines()[0]
            assert len(password) == 48 and secret.is_file()
            assert subprocess.run(["php", str(APP / "admin.php"), "provision"],
                                  env=env, capture_output=True).returncode != 0

            code, html, head = fetch("/admin")
            assert code == 200 and "Sign in" in html and "Recent enquiries" not in html
            assert "no-store" in head.get("Cache-Control", "")
            assert "noindex" in head.get("X-Robots-Tag", "")
            assert "frame-ancestors 'none'" in head.get("Content-Security-Policy", "")
            token = re.search(r'name="csrf" value="([a-f0-9]+)"', html).group(1)
            assert code == 200 and token
            assert fetch("/admin/login", {"csrf": token, "password": password}, origin=False)[0] == 403
            code, _, _ = fetch("/admin/login", {"csrf": token, "password": "incorrect"})
            assert code == 401
            code, html, _ = fetch("/admin")
            assert code == 200 and "Sign in" in html
            token = re.search(r'name="csrf" value="([a-f0-9]+)"', html).group(1)
            code, _, headers = fetch("/admin/login", {"csrf":token, "password":password})
            assert code == 303 and headers.get("Location") == "/admin"
            assert any(c.name == '__Host-PortfolioAdmin' for c in cookiejar)
            # PHP's session cookie is marked secure, therefore this HTTP-only local
            # browser won't re-send it. Explicitly forward it for the test alone.
            cookie = next(c for c in cookiejar if c.name == '__Host-PortfolioAdmin')
            cookie_header = cookie.name + "=" + cookie.value
            def authenticated_get(path):
                q = urllib.request.Request(BASE+path, headers={"Cookie": cookie_header})
                with urllib.request.urlopen(q, timeout=4) as response:
                    return response.status, response.read().decode(), response.headers
            code, page, headers = authenticated_get("/admin?days=7")
            assert code == 200 and "Website activity" in page and "Popular portfolio projects" in page
            assert "Recent enquiries" in page
            with sqlite3.connect(db) as c:
                c.execute("""INSERT INTO enquiries(id,created_at,sender_name,sender_email,company,
                    enquiry_type,message,email_hash) VALUES (?,?,?,?,?,?,?,?)""",
                    ("qa-admin-1", "2026-11-03T14:00:00+00:00", "<script>alert(1)</script>",
                     "qa@example.org", "", "General enquiry", "<b>testing</b>", "safe"))
                c.commit()
            code, page, _ = authenticated_get("/admin?days=30")
            assert "qa@example.org" in page
            assert "&lt;script&gt;alert(1)&lt;/script&gt;" in page
            assert "<script>alert(1)</script>" not in page
            assert "&lt;b&gt;testing&lt;/b&gt;" in page
            assert fetch("/admin/other")[0] == 404
            assert fetch("/admin/login", {"csrf": token, "password":"bad"})[0] in (401,403)
            print("PASS: private admin provision, no-default access, CSRF, login, session, CSP, read-only dashboard, escaped client content")
        finally:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()

if __name__ == "__main__":
    exercise()
