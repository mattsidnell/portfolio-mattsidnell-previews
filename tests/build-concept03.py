#!/usr/bin/env python3
"""Render three functional palette variants of Concept 03 from the canonical cyan portfolio.
No fake portraits, project screenshots, or claimed outcomes are introduced."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
base = (DOCS / "cyan" / "index.html").read_text()
switcher = """<div class="theme-switcher" aria-label="Colour concept switcher"><div class="wrap theme-switcher-inner"><span>CONCEPT 03 <span class="switcher-separator">/</span> COLOUR STUDIES</span><nav aria-label="Choose colour variation"><a href="../concept03-cyan/">01 / Cyan</a><a href="../concept03-yellow/">02 / Yellow accent</a><a href="../concept03-dark/">03 / Dark navy</a></nav><a class="switcher-all" href="../concept03/">Compare all ↗</a></div></div>"""
variants = {
  "cyan": {
     "folder": "concept03-cyan",
     "title": "01 / Cyan & Navy",
     "tag": "Clean & confident",
     "description": "A white, navy and cyan direction with just a hint of yellow. The most universally professional choice.",
     "css": r"""
:root{--cyan:#08b6d3;--cyan2:#079bb8;--soft:#e8faff}
.hero{background:linear-gradient(125deg,#fff 0%,#fff 45%,#edfaff 100%)}
.hero h1{position:relative}
.hero h1:after{content:"";display:block;background:#f5c53b;width:38px;height:5px;border-radius:9px;position:absolute;bottom:-13px;left:0}
.portrait-card{transform:rotate(-2deg);border-color:#c6ecf3}
.code-card{box-shadow:13px 20px 50px #005c7826}
.eyebrow .cyan-dot{background:#e7bf26}
.project:hover{border-color:#70cbe0}
.work-filter button[aria-pressed=true]{background:#102938;border-color:#102938}
"""
 },
 "yellow": {
     "folder": "concept03-yellow",
     "title": "02 / Cyan & Electric Yellow",
     "tag": "Creative & memorable",
     "description": "The same serious developer portfolio with more warmth, creative energy and distinctive yellow details.",
     "css": r"""
:root{--cyan:#00b7d5;--cyan2:#008fac;--soft:#fff7c5;--line:#e5e3cf}
body{background:#fffdf4}
.site-header{background:#fffdf3;border-bottom-color:#ece5cf}
.hero{background:linear-gradient(115deg,#fffdf3 0%,#fffdf6 51%,#e7faff 100%)}
.hero-orb{background:#ffe66f;opacity:.36}
.hero h1 em{position:relative;z-index:1}
.hero h1 em:after{content:"";position:absolute;background:#f9d64c;height:.115em;left:1%;right:0;bottom:0;z-index:-1;transform:rotate(-1.2deg);border-radius:5px}
.eyebrow .cyan-dot,.cyan-dot{background:#f3c926}
.hero-actions .button-outline{border-color:#eebd1e;background:#fffbea}
.hero-actions .button-outline:hover{background:#ffef9e}
.portrait-card{border-color:#f2cc33;box-shadow:13px 15px 0 #f7dd6755,0 22px 46px #213c5120;transform:rotate(1.5deg)}
.portrait-head{background:#fff0aa}
.cross{color:#f4be1a}
.visual-label{border-color:#efd961}
.capability-strip{background:#fff9e9;border-top-color:#f3e9d1;border-bottom-color:#e7dcc0}
.strip-content .strip-intro b{color:#e2ab00}
.work-section{background:#fffdf8}
.project{border-color:#e5dfcb}
.project:hover{border-color:#e8bc28;box-shadow:0 15px 30px #ca941b25}
.verified{background:#ebf9ef}
.project-tags span{border-color:#e3dbbc}
.section-header h2 span{color:#009cb7}
.work-filter button[aria-pressed=true]{background:#0c2939}
.service-section{background:#fff4c5}
.service-list,.service-item{border-color:#e6d89a}
.service-title h2 em{color:#008faa}
.about-section{background:#fffdf5}
.contact-section{background:#0f2335}
.button-light{background:#ffe46b;color:#162535}
.button-light:hover{background:#fff19b}
"""
 },
 "dark": {
     "folder": "concept03-dark",
     "title": "03 / Midnight Cyan",
     "tag": "Technical & bold",
     "description": "A dark navy systems-first aesthetic, bright cyan UI, technical credibility and a restrained yellow spark.",
     "css": r"""
:root{--ink:#eaf5f9;--ink2:#cddde2;--cyan:#16d8ec;--cyan2:#24d0df;--muted:#9eb8c3;--line:#294757;--soft:#103a49}
body{background:#091724;color:var(--ink)}
.site-header{background:#081725;border-bottom-color:#1d4351}
.wordmark span{color:#fff}.wordmark strong{color:var(--cyan)}
.nav a{color:#dcebf0}.nav a:hover{color:#42dceb}
.header-contact{background:#0c2b39;border-color:#12bfdc;color:white}
.header-contact:hover{background:#164658}
.hero{background:radial-gradient(circle at 74% 32%,#123b4b 0%,#0c2130 37%,#081725 75%)}
.hero-orb{background:#0e6881;opacity:.22}
.eyebrow{color:#7eb1c0}.eyebrow .cyan-dot{background:#f3c943}
.hero h1{color:#fff}.hero h1 em{color:var(--cyan)}
.lead{color:#bfd6dd}.sublead{color:#93afbe}
.skill-line{color:#b4cad1}.skill-line span{border-left-color:#486678}
.button-solid{background:#1cd9ea;color:#031620;border-color:#1cd9ea}.button-solid:hover{background:#9ff6ff}
.button-outline{background:transparent;border-color:#2bd6e8;color:#ecfaff}.button-outline:hover{background:#16435a}
.visual-grid{opacity:.35}
.portrait-card{background:#102e3d;border-color:#276a7e;color:#f2fbfc;transform:rotate(-2deg);box-shadow:0 18px 48px #0008}
.portrait-head{background:#1c6074}.portrait-copy small{color:#a4cbd5}.portrait-copy .eyebrow{color:#33d7e7}
.code-card{background:#071824;border-color:#246981;box-shadow:18px 15px 0 #0b3242}
.code-card-header{background:#102a3b}.visual-label{background:#143645;border-color:#2c6877;color:white}.visual-label span:last-child{color:#a3cbd5}
.cross{color:#dcbf32}
.capability-strip{background:#0e2735;border-color:#245063}.strip-content span{color:#9cc4d1}.strip-content .strip-intro{color:#e8fbff}.strip-intro b{color:#ebce4f}
.work-section{background:#0b1d2b}.section-header h2{color:white}.section-header h2 span{color:var(--cyan)}.work-intro p{color:#adc2ca}
.work-filter button{background:#122b38;border-color:#386073;color:#b8d2d9}.work-filter button[aria-pressed=true]{background:#13d5e7;border-color:#13d5e7;color:#031923}
.project{background:#112b39;border-color:#285363;color:var(--ink);box-shadow:none}.project:hover{border-color:#1ad5e3;box-shadow:0 15px 40px #0006}
.project-body{background:#112b39}
.project-meta{color:#a4c3ce}.verified{background:#174b4c;color:#9decdf}.preview-state{background:#334758;color:#d8e9ed}
.project h3{color:#f1fbff}.project p{color:#b3c9d1}.project-tags span{border-color:#3b6473;color:#d4e8ed}
.project-disclaimer{color:#9bb6be}
.service-section{background:#102d3a;color:white}.service-title h2{color:white}.service-title h2 em{color:var(--cyan)}.service-title p{color:#b3cbd1}.inline-link{color:#d7f8fa}
.service-list,.service-item{border-color:#36616d}.service-item h3{color:white}.service-item p{color:#a9c7cd}
.about-section{background:#0b1d2b;border-top-color:#31515e}.about-inner h2{color:white}.about-inner p{color:#a4beca}
.about-card{background:#153545;border-color:#346476}.about-card strong{color:white}.about-card span{color:#abc6cd}
.contact-section{background:#06111c;border-top:1px solid #2a4f61}.contact-section h2{color:white}.contact-section h2 span{color:#f4cb3b}
.button-light{background:#14d5e8;color:#062132}.button-light:hover{background:#9ef4fd}
footer{background:#081725;border-top:1px solid #2e5060}.footer-inner{color:#98b5be}
@media(max-width:650px){.nav{background:#0f2936;border-bottom-color:#315d70}.nav a{color:#effcff}.mobile-toggle{background:#0e3040;color:#f5fbff;border-color:#3b7889}}
"""
 }
}
for key, variant in variants.items():
    dest = DOCS / variant['folder']
    dest.mkdir(parents=True, exist_ok=True)
    html = base.replace('href="./styles.css"', 'href="../cyan/styles.css"><link rel="stylesheet" href="./variant.css"')
    hero_photo = '<div class="portrait-head"><img src="./assets/matt-headshot.png" alt="Matt Sidnell, using a genuine photograph cropped from an existing portrait" width="180" height="180"></div>'
    hero_placeholder = '<div class="portrait-head portrait-pending" role="img" aria-label="Illustrative placeholder for a casual photograph of Matt wearing a hoodie"><div class="hoodie-art" aria-hidden="true"><span class="hoodie-head"></span><span class="hoodie-body"></span></div></div>'
    assert hero_photo in html
    html = html.replace(hero_photo, hero_placeholder)
    html = html.replace('<span class="eyebrow">Hello, I\'m</span><strong>Matt.</strong>', '<span class="eyebrow">Casual photo to add</span><strong>Matt.</strong>')
    about_photo = '<img src="./assets/matt-headshot.png" width="180" height="180" alt="Genuine cropped photograph of Matt Sidnell">'
    assert about_photo in html
    html = html.replace(about_photo,'<div class="about-monogram" aria-label="Matt Sidnell initials">MS.</div>')

    html = html.replace('src="./site.js"', 'src="../cyan/site.js"')
    html = html.replace('src="./assets/', 'src="../cyan/assets/')
    html = html.replace('href="./assets/', 'href="../cyan/assets/')
    html = html.replace('<body>', f'<body class="theme-{key}">')
    html = html.replace('<header class="site-header">', switcher + '\n<header class="site-header">')
    html = html.replace('<title>Matt Sidnell', f'<title>{variant["title"]} — Matt Sidnell')
    (dest / "index.html").write_text(html)
    chrome = r"""
.theme-switcher{background:#092231;color:#d9f4f8;border-bottom:1px solid #1e5266;font:600 10px 'DM Sans',sans-serif;letter-spacing:.075em}
.theme-switcher-inner{display:flex;align-items:center;justify-content:space-between;gap:18px;min-height:40px;padding-top:6px;padding-bottom:6px}
.theme-switcher nav{display:flex;gap:8px;flex-wrap:wrap}
.theme-switcher nav a{padding:6px 10px;border:1px solid #325c6f;border-radius:3px}
.theme-switcher nav a:hover,.theme-switcher nav a[aria-current=page]{background:#16cde3;color:#0c2430;border-color:#16cde3}
.switcher-separator{color:#f1c83a}.switcher-all{color:#b3e7f1;white-space:nowrap}
@media(max-width:650px){.theme-switcher-inner{flex-wrap:wrap;padding-top:9px;padding-bottom:9px;gap:6px}.theme-switcher nav{order:3;width:100%;gap:5px}.theme-switcher nav a{padding:5px 6px;font-size:9px}.switcher-all{margin-left:auto;font-size:9px}}
"""
    chrome = chrome.replace('nav a[aria-current=page]','nav a[href="../'+variant['folder']+'/"]')
    chrome += r"""
/* Portrait placeholder, not a photograph or an AI-generated likeness. */
.portrait-head.portrait-pending{width:155px;height:155px;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#b8f0f5,#ddf6ff);border:1px solid #a8deeb;overflow:hidden}
.hoodie-art{position:relative;display:block;width:155px;height:155px}
.hoodie-head{display:block;position:absolute;top:26px;left:57px;width:43px;height:49px;border-radius:42% 42% 48% 48%;background:#173d50;box-shadow:0 0 0 9px #2a778a}
.hoodie-body{display:block;position:absolute;top:83px;left:11px;width:134px;height:116px;border-radius:60px 60px 0 0;background:linear-gradient(120deg,#153343,#276b81)}
.hoodie-body:before{content:'';position:absolute;left:43px;top:-8px;width:49px;height:30px;border-radius:40% 40% 50% 50%;background:#173d50;border:5px solid #2a778a}
.hoodie-body:after{content:'';position:absolute;left:67px;top:35px;width:2px;height:45px;background:#b4e3e8;box-shadow:10px 0 0 #b4e3e8}
.about-monogram{display:grid;place-items:center;flex:0 0 84px;width:84px;height:84px;border-radius:50%;background:#c8f6fa;color:#095169;font:800 26px 'Manrope';letter-spacing:-.1em}
.theme-dark .about-monogram{background:#226275;color:#c7faff}
@media(max-width:860px){.portrait-head.portrait-pending{width:110px;height:110px}.hoodie-art{transform:scale(.72);transform-origin:top left;flex:0 0 155px;align-self:flex-start}}
"""

    (dest / "variant.css").write_text(chrome + "\n" + variant['css'])
selector = {
   "project":"Matt Sidnell — Concept 03 Colour Studies",
   "category":"Personal portfolio design review",
   "title":"Concept 03. Three colour directions.",
   "summary":"Compare the same real developer portfolio in three colourways: a restrained cyan-led version, a livelier yellow-accented version and a dark technical version. Every preview includes actual project screenshots and real links where available.",
   "notice":"Design previews only. The person is represented by a small, genuine headshot cropped from an existing formal photograph. A casual hoodie/jeans portrait has not been fabricated: replace the headshot with a newly supplied genuine photo. Project previews are captured from live websites or labelled local development builds.",
   "concepts":[
       {"name":v["title"],"tag":v["tag"],"description":v["description"],"image":"../assets/previews/"+v["folder"]+".jpg","url":"../"+v["folder"]+"/"} for v in variants.values()
   ]
}
dest=DOCS/"concept03"
dest.mkdir(parents=True,exist_ok=True)
(dest/"selector.json").write_text(json.dumps(selector,indent=2))
print("Rendered:",", ".join([v["folder"] for v in variants.values()]))
