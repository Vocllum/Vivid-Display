from __future__ import annotations

from pathlib import Path
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = Path(__file__).resolve().parents[1] / "marketplace"
OUT.mkdir(parents=True, exist_ok=True)

FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Avenir Next.ttc",
    "/System/Library/Fonts/Supplemental/Helvetica Neue.ttc",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
]
FONT = next((Path(p) for p in FONT_CANDIDATES if Path(p).exists()), None)

NAVY = (9, 12, 22)
INK = (13, 18, 31)
CYAN = (91, 230, 255)
BLUE = (86, 142, 255)
VIOLET = (183, 116, 255)
WHITE = (244, 247, 255)
MUTED = (167, 181, 210)
LINE = (58, 76, 112)


def font(size: int, index: int = 0):
    if FONT is None:
        return ImageFont.load_default()
    try:
        return ImageFont.truetype(str(FONT), size=size, index=index)
    except Exception:
        return ImageFont.truetype(str(FONT), size=size)


def gradient(size: tuple[int, int], left=(9, 12, 22), right=(21, 28, 50)) -> Image.Image:
    w, h = size
    im = Image.new("RGB", (w, h), left)
    px = im.load()
    for y in range(h):
        for x in range(w):
            t = 0.7 * x / max(1, w - 1) + 0.3 * y / max(1, h - 1)
            px[x, y] = tuple(int(left[i] * (1 - t) + right[i] * t) for i in range(3))
    return im


