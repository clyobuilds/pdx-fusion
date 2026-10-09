# Putting PDX FUSION online

## Why not GitHub Pages
GitHub Pages only serves finished static files. Gancio is a program that has to keep running: it has a
database, user accounts, uploaded flyers, moderation, and background jobs (like creating recurring dates).
It needs a small always-on server. (GitHub is also owned by Microsoft, which doesn't fit your goal of
avoiding big-tech dependencies. If you want a place to keep the *code* online, **Codeberg** is a non-profit,
open-source alternative. It is not needed to run the site.)

## What you need
1. **A small server (VPS)**: Ubuntu 24.04 LTS, 25+ GB disk. Size: Gancio itself uses about **160 MB** of
   memory when idle (measured), so **1 GB** is enough to *run* it; only the one-time *build* is memory-hungry.
   - **Linode/Akamai Nanode 1 GB: $5/month** (try this first, with the swap file from step 3; if the build
     runs out of memory, resize up to 2 GB for a day, or start on 2 GB at **$12/month**).
   - Other providers are similar, but note Hetzner's cheap plans are Europe-only (their US plans are
     now about $20/month), so for a Portland audience Linode/Vultr/DigitalOcean are cheaper in the US.
   Prices change: check the provider's page.
2. **A domain name you control.** `pdxfusion.com` belongs to someone else for now, so use a **temporary test
   domain** (see "Temporary test domain" below). Moving to the real one later is a small change.
3. **Email sending** (Admin -> SMTP in the site) so password resets and notifications work. Simplest: an
   email account on your domain at SiteGround and use its SMTP details.

Not possible: SiteGround's normal web hosting. It runs PHP sites, not Docker programs like Gancio.

## Steps (about an hour, mostly waiting)
Do these in order. Things marked **YOU** need your accounts; I can't do them for you.

### 1. Get the server (YOU)
Create the VPS with your SSH key (the provider explains how) and note its **IP address**.

