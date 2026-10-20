# Architecture

How `_src/people.json` becomes the pages people scan, and how those pages reach the internet.

## Build

`_src/build.py` is one script with inline dependencies (PEP 723, only `segno`), so `uv run _src/build.py` installs
them on the fly. It reads `_src/people.json` and writes next to `_src/`:

| Output | When |
|---|---|
| `<slug>/index.html` | Per person. CSS, JS, logos and the QR SVG are inlined; fonts and icons come from `assets/` |
| `<slug>/contact.vcf`, `<slug>/contact.en.vcf` | Per person. vCard 3.0 with CRLF line endings, Ukrainian and English values |
| `<slug>/manifest.webmanifest` | Per person. Home-screen name "Візитка IDEA", theme colour, icons |
| `guide/index.html` | Always. Carries every person's URL, names, title, theme and QR paths as embedded JSON |
| `index.html` (landing) | Only when no person has `slug: ""` |
| `CNAME` | Only when `site` is not a `*.github.io` URL |

The QR code is drawn from `segno`'s module matrix (error correction M, 4-module quiet zone) as one SVG path, so the
guide can redraw the same code on a canvas. `.gitattributes` marks `*.vcf` as `-text`, so Git never rewrites the
CRLF.

## Sources

| Path | What |
|---|---|
| `_src/people.json` | All card data; `_src/person.example.json` is a filled-in entry to copy |
| `_src/base.css` | Brand tokens shared by every page, light and dark |
| `_src/card.html`, `card.css`, `card.js` | Card template and components; language toggle, full-screen QR, share |
| `_src/prepaint.js` | Runs before the first paint: picks the language and applies a `?theme=` preview |
| `_src/guide.html`, `guide.css`, `guide.js` | Interactive guide, including the canvas that draws the wallet image |
| `_src/landing.html` | Root page for the custom domain |
| `assets/` | Inter variable (Latin and Cyrillic subsets, SIL OFL 1.1), home-screen icons per theme |
| `scripts/` | Demo data, demo build (`demo_site.py`) and README screenshots (`screenshots.py`) |

## Themes

`THEMES` in `build.py` is the only place a colour lives. Each theme sets the pass colour, the monogram watermark,
the QR modules and the dark-mode surfaces. The build turns it into CSS, the favicon, the manifest `theme_color` and
the icon names `assets/icon-<size>-<theme>.png`. A person's theme is `people[].theme`, then `company.theme`, then the
first entry of `THEMES`.

Brand colours and the IDEA logo paths come from `14_CBT_PROTO/web/src/styles/tokens.css` and `web/public/brand/`.

## Language

Every bilingual string is rendered twice, as `<span data-l="uk">` and `<span data-l="en">`, and CSS hides the one
that does not match `<html data-lang>`. `prepaint.js` sets `data-lang` before the first paint: `?lang=` first, then
the footer toggle's earlier choice from `localStorage`, then the browser languages (`uk` and `ru` mean Ukrainian).
The Ukrainian page links `contact.vcf`, the English one `contact.en.vcf`.

## Publishing

`.github/workflows/publish.yml` runs on every push to `main`:

1. checks out this repo;
2. copies `assets/`, `guide/`, the root files and every top-level folder that holds an `index.html` into `public/`,
   so `_src/`, `scripts/` and `docs/` never leave;
3. pushes `public/` to `idea-denyshotsalo/team` as one orphan commit with `peaceiris/actions-gh-pages` (pinned to a
   commit SHA), using the `TEAM_DEPLOY_KEY` secret, a write deploy key on `team`.

So `team` never carries history, sources or `people.json`. Until the switch below, this repo's own GitHub Pages
(branch `main`, root) serves the same pages at `idea-denyshotsalo.github.io/card/`.

A merge that changes `.github/workflows/*`, made with a token that lacks the `workflow` scope, goes through, but
GitHub silently starts no run for it. The next merge, or a manual re-run, publishes.

## Custom domain

Planned address: `team.ideatravel.solutions`, served from `team`.

1. DNS: `CNAME team.ideatravel.solutions → idea-denyshotsalo.github.io`, plus the TXT record
   `_github-pages-challenge-idea-denyshotsalo.team.ideatravel.solutions` that GitHub shows for the verified domain.
   Then press **Verify** in the account's Pages settings.
2. In `people.json`, set `site` to `https://team.ideatravel.solutions/` and move the root card to its own slug, so
   the root becomes the landing page.
3. Rebuild (this writes `CNAME`), PR, merge. The workflow ships `CNAME` to `team`; turn on **Enforce HTTPS** there
   once GitHub issues the certificate.
4. Make this repo private. Its own Pages stop, and `idea-denyshotsalo.github.io/card/...` links stop with them, so
   hand out links and QR codes only after the switch.
