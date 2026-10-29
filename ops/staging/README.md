# Matt Sidnell — Staging preview deployment

This is a **dedicated** labelled Nginx container for `mattsidnell.preview.digipixel.uk`. It serves the existing three design previews and makes the approved electric cyan Concept 03 the default at `/`. It does not deploy WordPress and it does not alter other projects' containers.

## Inputs

* `PORTFOLIO_CONTENT_DIR=/home/mattsidnell/previews/mattsidnell` is the verified host source path, already uploaded by the Mac Bridge.
* `STAGING_INGRESS_NETWORK` **must** be read from the actual authorised staging Caddy network through Ops or a Docker-authorised deployment account. Do not invent this value, attach to another project's private network, or create an unrelated ingress network.
* Caddy is provisioned by Compose labels on `website`: `caddy`, `caddy.reverse_proxy` and `caddy.header.X-Robots-Tag`.

## Authorised installation (run only from an Ops-authorised Docker deployment identity)

```sh
cd /home/mattsidnell/previews/mattsidnell/.deployment
PORTFOLIO_CONTENT_DIR=/home/mattsidnell/previews/mattsidnell \
STAGING_INGRESS_NETWORK='<verified-existing-Caddy-network>' \
docker compose -f compose.preview.yml up -d
```

The user account `mattsidnell` currently has SSH but **no Docker socket access**, and noninteractive sudo is unavailable. The compose file is ready on staging, but must not be called deployed until the authorised runtime creates the service. Do not weaken Docker socket permissions or modify Caddy's generated config directly to bypass controls.

## Verification

`https://mattsidnell.preview.digipixel.uk/` should redirect to `/concept03/`, show the cyan hero and the approved About portrait, and expose all nine real portfolio images. Verify TLS, `X-Robots-Tag`, site links, mobile menu and 404 on missing paths. Use the GitHub Pages comparison as design review fallback, not evidence of completed staging HTTPS routing.

The hostname already resolves to Stg-01 (104.238.185.163).
