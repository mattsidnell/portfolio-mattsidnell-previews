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
