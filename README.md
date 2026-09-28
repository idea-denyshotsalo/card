# IDEA digital business cards

Static business-card pages for IDEA Travel Solutions staff, served by GitHub Pages:

- https://idea-denyshotsalo.github.io/card/ — Denys Hotsalo
- https://idea-denyshotsalo.github.io/card/alyona-shalahinova/ — Alyona Shalahinova

Each page shows the contact rows, a "Save contact" button (`contact.vcf`) and a QR code that points back to the page itself. Printed QR codes and wallet passes encode only the page URL, so contact details can change without reprinting.

## Add or edit a person

1. Edit `_src/people.json`. `slug` is the folder name and URL path (`""` = site root). `title`, `bio`, `city` take `uk` and `en` variants; `bio` and every entry in `links` are optional (`linkedin`, `telegram`, `instagram`, `github`).
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
| `_src/card.html`, `card.css`, `card.js`, `lang.js` | Page template, styles, behaviour, pre-paint language pick |
| `_src/build.py` | Renders pages, vCards (CRLF, RFC 2426) and inline QR codes (`segno`) |
| `assets/fonts/` | Inter variable, Latin + Cyrillic subsets, SIL OFL 1.1 |

Brand colours and the IDEA logo paths come from `14_CBT_PROTO/web/src/styles/tokens.css` and `web/public/brand/`. The brand display face (PP Neue Machina) is commercial and deliberately not shipped in this public repo; Inter is the brand's body face.

The page language follows the browser (`uk`/`ru` → Ukrainian, otherwise English); `?lang=en` or `?lang=uk` forces one, and the footer toggle remembers the choice.
