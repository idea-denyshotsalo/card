# /// script
# requires-python = ">=3.12"
# dependencies = ["segno>=1.6"]
# ///
"""Render every card in people.json into <slug>/index.html + <slug>/contact.vcf.

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
    return "".join(f'<span data-l="{lang}">{html.escape(text[lang])}</span>' for lang in ("uk", "en"))


def brand_svg(d: str, width: int, cls: str, label: str = "") -> str:
    a11y = f'role="img" aria-label="{label}"' if label else 'aria-hidden="true"'
    return f'<svg class="{cls}" viewBox="0 0 {width} 1080" {a11y}><path d="{d}"/></svg>'


def favicon() -> str:
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#00323c"/>'
        f'<path transform="translate(8 21.25) scale(.01991)" fill="#eb3c28" d="{SIGN_D}"/></svg>'
    )
    return "data:image/svg+xml," + quote(svg)


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


def qr_svg(url: str) -> str:
    svg = segno.make(url, error="m").svg_inline(dark="#00323c", light="#fff", border=4, omitsize=True)
    return svg.replace("<svg ", '<svg aria-hidden="true" ', 1)


def vcard_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("\n", "\\n").replace(",", "\\,").replace(";", "\\;")


def vcard(person: dict, company: dict, items: dict[str, str]) -> bytes:
    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{vcard_escape(person['last'])};{vcard_escape(person['first'])};;;",
        f"FN:{vcard_escape(person['first'] + ' ' + person['last'])}",
        f"ORG:{vcard_escape(company['name'])}",
        f"TITLE:{vcard_escape(person['title']['en'])}",
    ]
    if phone := items.get("phone"):
        lines.append(f"TEL;TYPE=CELL:{phone}")
    if email := items.get("email"):
        lines.append(f"EMAIL;TYPE=INTERNET:{email}")
    lines += [f"URL:{value}" for kind, value in items.items() if kind not in ("phone", "email")]
    if city := person.get("city"):
        lines.append(f"ADR;TYPE=WORK:;;;{vcard_escape(city['uk'])};;;")
    if bio := person.get("bio"):
        lines.append(f"NOTE:{vcard_escape(bio['uk'])}")
    lines.append("END:VCARD")
    return ("\r\n".join(lines) + "\r\n").encode()


def render(person: dict, data: dict, template: Template, parts: dict[str, str]) -> str:
    company = data["company"]
    slug = person["slug"]
    url = data["site"] + (f"{slug}/" if slug else "")
    full_name = f"{person['first']} {person['last']}"
    bio = f'<p class="bio">{bi(person["bio"])}</p>\n' if person.get("bio") else ""
    return template.substitute(
        parts,
        title=html.escape(f"{full_name} — {company['name']}"),
        description=html.escape(f"{person['title']['en']} · {company['name']}"),
        full_name=html.escape(full_name),
        url=url,
        assets="../" if slug else "",
        company=html.escape(company["name"]),
        first=html.escape(person["first"]),
        last=html.escape(person["last"]),
        role=bi(person["title"]),
        city=bi(person.get("city", "")),
        bio=bio,
        rows=rows_html(contacts(person, company)),
        qr=qr_svg(url),
        tagline=bi(company["tagline"]),
    )


def main() -> None:
    data = json.loads((SRC / "people.json").read_text(encoding="utf-8"))
    template = Template((SRC / "card.html").read_text(encoding="utf-8"))
    parts = {
        "css": (SRC / "card.css").read_text(encoding="utf-8"),
        "lang_js": (SRC / "lang.js").read_text(encoding="utf-8").strip(),
        "js": (SRC / "card.js").read_text(encoding="utf-8").strip(),
        "favicon": favicon(),
        "logo": brand_svg(LOGO_D, 4141, "pass-logo", "IDEA"),
        "mark": brand_svg(SIGN_D, 2411, "pass-mark"),
        "sign": brand_svg(SIGN_D, 2411, "foot-sign"),
        "icon_save": icon("save"),
        "icon_share": icon("share"),
    }
    for person in data["people"]:
        out = ROOT / person["slug"]
        out.mkdir(exist_ok=True)
        (out / "index.html").write_text(render(person, data, template, parts), encoding="utf-8", newline="\n")
        (out / "contact.vcf").write_bytes(vcard(person, data["company"], contacts(person, data["company"])))
        print(f"built {person['slug'] or '(root)'}")


if __name__ == "__main__":
    main()
