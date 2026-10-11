"""Ana pencere: Sahiplen, Dostlarım, Başarımlar ve Ayarlar sayfaları.

Tüm arayüz tek bir Canvas üzerine Pillow ile çizilir; böylece yuvarlak köşeler
standart Tk bileşenlerinden bağımsız olarak pürüzsüz görünür.
"""
import math
import random
import tkinter as tk
import webbrowser
from tkinter import font as tkfont
from tkinter import messagebox

from PIL import Image, ImageDraw, ImageTk

from . import APP_NAME, REPO, __version__, gfx
from .i18n import _, color_name, sp_text
from .sprites import ACCESSORIES, DRAGON_UNLOCK, SPECIES, SPECIES_ORDER, UI_ICONS, first_color
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
MONTHS = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül",
          "Ekim", "Kasım", "Aralık"]
BTN = {
    "primary": dict(normal=dict(fill=C["accent"]), hover=dict(fill=C["accent_hi"]), fg=C["ink"]),
    "secondary": dict(normal=dict(fill=C["surface2"], line=C["line"]),
                      hover=dict(fill="#2a2740", line=C["line2"]), fg=C["fg"]),
    "ghost": dict(normal=None, hover=dict(fill=C["surface2"]), fg=C["fg2"]),
    "soft": dict(normal=dict(fill="#24213a"), hover=dict(fill="#34305a"), fg=C["fg2"]),
    "danger": dict(normal=dict(fill="#2a1f33"), hover=dict(fill=C["red"]), fg=C["fg"]),
}


def content_bg(w, h, side):
    img = Image.new("RGBA", (w, h), gfx.rgba(C["bg"]))
    ImageDraw.Draw(img).rectangle((0, 0, side - 1, h), fill=gfx.rgba(C["side"]))
    ImageDraw.Draw(img).line((side - 1, 0, side - 1, h), fill=gfx.rgba(C["side_line"]))
    return img


