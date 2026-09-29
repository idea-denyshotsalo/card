# IDEA digital business cards

Static business-card pages for IDEA Travel Solutions staff, served by GitHub Pages:

- https://idea-denyshotsalo.github.io/card/ — Denys Hotsalo
- https://idea-denyshotsalo.github.io/card/alyona-shalahinova/ — Alyona Shalahinova

Each page shows the contact rows, a "Save contact" button and a QR code that points back to the page itself. Printed QR codes and wallet passes encode only the page URL, so contact details can change without reprinting.

The interactive guide for staff lives at `guide/`; `guide/?p=<slug>` (`?p=home` for the root card) opens it pre-filled for one person. It walks through the home-screen shortcut, Apple Wallet (WalletWallet fields with copy buttons) and Google Wallet (a branded PNG with the QR, drawn in the browser).

## Publishing

This repo holds the sources and history; the public site is served from [`idea-denyshotsalo/team`](https://github.com/idea-denyshotsalo/team). Every push to `main` runs `.github/workflows/publish.yml`, which copies the built pages (never `_src/`) into `team` as one orphan commit, so the public repo carries no history and no data files. The workflow pushes with the `TEAM_DEPLOY_KEY` secret, a write deploy key on `team`.

The workflow does not build: run `uv run _src/build.py` and commit the generated files in the same PR.

## Add or edit a person

1. Edit `_src/people.json`. `slug` is the folder name and URL path (`""` = site root). `first`, `last`, `title`, `bio`, `city` take `uk` and `en` variants; `bio` and every entry in `links` are optional (`linkedin`, `telegram`, `instagram`, `github`). `theme` picks the card colour: `burgundy`, `green` or `black` (defaults to `company.theme`).
2. Rebuild:

   ```
   uv run _src/build.py
   ```

   ```
   built (root)
   built alyona-shalahinova
   ```

3. Commit the generated `<slug>/index.html` and `<slug>/contact.vcf` together with the JSON, open a PR, merge. Pages redeploys in about a minute.

Never hand-edit the generated pages: the next build overwrites them. The old phone generator's `card-site.zip` export uses the previous design and must not be uploaded over these files.

## Layout

| Path | What |
|---|---|
| `_src/people.json` | All card data |
| `_src/base.css` | Brand tokens, light/dark themes, shared buttons |
| `_src/card.*`, `lang.js` | Card template, styles, behaviour, pre-paint language pick |
| `_src/guide.*` | Interactive guide |
| `_src/landing.html` | Root page, rendered only when no card has `slug: ""` |
| `_src/build.py` | Renders everything: pages, `contact.vcf` (UA) + `contact.en.vcf`, `manifest.webmanifest`, inline QR (`segno`), `CNAME` |
| `assets/` | Inter variable (Latin + Cyrillic, SIL OFL 1.1), home-screen icons |

## Custom domain

1. DNS: `CNAME <sub>.ideatravel.solutions → idea-denyshotsalo.github.io` (plus the `_github-pages-challenge-idea-denyshotsalo` TXT record if the domain is verified in GitHub).
2. In `people.json` set `site` to `https://<sub>.ideatravel.solutions/` and move the root card to its own slug, so the root becomes the landing page.
3. Rebuild (writes `CNAME`), PR, merge; then Settings → Pages → Enforce HTTPS once the certificate is issued.

Old `idea-denyshotsalo.github.io/card/...` links keep working: GitHub redirects them to the custom domain, path included.

Brand colours and the IDEA logo paths come from `14_CBT_PROTO/web/src/styles/tokens.css` and `web/public/brand/`. The brand display face (PP Neue Machina) is commercial and deliberately not shipped in this public repo; Inter is the brand's body face.

Colour themes live in `THEMES` in `build.py` (pass, watermark, QR, dark-mode surfaces, favicon, manifest, `assets/icon-<size>-<theme>.png`). `?theme=green` previews a card in another colour without changing it; the guide links to these previews and lets each person pick the wallet-card colour.

The page language follows the browser (`uk`/`ru` → Ukrainian, otherwise English); `?lang=en` or `?lang=uk` forces one, and the footer toggle remembers the choice.
