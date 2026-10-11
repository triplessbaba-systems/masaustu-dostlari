"""Pillow ile çizim: yumuşak kenarlı kutular, gradyanlar, logo, sahneler, konuşma balonları."""
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .sprites import UI_ICONS

LOGO_BG = "#ffb703"
LOGO_FG = "#1b1b2a"

# sahne: gökyüzü üst, gökyüzü alt, zemin, süs
STAGES = {
    "kedi":    ("#4a3c94", "#2a2454", "#3a3172", "stars"),
    "kopek":   ("#f59e6c", "#7a4f93", "#56387a", "sun"),
    "tavsan":  ("#62b6d9", "#a8dcc0", "#5c9c6c", "clouds"),
    "penguen": ("#5d9ad8", "#cfe6ff", "#f2f8ff", "snow"),
    "kurbaga": ("#2d6b70", "#5ea596", "#2f6a4f", "pond"),
}


def rgba(c, a=255):
    if isinstance(c, tuple):
        return c if len(c) == 4 else c + (a,)
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) + (a,)


def vgradient(w, h, top, bottom):
    mask = Image.linear_gradient("L").resize((max(1, w), max(1, h)))
    return Image.composite(Image.new("RGBA", mask.size, rgba(bottom)),
                           Image.new("RGBA", mask.size, rgba(top)), mask)


def hgradient(w, h, left, right):
    mask = Image.linear_gradient("L").rotate(90).resize((max(1, w), max(1, h)))
    return Image.composite(Image.new("RGBA", mask.size, rgba(right)),
                           Image.new("RGBA", mask.size, rgba(left)), mask)


def _mask(w, h, r, ss=3):
    m = Image.new("L", (w * ss, h * ss), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w * ss - 1, h * ss - 1), r * ss, fill=255)
    return m.resize((w, h), Image.LANCZOS)