def add_glow(base: Image.Image, center: tuple[int, int], radius: int, color: tuple[int, int, int], alpha: int):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x, y = center
    for r in range(radius, 0, -max(2, radius // 24)):
        a = int(alpha * (1 - r / radius) ** 2)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(*color, a))
    base.paste(layer.filter(ImageFilter.GaussianBlur(radius // 12)), (0, 0), layer.filter(ImageFilter.GaussianBlur(radius // 12)))


def rounded_gradient(size: tuple[int, int], radius: int, colors=((91, 230, 255), (183, 116, 255))) -> Image.Image:
    w, h = size
    rgb = Image.new("RGB", (w, h), colors[0])
    px = rgb.load()
    for y in range(h):
        for x in range(w):
            t = min(1.0, (x / max(1, w - 1)) * 0.65 + (y / max(1, h - 1)) * 0.35)
            px[x, y] = tuple(int(colors[0][i] * (1 - t) + colors[1][i] * t) for i in range(3))
    rgba = rgb.convert("RGBA")
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), radius=radius, fill=255)
    rgba.putalpha(mask)
    return rgba


def draw_mark(canvas: Image.Image, box: tuple[int, int, int, int], mono=False, glow=True):
    """Original light-gate mark: a display aperture with a closing dimming shutter."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    scale = min(w, h) / 256
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    stroke = max(2, int(13 * scale))
    radius = int(38 * scale)
    inset = int(32 * scale)
    bx0, by0, bx1, by1 = x0 + inset, y0 + inset, x1 - inset, y1 - inset
    if mono:
        edge = (247, 250, 255, 255)
        d.rounded_rectangle((bx0, by0, bx1, by1), radius=radius, outline=edge, width=stroke)
        slit_y = int(y0 + h * 0.56)
        d.rounded_rectangle((bx0 + int(15 * scale), slit_y - stroke // 2, bx1 - int(15 * scale), slit_y + stroke // 2), radius=stroke // 2, fill=edge)
        d.polygon([(bx1 - int(54 * scale), by0), (bx1, by0), (bx1, by0 + int(54 * scale))], fill=edge)
    else:
        mark = rounded_gradient((max(2, x1 - x0), max(2, y1 - y0)), int(38 * scale))
        mark_draw = ImageDraw.Draw(mark)
        # Carve the aperture and put a luminous shutter across it.
        mark_draw.rounded_rectangle((inset, inset, w - inset, h - inset), radius=radius, outline=(255, 255, 255, 225), width=stroke)
        slit_y = int(h * 0.56)
        mark_draw.rounded_rectangle((inset + int(15 * scale), slit_y - stroke // 2, w - inset - int(15 * scale), slit_y + stroke // 2), radius=stroke // 2, fill=(9, 12, 22, 235))
        mark_draw.rounded_rectangle((inset + int(15 * scale), slit_y - stroke // 2, int(w * 0.61), slit_y + stroke // 2), radius=stroke // 2, fill=(240, 250, 255, 245))
        mark_draw.polygon([(w - int(65 * scale), inset), (w - inset, inset), (w - inset, inset + int(65 * scale))], fill=(8, 12, 23, 235))
        layer.alpha_composite(mark, (x0, y0))
    if mono:
        layer = layer
    if not mono and glow:
        glow_layer = layer.filter(ImageFilter.GaussianBlur(max(2, int(18 * scale))))
        glow_layer.putalpha(glow_layer.getchannel("A").point(lambda p: p // 3))
        canvas.paste(glow_layer, (0, 0), glow_layer)
    canvas.paste(layer, (0, 0), layer)


def app_icon(size: int):
    im = gradient((size, size), NAVY, (18, 26, 51)).convert("RGBA")
    add_glow(im, (int(size * 0.76), int(size * 0.25)), int(size * 0.38), (84, 154, 255), 100)
    draw_mark(im, (int(size * 0.19), int(size * 0.19), int(size * 0.81), int(size * 0.81)), mono=False)
    return im.convert("RGB")


def panel(d: ImageDraw.ImageDraw, box, fill=(18, 25, 42), outline=(49, 66, 101), radius=22, width=2):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def pill(d, xy, text, fill=(31, 48, 78), text_fill=WHITE, f=None):
    f = f or font(26)
    bbox = d.textbbox((0, 0), text, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x, y = xy
    d.rounded_rectangle((x, y, x + tw + 34, y + th + 20), radius=(th + 20) // 2, fill=fill)
    d.text((x + 17, y + 10), text, font=f, fill=text_fill)


def display_card(im: Image.Image, box, value, label, dim=True):
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = box
    panel(d, box, fill=(16, 22, 38), outline=(51, 72, 111), radius=24, width=2)
    inner = (x0 + 22, y0 + 22, x1 - 22, y1 - 22)
    # Simulated desktop luminance surface; deliberately abstract and original.
    d.rounded_rectangle(inner, radius=14, fill=(32, 47, 76))
    d.rectangle((inner[0], inner[1], inner[2], inner[3] // 2 + inner[1] // 2), fill=(67, 113, 178))
    if dim:
        overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(overlay).rounded_rectangle(inner, radius=14, fill=(5, 8, 16, 140))
        im.paste(overlay, (0, 0), overlay)
    d.text((x0 + 28, y1 - 72), label, font=font(24), fill=MUTED)
    d.text((x1 - 112, y1 - 78), f"{value}%", font=font(34), fill=WHITE)


def base_gallery():
    im = gradient((1920, 960), (8, 11, 20), (19, 27, 49)).convert("RGBA")
    add_glow(im, (1500, 180), 480, (57, 142, 255), 85)
    add_glow(im, (1770, 760), 420, (181, 93, 255), 45)
    d = ImageDraw.Draw(im)
    # Fine grid, intentionally quiet.
    for x in range(0, 1920, 80):
        d.line((x, 0, x, 960), fill=(60, 79, 113, 22), width=1)
    for y in range(0, 960, 80):
        d.line((0, y, 1920, y), fill=(60, 79, 113, 22), width=1)
    draw_mark(im, (135, 112, 195, 172), mono=False, glow=False)
    d.text((215, 120), "VIVID DISPLAY", font=font(28), fill=(202, 214, 239))
    return im, d


def gallery_one():
    im, d = base_gallery()
    d.text((135, 280), "Set the light.", font=font(92), fill=WHITE)
    d.text((135, 390), "Keep the hardware.", font=font(92), fill=WHITE)
    d.text((138, 535), "Software dimming for Windows displays,\nright from your Stream Deck.", font=font(38), fill=MUTED, spacing=13)
    pill(d, (138, 720), "No DDC / CI", f=font(23))
    pill(d, (325, 720), "Reversible overlay", f=font(23))
    # Product surface on right.
    panel(d, (1040, 150, 1780, 815), fill=(13, 18, 31), outline=(62, 86, 130), radius=32, width=3)
    d.text((1100, 210), "BRIGHTNESS", font=font(24), fill=(111, 185, 255))
    d.text((1100, 260), "Display under pointer", font=font(36), fill=WHITE)
    display_card(im, (1100, 350, 1450, 660), 35, "PRIMARY DISPLAY")
    display_card(im, (1490, 350, 1720, 660), 65, "SECOND DISPLAY", dim=False)
    d.text((1100, 716), "Software brightness", font=font(25), fill=MUTED)
    d.text((1585, 700), "35%", font=font(52), fill=WHITE)
    return im.convert("RGB")


def gallery_two():
    im, d = base_gallery()
    d.text((135, 275), "One action.", font=font(92), fill=WHITE)
    d.text((135, 385), "Every display.", font=font(92), fill=WHITE)
    d.text((138, 535), "Choose a target, then tap, twist,\nor press your way through the day.", font=font(38), fill=MUTED, spacing=13)
    # Three target rails.
    items = [("ALL DISPLAYS", "01", CYAN), ("PRIMARY", "02", BLUE), ("UNDER POINTER", "03", VIOLET)]
    y = 715
    for i, (label, n, color) in enumerate(items):
        x = 138 + i * 252
        d.rounded_rectangle((x, y, x + 220, y + 64), radius=32, fill=(24, 33, 55), outline=color, width=2)
        d.ellipse((x + 18, y + 18, x + 42, y + 42), fill=color)
        d.text((x + 58, y + 17), label, font=font(21), fill=WHITE)
    # right visual: three display planes with a coherent dimming band.
    panel(d, (1050, 175, 1760, 785), fill=(13, 18, 31), outline=(62, 86, 130), radius=32, width=3)
    for i, value in enumerate([100, 72, 35]):
        x = 1110 + i * 175
        y0 = 285 + i * 74
        display_card(im, (x, y0, x + 470, y0 + 190), value, f"DISPLAY {i+1}", dim=value < 100)
    d.text((1110, 700), "Target-specific state", font=font(26), fill=(111, 185, 255))
    return im.convert("RGB")


def gallery_three():
    im, d = base_gallery()
    d.text((135, 275), "A safer dark.", font=font(92), fill=WHITE)
    d.text((138, 430), "By default.", font=font(92), fill=WHITE)
    d.text((138, 580), "A 5% minimum-brightness floor keeps\nrecovery one press away.", font=font(38), fill=MUTED, spacing=13)
    # Safety settings panel.
    panel(d, (1040, 170, 1775, 790), fill=(13, 18, 31), outline=(62, 86, 130), radius=32, width=3)
    d.text((1100, 230), "BRIGHTNESS", font=font(24), fill=(111, 185, 255))
    d.text((1100, 285), "Minimum brightness protection", font=font(31), fill=WHITE)
    d.text((1100, 350), "Keeps the screen recoverable", font=font(26), fill=MUTED)
    d.rounded_rectangle((1100, 445, 1695, 530), radius=42, fill=(25, 35, 57))
    d.rounded_rectangle((1100, 445, 1412, 530), radius=42, fill=(53, 132, 184))
    d.ellipse((1360, 456, 1519, 519), fill=(245, 249, 255))
    d.text((1100, 595), "SAFE FLOOR", font=font(22), fill=(111, 185, 255))
    d.text((1100, 635), "5%", font=font(76), fill=WHITE)
    pill(d, (1460, 632), "Enabled", fill=(37, 88, 88), text_fill=(177, 246, 229), f=font(23))
    return im.convert("RGB")


def main():
    # Marketplace app icon and plugin artwork.
    app_icon(288).save(OUT / "vivid-icon-288.png")
    app_icon(256).save(OUT / "plugin-256.png")
    app_icon(512).save(OUT / "plugin-512.png")
    app_icon(72).save(OUT / "brightness-key-72.png")
    app_icon(144).save(OUT / "brightness-key-144.png")
    for size, name in [(28, "category-28.png"), (56, "category-56.png"), (20, "brightness-list-20.png"), (40, "brightness-list-40.png")]:
        im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw_mark(im, (1, 1, size - 1, size - 1), mono=True, glow=False)
        im.save(OUT / name)
    gallery_one().save(OUT / "gallery-1.png")
    gallery_two().save(OUT / "gallery-2.png")
    gallery_three().save(OUT / "gallery-3.png")
    print("generated", *sorted(str(p) for p in OUT.glob("*.png")), sep="\n")


if __name__ == "__main__":
    main()
