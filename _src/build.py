# /// script
# requires-python = ">=3.12"
# dependencies = ["segno>=1.6"]
# ///
"""Render the whole site from people.json.

Per person: <slug>/index.html, contact.vcf (UA), contact.en.vcf, manifest.webmanifest.
Site-wide: guide/index.html, a landing page at the root when no card lives there,
and CNAME when `site` is a custom domain.

Run from anywhere: `uv run _src/build.py`.
"""

import html
import json
import re
from pathlib import Path
from string import Template
from urllib.parse import quote, urlparse

import segno

SRC = Path(__file__).resolve().parent
ROOT = SRC.parent
LANGS = ("uk", "en")

# IDEA brand marks (paths from 14_CBT_PROTO/web/public/brand).
LOGO_D = "M4050.61 0H3451.66L3055.47 836.397H2493.71L2530.52 654.043H3032.86L3075.76 424.321H2573.31L2610.12 243.575H3189.11L3236.63 0H2378.89L2338.45 206.516C2256.27 83.2007 2115.98 0 1952.95 0H211.429L163.93 243.603H410.452L294.021 834.925H48.999L0 1080L1853.59 1079.89C1979.37 1079.89 2096.68 1037.05 2190.15 964.021L2167.46 1079.89H3238.87L3390.39 753.606H3827.02L3851.56 1079.89H4141L4050.61 0ZM687.949 243.603H926.591L810.296 834.925H571.518L687.949 243.603ZM3502.27 510.112L3707.48 69.0203H3776.55L3808.67 510.112H3502.27Z"
SIGN_D = "M1952.64 0H211.383L163.888 243.603H410.389L293.968 834.925H48.9674L0 1080L1853.29 1079.89C2114.52 1079.89 2320.47 904.19 2389.7 638.69C2485.42 271.8 2244.19 0 1952.64 0ZM687.834 243.603H926.455L810.171 834.925H571.414L687.834 243.603Z"

# Tabler icons (MIT).
_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{}</svg>'
ICONS = {
    "phone": '<path d="M5 4h4l2 5l-2.5 1.5a11 11 0 0 0 5 5l1.5 -2.5l5 2v4a2 2 0 0 1 -2 2a16 16 0 0 1 -15 -15a2 2 0 0 1 2 -2"/>',
    "email": '<path d="M3 7a2 2 0 0 1 2 -2h14a2 2 0 0 1 2 2v10a2 2 0 0 1 -2 2h-14a2 2 0 0 1 -2 -2v-10"/><path d="M3 7l9 6l9 -6"/>',
    "website": '<path d="M3 12a9 9 0 1 0 18 0a9 9 0 0 0 -18 0"/><path d="M3.6 9h16.8"/><path d="M3.6 15h16.8"/><path d="M11.5 3a17 17 0 0 0 0 18"/><path d="M12.5 3a17 17 0 0 1 0 18"/>',
    "linkedin": '<path d="M8 11v5"/><path d="M8 8v.01"/><path d="M12 16v-5"/><path d="M16 16v-3a2 2 0 1 0 -4 0"/><path d="M3 7a4 4 0 0 1 4 -4h10a4 4 0 0 1 4 4v10a4 4 0 0 1 -4 4h-10a4 4 0 0 1 -4 -4l0 -10"/>',
    "telegram": '<path d="M15 10l-4 4l6 6l4 -16l-18 7l4 2l2 6l3 -4"/>',
    "instagram": '<path d="M4 8a4 4 0 0 1 4 -4h8a4 4 0 0 1 4 4v8a4 4 0 0 1 -4 4h-8a4 4 0 0 1 -4 -4l0 -8"/><path d="M9 12a3 3 0 1 0 6 0a3 3 0 0 0 -6 0"/><path d="M16.5 7.5v.01"/>',
    "github": '<path d="M9 19c-4.3 1.4 -4.3 -2.5 -6 -3m12 5v-3.5c0 -1 .1 -1.4 -.5 -2c2.8 -.3 5.5 -1.4 5.5 -6a4.6 4.6 0 0 0 -1.3 -3.2a4.2 4.2 0 0 0 -.1 -3.2s-1.1 -.3 -3.5 1.3a12.3 12.3 0 0 0 -6.2 0c-2.4 -1.6 -3.5 -1.3 -3.5 -1.3a4.2 4.2 0 0 0 -.1 3.2a4.6 4.6 0 0 0 -1.3 3.2c0 4.6 2.7 5.7 5.5 6c-.6 .6 -.6 1.2 -.5 2v3.5"/>',
    "go": '<path d="M17 7l-10 10"/><path d="M8 7l9 0l0 9"/>',
    "save": '<path d="M8 7a4 4 0 1 0 8 0a4 4 0 0 0 -8 0"/><path d="M16 19h6"/><path d="M19 16v6"/><path d="M6 21v-2a4 4 0 0 1 4 -4h4"/>',
    "share": '<path d="M3 12a3 3 0 1 0 6 0a3 3 0 1 0 -6 0"/><path d="M15 6a3 3 0 1 0 6 0a3 3 0 1 0 -6 0"/><path d="M15 18a3 3 0 1 0 6 0a3 3 0 1 0 -6 0"/><path d="M8.7 10.7l6.6 -3.4"/><path d="M8.7 13.3l6.6 3.4"/>',
    "copy": '<path d="M7 9.667a2.667 2.667 0 0 1 2.667 -2.667h8.666a2.667 2.667 0 0 1 2.667 2.667v8.666a2.667 2.667 0 0 1 -2.667 2.667h-8.666a2.667 2.667 0 0 1 -2.667 -2.667l0 -8.666"/><path d="M4.012 16.737a2.005 2.005 0 0 1 -1.012 -1.737v-10c0 -1.1 .9 -2 2 -2h10c.75 0 1.158 .385 1.5 1"/>',
    "download": '<path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2 -2v-2"/><path d="M7 11l5 5l5 -5"/><path d="M12 4l0 12"/>',
    "check": '<path d="M5 12l5 5l10 -10"/>',
    "ios_share": '<path d="M12 3v12"/><path d="M8 7l4 -4l4 4"/><path d="M7 11h-1a2 2 0 0 0 -2 2v6a2 2 0 0 0 2 2h12a2 2 0 0 0 2 -2v-6a2 2 0 0 0 -2 -2h-1"/>',
}

