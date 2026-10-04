"""Check the add-event form's button groups on phone-sized screens, in Chromium AND WebKit (what every iPhone browser uses).
Prints anything cut off. Run from the project folder:  design/phonecheck.sh [https://live-site]"""
import asyncio, sys
from playwright.async_api import async_playwright
BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 and sys.argv[1] else "http://gancio:13120"
SCAN = """() => { const out = [];
  document.querySelectorAll('.v-btn-toggle').forEach(g => { const gr = g.getBoundingClientRect(), vw = document.documentElement.clientWidth;
    g.querySelectorAll('.v-btn').forEach(b => { const r = b.getBoundingClientRect();
      if (r.bottom > gr.bottom + 1 || r.right > gr.right + 1 || r.right > vw + 1 || r.left < -1) out.push(b.textContent.trim()); }); });
  return { cutoff: out, shown: [...document.querySelectorAll('.v-btn-toggle .v-btn')].map(b => b.textContent.trim()) } }"""
async def main():
    async with async_playwright() as p:
        for engine in ("chromium", "webkit"):
            b = await getattr(p, engine).launch()
            for w, h in ((360, 780), (390, 844), (430, 932)):
                page = await (await b.new_context(viewport={"width": w, "height": h}, device_scale_factor=2, has_touch=True, is_mobile=(engine == "webkit"))).new_page()
                await page.goto(BASE + "/add", wait_until="networkidle"); await page.wait_for_timeout(1000)
                await page.locator(".vc-day:not(.is-not-in-month) >> text='20'").first.click()
                a = await page.evaluate(SCAN)
                await page.locator("button:has-text('Recurring')").click(); await page.wait_for_timeout(300)
                await page.locator("button:has-text('Each month')").click(); await page.wait_for_timeout(500)
                c = await page.evaluate(SCAN)
                need = {"Normal", "Multiple days", "Recurring", "Each week", "Every other weeks", "Each month", "Each year", "Each third Tuesday of the month"}
                missing = sorted(need - set(c["shown"]))
                cut = sorted({(x or "(an icon button)") for x in a["cutoff"] + c["cutoff"]})
                print(f"{engine:9s} {w}px: {'OK, nothing cut off' if not cut and not missing else 'PROBLEM: cut off ' + str(cut) + ', missing ' + str(missing)}")
                await page.context.close()
            await b.close()
asyncio.run(main())
