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