def fmt_duration(sec):
    m = int(sec // 60)
    return _("{h} sa {m} dk").format(h=m // 60, m=m % 60) if m >= 60 else _("{m} dk").format(m=m)


def requirement(acc):
    kind, value = ACCESSORIES[acc]["req"]
    if kind == "level":
        return _("Seviye {n}").format(n=value)
    if kind == "ach":
        return _("{n} başarım").format(n=value)
    return _("{month} ayında").format(month=_(MONTHS[value - 1]))


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
        self.name_var = tk.StringVar(value=random.choice(sp_text(self.species, "names")))
        self.t = 0
        self.cheer = 0
        self.hearts, self.toasts = [], []
        self.toast_seq = 0
        self.scroll = 0
        self.slide = 0
        self.live, self.cards = {}, {}
        self.hover_card = None
        self.stage_box = None
        self.wardrobe = None                  # aksesuar dolabı açıksa dostun kimliği
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

    def box(self, x, y, w, h, r, tags=("page",), state="disabled", **style):
        """Yuvarlak kutu çizer, öğesini döndürür."""
        x, y, w, h, r = int(x), int(y), int(w), int(h), int(r)
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

    def segmented(self, x, y, options, value, cmd, tags=("page",), sw=58, h=34):
        px = self.px
        sw, h = px(sw), px(h)
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
        root.title(_(APP_NAME))
        root.configure(bg=C["bg"])
        root.resizable(False, False)
        root.protocol("WM_DELETE_WINDOW", self.close)
        W, H = px(1120), px(700)
        self.W, self.H, self.SIDE = W, H, px(232)
        c = self.c = tk.Canvas(root, width=W, height=H, bg=C["bg"], highlightthickness=0, bd=0)
        c.pack()
        c.create_image(0, 0, anchor="nw", image=self.photo("bg", lambda: content_bg(W, H, self.SIDE)))
        c.create_image(px(22), px(28), anchor="nw", image=self.photo("logo32", lambda: gfx.make_logo(px(32))))
        c.bind("<MouseWheel>", self.on_wheel)
        self.entry = tk.Entry(c, textvariable=self.name_var, font=self.f(12), bg=C["surface2"],
                              fg=C["fg"], insertbackground=C["accent"], relief="flat", bd=0,
                              highlightthickness=0, selectbackground=C["accent2"])
        self.entry.bind("<Return>", lambda e: self.adopt())
        self.entry.bind("<FocusIn>", lambda e: self.field_focus(True))
        self.entry.bind("<FocusOut>", lambda e: self.field_focus(False))
        self.draw_static()
        self.draw_nav()
        self.draw_status()

    def draw_static(self):
        """Uygulama adı ve sağ üstteki hızlı eylemler."""
        px, app = self.px, self.app
        self.c.delete("static")
        tags = ("static",)
        self.text(px(66), px(44), _(APP_NAME), 12, "bold", display=True, anchor="w", tags=tags)
        game = (_("Oyunu Bitir"), "gamepad", app.stop_game, _("Mama Yağmuru'nu bitir")) if app.game else \
            (_("Mama Yağmuru"), "gamepad", app.start_game, _("Düşen mamaları dostunla yakala"))
        x = self.X1
        for text, icon, cmd, tip in (game,
                                     (_("Hepsini Çağır"), "target", app.gather, _("Tüm dostlar ortada toplansın")),
                                     (_("Top At"), "ball", app.throw_ball, _("Masaüstüne bir top bırak")),
                                     (_("Mama Ver"), "fish", app.drop_fish, _("Masaüstüne balık yağdır"))):
            w = self.measure(text, self.f(9, "bold")) + px(52)
            x -= w
            self.button(x, px(32), w, px(38), text, cmd, icon=icon, size=9, tags=tags, tip=tip)
            x -= px(10)

    def rebuild(self):
        """Dil değişince tüm metinleri yeniden çiz."""
        self.root.title(_(APP_NAME))
        self.random_name()
        self.draw_static()
        self.draw_nav()
        self.draw_status()
        self.show(self.page, animate=False)

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
            self.text(x + px(44), y + h / 2, _(label), 10, "bold" if active else "normal",
                      C["fg"] if active else C["fg2"], anchor="w", tags=("nav",))
            badge = None
            if key == "pets" and self.app.pets:
                badge = str(len(self.app.pets))
            elif key == "achievements":
                badge = f"{len(self.app.store.unlocked)}/{len(ACHIEVEMENTS)}"
            if badge:
                self.text(x + w - px(14), y + h / 2, badge, 9, color=C["muted"], anchor="e", tags=("nav",))
            y += h + px(4)

    def draw_status(self):
        c, px, H, app = self.c, self.px, self.H, self.app
        c.delete("status")
        tags = ("status",)
        x, w = px(28), px(176)
        if app.update:
            self.button(px(12), H - px(214), px(208), px(36), _("Yeni sürüm: {tag}").format(tag=app.update[0]),
                        app.open_update, style="soft", size=9, tags=tags)
        c.create_line(px(12), H - px(166), px(220), H - px(166), fill=C["side_line"], tags=tags)
        self.text(x, H - px(140), _("Dil"), 10, color=C["fg2"], anchor="w", tags=tags)
        self.segmented(x + w - px(96), H - px(155), [("tr", "TR"), ("en", "EN")], app.settings["lang"],
                       lambda v: app.set_setting("lang", v), tags=tags, sw=44, h=30)
        self.text(x, H - px(98), _("Dostları göster"), 10, color=C["fg2"], anchor="w", tags=tags)
        self.toggle(x + w - px(44), H - px(110), not app.hidden,
                    lambda v: (app.set_hidden(not v), self.draw_status()), tags=tags)
        self.button(px(12), H - px(62), px(208), px(40), _("Çıkış"), app.quit, style="ghost",
                    size=10, tags=tags)

    def header(self, count=None):
        title = _(PAGE_INFO[self.page])
        font = self.f(22, "bold", True)
        self.text(self.X0, self.px(51), title, 22, "bold", display=True, anchor="w")
        if count is not None:
            self.text(self.X0 + self.measure(title, font) + self.px(12), self.px(53), str(count), 16,
                      color=C["faint"], display=True, anchor="w")

    # ---------------------------------------------------------------- gezinme
    def show(self, page, animate=True):
        if page != self.page:
            self.scroll = 0
            self.wardrobe = None
        self.page = page
        self.hide_tip()
        self.c.delete("page")
        self.c.delete("overlay")
        self.live, self.cards, self.hearts = {}, {}, []
        self.stage_box = None
        self.hover_card = None
        self.c.config(cursor="")
        self.draw_nav()
        getattr(self, "page_" + page)()
        if self.wardrobe:
            self.draw_wardrobe()
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
        if self.page == "pets" and not self.wardrobe:
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
    def toast(self, title, body=""):
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
                items = self.c.find_withtag(t[0])
                if items:
                    target = self.px(88) + i * h
                    self.c.move(t[0], 0, target - self.c.coords(items[0])[1])

    # ---------------------------------------------------------------- Sahiplen
    def dragon_locked(self):
        return not self.app.store.dragon_unlocked()

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
        self.text(ix, iy, sp_text(self.species, "title"), 18, "bold", display=True)
        self.text(ix, iy + px(36), sp_text(self.species, "desc"), 10, color=C["muted"], width=hw - px(48))
        self.text(ix, iy + px(86), ", ".join(sp_text(self.species, "traits")), 10, color=C["fg2"])
        for i, (name, val) in enumerate(sp["stats"].items()):
            ry = iy + px(132) + i * px(26)
            self.text(ix, ry, _(name), 10, color=C["fg2"], anchor="w")
            for k in range(5):
                self.box(ix + px(110) + k * px(16), ry - px(5), px(10), px(10), px(2),
                         fill=C["fg2"] if k < val else C["track"])

        # sağ kolon: türler
        rx, rw = X0 + px(424), X1 - (X0 + px(424))
        self.label(rx, px(112), _("Tür"))
        gx = px(10)
        cw, ch = (rw - 3 * gx) // 4, px(92)
        for i, key in enumerate(SPECIES_ORDER + ["random"]):
            x = rx + (i % 4) * (cw + gx)
            y = px(136) + (i // 4) * (ch + gx)
            body = self.box(x, y, cw, ch, px(10), state="normal", fill=C["surface"], line=C["line"])
            spr = None
            if key == "random":
                c.create_image(x + cw / 2, y + px(38), image=self.icon("dice", C["muted"], max(3, round(4 * self.ui))),
                               state="disabled", tags=("page",))
                title = _("Rastgele")
            elif key == "ejderha" and self.dragon_locked():
                c.create_image(x + cw / 2, y + px(38), image=self.icon("lock", C["faint"], max(3, round(4 * self.ui))),
                               state="disabled", tags=("page",))
                title = _("{n} başarım").format(n=DRAGON_UNLOCK)
            else:
                spr = c.create_image(x + cw / 2, y + px(66), anchor="s", state="disabled", tags=("page",),
                                     image=self.app.img(key, first_color(key), "walk1", 1, self.card_scale))
                title = sp_text(key, "title")
            self.text(x + cw / 2, y + px(78), title, 9, "bold", anchor="center")
            c.tag_bind(body, "<Enter>", lambda e, k=key: self.set_hover(k))
            c.tag_bind(body, "<Leave>", lambda e: self.set_hover(None))
            c.tag_bind(body, "<Button-1>", lambda e, k=key: self.pick(k))
            self.cards[key] = (body, spr, cw, ch)
        self.update_cards()

        self.label(rx, px(452), _("Renk"))
        self.text(rx + rw, px(452), color_name(self.color), 9, color=C["fg2"], anchor="ne")
        d, ring = px(34), px(44)
        for i, (name, cpal) in enumerate(sp["colors"].items()):
            cx, cy = rx + d / 2 + px(5) + i * (d + px(16)), px(494)
            if name == self.color:
                c.create_image(cx, cy, tags=("page",), state="disabled", image=self.photo(
                    ("ring", ring), lambda: gfx.rounded(ring, ring, ring // 2, line=C["accent"], lw=2)))
            dot = c.create_image(cx, cy, tags=("page",), image=self.photo(
                ("swatch", cpal["O"], d), lambda col=cpal["O"]: gfx.rounded(
                    d, d, d // 2, fill=col, line=(255, 255, 255, 60))))
            c.tag_bind(dot, "<Button-1>", lambda e, n=name: self.pick_color(n))
            self.hand(dot)

        self.label(rx, px(530), _("İsim"))
        fw, fh, fy = rw - px(58), px(46), px(552)
        self.field_imgs = {s: self.photo(("field", s, fw, fh), lambda s=s: gfx.rounded(
            fw, fh, px(10), fill=C["surface2"], line=C["accent"] if s else C["line"]))
            for s in (False, True)}
        self.field = c.create_image(rx, fy, anchor="nw", image=self.field_imgs[False], tags=("page",))
        c.create_window(rx + px(16), fy + fh / 2, anchor="w", window=self.entry, width=fw - px(32),
                        tags=("page",))
        self.button(rx + rw - px(46), fy, px(46), fh, "", self.random_name, icon="dice", tip=_("Rastgele isim"))
        self.button(rx, px(614), rw, px(50), _("Sahiplen"), self.adopt, style="primary", size=11, r=px(10))
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
        if key == "ejderha" and self.dragon_locked():
            have = len(self.app.store.unlocked)
            self.toast(_("Ejderha kilitli"),
                       _("{need} başarım gerekiyor, şu an {have} tane açık.").format(need=DRAGON_UNLOCK, have=have))
            return
        if key == "random":
            choices = [k for k in SPECIES_ORDER if k != "ejderha" or not self.dragon_locked()]
            self.species = random.choice(choices)
            self.color = random.choice(list(SPECIES[self.species]["colors"]))
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
        self.name_var.set(random.choice(sp_text(self.species, "names")))

    def adopt(self):
        if self.species == "ejderha" and self.dragon_locked():
            return
        name = self.name_var.get().strip()[:20] or random.choice(sp_text(self.species, "names"))
        self.app.adopt(self.species, self.color, name)
        self.toast(_("{name} masaüstüne eklendi").format(name=name))
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
            self.text(cx, cy - px(20), _("Henüz dostun yok."), 12, color=C["muted"], anchor="center")
            self.button(cx - px(80), cy + px(14), px(160), px(42), _("Sahiplen"),
                        lambda: self.show("adopt"), style="primary", size=10, r=px(10))
            return
        cw, ch, gap = (X1 - X0 - px(20)) // 2, px(172), px(16)
        start = self.scroll * 2
        shown = pets[start:start + 6]
        for i, p in enumerate(shown):
            self.pet_card(p, X0 + (i % 2) * (cw + px(20)), px(112) + (i // 2) * (ch + gap), cw, ch)
        if n > 6:
            self.text(X1, px(74), f"{start + 1}–{start + len(shown)} / {n}", 9, color=C["faint"], anchor="ne")

    def pet_card(self, p, x, y, w, h):
        c, px = self.c, self.px
        self.box(x, y, w, h, px(12), fill=C["surface"], line=C["line"])
        ax, ay, aw, ah = x + px(14), y + px(14), px(118), h - px(28)
        c.create_image(ax, ay, anchor="nw", tags=("page",), image=self.photo(
            ("mini", p.species, aw, ah), lambda: gfx.stage_image(p.species, aw, ah, px(8), self.ui, 0.8)))
        sprite = c.create_image(ax + aw / 2, ay + int(ah * 0.8) + px(8), anchor="s", tags=("page",))
        friend = self.app.store.best_friend(p.id)
        other = self.app.pet_by_id(friend[0]) if friend else None
        tip = _("En iyi arkadaşı: {name} ({n} buluşma)").format(name=other.name, n=friend[1]) if other \
            else _("Henüz bir arkadaşı yok")

        def enter(e):
            c.config(cursor="hand2")
            self.show_tip(tip, ax + aw / 2, ay - px(4), ay + ah + px(4))

        def leave(e):
            c.config(cursor="")
            self.hide_tip()

        c.tag_bind(sprite, "<Enter>", enter)
        c.tag_bind(sprite, "<Leave>", leave)
        c.tag_bind(sprite, "<Button-1>", lambda e: p.pet())

        tx, right = ax + aw + px(18), x + w - px(18)
        self.text(tx, y + px(14), p.name, 13, "bold", display=True)
        need = xp_needed(p.level)
        stage_color = C["accent"] if p.stage[0] == 2 else C["fg2"]
        self.text(right, y + px(20), _("Seviye {n}").format(n=p.level), 9, "bold", stage_color, anchor="ne")
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

        by, bs, bw = y + h - px(42), px(30), px(32)
        actions = [("fish", _("Besle"), lambda: self.app.drop_fish(p.cx)),
                   ("heart", _("Sev"), p.pet),
                   ("moon", _("Uyandır") if p.state == "sleep" else _("Uyut"),
                    lambda: p.pet() if p.state == "sleep" else p.set_state("sleep", 800)),
                   ("target", _("Yanıma çağır"), lambda: p.call_to((self.app.area[0] + self.app.area[2]) / 2)),
                   ("hat", _("Aksesuar"), lambda: self.open_wardrobe(p.id))]
        for i, (icon, tip_text, cmd) in enumerate(actions):
            self.button(tx + i * (bw + px(5)), by, bw, bs, "", cmd, style="soft", icon=icon, tip=tip_text, r=px(9))
        self.button(right - bw, by, bw, bs, "", lambda: self.confirm_remove(p), style="danger",
                    icon="x", tip=_("Kaldır"), r=px(9))

    @staticmethod
    def pet_line(p):
        return f"{_(p.stage[1])} {sp_text(p.species, 'title').lower()}, {p.status.lower()}"

    def confirm_remove(self, p):
        if messagebox.askyesno(_(APP_NAME), _("{name} masaüstünden kaldırılsın mı?\n"
                                              "Seviyesi ve ilerlemesi silinir.").format(name=p.name),
                               parent=self.root):
            self.app.remove_pet(p)

    # ---------------------------------------------------------------- Aksesuar dolabı
    def open_wardrobe(self, pid):
        if self.page != "pets":
            self.show("pets", animate=False)
        self.wardrobe = pid
        self.draw_wardrobe()

    def close_wardrobe(self):
        self.wardrobe = None
        self.c.delete("overlay")
        self.hide_tip()

    def draw_wardrobe(self):
        c, px = self.c, self.px
        c.delete("overlay")
        pet = self.app.pet_by_id(self.wardrobe)
        if not pet:
            self.wardrobe = None
            return
        tags = ("overlay",)
        W, H = self.W, self.H
        dim = c.create_image(0, 0, anchor="nw", tags=tags, image=self.photo(
            ("dim", W, H), lambda: Image.new("RGBA", (W, H), (5, 4, 10, 170))))
        c.tag_bind(dim, "<Button-1>", lambda e: self.close_wardrobe())
        pw, ph = px(520), px(392)
        x, y = (W - pw) / 2, (H - ph) / 2
        panel = self.box(x, y, pw, ph, px(14), tags, state="normal", fill=C["surface"], line=C["line2"])
        c.tag_bind(panel, "<Button-1>", lambda e: "break")
        self.text(x + px(24), y + px(22), _("Aksesuar: {name}").format(name=pet.name), 14, "bold",
                  display=True, tags=tags)
        tw, th, gap = px(108), px(116), px(12)
        options = [None] + list(ACCESSORIES)
        store = self.app.store
        for i, acc in enumerate(options):
            tx = x + px(24) + (i % 4) * (tw + gap)
            ty = y + px(68) + (i // 4) * (th + gap)
            unlocked = acc is None or store.acc_unlocked(acc)
            selected = pet.acc == acc
            style = dict(fill=C["surface2"], line=C["accent"]) if selected else \
                dict(fill=C["surface2"] if unlocked else C["bg"], line=C["line"])
            tile = self.box(tx, ty, tw, th, px(10), tags, state="normal", **style)
            if unlocked:
                c.create_image(tx + tw / 2, ty + px(78), anchor="s", state="disabled", tags=tags,
                               image=self.app.img(pet.species, pet.color, "walk1", 1, self.card_scale, acc))
                name = _("Yok") if acc is None else _(ACCESSORIES[acc]["name"])
                c.tag_bind(tile, "<Button-1>", lambda e, a=acc: self.choose_acc(pet, a))
                self.hand(tile)
            else:
                c.create_image(tx + tw / 2, ty + px(44), state="disabled", tags=tags,
                               image=self.icon("lock", C["faint"], max(3, round(4 * self.ui))))
                name = requirement(acc)
            self.text(tx + tw / 2, ty + th - px(18), name, 9, "bold" if unlocked else "normal",
                      C["fg"] if unlocked else C["faint"], anchor="center", tags=tags)
        self.button(x + pw - px(124), y + ph - px(56), px(100), px(36), _("Kapat"), self.close_wardrobe,
                    tags=tags, size=9)

    def choose_acc(self, pet, acc):
        self.app.set_accessory(pet, acc)
        self.draw_wardrobe()

    # ---------------------------------------------------------------- Başarımlar
    def page_achievements(self):
        px = self.px
        X0, X1 = self.X0, self.X1
        store = self.app.store
        self.header()
        done = len(store.unlocked)
        x, y, w, h = X0, px(108), X1 - X0, px(80)
        self.box(x, y, w, h, px(12), fill=C["surface"], line=C["line"])
        self.text(x + px(24), y + px(16), _("{done} / {total} açıldı").format(done=done, total=len(ACHIEVEMENTS)),
                  16, "bold", display=True)
        self.bar(x + px(24), y + px(54), px(280), px(6), done / len(ACHIEVEMENTS), C["accent"])
        stats = store.stats
        bx = x + w - px(24)
        for label, value in ((_("Rekor"), str(stats.get("game_best", 0))),
                             (_("Oyun süresi"), fmt_duration(stats.get("playtime", 0))),
                             (_("Mama"), str(stats.get("feeds", 0))),
                             (_("Sevgi"), str(stats.get("pets", 0)))):
            self.text(bx, y + px(14), value, 15, "bold", display=True, anchor="ne")
            self.text(bx, y + px(46), label, 9, color=C["muted"], anchor="ne")
            bx -= max(px(96), self.measure(value, self.f(15, "bold", True)) + px(36))

        gap = px(10)
        tw, th = (w - 3 * gap) // 4, px(112)
        for i, ach in enumerate(ACHIEVEMENTS):
            self.achievement_tile(ach, X0 + (i % 4) * (tw + gap), px(200) + (i // 4) * (th + gap), tw, th)

    def achievement_tile(self, ach, x, y, w, h):
        c, px = self.c, self.px
        aid, title, desc, icon, goal, stat = ach
        store = self.app.store
        unlocked = aid in store.unlocked
        prog = min(store.progress(stat), goal)
        self.box(x, y, w, h, px(12), fill=C["surface"], line=C["line2"] if unlocked else C["line"])
        self.box(x + px(14), y + px(14), px(32), px(32), px(8), fill=C["accent_soft"] if unlocked else C["surface2"])
        c.create_image(x + px(30), y + px(30), state="disabled", tags=("page",),
                       image=self.icon(icon, C["accent"] if unlocked else C["faint"]))
        self.text(x + px(56), y + px(30), _(title), 10, "bold", C["fg"] if unlocked else C["fg2"],
                  anchor="w", width=w - px(66))
        self.text(x + px(14), y + px(52), _(desc), 8, color=C["muted"], width=w - px(28))
        if unlocked:
            self.text(x + px(14), y + h - px(14), _("Tamamlandı"), 9, color=C["green"], anchor="w")
        else:
            self.bar(x + px(14), y + h - px(17), w - px(78), px(6), prog / goal, C["accent"])
            self.text(x + w - px(14), y + h - px(14), f"{prog}/{goal}", 9, color=C["faint"], anchor="e")

    # ---------------------------------------------------------------- Ayarlar
    def page_settings(self):
        px = self.px
        X0, X1 = self.X0, self.X1
        app = self.app
        self.header()
        colw = (X1 - X0 - px(24)) // 2
        left = [(_("Görünüm"), [
                    (_("Dost boyutu"), _("Masaüstündeki dostların ne kadar büyük görüneceği."),
                     ("seg", "size", [("S", _("Küçük")), ("M", _("Orta")), ("L", _("Büyük"))])),
                    (_("Konuşma balonları"), _("Dostların ara sıra bir şeyler söylesin."), ("toggle", "bubbles")),
                    (_("Mevsim efektleri"), _("Kışın kar, sonbaharda yaprak, ilkbaharda çiçek yağsın."),
                     ("toggle", "seasons"))]),
                (_("Davranış"), [
                    (_("Pencerelerin üstünde gez"), _("Dostlar açık pencerelerin üst kenarında yürüyebilsin."),
                     ("toggle", "walk_windows")),
                    (_("İmleci kovala"), _("Dostlar ara sıra farenin peşine düşsün."), ("toggle", "chase_mouse")),
                    (_("Gece uykusu"), _("Gece saatlerinde dostlar daha çok uyusun."), ("toggle", "night_mode"))])]
        right = [(_("Sistem"), [
                    (_("Windows ile başlat"), _("Bilgisayar açılınca dostların da uyansın."), ("toggle", "autostart")),
                    (_("Bildirimler"), _("Bir dostun acıkınca ya da başarım açılınca haber ver."),
                     ("toggle", "notify")),
                    (_("Güncellemeleri denetle"), _("Yeni sürüm çıkınca haber ver."), ("toggle", "updates"))]),
                 (_("Veri"), [
                    (_("İlerlemeyi sıfırla"), _("İstatistikleri ve başarımları sıfırlar. Dostların kalır."),
                     ("button", _("Sıfırla"), self.reset_progress))])]
        self.settings_column(X0, colw, left)
        y = self.settings_column(X0 + colw + px(24), colw, right)

        x, w = X0 + colw + px(24), colw
        self.label(x, y + px(4), _("Hakkında"))
        y += px(28)
        self.box(x, y, w, px(64), px(10), fill=C["surface"], line=C["line"])
        self.text(x + px(18), y + px(13), _(APP_NAME), 10, "bold")
        self.text(x + px(18), y + px(35), _("Sürüm {v}, MIT lisansı").format(v=__version__), 8, color=C["muted"])
        if app.update:
            self.button(x + w - px(130), y + px(14), px(112), px(36), _("{tag} indir").format(tag=app.update[0]),
                        app.open_update, style="primary", size=9)
        else:
            self.button(x + w - px(112), y + px(14), px(94), px(36), "GitHub",
                        lambda: webbrowser.open(f"https://github.com/{REPO}"), size=9)

    def settings_column(self, x, w, sections):
        px = self.px
        y = px(112)
        settings = self.app.settings
        for title, rows in sections:
            self.label(x, y + px(4), title)
            y += px(28)
            for name, desc, ctrl in rows:
                h = px(64)
                self.box(x, y, w, h, px(10), fill=C["surface"], line=C["line"])
                ctrl_w = {"seg": px(182), "toggle": px(44), "button": px(96)}[ctrl[0]]
                self.text(x + px(18), y + px(12), name, 10, "bold")
                self.text(x + px(18), y + px(33), desc, 8, color=C["muted"], width=w - ctrl_w - px(56))
                cx = x + w - px(18) - ctrl_w
                if ctrl[0] == "toggle":
                    self.toggle(cx, y + (h - px(24)) / 2, bool(settings[ctrl[1]]),
                                lambda v, k=ctrl[1]: self.set_setting(k, v))
                elif ctrl[0] == "seg":
                    self.segmented(cx, y + (h - px(34)) / 2, ctrl[2], settings[ctrl[1]],
                                   lambda v, k=ctrl[1]: self.set_setting(k, v))
                else:
                    self.button(cx, y + (h - px(36)) / 2, ctrl_w, px(36), ctrl[1], ctrl[2], style="danger", size=9)
                y += h + px(8)
            y += px(8)
        return y

    def set_setting(self, key, value):
        self.app.set_setting(key, value)
        self.show("settings", animate=False)

    def reset_progress(self):
        if messagebox.askyesno(_(APP_NAME), _("Tüm istatistikler ve başarımlar sıfırlansın mı?\n"
                                              "Dostların ve seviyeleri olduğu gibi kalır."), parent=self.root):
            self.app.store.reset_progress()
            self.app.save()
            self.refresh()
            self.toast(_("İlerleme sıfırlandı"))

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
                                                                             self.mini_scale, p.acc))
        self.root.after(150, self.tick)

    def animate_adopt(self):
        c, app = self.c, self.app
        body, spr, w, h = self.cards[self.species]
        if spr:
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
