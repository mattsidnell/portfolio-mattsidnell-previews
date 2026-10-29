#!/usr/bin/env python3
"""Rebuild from the screenshot-matched BOLD YELLOW 'I MAKE WEBSITES & MORE' source.

This is Concept 03 as identified by the user from the phone screenshot.
Never replace it with the separate dark Systems Mind or cyan Design Led layouts.
"""
from pathlib import Path
import json, re

root=Path(__file__).resolve().parents[1]
docs=root/'docs'
reference=(root/'tests'/'concept03-bold-reference.html').read_text()

# The hero, navigation, and ticker are unchanged from the user's exact screenshot.
projects=[
  ("01","Grinders Golf","CUSTOM GOLF SOCIETY PLATFORM","A custom WordPress golf society website and management system.","grinders.jpg","https://grinders.golf/","WordPress · Club management","live"),
  ("02","Lyneham Flying Club","MEMBERSHIP & OPERATIONS","A specialist flying club website with membership and operational workflows.","lyneham.jpg",None,"WordPress · Membership","local"),
  ("03","Sidnell","HEADLESS PROFESSIONAL SERVICES","Decoupled professional services website powered by headless WordPress.","sidnell.jpg","https://sidnell.uk/","Headless · CMS","live"),
  ("04","Pixlwrk","DEVELOPER & SOFTWARE STUDIO","A portfolio for custom websites, software and engineering work.","pixlwrk.jpg",None,"Web engineering · Software","local"),
  ("05","Professional Structures","CONSULTANCY WEBSITE","Business consultancy website with a focus on meaningful enquiries.","pstructures.jpg","https://pstructures.com/","WordPress · Lead generation","live"),
  ("06","Web Designer Direct","LEAD GENERATION PLATFORM","A guided website enquiry and quotation experience.","wdd.jpg","https://webdesignerdirect.com/","Custom workflows · Conversion","live"),
  ("07","DigiPixel","DIGITAL AGENCY WEBSITE","Agency website focused on accessible digital services and project enquiries.","digipixel.jpg","https://digipixel.uk/","Web design · Development","live"),
  ("08","Sunnyside Accountancy","ACCOUNTANCY WEBSITE","Professional services website with clear services and contact pathways.","sunnyside.jpg","https://sunnysideaccountancy.co.uk/","Business websites · Responsive","live"),
  ("09","LPS Garden Buildings","TRADES & GARDEN BUILDINGS","Product and services presentation for a specialist garden buildings business.","lps.jpg","https://lpsgardenbuildings.co.uk/","Web design · Enquiries","live"),
]
cards=[]
for num,name,category,description,shot,link,tags,kind in projects:
    pic=f'<img src="../cyan/assets/projects/{shot}" alt="Actual screenshot of the {name} website" loading="lazy" width="1440" height="920">'
    if link:
        visual=f'<a class="project-screenshot" href="{link}" target="_blank" rel="noopener noreferrer" aria-label="Visit {name} live website">{pic}<span class="visit-label">Live website ↗</span></a>'
    else:
        visual=f'<div class="project-screenshot">{pic}<span class="visit-label local-label">Local development</span></div>'
    cards.append(f'''
<article class="work-card">
{visual}
<div class="work-card-content">
<div class="work-card-top"><span>PROJECT / {num}</span><span class="work-card-state">{category}</span></div>
<h3>{name}</h3>
<p>{description}</p>
<div class="work-card-footer"><span>{tags}</span>{f'<a href="{link}" target="_blank" rel="noopener noreferrer" aria-label="Open {name} live website">↗</a>' if link else '<small>LOCAL BUILD</small>'}</div>
</div></article>''')

work_section='''
<section class="work" id="work"><div class="wrap">
 <div class="section-top"><div><span class="kicker">01 / A few things I've built</span><h2>Selected<br>work<span class="headline-period">.</span></h2></div>
 <p>Not just a stack of pretty homepages. These projects involve custom functionality, content architecture, workflows and genuine software engineering.</p></div>
 <div class="work-grid">'''+"".join(cards)+'''</div>
 <p class="work-note">Real screenshots captured from working sites. Lyneham Flying Club and Pixlwrk are labelled as local development builds; live public links are omitted for those two. No invented portfolio screenshots, endorsements or performance results.</p>
</div></section>
'''

