"""Ana pencere: Sahiplen, Dostlarım, Başarımlar ve Ayarlar sayfaları.

Tüm arayüz tek bir Canvas üzerine Pillow ile çizilir; böylece yuvarlak köşeler,
gölgeler ve gradyanlar standart Tk bileşenlerinden bağımsız olarak pürüzsüz görünür.
"""
import math
import random
import time
import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox

from PIL import Image, ImageDraw, ImageTk

from . import APP_NAME, __version__, gfx
from .sprites import SPECIES, SPECIES_ORDER, UI_ICONS, first_color
from .store import ACHIEVEMENTS, xp_needed

C = dict(
    bg="#0f0e17", side="#13111e", side_line="#211e32",
    surface="#191727", surface2="#221f34", line="#28253d", line2="#3a3660",
    hover="#1c1a2b", active="#262241",
    fg="#f4f2ff", fg2="#c9c5e6", muted="#8f8bb0", faint="#5f5b80", ink="#17130a",
    accent="#ffb703", accent2="#ff8a1f", accent_hi="#ffd166", accent_soft="#33270f",
    green="#4ade80", red="#ff5d73", purple="#a78bfa", track="#2a2742",
)
NEEDS = [("food", "Tokluk", "fish", "#fb923c"),
         ("joy", "Mutluluk", "heart", "#f472b6"),
         ("energy", "Enerji", "bolt", "#facc15")]
NAV = [("adopt", "Sahiplen", "paw"), ("pets", "Dostlarım", "heart"),
       ("achievements", "Başarımlar", "trophy"), ("settings", "Ayarlar", "gear")]
PAGE_INFO = {"adopt": "Sahiplen", "pets": "Dostlarım", "achievements": "Başarımlar", "settings": "Ayarlar"}
BTN = {
    "primary": dict(normal=dict(fill=C["accent"]), hover=dict(fill=C["accent_hi"]), fg=C["ink"], shadow=None),
    "secondary": dict(normal=dict(fill=C["surface2"], line=C["line"]),
                      hover=dict(fill="#2a2740", line=C["line2"]), fg=C["fg"], shadow=None),
    "ghost": dict(normal=None, hover=dict(fill=C["surface2"]), fg=C["fg2"], shadow=None),
    "soft": dict(normal=dict(fill="#24213a"), hover=dict(fill="#34305a"), fg=C["fg2"], shadow=None),
    "danger": dict(normal=dict(fill="#2a1f33"), hover=dict(fill=C["red"]), fg=C["fg"], shadow=None),
}


def content_bg(w, h, side):
    img = Image.new("RGBA", (w, h), gfx.rgba(C["bg"]))
    ImageDraw.Draw(img).rectangle((0, 0, side - 1, h), fill=gfx.rgba(C["side"]))
    ImageDraw.Draw(img).line((side - 1, 0, side - 1, h), fill=gfx.rgba(C["side_line"]))
    return img