### 2. Point the domain at it (YOU)
In the DNS settings of your test domain (wherever you got it), set an **A record** for it pointing to the
server's IP address. It can take from a few minutes to a few hours to spread. Check with:
`ping qa.example.org` (use your test domain; it should show your server's IP).

### 3. Prepare the server
On the server (`ssh root@YOUR_IP`):
    apt update && apt -y upgrade
    apt -y install docker.io docker-compose-v2 python3 rsync ufw
    ufw allow OpenSSH && ufw allow 80 && ufw allow 443 && ufw --force enable
    # 2 GB RAM is tight for the first build: add some swap
    fallocate -l 2G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
On Ubuntu the command is `docker compose` (with a space) instead of `docker-compose`. Use whichever works.

### 4. Copy the project to the server
On your Mac, from this folder (note: not your test data, secrets, or screenshots):
    rsync -av --exclude data --exclude .env --exclude backups --exclude '*.log' \
      --exclude design/screenshots --exclude 'gancio-src/node_modules' \
      ./ root@YOUR_IP:/opt/pdxfusion/
(`gancio-src/` goes along, including our small source changes.)

### 5. Configure and start (on the server)
    cd /opt/pdxfusion
    cp .env.prod.example .env
    nano .env            # put a new secret from `openssl rand -base64 32` in NUXT_SESSION_PASSWORD
    mkdir -p data && chown -R 1000:1000 data     # the site runs as user 1000 and must own its data folder
    docker compose up -d --build        # first build takes 5-10 minutes
    docker compose ps                   # both containers "running"
Caddy then fetches the HTTPS certificate on its own. Open your test domain in a browser. (If it isn't ready,
look at `docker compose logs caddy`. The usual cause is DNS not having spread yet.)

> **Heads-up: until step 7 below, the live site looks like plain stock Gancio** (black theme, wide forms, the
> default slider and logo). That is expected, not a failure. The *code* ships in the Docker image, but the
> *look* (CSS, JavaScript, colors, wording) and the basic settings are stored as **data** (in `data/`), which
> is deliberately not copied from your Mac so the live site starts fresh. `design/apply.py` installs them.

### 6. Create the admin account FIRST, before telling anyone
**The first account registered becomes the admin.** Do this right away: open `https://YOUR-TEST-DOMAIN/register`
and sign up with your email and a strong password. Then log in.

### 7. Apply the design and basic settings (on the server)
    cd /opt/pdxfusion
    python3 design/apply.py
    chown -R 1000:1000 data      # harmless to repeat; keeps the data folder owned by the site's user
This sets the name, timezone, moderation, recurring events, fonts and colors (it restarts the site briefly).

### 7b. Check the live site matches your Mac (on your Mac, every time after a deploy)
    python3 design/audit.py https://YOUR-TEST-DOMAIN
It compares the live site's CSS, JavaScript, colors, settings and wording with your local site and lists any
difference ("MISSING" / "DIFFERENT"). Expected differences are only things you set on purpose (like
registration being off). Anything else: run step 7 again and re-check.

### 8. Lock it down (in the site, Admin -> Settings)
- Turn **registration OFF**.
- Check **moderation ON** and **anonymous events ON**.
- Admin -> **SMTP**: enter your email sending details and use the test button.
- Edit the **About** page and replace the placeholder feedback address `hello@pdxfusiondance.com`.
- Add your trusted organizers under Admin -> Users.

### 9. Backups (do this before launch)
    ./backup.sh                 # writes backups/pdxfusion-DATE.tar.gz
Run it daily with cron (`crontab -e`): `15 3 * * * cd /opt/pdxfusion && ./backup.sh`
**and copy the backups off the server** now and then (`rsync` or `scp` to your Mac or other storage). The
site's whole memory (events, accounts, flyers) is in that one folder.

## QA on the live site
Once it is up, test it on your phone like any website: open your test domain. Use
QA-CHECKLIST.md, with these extras that only make sense online: submit an event from your phone with a
real flyer photo, check the share button on a card (it should open your phone's share sheet), check the
page in light and dark mode on the phone, and check that password reset emails arrive.
The site is set to **keep search engines away** during QA (see "Search engines" below).

## Temporary test domain
You need a name that points at your server and can get an HTTPS certificate. In order of preference:
1. **A subdomain of a domain you already own**, e.g. `qa.yourdomain.org`. Free, instant, fully yours.
2. **A cheap throwaway domain** (about $10/year at any registrar). Clean, and keepable as a redirect later.
3. **`sslip.io`** (free, open source, no account): if your server's IP is `203.0.113.5`, the name
   `203-0-113-5.sslip.io` already points at it. Fine for a few days of testing; it can fail to get a
   certificate when many people use it at once. Use options 1-2 for anything longer.
Put the name in `.env` on the server: `DOMAIN=` (no https://) and `BASEURL=https://` + the same name.

**Moving to pdxfusion.com later** (once the owner agrees): point its DNS at the server, change `DOMAIN` and
`BASEURL` in `.env`, run `docker compose up -d`. Your data stays. Because federation is off, nothing
else depends on the domain name. After the move, regenerate your feed/calendar links if you shared them.

## Search engines: off while testing, on at launch
- **Now (QA):** `INDEXING=noindex` in `.env`. Every page is sent with a "do not index" instruction and
  `/robots.txt` says "keep out". Check: `curl -I https://YOUR-TEST-DOMAIN` shows `X-Robots-Tag: noindex`.
- **Hard launch:** set `INDEXING=index`, `DOMAIN` and `BASEURL` to the real domain, run `docker compose up -d`.
  The robots file then welcomes crawlers, hides the login/admin/API pages, and points to the sitemap
  (`/sitemap.xml`, already generated by Gancio, listing the home page, events, places).
- A test domain that was set to noindex never gets listed, so the real domain starts clean.

## Hard-launch SEO checklist
Already good: a sitemap, a page title per event, social-sharing tags (title, image), canonical links, and
structured "Event" data that Google can show as event listings.
To do for a strong launch (tell me when you want these built; none are needed for QA):
1. **Descriptions**: event pages have no meta description yet. Add one built from the title, date and
   venue. Add keywords to the home description (e.g. "fusion dance events in Portland, Oregon").
2. **Structured data**: check Google's Rich Results Test on an event page and fix anything it reports.
3. **Search Console + Bing Webmaster Tools**: verify the domain, submit `/sitemap.xml`.
4. **Speed on phones**: test with PageSpeed Insights, especially flyer images (size them, lazy-load).
5. **Content**: a real About page (who/why/where, the neighborhoods and venues), venue pages, and links from
   local studios, organizers and venues back to the calendar. Local backlinks matter most for a local site.
6. **Google Business-style presence**: consistent site name and description everywhere it is listed.

## Updating the live site later
1. Change things on your Mac and test them.
2. `rsync` the project to the server again (same command as step 4: it leaves data and `.env` alone).
3. On the server: `docker compose up -d --build`
   (design-only changes: `python3 design/apply.py` is enough).
4. Always run `./backup.sh` first.

## Other hosting options (for later)
- **YunoHost**: a friendly open-source server dashboard with one-click apps. It has a Gancio app, but it
  would not include our source changes (recurring-events fix, etc.) unless packaged separately.
- **Akash**: decentralized cloud, fits your values but is more work to set up. Worth a look once
  the site is stable.

## Decisions already made
- **Federation (Mastodon / fediverse) is OFF.** There is no follow button, and the site can't be found from
  Mastodon. It can be turned on later in Admin -> Federation, but think about the domain first: the fediverse
  identity includes the domain name.
- **Fresh data** on the live site: it starts with no test events.
- **Who runs it**: the About page makes no claims about who runs the site. Add a name or contact when ready.
