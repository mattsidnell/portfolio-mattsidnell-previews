# Matt Sidnell contractor portfolio — three design prototypes

Personal freelance and agency-contract portfolio for mattsidnell.co.uk. Not the Digipixel customer-facing offer, the Pixlwrk product brand, or the Sidnell brokerage business. No live-domain replacement is performed by this project.

## Concepts

1. The Independent `docs/independent/` — refined editorial independent contractor site with existing portrait
2. The Studio `docs/studio/` — bold graphic developer portfolio, project-first
3. The Systems Mind `docs/systems/` — product and engineering focused with working project filters

## Local development

`docker compose -f compose.local.yml up -d`

Local URL: http://127.0.0.1:8797/ and via Docker Caddy ingress `https://mattsidnell-portfolio.digipixel.test/`. Source lives in ~/Sites/mattsidnell-portfolio.

## Single canonical preview selector

The gallery homepage is generated from `preview-selector.json` using the single shared `~/Sites/digipixel-preview-selector/render.py` stylesheet and DigiPixel logo. The generator copies the canonical assets; do not fork or restyle the selector.

`python3 ~/Sites/digipixel-preview-selector/render.py --config preview-selector.json --output docs/index.html`

Preview pages have noindex headers and metadata. Contact actions use the existing personal email matt@sidnell.uk and never send a message automatically.

## Content boundaries

Project copy focuses on actual built systems, does not fabricate testimonials, client relationships, outcomes, or quantitative results. Missing live links for unverified projects are intentionally omitted. The illustrated visual treatment in one project card is not a screenshot and is labelled as such.

## Next step

Choose a direction, replace illustrative project artwork with verified screenshots and full case studies, and build the selected version on the intended production architecture. Only after approval consider switching mattsidnell.co.uk away from its current website.

## Selected direction: The Cyan Edition (29 October 2026)

- New responsive site: `docs/cyan/`, preview path `/cyan/` and linked first in the shared DigiPixel selector.
- Clean white background with navy and cyan accent; project-first portfolio for freelance web developer and agency contract applications.
- **Genuine small portrait:** `docs/cyan/assets/matt-headshot.png` is a cropped version of the existing publicly used Matt Sidnell portrait from the Sidnell website. It remains a formal source photo. Replace it with a genuine casual portrait when provided. Do not use an AI generated lookalike as a real picture of Matt.
- **Real screenshots:** collected using `tests/capture-projects.js` from live sites, plus two clearly marked local development sites in `tests/capture-local-projects.js`. Do not fabricate project website screenshots, testimonials, affiliations or performance metrics.
- Live examples verified at capture: Grinders Golf, Sidnell, DigiPixel, Professional Structures, Web Designer Direct, Sunnyside Accountancy and LPS Garden Buildings.
- Local examples captured from `lfc-v2.dev.digipixel.test` and `pixlwrk.preview.dev.digipixel.test`; these do not have working public live links at capture, therefore show no production links.
- Contact email for developer portfolio: `me@mattsidnell.co.uk`, phone `07723 994463`. These are separate from regulated mortgage services.
- Browser QA: `node tests/verify-cyan.js`; all 11 on-page image resources loaded after lazy-loading, 390px mobile without horizontal overflow, working navigation and project filters. The site and selector carry `noindex,nofollow` and no form sends data.
- This is a **review preview**, not production: the existing mattsidnell.co.uk home remains unchanged.

## Concept 03 colour comparison (29 October 2026)

Published as a dedicated comparison gallery at `/concept03/`, with three full responsive and interactive variations:

- `/concept03-cyan/`: clean cyan + navy with a tiny yellow detail.
- `/concept03-yellow/`: cyan + a more visible electric yellow accent.
- `/concept03-dark/`: dark navy, cyan and just a small amount of yellow.

All three are generated from the same canonical portfolio content (`docs/cyan/`), so project descriptions, nine captured real screenshots, public live links, contact routes, navigations and filters remain consistent. The comparative CSS is intentionally separate. Source of truth is `tests/build-concept03.py`. After changes run `python3 tests/build-concept03.py` and `python3 ~/Sites/digipixel-preview-selector/render.py --config docs/concept03/selector.json --output docs/concept03/index.html`. Shared DigiPixel selector styling is retained.

**Portrait correctness:** An earlier image-generation concept displayed a fictional face in a hoodie. The real cropped photo still showed a suit. Since no genuine casual photo of Matt has been provided, these three working sites use an explicitly labelled hoodie illustration in the hero and MS initials in the about block. Neither is represented as an actual portrait. Replace these elements with a user-approved genuine casual photo once supplied. Do not use synthetic faces or invented project screenshots as factual portfolio proof.

`node tests/verify-concept03.js` tests all three: desktop/mobile dimensions, image loads, navigation, filter operation and JS errors. This is preview-only, does not change mattsidnell.co.uk, and carries noindex metadata.

## Concept 03 correction — reference fidelity

