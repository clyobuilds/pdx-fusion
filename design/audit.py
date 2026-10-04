#!/usr/bin/env python3
"""Compare a live site with this Mac's site: which settings and wording differ?

    python3 design/audit.py https://pdx.hmu.click

Run it after every deploy. Anything listed under "MISSING" or "DIFFERENT" is a regression to look at.
(Local site must be running: docker-compose up -d.) Checks settings that are visible through the public API.
"""
import json
import sys
import urllib.request

LIVE = (sys.argv[1] if len(sys.argv) > 1 else "").rstrip("/")
LOCAL = "http://localhost:13120"
if not LIVE:
    raise SystemExit("usage: python3 design/audit.py https://your-site")

IGNORE = {"baseurl", "hostname", "version", "admin_email", "allow_registration"}  # expected to differ
# what should be on every site, whatever its content
DESIGN_KEYS = ["light_colors", "dark_colors"]
WORDING = [("common", "where"), ("event", "online_locations"), ("login", "not_registered"), ("common", "send"), ("event", "recurrent_until"), ("common", "today")]


def get(url):
    return json.load(urllib.request.urlopen(url, timeout=30))


live, local = get(LIVE + "/api/settings"), get(LOCAL + "/api/settings")
problems = 0

print("== DESIGN (CSS, JavaScript, colors)")
def text(url):
    return urllib.request.urlopen(url, timeout=30).read().decode()
for name, path in (("custom CSS", "/custom_css"), ("custom JavaScript", "/custom_js")):
    a, b = text(LOCAL + path), text(LIVE + path)
    same = a == b
    state = "ok       " if same else ("MISSING  " if "no custom" in b else "DIFFERENT")
    print(f"  {state} {name}: this Mac = {len(a)} bytes, live = {len(b)} bytes")
    problems += not same
for k in ("light_colors", "dark_colors"):
    same = live.get(k) == local.get(k)
    print(f"  {'ok       ' if same else 'MISSING  '} {k}")
    problems += not same

print("== SETTINGS")
for k in sorted((set(live) | set(local)) - IGNORE - set(DESIGN_KEYS)):
    a, b = local.get(k), live.get(k)
    if a != b:
        problems += 1
        print(f"  DIFFERENT {k}: this Mac = {json.dumps(a)[:50]}   live = {json.dumps(b)[:50]}")

print("== WORDING")
l1, l2 = get(LOCAL + "/api/locale/en"), get(LIVE + "/api/locale/en")
for sec, key in WORDING:
    a, b = l1[sec].get(key), l2[sec].get(key)
    ok = a == b
    problems += not ok
    print(f"  {'ok       ' if ok else 'DIFFERENT'} {sec}.{key}: this Mac = {a!r}   live = {b!r}")

print()
print("No differences." if not problems else f"{problems} difference(s). Run `python3 design/apply.py` on the server, then re-run this.")
