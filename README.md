# PDX Fusion

A community calendar for Portland's fusion dance scene, live at https://pdx.hmu.click (temporary address).
It is a customized copy of [Gancio](https://gancio.org), an open-source events calendar.

- **This repository:** the look and feel, wording, deploy files and documentation (`design/`, `docker-compose*.yml`, `DEPLOY.md`, ...).
- **Gancio source with our changes:** the `gancio-src/` folder (a separate repository, linked here as a submodule).
  Clone everything with `git clone --recurse-submodules <this repo's URL>`.
- **License:** AGPL-3.0 (see `LICENSE`), the same as Gancio. Anyone who uses the site can get its source.
- **Want to help?** See `CONTRIBUTING.md`.

---

# PDX Fusion — local site

Everything lives in this folder. Run commands from here:
`cd ~/Claude-Workspace/pdx-fusion`

## Start
    colima start                                # starts the hidden Linux VM (first, after every reboot)
    docker-compose up -d                        # starts Gancio
Then open http://localhost:13120

## Stop
    docker-compose down      # stops Gancio (data is kept)
    colima stop              # optional: stops the VM, frees memory

## See what's happening / restart
    docker-compose logs -f   # live log (Ctrl+C to leave)
    docker-compose restart

## Where things live
- `data/gancio.sqlite` — the database (events, users, settings)
- `data/uploads/` — flyers and images
- `.env` — config + a secret key (private; not for sharing or git)
- `docker-compose.yml` — how Gancio is launched
- `gancio-src/` — Gancio's source code, with our small fixes on separate git branches

## Back up (stop first so the database is consistent)
    docker-compose down
    tar czf ~/pdxfusion-backup-$(date +%F).tar.gz data .env docker-compose.yml
    docker-compose up -d
To restore: unpack the tarball into an empty project folder and start.

## Update Gancio
The site runs a copy of Gancio built from `gancio-src/` (official code plus a few small fixes).
Back up first, then follow "Updating Gancio later" in `UPSTREAM.md`.

## Rebuild after a code change
    docker-compose build      # takes several minutes
    docker-compose up -d

## Other files
- `DECISIONS.md` — what was configured or changed, and why
- `UPSTREAM.md` — the source changes and how to offer them to the Gancio project
- `QA-CHECKLIST.md` — steps to test the site
- `DEPLOY.md` — how to put the site online and keep it running
- `Dockerfile.gancio` — build recipe (Gancio's own, minus one flag our Docker can't read)

## Look and feel (design)
Styling and wording live in `design/` (changes to Gancio's own code are in `gancio-src/`, see `UPSTREAM.md`):
- `design/theme.css` — looks: font, rounded shapes, spacing, wavy divider, hover motion
- `design/functional.css` / `design/functional.js` — layout and behavior fixes (narrow add form, no hover labels on touch screens, etc.)
- `design/apply.py` — colors (the PALETTE at the top) and the step that installs everything

After editing any of those, apply it (briefly restarts the site), then hard-refresh your browser:
    python3 design/apply.py
To see the site as a phone/desktop in light/dark (needs the site running; saves pictures to `design/screenshots/`):
    design/shoot.sh my-label

## Going live
See `DEPLOY.md` (server setup, domain, HTTPS, first admin, backups, updating). Files for it:
`docker-compose.prod.yml`, `Caddyfile`, `.env.prod.example`, `backup.sh`.
