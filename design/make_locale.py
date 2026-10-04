#!/usr/bin/env python3
"""Write data/user_locale/en.json: our wording changes, on top of Gancio's own English text.

Gancio replaces whole sections of its text with what is in this file, so it holds full copies of the
`event`, `login` and `common` sections with our edits. Run it again after updating Gancio
(apply.py does it for you), so that new Gancio text does not show up as raw keys.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "gancio-src" / "i18n" / "locales" / "en.json"
TARGET = ROOT / "data" / "user_locale" / "en.json"

EDITS = {
    "event": {
        "online_locations": "Invite / RSVP link",
        "online_locations_help": "Facebook event, Partiful, or other invite link (optional, up to 3)",
        # visitors have no accounts, so no "log in or register" links
        "anon_description": "Anybody can submit an event to be added. An event organizer will review it before it appears, as soon as possible. You won't be able to edit it after submitting it.",
    },
    "login": {"not_registered": "Register"},
    "common": {"where": "Venue name", "send": "Submit"},
}

en = json.loads(SOURCE.read_text())
out = {section: {**en[section], **edits} for section, edits in EDITS.items()}
TARGET.parent.mkdir(parents=True, exist_ok=True)
TARGET.write_text(json.dumps(out, indent=2))
print(f"Wrote {TARGET.relative_to(ROOT)}")