def rounded(w, h, r, fill=None, grad=None, hgrad=None, line=None, lw=1):
    """Yumuşak kenarlı yuvarlak kutu."""
    w, h = max(1, int(w)), max(1, int(h))
    r = min(int(r), w // 2, h // 2)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if grad or hgrad or fill:
        if grad:
            body = vgradient(w, h, *grad)
        elif hgrad:
            body = hgradient(w, h, *hgrad)
        else:
            body = Image.new("RGBA", (w, h), rgba(fill))
        alpha = Image.new("L", (w, h), 0)
        alpha.paste(body.getchannel("A"), mask=_mask(w, h, r))
        body.putalpha(alpha)
        out.alpha_composite(body)
    if line:
        ss = 3
        ring = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
        ImageDraw.Draw(ring).rounded_rectangle((0, 0, w * ss - 1, h * ss - 1), r * ss,
                                               outline=rgba(line), width=lw * ss)
        out.alpha_composite(ring.resize((w, h), Image.LANCZOS))
    return out


def shadow(w, h, r, color="#000000", alpha=90, blur=10, dy=4, m=None):
    """Bir kutunun altına konacak yumuşak gölge. (resim, kenar payı) döner."""
    m = m if m is not None else blur * 2 + abs(dy)
    img = Image.new("RGBA", (int(w) + 2 * m, int(h) + 2 * m), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle((m, m + dy, m + w, m + h + dy), r, fill=rgba(color, alpha))
    return img.filter(ImageFilter.GaussianBlur(blur)), m


def make_logo(size, bg=LOGO_BG, fg=LOGO_FG):
    """Sade logo: turuncu yuvarlak kare üstünde pati izi (bg=None: sadece pati)."""
    big = 1024
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if bg:
        d.rounded_rectangle((0, 0, big - 1, big - 1), radius=230, fill=bg)
    d.ellipse((322, 470, 702, 800), fill=fg)                         # taban
    for cx, cy in ((240, 400), (400, 260), (624, 260), (784, 400)):  # parmaklar
        d.ellipse((cx - 85, cy - 105, cx + 85, cy + 105), fill=fg)
    return img.resize((size, size), Image.LANCZOS)


def pixel_image(rows, pal, scale):
    """Piksel art satırlarını RGBA resme çevir (boş pikseller tam şeffaf)."""
    w, h = max(len(r) for r in rows), len(rows)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = img.load()
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in pal:
                px[x, y] = rgba(pal[ch])
    return img.resize((w * scale, h * scale), Image.NEAREST) if scale > 1 else img


def ui_icon(name, color, scale):
    return pixel_image(UI_ICONS[name], {"X": color}, scale)


_fonts = {}


def font(px, bold=True):
    key = (px, bold)
    if key not in _fonts:
        windir = os.environ.get("WINDIR", r"C:\Windows")
        try:
            _fonts[key] = ImageFont.truetype(
                os.path.join(windir, "Fonts", "segoeuib.ttf" if bold else "segoeui.ttf"), px)
        except OSError:
            _fonts[key] = ImageFont.load_default()
    return _fonts[key]


def bubble(text, u):
    """Piksel kenarlı konuşma balonu. Kenarlar keskin (şeffaf pencerede saçak olmasın)."""
    f = font(6 * u)
    l, t, r, b = f.getbbox(text)
    tw, th = r - l, b - t
    bw, bh = tw + 10 * u, th + 8 * u
    tail = 3 * u
    img = Image.new("RGBA", (bw, bh + tail), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    K, W = rgba("#2b1d14"), rgba("#fffdf7")
    d.rectangle((u, 0, bw - 1 - u, bh - 1), fill=K)
    d.rectangle((0, u, bw - 1, bh - 1 - u), fill=K)
    d.rectangle((2 * u, u, bw - 1 - 2 * u, bh - 1 - u), fill=W)
    d.rectangle((u, 2 * u, bw - 1 - u, bh - 1 - 2 * u), fill=W)
    x0 = bw // 2 - 2 * u
    d.polygon([(x0, bh - u - 1), (x0 + 4 * u, bh - u - 1), (x0, bh + tail - 1)], fill=K)
    d.polygon([(x0 + u, bh - 2 * u), (x0 + 3 * u - 1, bh - 2 * u), (x0 + u, bh + tail - 1 - 2 * u)], fill=W)
    d.text((5 * u - l, 4 * u - t), text, font=f, fill=K)
    return img


def toggle(w, h, on, on_color, off_color):
    img = rounded(w, h, h // 2, fill=on_color if on else off_color)
    d = h - 6
    knob = rounded(d, d, d // 2, fill="#ffffff")
    img.alpha_composite(knob, (w - d - 3 if on else 3, 3))
    return img


def stage_image(species, w, h, r, ui, ground_ratio=0.78):
    """Türe özel arka plan sahnesi (yıldızlı gece, gün batımı, çayır, kar, gölet)."""
    top, bot, ground, decor = STAGES[species]
    w, h = int(w), int(h)
    img = vgradient(w, h, top, bot)
    d = ImageDraw.Draw(img, "RGBA")
    rnd = random.Random(species)
    gy = int(h * ground_ratio)
    k = h / 270          # sahne boyutuna göre süs ölçeği

    def dot(x, y, rad, col):
        d.ellipse((x - rad, y - rad, x + rad, y + rad), fill=col)

    if decor == "stars":
        for _ in range(int(34 * w / 320)):
            dot(rnd.randrange(w), rnd.randrange(max(1, int(gy * 0.85))), rnd.choice([1, 1, 2]) * ui,
                (255, 255, 255, rnd.randint(80, 220)))
        dot(w * 0.80, h * 0.20, 20 * ui * k, (255, 244, 214, 240))
        dot(w * 0.80 - 9 * ui * k, h * 0.20 - 6 * ui * k, 17 * ui * k, rgba(top))      # hilal
    elif decor == "sun":
        for i, a in enumerate((40, 60, 90, 255)):
            dot(w * 0.72, gy - 12 * ui * k, (60 - i * 12) * ui * k, (255, 214, 120, a))
    elif decor == "clouds":
        for cx, cy, s in ((0.22, 0.22, 1.0), (0.72, 0.14, 0.75), (0.55, 0.38, 0.55)):
            for ox, oy, rad in ((-18, 4, 14), (0, -6, 20), (20, 4, 15), (2, 8, 16)):
                dot(w * cx + ox * s * ui * k, h * cy + oy * s * ui * k, rad * s * ui * k,
                    (255, 255, 255, 215))
    elif decor == "snow":
        for _ in range(int(40 * w / 320)):
            dot(rnd.randrange(w), rnd.randrange(max(1, gy)), rnd.choice([1, 2, 2, 3]) * ui,
                (255, 255, 255, rnd.randint(120, 230)))

    d.ellipse((-w * 0.25, gy, w * 1.25, gy + h * 0.7), fill=rgba(ground))     # tepe
    if decor == "pond":
        for _ in range(9):
            dot(rnd.randrange(w), rnd.randrange(max(1, int(gy * 0.9))), rnd.choice([2, 3, 4]) * ui,
                (220, 255, 245, 90))
        for x in (0.15, 0.85):
            d.ellipse((w * x - 26 * ui * k, gy + 22 * ui * k, w * x + 26 * ui * k, gy + 34 * ui * k),
                      fill=(70, 160, 90, 255))
    elif decor == "snow":
        for x in (0.12, 0.88):
            d.ellipse((w * x - 30 * ui * k, gy + 14 * ui * k, w * x + 30 * ui * k, gy + 30 * ui * k),
                      fill=(214, 232, 250, 255))

    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((w / 2 - 58 * ui * k, gy + 4 * ui * k, w / 2 + 58 * ui * k, gy + 16 * ui * k),
                               fill=(0, 0, 0, 70))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(max(1, 4 * ui * k))))
    img.putalpha(_mask(w, h, int(r)))
    return img
