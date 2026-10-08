# Where things stand (updated 2026-10-08)

Read this first when picking the project up again. Background and reasons are in `DECISIONS.md` (newest at the bottom);
how to run, deploy and test are in `README.md`, `DEPLOY.md`, `QA-CHECKLIST.md`.

## Two copies of the site
- **Local:** http://localhost:13120 (`colima start`, then `docker-compose up -d`). Try changes here first.
- **Live (test domain):** https://pdx.hmu.click, on a small Linux server. Final domain is not chosen yet.
- The live site only changes when someone deploys on purpose (see "Deploying" below). Local and live are the same code today.

## Where the code is
- `gancio-src/` is Gancio plus our changes, in its own git repository. The `pdxfusion` branch is the one that gets built and deployed;
  every feature branch so far is merged into it. Commit there, never leave work uncommitted.
- Everything else (look, wording, deploy files, docs) is in this folder's own git repository (`design/`, `docker-compose*.yml`, ...).
- Commits are authored as `clyobuilds <...@users.noreply.github.com>` (set per repository). Check `git log` shows nothing else before publishing.

## Deploying (only when asked)
Back up first, then sync the files, rebuild on the server, restart, apply the design/settings, and run the audit:
1. `./backup.sh` on the server; copy the archive to this Mac.
2. `rsync` the project to the server (excludes in `DEPLOY.md` step 4, plus `gancio-src/.git` and `.git`).
3. On the server: `docker compose build` (takes ~5-10 minutes on the 1 GB server), `docker compose up -d`, `python3 design/apply.py`, `chown -R 1000:1000 data`.
4. On this Mac: `python3 design/audit.py https://pdx.hmu.click`. Two differences are expected and known (see below).
Design-only changes (CSS, wording, `design/`) need just the rsync of `design/` and `apply.py`; no rebuild.
Changes to `gancio-src/` need the rebuild. The server address and login are not stored in this repository.

## Open items
- **Final domain** - not chosen. Then: point DNS at the server, change `DOMAIN`/`BASEURL` in the server's `.env` (see `DEPLOY.md`).
- **Email** - set up a mailbox for the domain, then (a) Admin -> E-mail (SMTP) so approval and reset emails send, (b) replace the placeholder
  `feedback@pdxfusion.example` in the About page (edit it as admin, and in `design/about.html`).
- **Publish the code** - AGPL-3.0 requires it. Plan: GitHub account `clyobuilds`, two public repositories (site files; Gancio source with our changes,
  linked as a submodule), a footer "Source code" link, `CONTRIBUTING.md` is written. Waiting for the final domain. Not published yet.
- **Event types on old events** - events created before the Event type field have none; they only show under "All" until edited.
- **Inspire Fusion** (live, Oct 17) was created by mistake as a weekly series (25 extra dates). Fix: edit the series and set "Ends on a date" to Oct 17,
  or copy it as a single event and remove the series. Waiting on the owner's decision.
- **Two live settings differ from local** (`allow_event_without_end_time`, `show_download_media`; live = off, local = Gancio default on). Decide which is wanted.
- **Report to the Gancio project** (also in `UPSTREAM.md`): searching events with both a text query and a result limit (`max`) fails with a server error.
- **Ideas not built:** keeping the flyer when copying an event; showing the cost on cards; per-device "going" lists beyond favorites.

## Known behaviors worth remembering
- Repeating events are created 4 months ahead; a skipped date stays skipped; "Remove" under "Recurring event actions" deletes the whole series.
- Favorites are stored in the visitor's browser only.
- Days in the calendar are cut in the visitor's own time zone (Gancio behavior).

## Running Gancio's tests (before deploying a source change)
Copy `gancio-src/` (without `node_modules`) to a scratch folder under your home folder, then:
    docker run --rm -v "$PWD:/app" -w /app node:24-alpine sh -c "apk add --no-cache git coreutils jq; corepack enable; pnpm install --frozen-lockfile; npx vitest run"
Run the whole suite (`npx vitest run`), not one file: the unit tests rely on the API part to create the test database. Last result: 186 passed.
Browser checks: `design/shoot.sh` and `design/phonecheck.sh` run a headless browser in Docker; scripts must live under your home folder (the Docker VM only sees it)
and reach the local site at `http://gancio:13120` on the `pdx-fusion_default` network.
