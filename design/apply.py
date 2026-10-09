#!/usr/bin/env python3
"""Apply the PDX FUSION design to the running site.

    python3 design/apply.py

What it does (the site is briefly stopped, because Gancio reads its settings at startup):
  1. builds the custom CSS from design/functional.css + design/theme.css (+ the font, embedded)
  2. sets the custom JavaScript from design/functional.js
  3. sets the light and dark color palettes below (dark is the fallback; functional.js follows the device setting)
  4. sets the basic site settings below (name, timezone, recurring events, moderation, federation off) and, only if the site
     has no About text yet, the first draft in design/about.html (so edits made in the site are never overwritten)
  5. writes our wording changes (design/make_locale.py)
  6. writes them into Gancio's settings and starts the site again

Works the same on a brand-new site (start it once first: `docker-compose up -d`) and on this Mac.
On the server, run it with COMPOSE_FILE=docker-compose.prod.yml set (see DEPLOY.md).

Edit the files in design/, then run this again. Nothing here changes Gancio's code.
"""
import base64
import datetime
import json
import shutil
import sqlite3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DESIGN = ROOT / "design"
DB = ROOT / "data" / "gancio.sqlite"
# older installs have `docker-compose`, newer ones `docker compose`
COMPOSE = ["docker-compose"] if shutil.which("docker-compose") else ["docker", "compose"]

# Small, soft, warm palette. All text colors have a contrast ratio of at least 5.7:1 on their background.
PALETTE = {
    "light_colors": {
        "background": "#FBF7F0",   # warm paper
        "surface": "#FFFFFF",
        "on-background": "#2A2521",
        "on-surface": "#2A2521",
        "primary": "#A83F27",      # terracotta
        "secondary": "#3F6B58",    # sage
        "error": "#B3261E",
        "info": "#25627F",
        "success": "#2A6B45",
        "warning": "#8A5200",
    },
    "dark_colors": {
        "background": "#1C1A18",   # warm charcoal
        "surface": "#282523",
        "on-background": "#F1EBE3",
        "on-surface": "#F1EBE3",
        "primary": "#F29A7A",      # soft peach
        "secondary": "#9CC5AD",    # soft sage
        "error": "#FF8A80",
        "info": "#8CC4E3",
        "success": "#8FD0A4",
        "warning": "#F0B35C",
    },
}


# Basic settings of the site (Gancio's defaults would be: Rome timezone, no recurring events, no moderation)
SITE = {
    "title": "PDX FUSION DANCE",
    "description": "a community calendar for Portland's fusion dance scene",
    "instance_timezone": "America/Los_Angeles",
    "allow_recurrent_event": True,
    "enable_moderation": True,
    "recurrent_event_visible": True,
    "enable_federation": False,   # no Mastodon / fediverse
    "allow_online_event": True,    # this is the 'Invite / RSVP link' field of the add-event form
    "allow_geolocation": True,     # address suggestions while typing (also a map on the event page)
    "allow_event_without_end_time": False,  # an end time is required (the live site's choice)
    "show_download_media": False,           # visitors cannot download flyers (the live site's choice)
    "enable_report": True,                  # "Report event" button; reports email the admins (the live site's choice)
    "footerLinks": [      # Gancio's footer; /about and home first, then the public source code (AGPL-3.0)
        {"href": "/", "label": "common.home"},
        {"href": "/about", "label": "common.about"},
        {"href": "https://github.com/clyobuilds/gancio-pdxfusion", "label": "Source code"},
    ],
    "geocoding_provider": "https://photon.komoot.io/api/",   # Photon: made for search-as-you-type (public Nominatim forbids it)
}


def font_faces() -> str:
    faces = []
    for weight in (400, 700):
        data = base64.b64encode((DESIGN / "fonts" / f"atkinson-next-{weight}.woff2").read_bytes()).decode()
        faces.append(
            "@font-face { font-family: 'Atkinson Hyperlegible'; font-style: normal; "
            f"font-weight: {weight}; font-display: swap; "
            f"src: url(data:font/woff2;base64,{data}) format('woff2'); }}"
        )
    return "/* Atkinson Hyperlegible Next (Braille Institute / Applied Design Works), SIL Open Font License, see design/fonts/OFL-license.txt */\n" + "\n".join(faces)


def header_image() -> str:
    """The site name picture (made by design/make_header.py), as a data address for the CSS."""
    data = base64.b64encode((DESIGN / "header-title.webp").read_bytes()).decode()
    return f"data:image/webp;base64,{data}"


def header_aspect() -> str:
    """Width / height of the site name picture (written by design/make_header.py)."""
    return (DESIGN / "header-title.aspect").read_text().strip()


def main():
    if not DB.exists():
        raise SystemExit("No database yet. Start the site once first (docker-compose up -d), then run this again.")
    css = (DESIGN / "functional.css").read_text() + "\n" + (DESIGN / "theme.css").read_text().replace("/*FONTS*/", font_faces()).replace("/*HEADER_IMAGE*/", header_image()).replace("/*HEADER_ASPECT*/", header_aspect())
    settings = {
        "custom_css": css,
        "custom_js": (DESIGN / "functional.js").read_text(),
        "theme.is_dark": True,   # dark when the device setting is unknown (see functional.js)
        **SITE,
        **PALETTE,
    }
    defaults = {"about": (DESIGN / "about.html").read_text()}  # only set when missing

    subprocess.run(["python3", str(DESIGN / "make_locale.py")], check=True)
    subprocess.run([*COMPOSE, "stop", "gancio"], cwd=ROOT, check=True)
    try:
        now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S.000 +00:00")
        db = sqlite3.connect(DB)
        for key, value in settings.items():
            db.execute(
                "insert into settings(key,value,is_secret,createdAt,updatedAt) values(?,?,0,?,?) "
                "on conflict(key) do update set value=excluded.value, updatedAt=excluded.updatedAt",
                (key, json.dumps(value), now, now),
            )
        for key, value in defaults.items():
            db.execute(
                "insert or ignore into settings(key,value,is_secret,createdAt,updatedAt) values(?,?,0,?,?)",
                (key, json.dumps(value), now, now),
            )
        db.commit()
        db.close()
    finally:
        subprocess.run([*COMPOSE, "up", "-d"], cwd=ROOT, check=True)
    print("Design applied. Hard-refresh the browser (Cmd+Shift+R).")


if __name__ == "__main__":
    main()