# Row order and bilingual labels; brand names read the same in both languages.
ROWS = {
    "phone": {"uk": "Телефон", "en": "Phone"},
    "email": {"uk": "Пошта", "en": "Email"},
    "linkedin": "LinkedIn",
    "telegram": "Telegram",
    "website": {"uk": "Сайт", "en": "Website"},
    "instagram": "Instagram",
    "github": "GitHub",
}

Bilingual = str | dict[str, str]


def icon(name: str, cls: str = "") -> str:
    svg = _ICON.format(ICONS[name])
    return svg.replace("<svg ", f'<svg class="{cls}" ', 1) if cls else svg


def bi(text: Bilingual) -> str:
    """Both language variants as toggled spans; a plain string reads the same in both."""
    if isinstance(text, str) or text["uk"] == text["en"]:
        return html.escape(text if isinstance(text, str) else text["en"])
    return "".join(f'<span data-l="{lang}">{html.escape(text[lang])}</span>' for lang in LANGS)


def full_name(person: dict, lang: str) -> str:
    return f"{person['first'][lang]} {person['last'][lang]}"


def name_html(person: dict) -> str:
    """First and last name on separate lines, one wrapper per language."""

    def lines(lang: str) -> str:
        return f"<span>{html.escape(person['first'][lang])}</span> <span>{html.escape(person['last'][lang])}</span>"

    if full_name(person, "uk") == full_name(person, "en"):
        return f"<span>{lines('en')}</span>"
    return "".join(f'<span data-l="{lang}">{lines(lang)}</span>' for lang in LANGS)


def brand_svg(d: str, width: int, cls: str, label: str = "") -> str:
    a11y = f'role="img" aria-label="{label}"' if label else 'aria-hidden="true"'
    return f'<svg class="{cls}" viewBox="0 0 {width} 1080" {a11y}><path d="{d}"/></svg>'


def favicon() -> str:
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#00323c"/>'
        f'<path transform="translate(8 21.25) scale(.01991)" fill="#eb3c28" d="{SIGN_D}"/></svg>'
    )
    return "data:image/svg+xml," + quote(svg)


def font_css(prefix: str) -> str:
    latin = "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD"
    cyrillic = "U+0301, U+0400-045F, U+0490-0491, U+04B0-04B1, U+2116"
    return "".join(
        f'@font-face {{ font-family: "Inter"; font-style: normal; font-weight: 100 900; font-display: swap; '
        f'src: url("{prefix}assets/fonts/inter-{subset}-wght.woff2") format("woff2"); unicode-range: {ranges}; }}\n'
        for subset, ranges in (("latin", latin), ("cyrillic", cyrillic))
    )


def format_phone(phone: str) -> str:
    if m := re.fullmatch(r"\+380(\d{2})(\d{3})(\d{2})(\d{2})", phone):
        return "+380 " + " ".join(m.groups())
    return phone