def fmt_duration(sec):
    m = int(sec // 60)
    return f"{m // 60} sa {m % 60} dk" if m >= 60 else f"{m} dk"


class Hub:
    def __init__(self, app):
        self.app = app
        self.root = app.root
        self.ui = app.ui
        self.px = lambda n: int(round(n * self.ui))
        self.photos, self.fonts = {}, {}
        self.page = "adopt"
        self.species = SPECIES_ORDER[0]
        self.color = first_color(self.species)
        self.name_var = tk.StringVar(value=random.choice(SPECIES[self.species]["names"]))
        self.t = 0
        self.cheer = 0
        self.hearts, self.toasts = [], []
        self.toast_seq = 0
        self.scroll = 0
        self.slide = 0
        self.live, self.cards = {}, {}
        self.hover_card = None
        self.stage_box = None
        self.titled = False
        fams = set(tkfont.families())
        self.f_display = next((f for f in ("Segoe UI Variable Display", "Segoe UI") if f in fams), "TkDefaultFont")
        self.f_text = next((f for f in ("Segoe UI Variable Text", "Segoe UI") if f in fams), "TkDefaultFont")
        self.card_scale = max(2, round(3 * self.ui))
        self.big_scale = max(4, round(8 * self.ui))
        self.mini_scale = max(3, round(4 * self.ui))
        self.build()
        self.show("adopt", animate=False)
        self.tick()

    # ---------------------------------------------------------------- yardımcılar
    def f(self, size, weight="normal", display=False):
        return (self.f_display if display else self.f_text, size, weight)

    def measure(self, text, font):
        if font not in self.fonts:
            self.fonts[font] = tkfont.Font(family=font[0], size=font[1], weight=font[2])
        return self.fonts[font].measure(text)

    def photo(self, key, make):
        if key not in self.photos:
            self.photos[key] = ImageTk.PhotoImage(make())
        return self.photos[key]

    def clear_img(self, w, h):
        return self.photo(("clear", w, h), lambda: Image.new("RGBA", (w, h), (0, 0, 0, 0)))

    def icon(self, name, color, scale=None):
        scale = scale or max(2, round(2 * self.ui))
        return self.photo(("icon", name, color, scale), lambda: gfx.ui_icon(name, color, scale))

    def icon_w(self, name, scale):
        return len(UI_ICONS[name][0]) * scale

    def hand(self, item):
        self.c.tag_bind(item, "<Enter>", lambda e: self.c.config(cursor="hand2"), add="+")
        self.c.tag_bind(item, "<Leave>", lambda e: self.c.config(cursor=""), add="+")

    def box(self, x, y, w, h, r, tags=("page",), shadow=None, state="disabled", **style):
        """Gölgeli yuvarlak kutu çizer, gövde öğesini döndürür."""
        x, y, w, h, r = int(x), int(y), int(w), int(h), int(r)
        if shadow:
            col, a, blur, dy = shadow
            blur, dy = self.px(blur), self.px(dy)
            m = blur * 2 + abs(dy)
            img = self.photo(("shadow", w, h, r, col, a, blur, dy),
                             lambda: gfx.shadow(w, h, r, col, a, blur, dy, m)[0])
            self.c.create_image(x - m, y - m, anchor="nw", image=img, state="disabled", tags=tags)
        key = ("box", w, h, r) + tuple(sorted(style.items()))
        img = self.photo(key, lambda: gfx.rounded(w, h, r, **style))
        return self.c.create_image(x, y, anchor="nw", image=img, state=state, tags=tags)

    def text(self, x, y, text, size=10, weight="normal", color=None, anchor="nw",
             display=False, tags=("page",), **kw):
        return self.c.create_text(x, y, text=text, font=self.f(size, weight, display),
                                  fill=color or C["fg"], anchor=anchor, tags=tags,
                                  state="disabled", **kw)

    def label(self, x, y, text, tags=("page",), anchor="nw"):
        return self.text(x, y, text, 9, "bold", C["muted"], anchor=anchor, tags=tags)

    def button(self, x, y, w, h, text, cmd, style="secondary", icon=None, size=10,
               tags=("page",), tip=None, r=None):
        c, px = self.c, self.px
        x, y, w, h = int(x), int(y), int(w), int(h)
        st = BTN[style]
        r = r if r is not None else min(px(12), h // 2)
        if st["shadow"]:
            col, a, blur, dy = st["shadow"]
            self.box(x, y, w, h, r, tags, shadow=(col, a, blur, dy))
        imgs = {k: self.photo(("btn", style, k, w, h, r),
                              lambda k=k: gfx.rounded(w, h, r, **st[k]) if st[k]
                              else Image.new("RGBA", (w, h), (0, 0, 0, 0)))
                for k in ("normal", "hover")}
        body = c.create_image(x, y, anchor="nw", image=imgs["normal"], tags=tags)
        fg = st["fg"]
        font = self.f(size, "bold")
        isc = max(2, round(2 * self.ui))
        tw = self.measure(text, font) if text else 0
        iw = self.icon_w(icon, isc) if icon else 0
        gap = px(8) if text and icon else 0
        sx = x + (w - tw - iw - gap) / 2
        if icon:
            c.create_image(sx, y + h / 2, anchor="w", image=self.icon(icon, fg, isc),
                           state="disabled", tags=tags)
            sx += iw + gap
        if text:
            c.create_text(sx, y + h / 2, anchor="w", text=text, font=font, fill=fg,
                          state="disabled", tags=tags)

        def enter(e):
            c.itemconfig(body, image=imgs["hover"])
            c.config(cursor="hand2")
            if tip:
                self.show_tip(tip, x + w / 2, y - px(6), y + h + px(6))

        def leave(e):
            c.itemconfig(body, image=imgs["normal"])
            c.config(cursor="")
            self.hide_tip()

        def click(e):
            self.hide_tip()
            cmd()

        c.tag_bind(body, "<Enter>", enter)
        c.tag_bind(body, "<Leave>", leave)
        c.tag_bind(body, "<Button-1>", click)
        return body

    def show_tip(self, text, cx, above, below):
        """Butonun üstünde, yer yoksa altında küçük bir ipucu göster."""
        self.hide_tip()
        px = self.px
        font = self.f(9, "bold")
        w, h = self.measure(text, font) + px(20), px(28)
        top = above - h if above - h > px(4) else below
        cx = min(max(cx, w / 2 + px(4)), self.W - w / 2 - px(4))
        self.box(cx - w / 2, top, w, h, px(8), tags=("tip",), fill="#0a0910", line=C["line2"])
        self.c.create_text(cx, top + h / 2, text=text, font=font, fill=C["fg"],
                           tags=("tip",), state="disabled")
        self.c.tag_raise("tip")

    def hide_tip(self):
        self.c.delete("tip")

    def bar(self, x, y, w, h, frac, color, tags=("page",)):
        self.box(x, y, w, h, h // 2, tags, fill=C["track"])
        item = self.c.create_image(int(x), int(y), anchor="nw", tags=tags, state="disabled")
        self.set_bar(item, w, h, frac, color)
        return item

    def set_bar(self, item, w, h, frac, color):
        w, h = int(w), int(h)
        fw = int(round(w * max(0.0, min(1.0, frac))))
        if fw <= 0:
            self.c.itemconfig(item, image="")
            return
        fw = max(fw, h)
        self.c.itemconfig(item, image=self.photo(("bar", fw, h, color),
                                                 lambda: gfx.rounded(fw, h, h // 2, fill=color)))

    def toggle(self, x, y, value, cmd, tags=("page",)):
        w, h = self.px(44), self.px(24)
        img = self.photo(("toggle", value, w, h),
                         lambda: gfx.toggle(w, h, value, C["accent"], "#38345a"))
        item = self.c.create_image(int(x), int(y), anchor="nw", image=img, tags=tags)
        self.c.tag_bind(item, "<Button-1>", lambda e: cmd(not value))
        self.hand(item)
        return w

    def segmented(self, x, y, options, value, cmd, tags=("page",)):
        px = self.px
        sw, h = px(58), px(34)
        w = sw * len(options) + px(8)
        self.box(x, y, w, h, px(10), tags, fill=C["surface2"], line=C["line"])
        for i, (val, label) in enumerate(options):
            sx = x + px(4) + i * sw
            active = val == value
            if active:
                self.box(sx, y + px(4), sw, h - px(8), px(7), tags, fill=C["active"], line=C["line2"])
            hit = self.c.create_image(int(sx), int(y), anchor="nw", image=self.clear_img(sw, h), tags=tags)
            self.c.tag_bind(hit, "<Button-1>", lambda e, v=val: cmd(v))
            self.hand(hit)
            self.text(sx + sw / 2, y + h / 2, label, 9, "bold",
                      C["accent"] if active else C["fg2"], anchor="center", tags=tags)
        return w

    # ---------------------------------------------------------------- iskelet
    @property
    def X0(self):
        return self.px(264)

    @property
    def X1(self):
        return self.px(1088)

    def build(self):
        px, root = self.px, self.root
        root.title(APP_NAME)
        root.configure(bg=C["bg"])
        root.resizable(False, False)
        root.protocol("WM_DELETE_WINDOW", self.close)
        W, H = px(1120), px(700)
        self.W, self.H, self.SIDE = W, H, px(232)
        c = self.c = tk.Canvas(root, width=W, height=H, bg=C["bg"], highlightthickness=0, bd=0)
        c.pack()
        c.create_image(0, 0, anchor="nw", image=self.photo("bg", lambda: content_bg(W, H, self.SIDE)))
        c.bind("<MouseWheel>", self.on_wheel)

        # marka
        c.create_image(px(22), px(28), anchor="nw", image=self.photo("logo32", lambda: gfx.make_logo(px(32))))
        self.text(px(66), px(44), APP_NAME, 12, "bold", display=True, anchor="w", tags=("static",))

        # hızlı eylemler
        x = self.X1
        for text, icon, cmd, tip in (("Hepsini Çağır", "target", self.app.gather, "Tüm dostlar ortada toplansın"),
                                     ("Top At", "ball", self.app.throw_ball, "Masaüstüne bir top bırak"),
                                     ("Mama Ver", "fish", self.app.drop_fish, "Masaüstüne balık yağdır")):
            w = self.measure(text, self.f(9, "bold")) + px(52)
            x -= w
            self.button(x, px(32), w, px(38), text, cmd, icon=icon, size=9, tags=("static",), tip=tip)
            x -= px(10)

        self.entry = tk.Entry(c, textvariable=self.name_var, font=self.f(12), bg=C["surface2"],
                              fg=C["fg"], insertbackground=C["accent"], relief="flat", bd=0,
                              highlightthickness=0, selectbackground=C["accent2"])
        self.entry.bind("<Return>", lambda e: self.adopt())
        self.entry.bind("<FocusIn>", lambda e: self.field_focus(True))
        self.entry.bind("<FocusOut>", lambda e: self.field_focus(False))
        self.draw_nav()
        self.draw_status()

    def draw_nav(self):
        c, px = self.c, self.px
        c.delete("nav")
        y = px(88)
        w, h = px(208), px(40)
        for key, label, icon in NAV:
            x = px(12)
            active = key == self.page
            if active:
                body = self.box(x, y, w, h, px(8), ("nav",), state="normal", fill=C["active"])
            else:
                body = c.create_image(x, y, anchor="nw", image=self.clear_img(w, h), tags=("nav",))
                hov = self.photo(("navhover", w, h), lambda: gfx.rounded(w, h, px(8), fill=C["hover"]))
                clear = self.clear_img(w, h)
                c.tag_bind(body, "<Enter>", lambda e, b=body, i=hov: (c.itemconfig(b, image=i), c.config(cursor="hand2")))
                c.tag_bind(body, "<Leave>", lambda e, b=body, i=clear: (c.itemconfig(b, image=i), c.config(cursor="")))
            c.tag_bind(body, "<Button-1>", lambda e, k=key: self.show(k))
            col = C["fg"] if active else C["muted"]
            c.create_image(x + px(16), y + h / 2, anchor="w", image=self.icon(icon, col),
                           state="disabled", tags=("nav",))
            self.text(x + px(44), y + h / 2, label, 10, "bold" if active else "normal", C["fg"] if active else C["fg2"],
                      anchor="w", tags=("nav",))
            badge = None
            if key == "pets" and self.app.pets:
                badge = str(len(self.app.pets))
            elif key == "achievements":
                badge = f"{len(self.app.store.unlocked)}/{len(ACHIEVEMENTS)}"
            if badge:
                self.text(x + w - px(14), y + h / 2, badge, 9, color=C["muted"], anchor="e", tags=("nav",))
            y += h + px(4)

    def draw_status(self):
        c, px, H = self.c, self.px, self.H
        c.delete("status")
        tags = ("status",)
        x, w = px(28), px(176)
        c.create_line(px(12), H - px(118), px(220), H - px(118), fill=C["side_line"], tags=tags)
        self.text(x, H - px(92), "Dostları göster", 10, color=C["fg2"], anchor="w", tags=tags)
        self.toggle(x + w - px(44), H - px(104), not self.app.hidden,
                    lambda v: (self.app.set_hidden(not v), self.draw_status()), tags=tags)
        self.button(px(12), H - px(62), px(208), px(40), "Çıkış", self.app.quit, style="ghost",
                    size=10, tags=tags)

    def header(self, count=None):
        title = PAGE_INFO[self.page]
        font = self.f(22, "bold", True)
        self.text(self.X0, self.px(51), title, 22, "bold", display=True, anchor="w")
        if count is not None:
            self.text(self.X0 + self.measure(title, font) + self.px(12), self.px(53), str(count), 16,
                      color=C["faint"], display=True, anchor="w")

    # ---------------------------------------------------------------- gezinme
    def show(self, page, animate=True):
        if page != self.page:
            self.scroll = 0
        self.page = page
        self.hide_tip()
        self.c.delete("page")
        self.live, self.cards, self.hearts = {}, {}, []
        self.stage_box = None
        self.hover_card = None
        self.c.config(cursor="")
        self.draw_nav()
        getattr(self, "page_" + page)()
        self.c.tag_raise("toast")
        if animate:
            self.slide = self.px(26)
            self.c.move("page", self.slide, 0)
            self.animate_slide()

    def animate_slide(self):
        if self.slide > 0:
            d = max(1, math.ceil(self.slide * 0.3))
            self.c.move("page", -d, 0)
            self.slide -= d
            self.root.after(15, self.animate_slide)

    def refresh(self):
        """Dost listesi ya da seviyeler değişince çağrılır."""
        self.draw_nav()
        self.draw_status()
        if self.page in ("pets", "achievements"):
            self.show(self.page, animate=False)
        elif self.page == "adopt" and self.stage_box:
            self.c.itemconfig(self.count_text, text=self.count_label())

    def on_second(self):
        if not self.root.winfo_viewable() or self.page != "pets":
            return
        for p in self.app.pets:
            refs = self.live.get(p.id)
            if not refs:
                continue
            if refs["level"] != p.level:
                self.show("pets", animate=False)
                return
            for key, label, icon, color in NEEDS:
                item, w, h, pct = refs["needs"][key]
                v = getattr(p, key)
                self.set_bar(item, w, h, v / 100, color)
                self.c.itemconfig(pct, text=f"{int(v)}")
            item, w, h = refs["xpbar"]
            self.set_bar(item, w, h, p.xp / xp_needed(p.level), C["purple"])
            self.c.itemconfig(refs["sub"], text=self.pet_line(p))

    def on_wheel(self, e):
        if self.page == "pets":
            rows = math.ceil(len(self.app.pets) / 2)
            new = max(0, min(self.scroll + (-1 if e.delta > 0 else 1), max(0, rows - 3)))
            if new != self.scroll:
                self.scroll = new
                self.show("pets", animate=False)

    def close(self):
        if self.app.pets or self.app.tray:
            self.root.withdraw()
        else:
            self.app.quit()

    # ---------------------------------------------------------------- bildirimler
    def toast(self, title, body="", icon=None):
        if not self.root.winfo_viewable():
            return False
        c, px = self.c, self.px
        self.toast_seq += 1
        tag = f"toast{self.toast_seq}"
        tags = ("toast", tag)
        w, h = px(300), px(60) if body else px(42)
        x = self.X1 - w
        y = px(88) + len(self.toasts) * (px(60) + px(8))
        self.box(x, y, w, h, px(8), tags, fill="#23203a", line=C["line2"])
        if body:
            self.text(x + px(16), y + px(12), title, 10, "bold", tags=tags)
            self.text(x + px(16), y + px(33), body, 9, color=C["muted"], tags=tags, width=w - px(32))
        else:
            self.text(x + px(16), y + h / 2, title, 10, "bold", anchor="w", tags=tags)
        c.tag_raise("toast")
        offset = px(40)
        c.move(tag, offset, 0)
        self.toasts.append([tag, 28, offset])
        self.animate_toasts()
        return True

    def animate_toasts(self):
        busy = False
        for t in self.toasts:
            if t[2] > 0:
                d = max(1, math.ceil(t[2] * 0.3))
                self.c.move(t[0], -d, 0)
                t[2] -= d
                busy = True
        if busy:
            self.root.after(15, self.animate_toasts)

    def expire_toasts(self):
        changed = False
        for t in self.toasts[:]:
            t[1] -= 1
            if t[1] <= 0:
                self.c.delete(t[0])
                self.toasts.remove(t)
                changed = True
        if changed:
            h = self.px(68)
            for i, t in enumerate(self.toasts):
                bbox = self.c.bbox(t[0])
                if bbox:
                    target = self.px(88) + i * h
                    current = self.c.coords(self.c.find_withtag(t[0])[0])[1]
                    self.c.move(t[0], 0, target - current)

    # ---------------------------------------------------------------- Sahiplen
    def count_label(self):
        n = len(self.app.pets)
        return f"Masaüstünde {n} dost var" if n else ""

    def page_adopt(self):
        c, px = self.c, self.px
        X0, X1 = self.X0, self.X1
        self.header()
        sp = SPECIES[self.species]

        # vitrin kartı
        hx, hy, hw, hh = X0, px(112), px(400), px(556)
        self.box(hx, hy, hw, hh, px(12), fill=C["surface"], line=C["line"])
        sx, sy, sw, sh = hx + px(10), hy + px(10), hw - px(20), px(262)
        self.stage_box = (sx, sy, sx + sw, sy + sh)
        self.stage_gy = int(sh * 0.78)
        img = self.photo(("stage", self.species, sw, sh),
                         lambda: gfx.stage_image(self.species, sw, sh, px(8), self.ui))
        stage = c.create_image(sx, sy, anchor="nw", image=img, tags=("page",))
        self.stage_pet = c.create_image(sx + sw / 2, sy + self.stage_gy + px(10), anchor="s", tags=("page",))
        for item in (stage, self.stage_pet):
            c.tag_bind(item, "<Button-1>", lambda e: self.do_cheer())
            self.hand(item)

        iy = sy + sh + px(20)
        ix = hx + px(24)
        self.text(ix, iy, sp["title"], 18, "bold", display=True)
        self.text(ix, iy + px(36), sp["desc"], 10, color=C["muted"], width=hw - px(48))
        self.text(ix, iy + px(86), ", ".join(sp["traits"]), 10, color=C["fg2"])
        for i, (name, val) in enumerate(sp["stats"].items()):
            ry = iy + px(132) + i * px(26)
            self.text(ix, ry, name, 10, color=C["fg2"], anchor="w")
            for k in range(5):
                self.box(ix + px(110) + k * px(16), ry - px(5), px(10), px(10), px(2),
                         fill=C["fg2"] if k < val else C["track"])

        # sağ kolon
        rx, rw = X0 + px(424), X1 - (X0 + px(424))
        self.label(rx, px(112), "Tür")
        cw, ch, gx, gy = (rw - px(32)) // 3, px(106), px(16), px(14)
        for i, key in enumerate(SPECIES_ORDER + ["random"]):
            x = rx + (i % 3) * (cw + gx)
            y = px(136) + (i // 3) * (ch + gy)
            body = self.box(x, y, cw, ch, px(10), state="normal", fill=C["surface"], line=C["line"])
            if key == "random":
                c.create_image(x + cw / 2, y + px(38), image=self.icon("dice", C["muted"], max(3, round(4 * self.ui))),
                               state="disabled", tags=("page",))
                spr = None
                title, sub = "Rastgele", ""
            else:
                spr = c.create_image(x + cw / 2, y + px(14), anchor="n", state="disabled", tags=("page",),
                                     image=self.app.img(key, first_color(key), "walk1", 1, self.card_scale))
                title, sub = SPECIES[key]["title"], f"{len(SPECIES[key]['colors'])} renk"
            self.text(x + cw / 2, y + px(76), title, 10, "bold", anchor="center")
            self.text(x + cw / 2, y + px(93), sub, 8, color=C["faint"], anchor="center")
            c.tag_bind(body, "<Enter>", lambda e, k=key: self.set_hover(k))
            c.tag_bind(body, "<Leave>", lambda e: self.set_hover(None))
            c.tag_bind(body, "<Button-1>", lambda e, k=key: self.pick(k))
            self.cards[key] = (body, spr, cw, ch)
        self.update_cards()

        self.label(rx, px(388), "Renk")
        self.text(rx + rw, px(388), self.color, 9, color=C["fg2"], anchor="ne")
        colors = sp["colors"]
        d, ring = px(34), px(44)
        for i, (name, cpal) in enumerate(colors.items()):
            cx, cy = rx + d / 2 + px(5) + i * (d + px(16)), px(432)
            if name == self.color:
                c.create_image(cx, cy, tags=("page",), state="disabled", image=self.photo(
                    ("ring", ring), lambda: gfx.rounded(ring, ring, ring // 2, line=C["accent"], lw=2)))
            dot = c.create_image(cx, cy, tags=("page",), image=self.photo(
                ("swatch", cpal["O"], d), lambda col=cpal["O"]: gfx.rounded(
                    d, d, d // 2, fill=col, line=(255, 255, 255, 60))))
            c.tag_bind(dot, "<Button-1>", lambda e, n=name: self.pick_color(n))
            self.hand(dot)

        self.label(rx, px(470), "İsim")
        fw, fh, fy = rw - px(58), px(48), px(494)
        self.field_imgs = {s: self.photo(("field", s, fw, fh), lambda s=s: gfx.rounded(
            fw, fh, px(10), fill=C["surface2"], line=C["accent"] if s else C["line"]))
            for s in (False, True)}
        self.field = c.create_image(rx, fy, anchor="nw", image=self.field_imgs[False], tags=("page",))
        c.create_window(rx + px(16), fy + fh / 2, anchor="w", window=self.entry, width=fw - px(32),
                        tags=("page",))
        self.button(rx + rw - px(48), fy, px(48), fh, "", self.random_name, icon="dice", tip="Rastgele isim")
        self.button(rx, px(574), rw, px(50), "Sahiplen", self.adopt, style="primary", size=11, r=px(10))
        self.count_text = self.text(rx + rw / 2, px(648), self.count_label(), 9, color=C["faint"], anchor="center")
        self.update_stage("walk1")

    def field_focus(self, on):
        if self.page == "adopt" and self.stage_box:
            self.c.itemconfig(self.field, image=self.field_imgs[on])

    def set_hover(self, key):
        if key != self.hover_card:
            self.hover_card = key
            self.c.config(cursor="hand2" if key else "")
            self.update_cards()

    def update_cards(self):
        px = self.px
        for key, (body, spr, w, h) in self.cards.items():
            state = "sel" if key == self.species else "hover" if key == self.hover_card else "normal"
            style = {"sel": dict(fill=C["surface2"], line=C["accent"]),
                     "hover": dict(fill=C["surface2"], line=C["line2"]),
                     "normal": dict(fill=C["surface"], line=C["line"])}[state]
            self.c.itemconfig(body, image=self.photo(("card", state, w, h),
                                                     lambda: gfx.rounded(w, h, px(10), **style)))
            if spr and key != self.species:
                self.c.itemconfig(spr, image=self.app.img(key, first_color(key), "walk1", 1, self.card_scale))

    def pick(self, key):
        if key == "random":
            key = random.choice(SPECIES_ORDER)
            self.species = key
            self.color = random.choice(list(SPECIES[key]["colors"]))
            self.random_name()
            self.show("adopt", animate=False)
            self.do_cheer()
            return
        if key != self.species:
            self.species = key
            self.color = first_color(key)
            self.random_name()
            self.show("adopt", animate=False)

    def pick_color(self, name):
        self.color = name
        self.show("adopt", animate=False)

    def random_name(self):
        self.name_var.set(random.choice(SPECIES[self.species]["names"]))

    def adopt(self):
        name = self.name_var.get().strip()[:20] or random.choice(SPECIES[self.species]["names"])
        self.app.adopt(self.species, self.color, name)
        self.toast(f"{name} masaüstüne eklendi")
        self.do_cheer()
        self.random_name()

    def do_cheer(self):
        self.cheer = 12

    def update_stage(self, frame):
        self.c.itemconfig(self.stage_pet, image=self.app.img(self.species, self.color, frame, 1, self.big_scale))

    def place_stage_pet(self, lift):
        x0, y0, x1, y1 = self.stage_box
        self.c.coords(self.stage_pet, (x0 + x1) / 2, y0 + self.stage_gy + self.px(10) - lift)

    # ---------------------------------------------------------------- Dostlarım
    def page_pets(self):
        px = self.px
        pets = self.app.pets
        n = len(pets)
        self.header(n if n else None)
        X0, X1 = self.X0, self.X1
        if not pets:
            cx, cy = (X0 + X1) / 2, px(380)
            self.text(cx, cy - px(20), "Henüz dostun yok.", 12, color=C["muted"], anchor="center")
            self.button(cx - px(80), cy + px(14), px(160), px(42), "Sahiplen",
                        lambda: self.show("adopt"), style="primary", size=10, r=px(10))
            return
        cw, ch, gap = (X1 - X0 - px(20)) // 2, px(172), px(16)
        start = self.scroll * 2
        shown = pets[start:start + 6]
        for i, p in enumerate(shown):
            self.pet_card(p, X0 + (i % 2) * (cw + px(20)), px(112) + (i // 2) * (ch + gap), cw, ch)
        if n > 6:
            self.text(X1, px(74), f"{start + 1}–{start + len(shown)} / {n}", 9,
                      C["faint"], anchor="ne")

    def pet_card(self, p, x, y, w, h):
        c, px = self.c, self.px
        self.box(x, y, w, h, px(12), fill=C["surface"], line=C["line"])
        ax, ay, aw, ah = x + px(14), y + px(14), px(118), h - px(28)
        c.create_image(ax, ay, anchor="nw", tags=("page",), image=self.photo(
            ("mini", p.species, aw, ah), lambda: gfx.stage_image(p.species, aw, ah, px(8), self.ui, 0.8)))
        sprite = c.create_image(ax + aw / 2, ay + int(ah * 0.8) + px(8), anchor="s", tags=("page",))
        c.tag_bind(sprite, "<Button-1>", lambda e: p.pet())
        self.hand(sprite)
        tx, right = ax + aw + px(18), x + w - px(18)
        self.text(tx, y + px(14), p.name, 13, "bold", display=True)
        need = xp_needed(p.level)
        self.text(right, y + px(20), f"Seviye {p.level}", 9, "bold", C["fg2"], anchor="ne")
        sub = self.text(tx, y + px(42), self.pet_line(p), 9, color=C["muted"])
        xpbar = self.bar(tx, y + px(64), right - tx, px(4), p.xp / need, C["purple"])
        refs = {"sprite": sprite, "sub": sub, "xpbar": (xpbar, right - tx, px(4)),
                "needs": {}, "level": p.level, "pet": p}
        for i, (key, label, icon, color) in enumerate(NEEDS):
            ny = y + px(78) + i * px(20)
            c.create_image(tx, ny + px(4), anchor="w", image=self.icon(icon, color), state="disabled", tags=("page",))
            bw = right - tx - px(24) - px(40)
            v = getattr(p, key)
            item = self.bar(tx + px(24), ny, bw, px(8), v / 100, color)
            pct = self.text(right, ny + px(4), f"{int(v)}", 9, color=C["fg2"], anchor="e")
            refs["needs"][key] = (item, bw, px(8), pct)
        self.live[p.id] = refs

        by, bs = y + h - px(42), px(30)
        actions = [("fish", "Besle", lambda: self.app.drop_fish(p.x + p.W / 2)),
                   ("heart", "Sev", p.pet),
                   ("moon", "Uyandır" if p.state == "sleep" else "Uyut",
                    lambda: p.pet() if p.state == "sleep" else p.set_state("sleep", 800)),
                   ("target", "Yanıma çağır", lambda: p.call_to((self.app.area[0] + self.app.area[2]) / 2))]
        for i, (icon, tip, cmd) in enumerate(actions):
            self.button(tx + i * (px(36) + px(6)), by, px(36), bs, "", cmd, style="soft", icon=icon, tip=tip, r=px(9))
        self.button(right - px(36), by, px(36), bs, "", lambda: self.confirm_remove(p), style="danger",
                    icon="x", tip="Kaldır", r=px(9))

    @staticmethod
    def pet_line(p):
        return f"{p.color} {p.sp['title'].lower()}, {p.status.lower()}"

    def confirm_remove(self, p):
        if messagebox.askyesno(APP_NAME, f"{p.name} masaüstünden kaldırılsın mı?\n"
                                         "Seviyesi ve ilerlemesi silinir.", parent=self.root):
            self.app.remove_pet(p)

    # ---------------------------------------------------------------- Başarımlar
    def page_achievements(self):
        c, px = self.c, self.px
        X0, X1 = self.X0, self.X1
        store = self.app.store
        self.header()
        done = len(store.unlocked)
        x, y, w, h = X0, px(112), X1 - X0, px(100)
        self.box(x, y, w, h, px(12), fill=C["surface"], line=C["line"])
        self.text(x + px(24), y + px(24), f"{done} / {len(ACHIEVEMENTS)} açıldı", 16, "bold", display=True)
        self.bar(x + px(24), y + px(62), px(320), px(6), done / len(ACHIEVEMENTS), C["accent"])
        stats = store.stats
        bx = x + w - px(24)
        for label, value in (("Oyun süresi", fmt_duration(stats.get("playtime", 0))),
                             ("Mama", str(stats.get("feeds", 0))),
                             ("Sevgi", str(stats.get("pets", 0)))):
            self.text(bx, y + px(26), value, 16, "bold", display=True, anchor="ne")
            self.text(bx, y + px(58), label, 9, color=C["muted"], anchor="ne")
            bx -= px(130)

        tw, th, gap = (w - px(32)) // 3, px(96), px(14)
        for i, ach in enumerate(ACHIEVEMENTS):
            self.achievement_tile(ach, X0 + (i % 3) * (tw + px(16)), px(232) + (i // 3) * (th + gap), tw, th)

    def achievement_tile(self, ach, x, y, w, h):
        c, px = self.c, self.px
        aid, title, desc, icon, goal, stat = ach
        store = self.app.store
        unlocked = aid in store.unlocked
        prog = min(store.progress(stat), goal)
        if unlocked:
            self.box(x, y, w, h, px(12), fill=C["surface"], line=C["line2"])
            self.box(x + px(14), y + px(22), px(52), px(52), px(8), fill=C["accent_soft"])
            ic = C["accent"]
        else:
            self.box(x, y, w, h, px(12), fill=C["surface"], line=C["line"])
            self.box(x + px(14), y + px(22), px(52), px(52), px(8), fill=C["surface2"])
            ic = C["faint"]
        c.create_image(x + px(40), y + px(48), image=self.icon(icon, ic, max(2, round(3 * self.ui))),
                       state="disabled", tags=("page",))
        tx = x + px(80)
        self.text(tx, y + px(14), title, 10, "bold", C["fg"] if unlocked else C["fg2"])
        self.text(tx, y + px(35), desc, 8, color=C["muted"], width=w - px(96))
        if unlocked:
            self.text(tx, y + h - px(18), "Tamamlandı", 9, color=C["green"], anchor="w")
        else:
            bw = w - (tx - x) - px(66)
            self.bar(tx, y + h - px(21), bw, px(6), prog / goal, C["accent"])
            self.text(x + w - px(16), y + h - px(18), f"{prog}/{goal}", 9, color=C["faint"], anchor="e")

    # ---------------------------------------------------------------- Ayarlar
    def page_settings(self):
        px = self.px
        X0, X1 = self.X0, self.X1
        self.header()
        colw = (X1 - X0 - px(24)) // 2
        left = [("Görünüm", [
                    ("Dost boyutu", "Masaüstündeki dostların ne kadar büyük görüneceği.",
                     ("seg", "size", [("S", "Küçük"), ("M", "Orta"), ("L", "Büyük")])),
                    ("Konuşma balonları", "Dostların ara sıra bir şeyler söylesin.", ("toggle", "bubbles"))]),
                ("Davranış", [
                    ("Pencerelerin üstünde gez", "Dostlar açık pencerelerin üst kenarına çıkıp yürüyebilsin.",
                     ("toggle", "walk_windows")),
                    ("İmleci kovala", "Dostlar ara sıra farenin peşine düşsün.", ("toggle", "chase_mouse")),
                    ("Gece uykusu", "Gece saatlerinde dostlar daha çok uyusun.", ("toggle", "night_mode"))])]
        right = [("Sistem", [
                    ("Windows ile başlat", "Bilgisayar açılınca dostların da uyansın.", ("toggle", "autostart")),
                    ("Bildirimler", "Bir dostun acıkınca ya da başarım açılınca haber ver.", ("toggle", "notify"))]),
                 ("Veri", [
                    ("İlerlemeyi sıfırla", "İstatistikleri ve başarımları sıfırlar. Dostların kalır.",
                     ("button", "Sıfırla", self.reset_progress))])]
        y = self.settings_column(X0, colw, left)
        y = self.settings_column(X0 + colw + px(24), colw, right)

        x, w = X0 + colw + px(24), colw
        self.label(x, y + px(4), "Hakkında")
        y += px(28)
        self.box(x, y, w, px(72), px(10), fill=C["surface"], line=C["line"])
        self.text(x + px(18), y + px(15), APP_NAME, 10, "bold")
        self.text(x + px(18), y + px(37), f"Sürüm {__version__}, MIT lisansı", 8, color=C["muted"])

    def settings_column(self, x, w, sections):
        px = self.px
        y = px(112)
        settings = self.app.settings
        for title, rows in sections:
            self.label(x, y + px(4), title)
            y += px(28)
            for name, desc, ctrl in rows:
                h = px(72)
                self.box(x, y, w, h, px(10), fill=C["surface"], line=C["line"])
                ctrl_w = {"seg": px(182), "toggle": px(44), "button": px(96)}[ctrl[0]]
                self.text(x + px(18), y + px(15), name, 10, "bold")
                self.text(x + px(18), y + px(37), desc, 8, color=C["muted"], width=w - ctrl_w - px(56))
                cx = x + w - px(18) - ctrl_w
                if ctrl[0] == "toggle":
                    self.toggle(cx, y + (h - px(24)) / 2, bool(settings[ctrl[1]]),
                                lambda v, k=ctrl[1]: self.set_setting(k, v))
                elif ctrl[0] == "seg":
                    self.segmented(cx, y + (h - px(34)) / 2, ctrl[2], settings[ctrl[1]],
                                   lambda v, k=ctrl[1]: self.set_setting(k, v))
                else:
                    self.button(cx, y + (h - px(36)) / 2, ctrl_w, px(36), ctrl[1], ctrl[2], style="danger", size=9)
                y += h + px(10)
            y += px(8)
        return y

    def set_setting(self, key, value):
        self.app.set_setting(key, value)
        self.show("settings", animate=False)

    def reset_progress(self):
        if messagebox.askyesno(APP_NAME, "Tüm istatistikler ve başarımlar sıfırlansın mı?\n"
                                         "Dostların ve seviyeleri olduğu gibi kalır.", parent=self.root):
            self.app.store.reset_progress()
            self.app.save()
            self.refresh()
            self.toast("İlerleme sıfırlandı")

    # ---------------------------------------------------------------- animasyon
    def tick(self):
        self.t += 1
        if self.root.winfo_viewable():
            self.expire_toasts()
            if self.slide <= 0:
                if self.page == "adopt" and self.stage_box:
                    self.animate_adopt()
                elif self.page == "pets":
                    for refs in self.live.values():
                        p = refs["pet"]
                        frame = "sleep" if p.state == "sleep" else ("walk1" if self.t % 2 else "walk2")
                        self.c.itemconfig(refs["sprite"], image=self.app.img(p.species, p.color, frame, 1,
                                                                             self.mini_scale))
        self.root.after(150, self.tick)

    def animate_adopt(self):
        c, app = self.c, self.app
        body, spr, w, h = self.cards[self.species]
        c.itemconfig(spr, image=app.img(self.species, first_color(self.species),
                                        "walk1" if self.t % 2 else "walk2", 1, self.card_scale))
        frames = SPECIES[self.species]["frames"]
        if self.cheer > 0:
            self.cheer -= 1
            frame = "happy2" if "happy2" in frames and self.t % 2 else "happy"
            self.place_stage_pet(abs(math.sin(self.cheer * 0.8)) * self.px(16))
            if self.cheer % 3 == 0:
                x0, y0, x1, y1 = self.stage_box
                x = (x0 + x1) / 2 + random.randint(-self.px(70), self.px(70))
                hid = c.create_image(x, y0 + self.stage_gy - self.px(120), tags=("page",),
                                     image=app.effect("heart", max(2, round(3 * self.ui))))
                self.hearts.append([hid, 10])
        else:
            self.place_stage_pet(0)
            frame = "blink" if self.t % 25 == 0 else "walk1" if self.t % 2 else "walk2"
        self.update_stage(frame)
        for hrt in self.hearts[:]:
            c.move(hrt[0], 0, -self.px(6))
            hrt[1] -= 1
            if hrt[1] <= 0:
                c.delete(hrt[0])
                self.hearts.remove(hrt)
