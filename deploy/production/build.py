#!/usr/bin/env python3
"""Build the approved bold electric-cyan portfolio as a clean production web root.

This does not deploy. It transforms the reviewed static preview into the exact
root-site artifact served by the dedicated production Nginx container.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
OUT = ROOT / "dist-production"

def main() -> None:
    reviewed = DOCS / "concept03" / "index.html"
    source = reviewed.read_text()
    if 'noindex,nofollow,noarchive' not in source or 'matt-seated.webp' not in source:
        raise ValueError("Selected preview is missing expected source or metadata")
    OUT.mkdir(exist_ok=True)

    html = source.replace(
        'content="noindex,nofollow,noarchive"',
        'content="index,follow,max-image-preview:large"',
    ).replace(
        "Matt Sidnell | Concept 03 — Electric Cyan",
        "Matt Sidnell | Freelance Web Developer & Software Engineer",
    ).replace(
        "../cyan/assets/projects/",
        "/assets/projects/",
    ).replace(
        "../assets/portrait/",
        "/assets/portrait/",
    )
    html = html.replace(
        "<head>",
        '<head><link rel="canonical" href="https://mattsidnell.co.uk/">',
        1,
    ).replace(
        "</head>",
        '<meta property="og:title" content="Matt Sidnell | Freelance Web Developer">'
        '<meta property="og:type" content="website">'
        '<meta property="og:url" content="https://mattsidnell.co.uk/">'
        '<meta property="og:description" content="Freelance web development, '
        'custom WordPress, Laravel and complex software systems."></head>',
        1,
    )
    (OUT / "index.html").write_text(html)

    assets = list((DOCS / "cyan" / "assets" / "projects").glob("*"))
    if len(assets) != 9:
        raise ValueError("Expected nine verified portfolio project images")
    for asset in assets:
        dest = OUT / "assets" / "projects" / asset.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(asset, dest)

    portrait = DOCS / "assets" / "portrait" / "matt-seated.webp"
    if not portrait.is_file():
        raise FileNotFoundError(portrait)
    dest = OUT / "assets" / "portrait" / portrait.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(portrait, dest)

    (OUT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nSitemap: https://mattsidnell.co.uk/sitemap.xml\n"
    )
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        '<url><loc>https://mattsidnell.co.uk/</loc></url></urlset>'
    )
    (OUT / "404.html").write_text(
        '<!doctype html><html lang="en"><head><meta name="viewport" '
        'content="width=device-width,initial-scale=1"><title>Page not found | '
        'Matt Sidnell</title></head><body style="font:20px system-ui;'
        'padding:10vw;background:#43d6e9;color:#0c2535"><h1>Page not found.'
        '</h1><p><a href="/">Back to Matt’s portfolio</a></p></body></html>'
    )
    print(json.dumps({
        "files": len([p for p in OUT.rglob("*") if p.is_file()]),
        "homepage_sha256": hashlib.sha256(html.encode()).hexdigest(),
        "portrait_sha256": hashlib.sha256(dest.read_bytes()).hexdigest(),
        "destination": str(OUT),
    }, indent=2))


if __name__ == "__main__":
    main()
