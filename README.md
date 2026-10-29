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
