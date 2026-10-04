import sys, asyncio
from playwright.async_api import async_playwright
tag = sys.argv[1]
BASE = sys.argv[2].rstrip("/") if len(sys.argv) > 2 and sys.argv[2] else "http://gancio:13120"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for name, vp in [("mobile", {"width": 390, "height": 844}), ("desktop", {"width": 1280, "height": 900})]:
            for mode in ["dark", "light"]:
                ctx = await b.new_context(viewport=vp, device_scale_factor=1, reduced_motion="reduce")
                page = await ctx.new_page()
                await page.goto(BASE + "/", wait_until="networkidle")
                await page.wait_for_timeout(1200)
                is_dark = await page.evaluate("document.querySelector('.v-theme--dark') !== null")
                if (mode == "dark") != is_dark:
                    await page.click("button:has(.mdi-weather-sunny), button:has(.mdi-weather-night)")
                    await page.wait_for_timeout(600)
                await page.screenshot(path=f"/out/{tag}-home-{name}-{mode}.png", full_page=False)
                if name == "mobile" and mode == "light":
                    await page.screenshot(path=f"/out/{tag}-home-mobile-full.png", full_page=True)
                if mode == "light" and BASE.startswith("http://gancio"):
                    await page.goto(BASE + "/event/boom-1", wait_until="networkidle")
                    await page.wait_for_timeout(800)
                    await page.screenshot(path=f"/out/{tag}-event-{name}-{mode}.png", full_page=(name == "mobile"))
                if mode == "dark" or name == "mobile":
                    await page.goto(BASE + "/add", wait_until="networkidle")
                    await page.wait_for_timeout(1000)
                    await page.screenshot(path=f"/out/{tag}-add-{name}-{mode}.png", full_page=False)
                if name == "mobile" and mode == "light" and BASE.startswith("http://gancio"):
                    await page.goto(BASE + "/", wait_until="networkidle")
                    await page.wait_for_timeout(800)
                    cards = page.locator("#home .event")
                    await cards.nth(1).screenshot(path=f"/out/{tag}-card.png")
                await ctx.close()
        await b.close()
asyncio.run(main())
