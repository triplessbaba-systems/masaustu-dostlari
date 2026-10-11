"""README görsellerini üretir:  python tools/readme_assets.py

assets/banner.png  - üst afiş
assets/demo.gif    - masaüstünde gezen dostlar
assets/pets.png    - tüm türler ve renkler
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dostlar import APP_NAME                                         # noqa: E402
from dostlar.gfx import font, make_logo, pixel_image, rgba, rounded  # noqa: E402
from dostlar.sprites import BASE_PALETTE, EFFECTS, SPECIES, SPECIES_ORDER, first_color, palette  # noqa: E402

ASSETS = os.path.join(ROOT, "assets")


def backdrop(w, h):
    return Image.new("RGBA", (w, h), rgba("#14121f"))


def sprite(species, color, frame="walk1", scale=6, facing=1):
    rows = SPECIES[species]["frames"][frame]
    if facing == -1:
        rows = [r[::-1] for r in rows]
    return pixel_image(rows, palette(species, color), scale)


def banner():
    w, h = 1280, 400
    img = backdrop(w, h)
    d = ImageDraw.Draw(img)
    logo = make_logo(84)
    title_f, tag_f = font(64), font(24, bold=False)
    tw = d.textlength(APP_NAME, font=title_f)
    x = (w - (84 + 24 + tw)) / 2
    img.alpha_composite(logo, (int(x), 62))
    d.text((x + 108, 52), APP_NAME, font=title_f, fill=rgba("#f4f2ff"))
    tag = "Windows masaüstünde gezen piksel art evcil hayvanlar"
    d.text(((w - d.textlength(tag, font=tag_f)) / 2, 160), tag, font=tag_f, fill=rgba("#a7a3c9"))

    ground = 350
    d.rectangle((0, ground, w, h), fill=rgba("#1c1a2b"))
    lineup = [("kedi", "Turuncu", "walk1", 1), ("kopek", "Altın", "happy2", 1), ("tavsan", "Beyaz", "walk1", -1),
              ("penguen", "Klasik", "walk1", 1), ("kurbaga", "Yeşil", "happy", -1)]
    step = w / (len(lineup) + 1)
    for i, (sp, col, fr, face) in enumerate(lineup):
        s = sprite(sp, col, fr, 6, face)
        img.alpha_composite(s, (int(step * (i + 1) - s.width / 2), ground - s.height + 6))
    img.convert("RGB").save(os.path.join(ASSETS, "banner.png"), optimize=True)


def demo_gif():
    w, h, scale = 820, 260, 4
    bg = backdrop(w, h)
    d = ImageDraw.Draw(bg)
    taskbar = h - 34
    d.rectangle((0, taskbar, w, h), fill=rgba("#191727"))
    d.line((0, taskbar, w, taskbar), fill=rgba("#3a3660"), width=1)
    # sahte pencere: dostlar onun üstünde de yürüyebilir
    win = (430, 70, 760, taskbar - 24)
    bg.alpha_composite(rounded(win[2] - win[0], win[3] - win[1], 10, fill="#1f1c33", line="#3a3660"), win[:2])
    d.rectangle((win[0] + 1, win[1] + 1, win[2] - 2, win[1] + 22), fill=rgba("#2a2645"))
    for i, col in enumerate(("#ff5d73", "#ffd166", "#4ade80")):
        d.ellipse((win[0] + 12 + i * 16, win[1] + 7, win[0] + 22 + i * 16, win[1] + 17), fill=rgba(col))

    actors = [  # tür, renk, başlangıç x, hız, zemin
        ("kedi", "Siyah", 40, 2.2, taskbar), ("kopek", "Husky", 300, -3.4, taskbar),
        ("tavsan", "Kahve", 120, 2.6, taskbar), ("penguen", "Mavi", 600, -1.2, taskbar),
        ("kurbaga", "Turuncu", 470, 1.6, win[1]),
    ]
    frames = []
    n = 48
    for f in range(n):
        img = bg.copy()
        for sp, col, x0, v, ground in actors:
            info = SPECIES[sp]
            if ground == win[1]:
                lo, hi = win[0], win[2] - 20 * scale
            else:
                lo, hi = 0, w - 20 * scale
            span = hi - lo
            pos = (x0 - lo + v * f * 4) % (2 * span)
            facing = 1 if pos < span else -1
            x = lo + (pos if pos < span else 2 * span - pos)
            if info["hop"]:
                lift = math.sin((f % 8) / 8 * math.pi) * 14
                frame = "walk2" if lift > 4 else "walk1"
            else:
                lift = 0
                frame = "walk1" if (f // 2) % 2 == 0 else "walk2"
            s = sprite(sp, col, frame, scale, facing)
            img.alpha_composite(s, (int(x), int(ground - s.height - lift)))
        if 10 <= f < 30:
            heart = pixel_image(EFFECTS["heart"], BASE_PALETTE, 2)
            img.alpha_composite(heart, (230, int(taskbar - 90 - (f - 10) * 2)))
        frames.append(img.convert("RGB"))
    # tek ortak palet: sprite renkleri bozulmasın
    sheet = Image.new("RGB", (w, h * 4))
    for i, k in enumerate((0, n // 4, n // 2, 3 * n // 4)):
        sheet.paste(frames[k], (0, i * h))
    pal = sheet.quantize(colors=255, method=Image.MEDIANCUT)
    frames = [f.quantize(palette=pal, dither=Image.NONE) for f in frames]
    frames[0].save(os.path.join(ASSETS, "demo.gif"), save_all=True, append_images=frames[1:],
                   duration=90, loop=0)


def pets_sheet():
    scale = 4
    cols = max(len(SPECIES[s]["colors"]) for s in SPECIES_ORDER)
    cw, ch = 20 * scale + 40, 16 * scale + 44
    w, h = cols * cw + 180, len(SPECIES_ORDER) * ch + 30
    img = backdrop(w, h)
    d = ImageDraw.Draw(img)
    for r, sp in enumerate(SPECIES_ORDER):
        y = 20 + r * ch
        d.text((24, y + 26), SPECIES[sp]["title"], font=font(20), fill=rgba("#f4f2ff"))
        for c, col in enumerate(SPECIES[sp]["colors"]):
            x = 170 + c * cw
            img.alpha_composite(sprite(sp, col, "walk1", scale), (x + 20, y))
            label = font(12, bold=False)
            d.text((x + 20 + (20 * scale - d.textlength(col, font=label)) / 2, y + 16 * scale + 6),
                   col, font=label, fill=rgba("#a7a3c9"))
    img.convert("RGB").save(os.path.join(ASSETS, "pets.png"), optimize=True)


if __name__ == "__main__":
    os.makedirs(ASSETS, exist_ok=True)
    random.seed(7)
    banner()
    demo_gif()
    pets_sheet()
    print("assets/ güncellendi")
