# Changes to Gancio's source, and how to offer them upstream

Gancio's code lives in `gancio-src/` (a git clone of https://framagit.org/les/gancio, base: `main` at
2.0.0-beta.5, commit 1371385). We do NOT keep a fork. Each change is a small branch off `main`:

| Branch | What | Files |
|---|---|---|
| `fix-recurrent-generation` | (1) Task manager delays were 60x too long: recurring-event generation ran every 30 hours, not 30 minutes. (2) Approving a recurring event now creates its next occurrence immediately. Includes a unit test. | `server/services/taskManager.ts`, `server/api/events/[id]/toggle.put.ts`, `tests/unit/Recurrent.test.ts` |
| `time-select-dropdown` | Event form: 15-minute time dropdowns instead of the browser's native time inputs. | `app/components/DateInput.vue` |
| `recurrent-horizon` | Built on top of `fix-recurrent-generation`. Occurrences of recurring events are created 6 months ahead (was: only the next one). Dates are calculated in the site's timezone and anchored to the series start (fixes DST drift, wrong "Nth weekday" for evening events, every-other-week drift, ignored `2m` frequency). Editing a series refreshes its future dates; hiding/deleting it removes them; skipped dates stay skipped. Federation announcements go out when a date is within 7 days. Includes unit tests. | `server/services/recurrent.ts`, `server/services/events.ts`, `server/api/events/[id]/toggle.put.ts`, `server/api/events/[id]/index.delete.ts`, `shared/types/settings.ts`, `tests/unit/Recurrent.test.ts` |
| `fix-show-recurrent-default` | Query defaults were evaluated once at server start: the "show recurring events by default" setting was ignored (plain `/feed/ics` and `/feed/rss` never included recurring events) and the default start time was frozen at boot. Now evaluated per request. Includes a test. | `server/services/events.ts`, `server/services/collections.ts`, `tests/unit/Recurrent.test.ts` |
| `fix-recurrent-type-optional` | Editing/creating a weekly recurring event from the form failed with "Invalid option: expected one of 1\|2\|3\|4\|ordinal\|-1": the form only sends `type` for monthly events but the schema required it. Now defaults to `ordinal`. Includes a test. | `server/services/db.ts`, `tests/unit/Recurrent.test.ts` |
| `recurrent-until` | Built on top of `recurrent-horizon` + `fix-recurrent-type-optional`. Recurring events can have an end date (`until` in the recurrence details): "Ends on" field in the event form, generator stops there, event page shows "... until <date>". Also returns the recurrence details of a series from the API so the form shows them when editing (it showed a series as a "Normal" event). Includes server tests. | `server/services/db.ts`, `server/services/events.ts`, `server/services/recurrent.ts`, `app/components/DateInput.vue`, `app/composables/useTime.ts`, `i18n/locales/en.json`, `tests/unit/Recurrent.test.ts` |
| `calendar-today-button` | Home calendar: "Today" button (bottom right) that returns to the current month and clears the selected date. Adds `common.today` to `en.json`. | `app/components/Core/Calendar.vue`, `i18n/locales/en.json` |
| `card-share-button` | Event cards: the "part of a recurring event" icon is replaced by a share button (system share dialog, or copies the link when not available). | `app/components/Event/Card.vue` |
| `home-month-headings` | Home list: a heading before the first event of each month (year shown when not the current one); not shown while searching or with a day selected. | `app/pages/index.vue` |
| `event-form-fixes` | Built on top of the other branches (it touches the same form). Event form: end-time list only offers times after the start and continues past midnight ("next day"), so a 9 PM-1 AM dance can be entered; changing the start clears an impossible end; a late-night event under 24 h is one evening (shown "9:00 PM-1:00 AM") and not a multi-day event; recurrence end is a "no end / ends on a date" choice. | `app/components/DateInput.vue`, `app/composables/useTime.ts`, `i18n/locales/en.json` |
| `pdxfusion` | Just a merge of the branches above. This is what the site is built from. Never send this upstream. | - |

## Status
- `fix-recurrent-generation`: full upstream test suite passes (172 passed). The new test fails on
  unpatched code and passes with the fix. A clear bug fix; good candidate to send.
- `event-form-fixes`: full suite passes; the form behavior was tested in a headless browser (end list, wrap past midnight, clearing, no-end default, submit), not by unit tests. Known upstream quirk found, NOT fixed: the calendar day is read in the browser's timezone but saved in the site's timezone, so a browser in another timezone can save the day before.
- `card-share-button`, `home-month-headings`: small UI features; full suite passes; the card button's copy-link message and the headings were checked in a headless browser, not on real phones. Upstream may prefer the repeat icon to stay (the share button replaces it).
- `calendar-today-button`: small UI addition; suite passes; not tested in a browser by the author.
- `recurrent-until`: server side covered by tests (suite passes); the form field itself has no automated
  test. A feature: propose it together with (or after) `recurrent-horizon`.
- `fix-recurrent-type-optional`: full suite passes. A clear bug fix; good candidate to send.
- `fix-show-recurrent-default`: full suite passes. A clear bug fix; good candidate to send.
- `recurrent-horizon`: full suite passes (182 passed). This is a feature/behaviour change, not just a bug
  fix: discuss with the maintainers (open an issue) before sending. The timezone/anchoring fixes inside it
  are bug fixes and could be split out and sent on their own. The 6-month horizon and 7-day notify window
  are constants in `recurrent.ts`; upstream would likely want them as settings.
- `time-select-dropdown`: a UI preference, not a bug fix; upstream may or may not want it. Not yet
  viewed in a browser by the author of the change, and has no test.

## Before sending upstream
1. The commits use a placeholder author (`pdxfusion <local@example.invalid>`). Re-author them with
   your real name/email first.
2. Create an account on framagit.org, fork les/gancio, push the branch, open a merge request against
   `main`. Read `gancio-src/CONTRIBUTING.md` first. Check the issue tracker for an existing report.
3. Once a fix is merged and released upstream, delete that branch here and rebuild.

## Updating Gancio later
**Do not rebuild the `pdxfusion` branch from a list of branches** (older instructions did): later work was committed directly on
`pdxfusion` (for example the 4-month horizon, the day-list fix, the favorites merge), so a reset would lose it. Instead bring the new
upstream code into `pdxfusion` and resolve any conflicts:
    cd gancio-src
    git fetch origin
    git checkout pdxfusion
    git merge origin/main        # conflicts are most likely in tests/unit/Recurrent.test.ts, app/pages/index.vue, app/pages/add/[[eventId]].vue
    # then run the test suite (see DECISIONS.md: throwaway container, `npx vitest run`), rebuild, and compare local vs live with design/audit.py
    cd .. && docker-compose build && docker-compose up -d
Back up first (live: `./backup.sh`; local: copy `data/gancio.sqlite`). If no patch is left, `docker-compose.yml` can go back to `image: cisti/gancio:beta`.

## After any change to Gancio's English text (`i18n/locales/en.json`)
`data/user_locale/en.json` overrides whole sections (`event`, `login`, `common`), so it must be regenerated
from the new `en.json` with our four edits re-applied (see DECISIONS.md), otherwise new labels show as raw keys.

## Found while building PDX Fusion (not patched, worth reporting)
- `GET /api/events?query=...&max=...` returns a server error (500, "no such column: name") when a text query is combined with a result
  limit: the venue-name part of the search runs inside the limited sub-query before the places table is joined. Without `max` it works.
- The admin "Clone" button (and any form that sets `image_url` to a stored flyer's file name) silently drops the flyer, because the server
  only accepts `http(s)://` addresses for `image_url`, while stored flyers are file names.
