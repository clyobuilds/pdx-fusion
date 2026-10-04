# Contributing to PDX Fusion

Thanks for helping! Anyone can propose a change; only the site's maintainers publish changes to the live site.

## Ways to help
- **Report a bug or suggest an idea:** open an *Issue* (or email the address on the site's About page).
- **Fix or improve something:** send a *pull request* (a proposed change that maintainers review before it is merged).

## Where do changes go?
- Look, wording, colors, layout tweaks: `design/` (this repository). `design/theme.css` is looks, `design/functional.css` is
  layout and behavior fixes, `design/apply.py` holds the colors and installs everything.
- How the site works (event form, calendar, recurring events): `gancio-src/` (its own repository, linked as a submodule).
  Changes that would help every Gancio site are best also offered to the Gancio project (see `UPSTREAM.md`).

## Running it on your computer
See `README.md` ("Start"). In short: `colima start`, `docker-compose up -d`, open http://localhost:13120. After editing
`design/`, run `python3 design/apply.py`. After editing `gancio-src/`, run `docker-compose build` first.

## Before you send a pull request
- Try it in a browser, on a **phone-sized screen** as well as desktop, in **light and dark** mode.
- Keep the site accessible: readable contrast, no motion effects, everything usable by keyboard and touch.
- Keep changes small and focused, and say in the description what you changed and why.
- **Never** include secrets or data: no `.env`, database files, passwords or keys, and no flyers or personal information.
- By contributing you agree your work is released under the project's license (AGPL-3.0).

## What happens next
A maintainer reviews your pull request, may ask for changes, and merges it when it is ready. Maintainers then deploy
(see `DEPLOY.md`). Not every proposal will be accepted; the aim is a calm, simple, welcoming calendar.
