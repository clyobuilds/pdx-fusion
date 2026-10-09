#!/usr/bin/env python3
"""Make the site header picture from the logo (design/logo-source.png).

    python3 design/make_header.py    (needs Pillow: pip3 install pillow)

The logo says "PDX FUSION / DANCE.COM / COMMUNITY CALENDAR". The header needs "PDX FUSION DANCE" on one line,
with no frame, no ".COM" and no "community calendar" line (the page shows its subtitle). This script cuts the two
words out of the logo and sets them on one line with the same pale letters and red glow, on a transparent background.
Output: design/header-title.webp
"""
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

DESIGN = Path(__file__).resolve().parent
SRC = DESIGN / "logo-source.png"
OUT = DESIGN / "header-title.webp"   # WebP: about a third of the PNG size, embedded in the site CSS by apply.py

# coordinates in the original 2400x1260 image (the logo as shown at 2000x1050, times 1.2)
LINE1 = (480, 330, 1920, 580)        # "PDX FUSION"
LINE2 = (480, 590, 1296, 800)        # "DANCE" (".COM" starts at x=1302, so stop before it)
SMALL = (640, 840, 1760, 940)        # "COMMUNITY CALENDAR" (removed)
CLEAR = (260, 250, 2140, 990)        # the area redrawn (it reaches past the old glow)
BG = (29, 22, 22)                    # the logo's flat dark background (sampled)
FILL = (255, 226, 220)               # pale letter color (sampled)
GLOW = (205, 40, 38)                 # red glow (sampled)
FRAME_CROP = (100, 110, 2300, 1150)  # the neon frame with a small margin


def letter_mask(img, box):
    """Alpha of the pale letters: the glow is red (low green), the letters are pale (high green)."""
    band = img.crop(box).convert("RGB")
    green = band.getchannel("G")
    return green.point(lambda g: max(0, min(255, int((g - 60) * 255 / 170))))


def tight(mask):
    """The mask cut down to the letters themselves."""
    return mask.crop(mask.point(lambda v: 255 if v > 128 else 0).getbbox())


def main():
    logo = Image.open(SRC).convert("RGB")

    # the two words, cut out of the logo: "PDX FUSION" and "DANCE" (".COM" and the small line are left out)
    pdx = tight(letter_mask(logo, LINE1))
    dance = tight(letter_mask(logo, LINE2))

    # one line: PDX FUSION, a word space, DANCE; the letters keep their height (they are the same size in the logo)
    gap = round(pdx.height * 0.45)
    width = pdx.width + gap + dance.width
    top = max(pdx.height, dance.height)
    words = Image.new("L", (width, top), 0)
    words.paste(pdx, (0, 0))
    words.paste(dance, (pdx.width + gap, 0))

    # the red glow (a wide soft halo and a tighter one) behind the pale letters
    pad = 90
    canvas = (width + 2 * pad, top + 2 * pad)
    layer = Image.new("L", canvas, 0)
    layer.paste(words, (pad, pad))
    halo = layer.filter(ImageFilter.GaussianBlur(26)).point(lambda v: min(255, int(v * 1.6 * 0.7)))
    close = layer.filter(ImageFilter.GaussianBlur(7)).point(lambda v: min(255, int(v * 1.2 * 0.6)))
    glow_alpha = ImageChops.lighter(halo, close)
    glow = Image.new("RGBA", canvas, GLOW + (0,))
    glow.putalpha(glow_alpha)
    letters = Image.new("RGBA", canvas, FILL + (0,))
    letters.putalpha(layer)

    out = Image.alpha_composite(glow, letters)
    # cut to the words plus the glow, then scale to 1200 px wide (shown at about 600 px, sharp on phones)
    out = out.crop(out.getbbox())
    out = out.resize((1200, round(out.height * 1200 / out.width)), Image.LANCZOS)
    out.save(OUT, quality=92, method=6)
    (DESIGN / "header-title.aspect").write_text(f"{out.width} / {out.height}\n")  # read by apply.py (no Pillow needed there)
    print(f"wrote {OUT} ({out.width}x{out.height}, one line, transparent)")


if __name__ == "__main__":
    main()