def display_value(kind: str, value: str) -> str:
    match kind:
        case "phone":
            return format_phone(value)
        case "email":
            return value
        case "telegram" | "instagram":
            return "@" + urlparse(value).path.strip("/")
        case "linkedin":
            return urlparse(value).path.strip("/").removeprefix("in/")
        case "github":
            return urlparse(value).path.strip("/")
        case _:
            parsed = urlparse(value)
            return (parsed.netloc + parsed.path).strip("/").removeprefix("www.")


def href(kind: str, value: str) -> str:
    return {"phone": f"tel:{value}", "email": f"mailto:{value}"}.get(kind, value)


def contacts(person: dict, company: dict) -> dict[str, str]:
    found = {"phone": person.get("phone"), "email": person.get("email"), "website": company["website"], **person.get("links", {})}
    return {kind: found[kind] for kind in ROWS if found.get(kind)}


def rows_html(items: dict[str, str]) -> str:
    rows = []
    for kind, value in items.items():
        external = "" if kind in ("phone", "email") else ' target="_blank" rel="noopener"'
        shown = html.escape(display_value(kind, value))
        if kind == "email":
            shown = shown.replace("@", "@<wbr>")
        rows.append(
            f'<a class="row" href="{html.escape(href(kind, value))}"{external}>'
            f'<span class="row-ic">{icon(kind)}</span>'
            f'<span class="row-t"><span class="row-k">{bi(ROWS[kind])}</span>'
            f'<span class="row-v{" num" if kind == "phone" else ""}">{shown}</span></span>'
            f'{icon("go", "row-go")}</a>'
        )
    return "\n".join(rows)


def qr_path(url: str) -> tuple[int, str]:
    """Module grid as one SVG/Path2D path of filled runs, 4-module quiet zone included."""
    rows = [list(row) for row in segno.make(url, error="m").matrix_iter(border=4)]
    runs = []
    for y, row in enumerate(rows):
        x = 0
        while x < len(row):
            if not row[x]:
                x += 1
                continue
            start = x
            while x < len(row) and row[x]:
                x += 1
            runs.append(f"M{start} {y}h{x - start}v1h-{x - start}z")
    return len(rows), "".join(runs)


def qr_svg(url: str) -> str:
    n, d = qr_path(url)
    return (
        f'<svg viewBox="0 0 {n} {n}" shape-rendering="crispEdges" aria-hidden="true">'
        f'<rect width="{n}" height="{n}" fill="#fff"/><path fill="#00323c" d="{d}"/></svg>'
    )


def vcard_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("\n", "\\n").replace(",", "\\,").replace(";", "\\;")


def vcard(person: dict, company: dict, items: dict[str, str], lang: str) -> bytes:
    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{vcard_escape(person['last'][lang])};{vcard_escape(person['first'][lang])};;;",
        f"FN:{vcard_escape(full_name(person, lang))}",
        f"ORG:{vcard_escape(company['name'])}",
        f"TITLE:{vcard_escape(person['title'][lang])}",
    ]
    if phone := items.get("phone"):
        lines.append(f"TEL;TYPE=CELL:{phone}")
    if email := items.get("email"):
        lines.append(f"EMAIL;TYPE=INTERNET:{email}")
    lines += [f"URL:{value}" for kind, value in items.items() if kind not in ("phone", "email")]
    if city := person.get("city"):
        lines.append(f"ADR;TYPE=WORK:;;;{vcard_escape(city[lang])};;;")
    if bio := person.get("bio"):
        lines.append(f"NOTE:{vcard_escape(bio[lang])}")
    lines.append("END:VCARD")
    return ("\r\n".join(lines) + "\r\n").encode()


