# Matt Sidnell production portfolio, deployed 29 October 2026

The bold electric cyan design from `docs/concept03/index.html` is live at **https://mattsidnell.co.uk/**. Both root and www returned HTTPS 200; browser checks at 390px and 1440px passed with 10/10 images, working mobile menu, no JavaScript errors and no horizontal overflow.

## Production artifact and runtime

- Build: `python3 deploy/production/build.py`. Output: ignored `dist-production/` web root. This modifies only the selected static preview's root-relative asset paths, search indexing metadata and canonical page title; approved portrait and nine project screenshots are copied without editing.
- Production target: `prod-01`, `192.248.171.250`, SSH identity `auto-ops` through the Mac Bridge.
- Uploaded site files: `/home/auto-ops/sites/mattsidnell-production/site/`; Nginx configuration: `/home/auto-ops/sites/mattsidnell-production/config/nginx.conf`.
- Dedicated runtime: `mattsidnell-portfolio-prod`, using approved `nginx@sha256:a8b39bd9cf0f83869a2162827a0caf6137ddf759d50a171451b335cecc87d236` and read-only bind mounts for website files and web configuration. No published host ports. Runtime attached to existing gateway ingress network `pw-service-f1c1a569-de48-4d53-895e-b708f47635cd`, without modifying other website containers.
- Caddy gateway: `pw-ops-gateway`. The exact two hostnames `mattsidnell.co.uk` and `www.mattsidnell.co.uk` were previously routed to the redirect backend `e9f4a17f-e386-42c0-b387-8413cdab85f6-web:80` and returned a redirect to `sidnell.uk`. They now reverse proxy to `mattsidnell-portfolio-prod:80`. Caddy configuration was validated before reload.
- Caddy rollback file on Prod-01: `/var/lib/pixlwrk-ops-host/gateway/config/caddy.backup-before-mattsidnell-20261029.json`. Current config: `/var/lib/pixlwrk-ops-host/gateway/config/caddy.json`.

## Important source-of-truth reconciliation

The production release was an **urgent authorised direct deployment through AutoOps** so the portfolio could be used for a contract application immediately. The two existing Caddy ingress routes were surgically switched, preserving all unrelated route entries and the original Caddy route response headers. **This direct change is not yet represented as a new Ops-managed package/domain record**, and future gateway regeneration by an Ops host worker could overwrite it. Reconcile those exact two domain records into the Ops website/package lifecycle promptly; do not leave direct Caddy manipulation as the standard deployment workflow.

The portfolio currently runs as static HTML/CSS/JS, **not WordPress**. Conversion to an editable custom WordPress theme/plugin is a separate later project, once the immediate CV use is complete. Do not re-publish the DigiPixel preview selector or noindex metadata at the production root.

## Repeated safe deployment

1. Update the approved portfolio source and review the nine actual case-study screenshots.
2. Run `python3 deploy/production/build.py` and browser tests locally.
3. Deploy the exact new `dist-production/` files to the existing site content volume. The web server does not need rebuilding for static file changes.
4. Verify public HTTPS, page title, photos, all project images, mobile menu, contact links and sitemap. Preserve a previous content revision for rollback. Future rollout should be through Ops's approved Publish action once the new website creation/publishing flow is implemented.

Production email links use `me@mattsidnell.co.uk`, distinct from the DigiPixel and regulated mortgage mailboxes.

## Contact form production update — 29 October 2026

The production footer now reads **Freelance web developer & software engineer** with a privacy notice link; no preview or Concept 03 designation remains. Four former mailto CTAs open an accessible native HTML dialog. Files: `contact.html`, `contact.css`, `contact.js`; `build.py` injects them into the approved homepage.

- Route: same-origin `POST https://mattsidnell.co.uk/api/contact`, proxied by the existing read-only Nginx site container to the dedicated internal-only `mattsidnell-contact-api` container on the existing gateway network. No public API container port. The Nginx configuration change has a Prod-01 rollback copy at `/home/auto-ops/sites/mattsidnell-production/config/nginx.before-contact-20261029.conf`.
- Runtime: `python@sha256:5789aa194f757888f41fa3d48e14b6feaa1b57c0af0b56fcb1372d6474d3bff0`, non-root UID 10001, read-only root filesystem, no additional Linux capabilities, constrained resources. Code is read-only bound from `/home/auto-ops/sites/mattsidnell-production/contact-api/app.py`.
- Enquiry storage: a private SQLite DB at `/home/auto-ops/sites/mattsidnell-production/contact-data/enquiries.sqlite`, mode 0700 directory, writable only by the application UID and root. The API validates fields, requires an exact-site Origin, protects against cross-origin requests, uses a honeypot, per-sender/global throttling, size limits and idempotency; automatically purges data older than 180 days. There is no public admin route or data export.
- Review enquiries on an authorised host session: `sudo docker exec mattsidnell-contact-api python /app/app.py list`. To display one complete message, run `sudo docker exec mattsidnell-contact-api python /app/app.py show UUID`. Do not expose these outputs publicly or paste actual personal data into source control.
- QA: a synthetic form was accepted through the live public website and confirmed in SQLite, then the exact test record was deleted. Invalid-origin submissions returned HTTP 403. Desktop and mobile modal opening, focus, success feedback, Escape/close, no overflow and footer copy were checked in Chromium.
- **Remaining delivery dependency:** no outgoing SMTP/Graph notification transport is configured for this endpoint. A successful confirmation means the enquiry was **saved**, NOT emailed. The shared DigiPixel Forms API at `forms.digipixel.uk` was unavailable (network timeout) when this was deployed, so it was not used. A properly authenticated notification transport and off-machine backup policy for this new database must be set up and verified before considering the contact system fully operational for unattended lead handling. Do not claim alerts or offsite protection for this new DB until proven.
