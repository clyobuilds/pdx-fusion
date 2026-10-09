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
Done (2026-10-09): domain moved to https://pdxfusiondance.com (HTTPS by Caddy); email (hello@ via Namecheap Private Email, SMTP
working); backup cron on the server (03:15 UTC) plus a daily copy to the Mac (launchd, 09:30 local, `~/pdxfusion-live-backups/`);
code published (github.com/clyobuilds/pdx-fusion and /gancio-pdxfusion, AGPL source link in the footer); INDEXING=index (launch).

Still open:
1. **www** - add a DNS CNAME `www` -> `pdxfusiondance.com.` at Namecheap. Caddy then redirects www to the bare domain (already in the Caddyfile).
2. **Search Console + Bing Webmaster Tools** - verify the domain (DNS TXT record, done by the owner) and submit `/sitemap.xml`.
3. **Three live settings differ from local** (`design/audit.py`): `allow_event_without_end_time`, `show_download_media`, `enable_report` (live on). Decide which is wanted.
4. **Admin notifications** - add each new admin/editor with Notify ticked; hello@ mail reaches people only through Namecheap forwarding (manual).
5. **Inspire Fusion** (weekly series by mistake) - waiting on the owner's decision.

## Planned: new ways to log in (not started, nothing built)
Decided to plan these before building. Build the first one only when the user says so.
1. **Email code login (first):** a 6-digit code emailed to the user, entered on `/login`; no password needed. Expires in about 15 minutes,
   one use only, rate limited. Passwords stay as a fallback until everyone has used the email code once. Difficulty: moderate, about a day
   with testing. Reuses the existing mail setup (hello@) and the password-reset pattern (`recover_code`).
2. **Passkeys (fingerprint, face or device PIN), later:** feasible with a standard library; moderate to high difficulty. A passkey is tied to the
   domain name, so if the domain changes, passkeys must be set up again. Users still need the email code as their way back in.
3. **Bluesky sign-in (optional, later):** feasible, moderate to high difficulty. Bluesky uses OAuth (PKCE, PAR, DPoP). Needs a client
   metadata document published at a public URL on our domain, and a maintained OAuth library rather than custom code. The Bluesky guide:
   https://docs.bsky.app/docs/advanced-guides/oauth-client

Adding an admin today: Admin -> Users -> new user (email, role admin). They get a "user_confirm" email with a link to choose a password,
then log in at /login. (Test once with a real address before relying on it.)

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