def manifest(person: dict, company: dict, prefix: str) -> str:
    icons = [
        {"src": f"{prefix}assets/icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": f"{prefix}assets/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
    ]
    body = {
        "name": f"{full_name(person, 'uk')} — {company['name']}",
        "short_name": "Візитка IDEA",
        "start_url": "./",
        "scope": "./",
        "display": "browser",
        "background_color": "#e1dcd5",
        "theme_color": "#00323c",
        "icons": icons,
    }
    return json.dumps(body, ensure_ascii=False, indent=2) + "\n"


def person_id(person: dict) -> str:
    return person["slug"] or "home"


def person_url(person: dict, site: str) -> str:
    return site + (f"{person['slug']}/" if person["slug"] else "")


def render_card(person: dict, data: dict, template: Template, parts: dict[str, str]) -> str:
    company = data["company"]
    url = person_url(person, data["site"])
    name = {lang: full_name(person, lang) for lang in LANGS}
    title = person["title"]
    role = f"{title['uk']} · {title['en']}" if title["uk"] != title["en"] else title["en"]
    bio = f'<p class="bio">{bi(person["bio"])}</p>\n' if person.get("bio") else ""
    prefix = "../" if person["slug"] else ""
    return template.substitute(
        parts,
        title_uk=html.escape(f"{name['uk']} — {company['name']}"),
        title_en=html.escape(f"{name['en']} — {company['name']}"),
        og_title=html.escape(f"{name['uk']} · {name['en']}" if name["uk"] != name["en"] else name["en"]),
        description=html.escape(f"{role} · {company['name']}"),
        url=url,
        assets=prefix,
        font_css=font_css(prefix),
        company=html.escape(company["name"]),
        website=company["website"],
        name=name_html(person),
        role=bi(title),
        city=bi(person.get("city", "")),
        bio=bio,
        rows=rows_html(contacts(person, company)),
        qr=qr_svg(url),
        tagline=bi(company["tagline"]),
    )


def render_guide(data: dict, template: Template, parts: dict[str, str]) -> str:
    company = data["company"]
    people = []
    for person in data["people"]:
        url = person_url(person, data["site"])
        n, d = qr_path(url)
        gn, gd = qr_path(f"{data['site']}guide/?p={person_id(person)}")
        people.append({
            "id": person_id(person),
            "url": url,
            "first": person["first"],
            "last": person["last"],
            "title": person["title"],
            "qr": {"n": n, "d": d},
            "guideQr": {"n": gn, "d": gd},
        })
    payload = {"company": company["name"], "brand": {"logo": LOGO_D, "sign": SIGN_D}, "people": people}
    options = "".join(f'<option value="{person_id(p)}">{html.escape(full_name(p, "uk"))}</option>' for p in data["people"])
    return template.substitute(
        parts,
        assets="../",
        font_css=font_css("../"),
        company=html.escape(company["name"]),
        website=company["website"],
        contact_name=html.escape(company["contact"]["name"]),
        contact_tg=company["contact"]["telegram"],
        options=options,
        data_json=json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"),
    )


def render_landing(data: dict, template: Template, parts: dict[str, str]) -> str:
    company = data["company"]
    return template.substitute(
        parts,
        font_css=font_css(""),
        company=html.escape(company["name"]),
        website=company["website"],
        tagline=bi(company["tagline"]),
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    data = json.loads((SRC / "people.json").read_text(encoding="utf-8"))
    company = data["company"]

    def read(name: str) -> str:
        return (SRC / name).read_text(encoding="utf-8")

    base, card_css = read("base.css"), read("card.css")
    shared = {
        "favicon": favicon(),
        "logo": brand_svg(LOGO_D, 4141, "pass-logo", "IDEA"),
        "mark": brand_svg(SIGN_D, 2411, "pass-mark"),
        "sign": brand_svg(SIGN_D, 2411, "foot-sign"),
        "lang_js": read("lang.js").strip(),
        "js": read("card.js").strip(),
    }
    card_parts = {**shared, "css": base + card_css, "icon_save": icon("save"), "icon_share": icon("share")}
    card_tpl = Template(read("card.html"))

    for person in data["people"]:
        out = ROOT / person["slug"]
        items = contacts(person, company)
        write(out / "index.html", render_card(person, data, card_tpl, card_parts))
        write(out / "manifest.webmanifest", manifest(person, company, "../" if person["slug"] else ""))
        (out / "contact.vcf").write_bytes(vcard(person, company, items, "uk"))
        (out / "contact.en.vcf").write_bytes(vcard(person, company, items, "en"))
        print(f"built {person['slug'] or '(root)'}")

    guide_parts = {
        **shared,
        "css": base + card_css + read("guide.css"),
        "js": read("guide.js").strip(),
        **{f"icon_{name}": icon(name) for name in ("go", "copy", "download", "check", "ios_share")},
    }
    write(ROOT / "guide" / "index.html", render_guide(data, Template(read("guide.html")), guide_parts))
    print("built guide")

    if not any(p["slug"] == "" for p in data["people"]):
        write(ROOT / "index.html", render_landing(data, Template(read("landing.html")), {**shared, "css": base + card_css}))
        print("built landing")

    host = urlparse(data["site"]).hostname
    if not host.endswith(".github.io"):
        write(ROOT / "CNAME", host + "\n")
        print(f"CNAME {host}")


if __name__ == "__main__":
    main()