The user clarified Concept 03 by supplying the dark navy/cyan visual showing a two-column hero, a casual profile image with code-editor overlays, technical flow boxes, an expertise strip, and four side-by-side project screenshot cards. The previous `docs/concept03-*` pages incorrectly replicated the separate white `docs/cyan` design. **The corrected variations are now built from `tests/concept03-reference.html`, not `docs/cyan/index.html`.**

- `docs/concept03-dark/`: closest to the selected dark original, bright cyan highlights, subtle yellow marks.
- `docs/concept03-cyan/`: faithful same layout with clean bright cyan and navy.
- `docs/concept03-yellow/`: faithful same layout with warmer white background and yellow highlights.
- `docs/concept03/`: comparison gallery rendered from the existing reusable DigiPixel selector.
- Generator: `python3 tests/build-concept03.py`, then selector renderer. Visual CSS and JS: `docs/concept03/assets/site.css` and `site.js`.
- The top four project images use **real captured website screenshots**: Sidnell (live), Grinders (live), Lyneham Flying Club (local), Pixlwrk (local). Further actual public sites are under More selected work. Do not imply the local builds are public.
- The hero intentionally uses a **clearly labelled illustration/composite** of Matt's real facial portrait with a CSS hoodie, not a claim that he has been photographed wearing a hoodie. To replace with an authentic hoodie-and-jeans photo, request a genuine casual source photograph and preserve the verified layout.
- Verify `node tests/verify-concept03.js` on desktop and mobile. All comparisons noindex and staging/review only. Do not change mattsidnell.co.uk without separately requested production deployment.

## AUTHORITATIVE CONCEPT 03 — screenshot confirmed (29 October 2026)

**This replaces all earlier, incorrect references to Concept 03.** The user supplied an actual screenshot identifying Concept 03 as the **BOLD YELLOW** homepage, with `I MAKE / WEBSITES / & MORE`, yellow background, huge black/outlined display lettering, a circular `SEE THE WORK` button, and a black technology ticker. It was initially named `The Studio` in the first group of concepts. It is NOT the separate dark Systems Mind design, nor the later cyan Design Led page.

**URLs**
- `/concept03/` — canonical original yellow screenshot-matched page. This deliberately opens the page, not a gallery.
- `/studio/` and `/concept03-yellow/` — the same original yellow design.
- `/concept03-cyan/` — the same exact layout with cyan as the principal colour.
- `/concept03-dark/` — the same exact layout with dark navy, cyan and small yellow accents.
- `/concept03-compare/` — colour comparison gallery using the shared DigiPixel preview selector.

**Implementation**
- `tests/concept03-bold-reference.html`: canonical unedited original `studio/index.html` captured from the initial design, retaining the precise hero layout.
- `tests/build-bold-concept03.py`: the only current generator for these Concept 03 pages. Updates project showcases and the About graphic *without modifying the original bold hero layout*.
- Uses nine real screenshots in `docs/cyan/assets/projects/`; the first four include Grinders, Lyneham Flying Club (clearly local), Sidnell, and Pixlwrk (clearly local).
- No face compositing, invented hoodie photo, formal suit photograph or other portrait. The screenshot has no hero portrait. The About section uses a bold typographic block, not a picture. This avoids pretending a synthetic casual portrait is a real photo.
- Verify `node tests/verify-bold-concept03.js`. Tested desktop 1440px, mobile 390px, no overflow, 9 real screenshot images loaded, menu functional, no JS exceptions.
- Do not alter the production `mattsidnell.co.uk` site until user requests deployment.

**Rebuild**
```
python3 tests/build-bold-concept03.py
python3 ~/Sites/digipixel-preview-selector/render.py --config docs/concept03-compare/selector.json --output docs/concept03-compare/index.html
node tests/verify-bold-concept03.js
```

## 29 October 2026 — Cyan-first staging delivery

The selected Concept 03 is the bold `I MAKE WEBSITES & MORE` design, not the unrelated systems-minded design. Three variants share the original layout:

1. `docs/concept03-cyan/` — preferred electric cyan, small yellow accent.
2. `docs/concept03-yellow/` — original yellow reference.
3. `docs/concept03-dark/` — midnight navy with cyan highlights.

`docs/concept03/` is now the cyan version and `docs/concept03-compare/` is the shared DigiPixel-branded selector, cyan listed first. All developer contact links in these versions use `me@mattsidnell.co.uk`. Nine real project screenshots, mobile navigation and contact links are verified.

Staging origin files are copied to `stg-01` (104.238.185.163), `/home/mattsidnell/previews/mattsidnell/`, using Mac Bridge SSH as the authorised `mattsidnell` user. A user-owned static HTTP service on port 8765 returns 200 on that server. However public traffic to port 8765 is blocked and `mattsidnell.preview.digipixel.uk` has no Caddy HTTPS route/certificate yet. Do **not** claim the branded staging URL is live until that reverse-proxy route is provisioned in Ops and verified externally. Account does not have permission for the root-owned Docker socket/Caddy route; `sudo -n` requires interactive authentication. The GitHub Pages preview remains the externally accessible review fallback. Public HTTPS routing on the staging domain is the remaining blocker; source and site files are already staged.

Do not deploy over `mattsidnell.co.uk` without a separate production instruction.
