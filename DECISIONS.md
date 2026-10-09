# Decisions

## Phase 1
- **Runtime:** Colima + docker CLI + docker-compose via Homebrew (approved). Chose the
  standalone `docker-compose` command so we didn't have to edit ~/.docker/config.json.
- **Image:** `cisti/gancio:beta` (Gancio 2.0 beta, native arm64). `latest` is an old
  1.x amd64-only image; the official docs now point to `beta`. Revisit pinning a
  specific version before going public.
- **Port bound to 127.0.0.1 only**, so nothing on the network can reach it yet.
- **Data:** one `./data` folder (sqlite DB, uploads, logs); config in `.env`.
- **Not yet done:** admin account + settings (done in Gancio's web UI; see below).

## Phase 1 corrections (after first browser test)
- Gancio 2.0 beta has **no setup wizard**. The first account registered becomes admin.
  Registration must stay ON until that account exists, then be turned OFF in Admin → Settings.
- Written directly into the settings table (Gancio stores settings there): timezone
  America/Los_Angeles (default was Europe/Rome), recurrent events ON, moderation ON.
- **Invite link:** Gancio's "online locations" field is its RSVP/invite-URL field. Kept it
  and relabeled it via `data/user_locale/en.json` ("Invite / RSVP link"). No source change.
- **Narrow add page:** custom CSS setting (max-width 640px), not source.
- Still unset: site title/subtitle (waiting on exact wording).

## Round 2 fixes
- **Gotcha:** `user_locale` overrides replace a *whole top-level section* (e.g. all of `event`),
  not single strings. `data/user_locale/en.json` therefore holds full copies of `event` and
  `login` with our edits. When updating Gancio, re-copy those sections from
  `gancio-src/i18n/locales/en.json` so new strings don't show as raw keys.
- Title "PDX Fusion" and subtitle set via settings. "Not registered?" → "Register".
- Width CSS needs `!important` because Gancio sets `max-width:1400px` inline.
- Recurring-events switch in the top bar gets a hover label via the custom JS setting.
- Registering does not log you in; you must log in afterward. Admin is in the ⋮ menu once logged in.

## Round 3
- Title is "PDX FUSION" (setting). Login failure was Safari rejecting Gancio's Secure-only cookie on
  plain http://localhost; Chrome/Firefox work. Not an issue once served over https.
- Repeating-events filter: Gancio's top-bar switch is hidden by CSS; custom JS adds a checkbox
  between calendar and list that clicks the original. No source change.
- About page: the editor is admin-only by design (visitors see static text). Draft text stored in the
  `about` setting; edit it by visiting /about while logged in as admin.

## Feedback
- No built-in general feedback form in Gancio (only per-event "Report", which needs SMTP).
- Footer links must be https:// (mailto breaks), so the feedback mailto link is in the About text.
- **PLACEHOLDER:** `feedback@pdxfusion.example` is fake. Replace it in the About page (edit as admin)
  once a real address exists.

## Round 4
- `recurrent_event_visible` = true (repeating events shown by default). Note: Gancio's checkbox *adds*
  repeating events to the list; it is not a "only repeating" filter.
- Tags field hidden on the add form via CSS (tags still exist in Gancio; undo by deleting that CSS rule).
- **First source change:** `gancio-src` branch `time-select-dropdown` replaces the native time inputs
  (confusing placeholder, "From is required" until every part touched) with 15-minute dropdowns in
  `app/components/DateInput.vue`. One small commit, suitable to propose upstream.
- Because of that, the site now runs a **locally built image** (`pdxfusion-gancio:local`) built from
  `gancio-src`, using `Dockerfile.gancio` (copy of Gancio's Dockerfile minus `--platform=$BUILDPLATFORM`,
  which the old builder can't parse; avoids installing buildx). Colima VM raised to 4 CPU / 6 GB for builds.
- Found: recurring-event generation is slow (approval doesn't trigger it; task timer units look wrong,
  ~30 h not 30 min). Fix pending, to be done on Opus on its own branch.

## Round 5: recurring-event fixes (done on Opus)
- Branch `fix-recurrent-generation` (2 commits, see UPSTREAM.md):
  1. Task manager timing: delays were counted as if a tick were 1 s while the loop ticks every 60 s,
     so "every 30 minutes" was really every 30 hours. Now correct.
  2. Approving (confirming) a recurring event creates its next occurrence immediately.
- Verified with Gancio's own test suite in a throwaway container (172 passed); new test fails without the fix.
- Site is built from branch `pdxfusion` = upstream main + the patch branches.
- Known Gancio design, unchanged: only the *next* occurrence of each series exists at a time; later
  dates are generated as each one passes.

## Round 6
- Gancio bug (not patched): the home list reads "show repeating events" only at page load; toggling it
  saves a cookie but doesn't refresh the list. Since this site wants repeating events always visible,
  the switch is hidden by CSS and a custom JS snippet clears any old `showRecurrent` cookie once.
- Home list is a single vertical column (custom CSS, max-width 680px). 'Show preview' switch label
  no longer wraps (custom CSS).
- OPEN: show recurring events months ahead. Gancio only creates the next occurrence of each series.
  Needs a generation change (create occurrences up to a horizon, e.g. 6 months). Pending: horizon choice
  and switching to Opus.

## Round 7: recurring events shown 6 months ahead (done on Opus)
- Branch `recurrent-horizon` (on top of `fix-recurrent-generation`), see UPSTREAM.md.
- Every occurrence up to 6 months ahead now exists as its own event; topped up every 30 minutes.
- Date maths now uses the site timezone (America/Los_Angeles) instead of the server clock (UTC):
  weekly events keep their local time across clock changes; "first Saturday" is right for evening events.
- Editing a series replaces its future (visible) dates, so edits made to a single future date are lost
  when the whole series is edited. Skipped dates stay skipped. Deleting/hiding a series removes its
  future dates; past ones are kept.
- Federation: a date is announced when it is within 7 days, not all 26 at once.
- Verified: Gancio test suite (182 passed) + live data (existing weekly event got 26 dates through
  2027-03-31, all at 1:00 PM Pacific, no duplicates). DB backup from before: `data/gancio.sqlite.bak-before-horizon`.
- To change the horizon: `RECURRENT_HORIZON` in `gancio-src/server/services/recurrent.ts`, then rebuild.
- Branch `fix-show-recurrent-default`: plain `/feed/ics` and `/feed/rss` now include recurring events
  (Gancio read the setting before settings were loaded), and their default start time is no longer
  frozen at server start. All branches merged in `pdxfusion`: 183 tests pass.

## Round 8
- Branch `fix-recurrent-type-optional`: weekly recurrence from the form no longer fails validation
  (the form doesn't send `type` for weekly; server now defaults it to `ordinal`). 184 tests pass.
- Recurrence frequency buttons wrap onto several lines (custom CSS) so all options are visible.
- NOT supported by Gancio: an end date for a recurring series. Needs a generator + form change.
- NOT done: loading the home list in 30-day windows. Home currently loads everything from the start of the
  month; cards beyond the first 9 are already lazy-rendered.

## Round 9: end date for recurring events (done on Opus)
- Branch `recurrent-until`. "Ends on (optional)" date in the add/edit form when "Recurring" is selected.
  The last occurrence is on or before that day; no end date = repeats indefinitely (6 months shown).
- Changing or adding an end date on an existing series removes/creates future dates accordingly.
- Editing a series now opens the form with "Recurring" and its settings pre-selected (Gancio showed "Normal").
- `data/user_locale/en.json` regenerated to include the new labels. Our edits in that file:
  event.online_locations, event.online_locations_help, login.not_registered, common.where.
- Known limitation (Gancio, unchanged): switching a series back to "Normal" in the form does not stop it
  repeating; delete the series instead.
- DB backup from before: `data/gancio.sqlite.bak-before-until`.

## Round 10
- Branch `calendar-today-button`: "Today" button in the calendar's footer (bottom right). New text key
  `common.today`, so `data/user_locale/en.json` was regenerated (it overrides whole sections).

## Phase 3 design, first pass
- Used Gancio's built-in settings where they exist: light/dark color palettes (incl. background and surface),
  custom CSS, default theme (now light). Nothing in Gancio's source was changed for the design.
- Font: Atkinson Hyperlegible **Next** (open source, SIL OFL), embedded in the CSS (no Google/CDN),
  with system-font fallbacks. It always draws a slashed zero (a legibility feature); cannot be turned off.
- Palette (all text >= 5.7:1 contrast): light = warm paper #FBF7F0 + terracotta #A83F27 + sage #3F6B58;
  dark = warm charcoal #1C1A18 + peach #F29A7A + soft sage #9CC5AD.
- Header: removed Gancio's silhouette image and hid the Gancio logo (not a Gancio-branded site).
- Organic touches (kept light): rounded corners/pill buttons, ONE wavy divider under the header,
  gentle hover lift on cards. All motion is off under `prefers-reduced-motion`.
- Home list uses compact cards (small flyer thumbnail beside title/date/place) so 26 repeats stay short.
- Event page: flyer capped at 55% of the screen height so details are visible on a phone.
- Tags: field hidden on the add form earlier, so the "starter tags" are moot unless tags come back.
- Design tooling: `design/shoot.sh` uses a throwaway headless browser in Docker (image pulled once, ~900 MB).
- DB backup before design: `data/gancio.sqlite.bak-before-design`.

## Phase 3 design, feedback round 1
- Hover lift removed from all buttons (kept on event cards only). Buttons are now squared-off rectangles
  (6px corners) instead of pills, everywhere in the site; 'Add event' solid, 'Share' outlined.
- Wavy divider: more space above (26px) and below (22px); waves are scaled so both ends finish cleanly.
- Light/dark: follows the device setting; dark if unknown. Implemented in `design/functional.js` by keeping
  Gancio's `theme` cookie equal to the device setting (so the server draws the right theme, no flash on later
  visits). A choice made with the sun/moon button is kept and wins. One-time catch: a light-mode device's very
  first visit draws dark, then reloads once to light. (Gancio's own 'system' value would flash white at dark
  users on every page, so it isn't used.)
- Fixed a gap between a card's title and date when the thumbnail is taller than the text.

## Phase 3 design, feedback round 2
- No hover lift on anything (cards too). No motion effects at all now.
- 'Add event' and 'Share' are back to Gancio's plain text buttons (orange + icon, white share icon), no box.
- Event cards: the repeat icon (meant "part of a recurring event") became a **share button** (source change,
  branch `card-share-button`): system share sheet on phones/Safari, otherwise copies the link and shows "Copied".
  Cards no longer show that an event repeats; the event page still says "(Each Wednesday)".
- Home list has **month headings** (underlined) (source change, branch `home-month-headings`): "October",
  "November", ... with the year added once it isn't the current year. Hidden while searching or with a day
  selected. Events already under way are listed under the current month.
- Site now runs a build containing all branches merged in `pdxfusion` (186 tests pass).

## Hosting / going to production (prepared, nothing deployed)
- GitHub Pages cannot run Gancio (needs a server, database, background jobs); GitHub is also big tech.
  Plan: small VPS (Ubuntu, 2 GB RAM) + Docker + Caddy (open source, automatic HTTPS). Domain stays at
  SiteGround (DNS only). SiteGround shared web hosting cannot run Gancio. Code remote, if wanted: Codeberg.
- `design/apply.py` now sets up a whole fresh site (name, timezone, moderation, recurring, palette, wording,
  first About text only if none exists). Tested from an empty database in a throwaway copy.
- `design/make_locale.py` regenerates `data/user_locale/en.json` (our four wording edits).
- Added: `docker-compose.prod.yml`, `Caddyfile`, `.env.prod.example`, `backup.sh`, `DEPLOY.md`.
  Prod compose and Caddyfile validated; **the server steps themselves are untested** (no server yet).
- Month headings are centered (CSS).

## Temporary domain, federation off, indexing
- pdxfusion.com is owned by someone else: testing happens on a temporary domain (options in DEPLOY.md).
  `DOMAIN` and `BASEURL` in the server's `.env` are the only places the name lives.
- Federation OFF (`enable_federation` set false by `design/apply.py`): verified fediverse lookup returns 404 and
  the footer follow button is gone. (`/.well-known/nodeinfo` still answers; it only names the software.)
- Search engines: `INDEXING` in `.env` (read by the Caddyfile). `noindex` = X-Robots-Tag header + robots.txt
  Disallow all (both modes tested against the local site). `index` = open robots.txt that blocks only
  login/admin/api pages and lists the sitemap. Switch only at hard launch.
- SEO baseline checked (sitemap, canonical, og tags, schema.org Event microdata exist). Gaps: no robots.txt
  (now served by Caddy), no meta description on event pages. Launch checklist is in DEPLOY.md.
- Live data starts fresh (server starts empty; `design/apply.py` sets it up).

## Hosting alternatives checked (Vercel / Cloudflare free tiers)
- Not workable for Gancio without rewriting it: it saves flyers to local disk (sharp -> UPLOAD_PATH), uses a local
  SQLite file, and runs recurring-event generation on an in-process timer loop (server/services/taskManager.ts).
  Serverless platforms (Vercel) have no persistent disk or background timers (Hobby cron: 2 jobs, once a day).
  Cloudflare Workers cannot run its native modules (sharp, sqlite3). Porting storage/jobs = a long-lived fork.
- Cloudflare's free plan is still useful IN FRONT of a VPS (DNS, CDN, DDoS protection) if wanted later.
- Chosen: small VPS, ~$5-12/month (Linode Nanode 1 GB / 2 GB). Gancio measured at ~160 MB RAM idle.

## First live deploy: look missing (found by the user)
- Symptom: live site showed stock Gancio (black theme, wide add form, slider, no Location/Invite wording).
- Cause: the look and the basic settings are DATA (settings table + data/user_locale), installed by
  `design/apply.py`. The rsync deliberately skips `data/` (live starts fresh), and apply.py had not run on the
  server yet (live CSS = 27 bytes, no palette, no wording, moderation off, federation on). The CODE did ship
  (Today button, end-date label present). I did not warn that the site looks stock until apply runs: my miss.
- Also found on live (not caused by apply.py): `allow_online_event` = false (hides the Invite/RSVP link field),
  `allow_event_without_end_time` = false, `show_download_media` = false, timezone `Canada/Pacific`.
  apply.py now forces `allow_online_event` true (the Invite link needs it) and sets America/Los_Angeles.
- New: `design/audit.py URL` compares a live site with this Mac (CSS/JS bytes, palette, settings, wording).
  Its first version falsely passed CSS/JS (the public API doesn't expose them); fixed and proven against itself.
- apply.py's `docker compose` (v2) code path is untested here (this Mac only has `docker-compose`).

## Event form fixes (from first live test)
- Recurrence end: 'Repeats with no end' / 'Ends on a date' choice; the date box appears only for the second,
  pre-filled 3 months after the picked day. (Safari draws today's date in an EMPTY date box, which looked filled.)
- End time list: only times after the start; single-day events continue past midnight, marked "(next day)", up to
  12 h after the start (longer = multi-day). Changing the start clears an end that is no longer possible, so the
  'end before start' error cannot happen; multi-day events that end on their first day get an inline error.
- An event ending the next day but lasting under 24 h is ONE evening (shows "09:00 PM-01:00 AM"; edits as Normal).
- Wording: `common.send` -> "Submit" (all pages that use it: add event, register, password recovery).
- Admin email on new submissions: Gancio already has this notification built in, but it needs Admin -> SMTP
  (mail server) AND an admin email address; neither was set on the live site, which is why nothing arrived.

## Placeholder overlap (Admin -> E-mail) and moderator emails
- Overlap cause: MY CSS rule from the first design pass forced placeholders visible (`opacity: 1 !important`),
  undoing Vuetify's rule that hides a labeled field's placeholder until it is active. Fixed: the brighter-placeholder
  rule now applies only to active fields and label-less fields (e.g. Search). Checked idle state in Chromium and
  Firefox (hidden for labeled fields, visible in Search). The focused look was not verified in a browser.
- Moderators by email: Gancio emails the "Admin e-mail" address PLUS every ACTIVE admin AND editor whose "Notify"
  switch is on (default on) when an event needs approval. Recipients share one `To:` line. Needs Admin -> E-mail (SMTP).
  Recommended: give community moderators the **editor** role (can approve events; users, settings and mail setup
  stay admin-only on the server).
- Finding (upstream, not fixed): `/api/events/unconfirmed` only requires a logged-in user, so any account (even a plain
  trusted organizer) can list pending submissions through the API; the Admin UI doesn't show them to such accounts.
- Gancio's approve button is a toggle: two moderators approving the same event at once would hide it again.

## No visitor accounts: login hidden
- The login icon is hidden for logged-out visitors (functional.css); moderators/admins get the address /login directly.
  The add-event text no longer mentions logging in or registering (wording edit `event.anon_description`).
  This is tidiness, NOT security: /login is still public and guessable, so admin passwords must be strong and unique.
  Gancio shows no sign of limiting repeated wrong passwords (none found in the login code): consider Caddy/Cloudflare
  rate limiting at launch.
- Mail sender: Gancio sends from the "Admin e-mail" address, so for now a personal/throwaway mailbox is the sender;
  swap it in Admin -> E-mail when the real domain and mailbox exist (settings only, no rebuild).

## Phone layout bug (found by the user on a phone)
- Bug: Gancio gives its button groups (`v-btn-toggle`) a fixed height and clips what doesn't fit. On phones, the
  'Recurring' button, and the monthly 'Each third Tuesday of the month' choice, were hidden (so phone users could not
  create a recurring event, nor choose the 'nth weekday' option). Desktop and my earlier checks (which stopped at
  desktop/390px and never reached those groups) did not show it: my miss.
- Fix: one general rule in `design/functional.css` (groups grow, wrap, show every choice). It replaced two one-off
  rules; folding them together briefly stacked the 'how often' buttons in a column on desktop; caught and restored.
- New check: `design/phonecheck.sh [live URL]` tests the groups at 360/390/430px in Chromium AND WebKit (iPhone engine).
  Pass locally; run against the live site to confirm after deploying.

## Event types (tabs + required dropdown), address suggestions, phone hover labels
- Source branch `event-categories-address-suggest` (committed and merged into `pdxfusion`, deployed to pdx.hmu.click 2026-10-04).
- Event type = an ordinary Gancio tag, one of Social / Lesson / Workshop (`gancio-src/shared/utils/eventCategories.ts`).
  The add form's free-text tags field is replaced by a REQUIRED "Event type" dropdown (other tags an event already has
  are kept). Cards and event pages show the tag chip again. Home page has tabs All / Socials / Lessons / Workshops
  (filters the loaded list in the browser). Events created before this have no type: they appear only under "All" until edited.
- Address suggestions: the Address field now suggests places while typing (and fills coordinates). Uses Gancio's geocoder,
  which needs `allow_geolocation` (now set by `design/apply.py`; side effect: event pages show an OpenStreetMap map).
  The public Nominatim server forbids search-as-you-type, so the provider is Photon (`https://photon.komoot.io/api/`),
  added to `server/services/geocode.ts`, biased toward Portland. Photon's public server is fair-use; for heavy traffic, self-host it.
  Addresses are sent to that third party as people type.
- Phones: hover labels (tooltips) are hidden on touch screens (`@media (hover: none)` in functional.css). They stuck after a tap.
- Needs: `docker-compose build` + `python3 design/apply.py` (locally done); on the server, rebuild and run apply.py too.
- DB backup from before: `data/gancio.sqlite.bak-before-categories`.
- Follow-up: an event can have several types (multi-select, at least one). Description toolbar overlap fixed (my button-group rule
  was also hitting Gancio's formatting toolbar; now excluded). "Every other week" wording. The 'how often' / 'which day' choices
  are small filled pills (class `frequency-toggle`, source change in DateInput.vue) so they differ from the Normal / Multiple days / Recurring boxes.
- Follow-up 2: address suggestions are limited to the Portland area (bbox in `geocode.ts`) and to results with a house number
  (no towns, counties or bare streets). Coverage is only as good as OpenStreetMap's house numbers: some real addresses won't suggest.
  Description box: the 3px keyboard-focus ring is now drawn inside the box (it rode up over the toolbar). Recurrence end radios centered.
- Follow-up 3: removed a stray `[]` under the calendar for weekly/every-other-week/yearly recurrence (DateInput.vue printed an empty
  list). `common.where` now reads "Venue name" (make_locale.py); its hint line removed. "Event type" has its own full-width row
  (it sat beside the flyer controls, whose Edit/Remove buttons overlapped its error text).
- Follow-up 4: wording for the add form intro (`event.anon_description`) and the About page (design/about.html; the stored
  `about` setting was replaced with it, since apply.py never overwrites it). About links: "Add Event" -> /add, "Share" -> /export.
  About sections now have spacing (functional.css). Recurrence: the monthly-choice row's space is reserved (`.pattern-slot`)
  so the end-date options below no longer jump when "Each month" is chosen or a date is picked.

## Cost field, copy address, venue map link
- Branch `event-cost-copy-map`. New optional event field `cost` (free text, max 60, e.g. "$5-15"): DB column via migration
  `20261004190000-event_cost.js` (runs on startup), add-form field, shown under the address on the event page. Copied to
  repeat dates of a series. Not shown on cards / in the calendar feed.
- Copy button beside the address on the event page (reuses Gancio's clipboard helper, shows "Copied").
- Venue page map: tapping it opens the visitor's own maps app (Apple Maps on iPhone, geo: link on Android, OpenStreetMap
  elsewhere; `app/composables/useMapLink.ts`). Venues without saved coordinates get them looked up from the address when the page
  opens (not saved). Zoom buttons hidden there (functional.css).
- Local DB backup before the migration: `data/gancio.sqlite.bak-before-cost`. NOT deployed to pdx.hmu.click yet.
- Cost field / copy address / venue map link deployed to pdx.hmu.click 2026-10-04 (live backup first: `~/pdxfusion-live-backups/*-before-cost.tar.gz`).
  I had built it locally and not deployed it when the user first looked for it on the live site.
- Git identity: commits in `gancio-src/` and the top-level repo are authored as `clyobuilds <297059659+clyobuilds@users.noreply.github.com>`
  (set per-repo; the Mac's global git name/email is left alone). Earlier local commits were rewritten to remove the personal name/email.
  Nothing is published yet; the GitHub repos wait for the final domain. rsync now also excludes `gancio-src/.git`.
- Event page: address indented under the venue name (functional.css), deployed live (design-only: rsync design/ + apply.py).

## Copy from an existing event
- Branch `copy-from-existing-event`. Optional search box at the top of the add form (`EventCopyPicker.vue`): finds visible past and
  upcoming events by title or venue (a series is listed once); picking one opens `/add?copy=ID` filled in. Works for visitors without
  an account (it only uses public events). Dates are cleared; a series keeps only its frequency; the flyer is NOT copied.
- Why no flyer: the server only accepts a web address for `image_url`; stored flyers are file names, so Gancio's admin "Clone" has
  silently dropped the flyer all along. Reusing the file would need a source change plus care about deleting the original.
- Found (Gancio bug, not patched): `/api/events` with BOTH a text `query` and `max` returns 500 ("no such column: name"; the venue-name
  filter runs before the places join). The picker avoids `max`. Worth reporting upstream.
- To skip one date of a repeating event: open that date's page as admin/editor -> "Skip" (hides only that date; it is not recreated).
  "Remove" under "Recurring event actions" deletes the WHOLE series.

## 4-month horizon, day list fix, picker moved
- Repeating events now exist and show 4 months ahead instead of 6 (`shared/utils/recurrentHorizon.ts`, used by the server generator and the
  home page). Dates already created beyond 4 months are not deleted (that could re-create dates an admin skipped); the home list and
  calendar hide them until they come within 4 months. The two tests that assumed 6 months were updated; full suite: 186 passed.
- Home page, clicking a day: a day lists events that START that day. An event running past midnight (or ending exactly at midnight) no
  longer appears on the next day. Events lasting 24 h or more (festivals) still appear on every day they cover. Calendar dots were already by start day.
  NOTE: days are cut in the visitor's browser time zone (Gancio behavior), so a visitor outside Pacific time can see a day shifted.
- "Start from an existing event" now sits above the form box (not inside it); label shortened, no "(optional)".

## Home reset, picker lists repeating series, copy never repeats
- Clicking the site title or the footer Home link now acts like a refresh of the home page (selected day, search and browsed month are
  forgotten): `useGoHome.ts`. A browser refresh already reset the day (tested).
- "Start from an existing event" now finds repeating series: it passes `include_parent` (the earlier `show_recurrent=false` alone hid every
  series, because Gancio's "no repeating events" excludes both the series and its dates). A series is listed once, by its first date.
- A copy never carries a repeat setting. Before, it kept the weekly frequency and opened as "Recurring", which made a one-time copy repeat
  weekly (live example: "Inspire Fusion", Oct 17, created as a weekly series; 25 later dates were generated).
- Cleaning up a series made by mistake: edit the series, set "Ends on a date" to its first day (removes all later dates), or copy it as a
  Normal event and use "Remove" under "Recurring event actions" on the old one.

## Favorites (merged into pdxfusion, deployed 2026-10-07)
- Branch `favorites` in gancio-src. A star on each event card (left of Share) and a "Favorite" row above Share on the event page. Favorites are
  event ids in the browser's localStorage (`pdxFavorites`), no account; they do not follow the person to another browser or device.
- "Favorites" tab (star icon, plus the word on wider screens) after Workshops: fetches each favorited event by id, so events that have ended
  and are no longer in the home list still appear. Upcoming first (soonest first); ended ones below under "Past Events", greyed out.
- Each date of a repeating event is its own favorite (a favorite is one date, not the series).
- Deleted or hidden events simply drop out of the tab (their ids stay in storage, harmless).

## Past Events archive, site name (local only, 2026-10-08)
- New page `/past` (gancio-src branch `past-events`): every event that is over, newest first, 60 at a time with "Load more". The home list
  ends with a "Past Events" button linking to it. Uses the existing `/api/events` with `older`, `reverse`, `start=now`.
- Site name is now "PDX FUSION DANCE"; subtitle is "a community calendar for Portland's fusion dance scene" (lowercase "a", in `design/apply.py`).
- Not deployed yet: both changes are on branches (`past-events` in each repo) until the user says "push to prod".
