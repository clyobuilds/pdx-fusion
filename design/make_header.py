#!/usr/bin/env python3
"""Make the site header picture from the logo (design/logo-source.png).

    python3 design/make_header.py    (needs Pillow: pip3 install pillow)

The logo says "PDX FUSION / DANCE.COM / COMMUNITY CALENDAR". The header needs only "PDX FUSION" over "DANCE"
(no ".COM", no "community calendar" line, since the page already shows its subtitle). This script:
  1. clears the words and the small line from the logo, keeping its neon frame and background
  2. redraws the two lines with the same pale letters and red glow, and centers "DANCE" under "PDX FUSION"
Output: design/header-title.webp (the frame included, so it looks like the logo).
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


def main():
    logo = Image.open(SRC).convert("RGB")

    line1 = letter_mask(logo, LINE1)
    line2 = letter_mask(logo, LINE2)
    # "DANCE" moves right so its center matches "PDX FUSION" (the logo centered "DANCE.COM", so this is the same center)
    def center_x(mask):
        bbox = mask.point(lambda v: 255 if v > 128 else 0).getbbox()
        return (bbox[0] + bbox[2]) / 2, bbox
    c1, _ = center_x(line1)
    c2, _ = center_x(line2)
    dx = round(c1 - c2)

    # the full text layer, with DANCE moved
    # the two lines move down a little, so they sit in the middle of the frame (the logo's small line was below them)
    dy = 60
    words = Image.new("L", logo.size, 0)
    words.paste(line1, (LINE1[0], LINE1[1] + dy))
    words.paste(line2, (LINE2[0] + dx, LINE2[1] + dy))

    # clear the old words and the small line, then paint the flat background there
    out = logo.copy()
    # inside CLEAR, every pixel that is not the flat background becomes background (letters and their glow);
    # the rest of the logo (the frame, the flat background) is left as it is, so no lines show at the edges
    diff = ImageChops.difference(out.crop(CLEAR), Image.new("RGB", (CLEAR[2] - CLEAR[0], CLEAR[3] - CLEAR[1]), BG))
    changed = diff.convert("L").point(lambda v: 255 if v > 0 else 0)
    out.paste(Image.new("RGB", changed.size, BG), CLEAR, changed)

    # red glow: a wide soft halo and a tighter one, behind the letters
    halo = words.filter(ImageFilter.GaussianBlur(26)).point(lambda v: min(255, int(v * 1.6)))
    close = words.filter(ImageFilter.GaussianBlur(7)).point(lambda v: min(255, int(v * 1.2)))
    glow_layer = Image.new("RGB", logo.size, GLOW)
    out.paste(glow_layer, (0, 0), ImageChops.lighter(halo.point(lambda v: v * 0.7), close.point(lambda v: v * 0.6)))

    # pale letters on top
    fill_layer = Image.new("RGB", logo.size, FILL)
    out.paste(fill_layer, (0, 0), words)

    out = out.crop(FRAME_CROP)
    # 1200 px wide is plenty for a header (shown at about 600 px, so it stays sharp on phones)
    out = out.resize((1200, round(out.height * 1200 / out.width)), Image.LANCZOS)
    out.save(OUT, quality=90, method=6)
    print(f"wrote {OUT} ({out.width}x{out.height}), DANCE moved {dx} px")


if __name__ == "__main__":
    main()