about_section='''''
<section class="about" id="about"><div class="wrap about-grid">
<figure class="about-photo"><img src="../assets/portrait/matt-seated.webp" width="1000" height="1199" loading="lazy" alt="Matt Sidnell seated in his office wearing a navy hoodie and jeans"></figure>
<div><span class="kicker">03 / The human behind the code</span><h2>Hi, I'm Matt.</h2>
<p>I'm an independent web developer based in Wiltshire. I enjoy the meeting point between great design and difficult technical challenges.</p>
<p>Need extra hands for an agency project, a specialist build or a short contract? I can work alongside your existing team without making everything more complicated.</p>
<a class="small-btn" href="mailto:me@mattsidnell.co.uk?subject=Agency%20contract%20opportunity">Let's talk about it ↗</a>
</div></div></section>
'''''

work_re=r'<section class="work" id="work">.*?</section>'
about_re=r'<section class="about" id="about">.*?</section>'
assert len(re.findall(work_re,reference,re.S))==1 and len(re.findall(about_re,reference,re.S))==1
html=re.sub(work_re,work_section,reference,count=1,flags=re.S)
html=re.sub(about_re,about_section,html,count=1,flags=re.S)

base_css=r'''
/* Genuine website screenshot portfolio cards added without changing the hero layout. */
.work-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:27px}
.work-card{min-width:0;border:2px solid var(--black);background:var(--cream);display:flex;flex-direction:column;transition:transform .18s,box-shadow .18s}
.work-card:hover{transform:translateY(-4px);box-shadow:8px 8px 0 var(--black)}
.project-screenshot{height:305px;display:block;overflow:hidden;position:relative;background:#d2d5d0;border-bottom:2px solid var(--black)}
.project-screenshot img{width:100%;height:100%;object-fit:cover;object-position:top center;transition:transform .2s}
.work-card:hover .project-screenshot img{transform:scale(1.025)}
.visit-label{position:absolute;right:16px;bottom:16px;background:var(--yellow);border:1px solid var(--black);box-shadow:3px 3px 0 var(--black);font:700 11px 'Space Grotesk';text-transform:uppercase;padding:9px 13px;color:var(--black)}
.visit-label.local-label{background:var(--cream);color:var(--black)}
.work-card-content{padding:26px 26px 24px;display:flex;flex-direction:column;flex:1}
.work-card-top{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;font:700 10px 'Space Grotesk';letter-spacing:.04em}
.work-card-state{text-align:right;opacity:.65}
.work-card h3{font:clamp(29px,3vw,42px)/1.07 'Archivo Black';text-transform:uppercase;letter-spacing:-.065em;margin:19px 0 13px}
.work-card p{font-size:15px;line-height:1.5;margin:0 0 23px;max-width:530px}
.work-card-footer{display:flex;justify-content:space-between;align-items:center;border-top:1px solid var(--black);margin-top:auto;padding-top:15px;gap:12px;font-size:12px;font-weight:700}
.work-card-footer a{display:grid;place-items:center;border:2px solid var(--black);border-radius:50%;width:35px;height:35px;font-size:20px}
.work-card-footer a:hover{background:var(--yellow)}
.work-card-footer small{font-size:10px;letter-spacing:.06em}
.headline-period{color:#dc4b7d}
.about-art{min-height:475px;display:flex;flex-direction:column;justify-content:space-between;overflow:hidden;border:3px solid var(--black);background:var(--yellow);box-shadow:18px 18px 0 #1d1f1836;padding:27px 28px}
.about-art-top,.about-art-bottom{font:700 13px 'Space Grotesk';letter-spacing:.04em;line-height:1.4}
.about-art>strong{font:clamp(58px,6.7vw,104px)/.89 'Archivo Black';letter-spacing:-.09em}
.about-art>strong span{color:#e86696}
.about-art-bottom{display:flex;justify-content:space-between;border-top:2px solid var(--black);padding-top:14px}
.about-art-bottom span{font-size:24px;line-height:.7}
.about-portrait{display:block;position:relative;overflow:hidden;border:3px solid var(--black);background:#183c47;box-shadow:18px 18px 0 #11283235;margin:0;aspect-ratio:850/980}
.about-portrait img{display:block;width:100%;height:100%;object-fit:cover;object-position:center 24%;filter:saturate(.95)}
.about-portrait figcaption{position:absolute;bottom:0;left:0;right:0;background:var(--yellow);color:#0c2435;border-top:3px solid var(--black);font:800 11px 'Space Grotesk';letter-spacing:.12em;padding:16px 19px;display:flex;justify-content:space-between;align-items:center}
.about-portrait figcaption span{font-size:23px;line-height:1}
body[data-colour=dark] .about-portrait{border-color:#43cfdf;box-shadow:18px 18px 0 #17a9c922}
@media(max-width:720px){.about-portrait{max-width:500px;aspect-ratio:850/960}}
body[data-colour=cyan]{--yellow:#44d9ed;--cream:#f1fbff;--pink:#ffe77d;--black:#0c2535}
body[data-colour=cyan] .hero{background:#43d6e9}
body[data-colour=cyan] .ticker{color:#9aeeff}
body[data-colour=cyan] .hero h1 .outlined{-webkit-text-stroke:2px #0c2535}
body[data-colour=cyan] .hero h1 span[style]{color:#f0d33b!important}
body[data-colour=cyan] .headline-period{color:#e6bd28}
body[data-colour=cyan] .about-art>strong span{color:#eac733}
body[data-colour=dark]{--yellow:#07263a;--cream:#112d3f;--pink:#d8b744;--black:#d7f8ff}
body[data-colour=dark]{background:#07263a;color:#eefaff}
body[data-colour=dark] .top{background:#071a27;border-color:#38677a}
body[data-colour=dark] .hero{background:#08293d;color:#f2fcff}
body[data-colour=dark] .hero h1 .outlined{-webkit-text-stroke:2px #48d7f0}
body[data-colour=dark] .hero h1 span[style]{color:#ecd04b!important}
body[data-colour=dark] .top-right .hire{background:#31d6ee;border-color:#31d6ee;color:#061b29}
body[data-colour=dark] .top-right .hire:hover{background:#fcde65}
body[data-colour=dark] .ticker{background:#051b2a;color:#79ecff;border-color:#326075}
body[data-colour=dark] .work{background:#102e40;color:#f0fcff}
body[data-colour=dark] .work-card{background:#0b2638;color:#f1fbff;border-color:#4a8092}
body[data-colour=dark] .work-card:hover{box-shadow:8px 8px 0 #1cd3ec}
body[data-colour=dark] .visit-label{background:#28d7ee;color:#061d2b;border-color:#071925}
body[data-colour=dark] .visit-label.local-label{background:#24495c;color:white;border-color:#b5e8f0}
body[data-colour=dark] .work-card-footer{border-color:#568696}
body[data-colour=dark] .work-card-footer a{border-color:#58c7df}
body[data-colour=dark] .work-card-footer a:hover{background:#17687e}
body[data-colour=dark] .work-card-state{color:#c5dce6}
body[data-colour=dark] .work-note{color:#aacad5}
body[data-colour=dark] .headline-period{color:#f1d048}
body[data-colour=dark] .split-left{background:#0b364a;color:#fff}
body[data-colour=dark] .split-right{background:#071722;color:#eefaff}
body[data-colour=dark] .split-left .scribble{color:#16546d}
body[data-colour=dark] .about{background:#0b293a;color:#f9fcff}
body[data-colour=dark] .about-art{background:#0d3b50;border-color:#52d5ea;box-shadow:18px 18px 0 #1abbd522}
body[data-colour=dark] .about-art>strong span{color:#f6d54e}
body[data-colour=dark] .contact{background:#071925;color:#f0fdff;border-color:#538398}
body[data-colour=dark] .contact .big-arrow{color:#46d9f1}
body[data-colour=dark] .foot{background:#04121c;color:#d0ecf4;border-top:1px solid #31637b}
body[data-colour=dark] .logo{color:#f0fdff}
body[data-colour=dark] .top-right a{color:#f0fdff}
body[data-colour=dark] .top-right .hire{color:#071925}
body[data-colour=dark] .toggle{color:#f7fcff;border-color:#81d7eb}
body[data-colour=dark] .desc b{background:#2be0f1;color:#051d2b}
body[data-colour=dark] .circle-btn{background:#27d8ec;color:#061b2b;border-color:#27d8ec}
body[data-colour=dark] .big-disc{background:#edd04c;color:#061923;border-color:#061923}
@media(max-width:960px){.work-grid{gap:18px}.project-screenshot{height:260px}.work-card-content{padding:21px}.about-art{min-height:400px}}
@media(max-width:720px){.work-grid{grid-template-columns:1fr}.project-screenshot{height:240px}.work-card h3{font-size:clamp(25px,7vw,37px)}.about-art{min-height:320px;max-width:500px}.about-art>strong{font-size:clamp(60px,16vw,110px)}.about-grid{gap:46px}body[data-colour=dark] .top-right{background:#072a3b}body[data-colour=dark] .top-right a{color:#e8faff}}
'''
photo_css=r'''
.about-photo{margin:0;min-height:475px;overflow:hidden;border:3px solid var(--black);box-shadow:18px 18px 0 #1d1f1836;background:#c4eaf1}
.about-photo img{width:100%;height:475px;object-fit:cover;object-position:center 31%;display:block}
body[data-colour=cyan] .about-photo{border-color:#08293a;box-shadow:18px 18px 0 #08465825}
body[data-colour=dark] .about-photo{border-color:#52d5ea;box-shadow:18px 18px 0 #1abbd522}
@media(max-width:960px){.about-photo,.about-photo img{min-height:0;height:410px}}
@media(max-width:720px){.about-photo{max-width:500px}.about-photo,.about-photo img{height:385px}}
'''
html=html.replace('</style>',base_css+photo_css+'</style>',1)
html=html.replace('Creative developer / Design concept 02','Personal developer portfolio / Concept 03')
html=html.replace('matt@sidnell.uk','me@mattsidnell.co.uk')
# The user's screenshot is the selected hero. DO NOT alter that hero's typography or layout.
base=html
for name,label in [('yellow','Original Yellow'),('cyan','Electric Cyan'),('dark','Midnight Navy')]:
    page=base.replace('<body>','<body data-colour="'+name+'">')
    page=page.replace('<title>Matt Sidnell — Creative developer, no fuss</title>','<title>Matt Sidnell | Concept 03 — '+label+'</title>')
    folder=docs / ('studio' if name=='yellow' else 'concept03-'+name)
    folder.mkdir(parents=True,exist_ok=True)
    # For same-level variant directories, ../cyan/assets/projects relative paths stay valid.
    (folder/'index.html').write_text(page)
    if name=='yellow':
        (docs/'concept03-yellow'/'index.html').write_text(page)

