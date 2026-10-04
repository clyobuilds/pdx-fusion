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
    cd gancio-src
    git fetch origin && git checkout main && git pull
    git checkout pdxfusion && git reset --hard main
    git merge time-select-dropdown calendar-today-button card-share-button home-month-headings recurrent-until event-form-fixes   # contains recurrent-horizon, fix-recurrent-generation, fix-recurrent-type-optional
    git merge fix-show-recurrent-default   # conflicts in tests/unit/Recurrent.test.ts: keep both tests
    # (recurrent-horizon already contains fix-recurrent-generation; rebase it on main if main moved)
    cd .. && docker-compose build && docker-compose up -d
If no patch branches remain, switch `docker-compose.yml` back to `image: cisti/gancio:beta`.

## After any change to Gancio's English text (`i18n/locales/en.json`)
`data/user_locale/en.json` overrides whole sections (`event`, `login`, `common`), so it must be regenerated
from the new `en.json` with our four edits re-applied (see DECISIONS.md), otherwise new labels show as raw keys.
