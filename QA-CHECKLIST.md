# QA checklist (local site at http://localhost:13120, use Firefox or Chrome)

Start first: `colima start` then `docker-compose up -d` (see README.md). Hard-refresh (Cmd+Shift+R) after any change.

## 1. Look and wording
- [ ] Home page shows "PDX FUSION DANCE" and the subtitle.
- [ ] "Show repeating events" checkbox sits between the calendar and the event list; toggling it works.
- [ ] Add event page is a narrow column; Location + Address share a row; **Invite / RSVP link is on its own row below**.
- [ ] Login page says "Register" (not "Not registered?").

## 2. Add an event anonymously
- [ ] Log out (⋮ menu → Logout), or use a private window.
- [ ] Add event → fill Title, Location (type a venue name), Address, date, time.
- [ ] Paste an invite link (any https:// URL) in the Invite / RSVP link field.
- [ ] Attach a flyer image. Submit.
- [ ] Expect a message that the event awaits approval. It must NOT appear on the home page yet.

## 3. Approve it as admin
- [ ] Log in as admin → ⋮ menu → **Admin** → **Events** tab (pending events are listed or marked).
- [ ] Open the pending event and approve/confirm it.
- [ ] Event now appears on the home page for logged-out visitors (private window).

## 4. List and calendar views
- [ ] Home page: the event is in the list; flyer and invite link show on its detail page.
- [ ] The date is highlighted in the calendar; clicking the date filters the list to that day.
- [ ] Use the calendar's arrows to change month and back.

## 5. Recurring events
- [ ] Add event → choose **Recurring** → try "Each month". Look for a "first Saturday"-style option (Phase 2 will decide if it exists).
- [ ] Submit, approve, and confirm several future dates show with the repeating-events checkbox on.

## 6. Feeds
- [ ] http://localhost:13120/feed/rss opens (XML of events).
- [ ] http://localhost:13120/feed/ics downloads/opens a calendar file; import it into a calendar app.
- [ ] The home page "Share" button shows the same links.

## 7. Accounts (do last)
- [ ] Admin → **Users** → add the test organizer (email; set a password if the form offers it. Invite emails will not send until email/SMTP is configured, so this may need a password set by you).
- [ ] Log in as the organizer in a private window; submit an event; it should publish without approval if the account is trusted (check what actually happens and tell me).
- [ ] Admin → Settings → turn **Registration OFF**. Then log out and confirm /register no longer lets anyone sign up.

## 8. About page
- [ ] As admin: /about shows an editor + Save. In a private window: it shows plain text.