selector={
  "project":"Matt Sidnell — Concept 03 cyan-led colour comparison",
  "category":"Personal portfolio website design review",
  "title":"Concept 03. Cyan first, three bold directions.",
  "summary":"The bold 'I MAKE WEBSITES & MORE' portfolio design you picked, available in three colourways. Cyan is the leading option, with original yellow and dark navy for comparison.",
  "notice":"Design previews, not production. The About section uses the newly approved AI-assisted portrait created from Matt’s reference images. The portfolio cards show nine genuine site screenshots with local builds clearly labelled. The production mattsidnell.co.uk website is unchanged.",
  "concepts":[
    {"name":"01 / Electric Cyan","tag":"Preferred direction","description":"Your original bold typography with electric cyan dominant and controlled yellow accents.","image":"../assets/previews/concept03-cyan.jpg","url":"../concept03-cyan/"},
    {"name":"02 / Original Yellow","tag":"Original reference","description":"The black-on-yellow treatment from your screenshot; identical layout, exact original headline and navigation.","image":"../assets/previews/concept03-yellow.jpg","url":"../concept03-yellow/"},
    {"name":"03 / Midnight Navy","tag":"Dark alternative","description":"Same giant type and content layout on deep navy, accented with bright cyan and yellow.","image":"../assets/previews/concept03-dark.jpg","url":"../concept03-dark/"}
  ]
}
# The primary /concept03/ address must show the screenshot-matched website,
# never a selector or a different concept. The comparison lives separately.
(docs/'concept03'/'index.html').write_text((docs/'concept03-cyan'/'index.html').read_text())
compare=docs/'concept03-compare'
compare.mkdir(parents=True,exist_ok=True)
(compare/'selector.json').write_text(json.dumps(selector,indent=2)+'\n')
print('Rendered screenshot-faithful original and 3 Concept 03 colour variants, with',len(cards),'real project screenshots and the approved About portrait.')
