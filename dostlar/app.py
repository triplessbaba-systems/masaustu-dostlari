"""Uygulama: ana döngü, sistem tepsisi, kayıt ve her şeyi birbirine bağlayan parça."""
import json
import os
import queue
import random
import threading
import time
import tkinter as tk
import urllib.request
import webbrowser
from tkinter import messagebox

from PIL import ImageTk

from . import APP_ID, APP_NAME, REPO, __version__, gfx, i18n, winapi
from .desktop import Ball, Fish, Pet, clamp
from .games import MiniGame
from .hub import C, Hub
from .i18n import _, mood
from .seasons import SeasonFx
from .sprites import BASE_PALETTE, EFFECTS, SPECIES
from .store import Store, new_pet

try:
    import pystray
except ImportError:          # pystray yoksa tepsi ikonu olmadan çalışır
    pystray = None

TICK_MS = 40                 # ~25 fps
SIZE_MULT = {"S": 0.75, "M": 1.0, "L": 1.35}


def version_tuple(v):
    try:
        return tuple(int(x) for x in v.lstrip("v").split("."))
    except ValueError:
        return (0,)


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.ui = winapi.dpi_scale()
        self.store = Store()
        self.settings = self.store.settings
        self.settings["autostart"] = winapi.get_autostart(APP_ID)
        i18n.set_lang(self.settings["lang"])
        self.pid = os.getpid()
        self.refresh_screens()
        self.cache = {}
        self.pets, self.fish, self.balls, self.platforms = [], [], [], []
        self.game = None
        self.update = None                    # (sürüm, adres) yeni sürüm varsa
        self.hidden = self.closed = False
        self.tray = None
        self.jobs = queue.Queue()             # başka thread'lerden gelen işler
        self.menu = tk.Menu(self.root, tearoff=0)
        self.logo = ImageTk.PhotoImage(gfx.make_logo(64))
        self.root.iconphoto(True, self.logo)
        self.seasons = SeasonFx(self)
        self.hub = Hub(self)

        away = max(0.0, time.time() - self.store.data["last_seen"])
        for d in self.store.data["pets"]:
            self.catch_up(d, away)
            self.pets.append(Pet(self, d))
        self.hub.refresh()
        if not self.pets:
            self.show_hub()
        elif away > 3 * 3600:
            self.root.after(3500, lambda: self.pets and random.choice(self.pets).say(mood("missed")))

        self.start_tray()
        self.seasons.refresh()
        self.t = 0
        self.root.after(TICK_MS, self.loop)
        self.root.after(1000, self.second)
        self.root.after(6000, self.check_update)

    # -- ekranlar --
    def refresh_screens(self):
        """Ana ekran (area), tüm ekranların birleşimi (bounds) ve tek tek ekranlar."""
        mons = winapi.monitors()
        if not mons:
            mons = [winapi.work_area() or (0, 0, self.root.winfo_screenwidth(), self.root.winfo_screenheight())]
        self.monitors = mons
        self.area = mons[0]
        self.bounds = (min(m[0] for m in mons), min(m[1] for m in mons),
                       max(m[2] for m in mons), max(m[3] for m in mons))

    def monitor_at(self, x):
        for m in self.monitors:
            if m[0] <= x < m[2]:
                return m
        return min(self.monitors, key=lambda m: min(abs(x - m[0]), abs(x - m[2])))

    def floor_at(self, x):
        return self.monitor_at(x)[3]

    def top_at(self, x):
        return self.monitor_at(x)[1]

    # -- ölçek ve görseller --
    @property
    def s(self):
        return max(2, round(4 * self.ui * SIZE_MULT.get(self.settings["size"], 1)))

    def img(self, species, color, frame, facing, scale, acc=None):
        key = ("pet", species, color, frame, facing, scale, acc)
        if key not in self.cache:
            self.cache[key] = ImageTk.PhotoImage(gfx.sprite_image(species, color, frame, facing, scale, acc))
        return self.cache[key]

    def effect(self, name, scale):
        key = ("fx", name, scale)
        if key not in self.cache:
            self.cache[key] = ImageTk.PhotoImage(gfx.pixel_image(EFFECTS[name], BASE_PALETTE, scale))
        return self.cache[key]

    def bubble_img(self, text):
        u = max(2, round(self.s / 2))
        key = ("bubble", text, u)
        if key not in self.cache:
            self.cache[key] = ImageTk.PhotoImage(gfx.bubble(text, u))
        return self.cache[key]

    # -- dostlar --
    @staticmethod
    def catch_up(d, away):
        """Uygulama kapalıyken geçen süreyi (en fazla 8 saat) yavaşça işle."""
        mins = min(away, 8 * 3600) / 60
        d["food"] = clamp(d["food"] - mins * 0.5, 10)
        d["joy"] = clamp(d["joy"] - mins * 0.35, 10)
        d["energy"] = clamp(d["energy"] + mins * 2)

    def adopt(self, species, color, name):
        if self.hidden:
            self.set_hidden(False)
        self.pets.append(Pet(self, new_pet(species, color, name)))
        events = self.store.bump("adopted") + self.store.add_species(species) \
            + self.store.set_max("max_active", len(self.pets))
        if species == "ejderha":
            events += self.store.set_max("dragon", 1)
        self.announce(events)
        self.save()
        self.hub.refresh()

    def remove_pet(self, pet):
        if pet not in self.pets:
            return
        if self.game and self.game.pet is pet:
            self.stop_game()
        pet.destroy()
        self.pets.remove(pet)
        self.store.forget(pet.id)
        self.save()
        self.hub.refresh()
        if not self.pets:
            self.show_hub("adopt")

    def pet_by_id(self, pid):
        return next((p for p in self.pets if p.id == pid), None)

    def set_accessory(self, pet, acc):
        pet.set_acc(acc)
        if acc:
            self.announce(self.store.set_max("dressed", 1))
        self.save()

    def respawn(self):
        """Boyut değişince pencereleri yeni ölçekle baştan kur."""
        self.stop_game()
        data = [p.to_dict() for p in self.pets]
        for p in self.pets:
            p.destroy()
        for obj in self.fish + self.balls:
            obj.win.destroy()
        self.fish, self.balls = [], []
        self.pets = [Pet(self, d) for d in data]
        self.seasons.clear()
        self.seasons.refresh()

    def drop_fish(self, x=None):
        if self.hidden:
            self.set_hidden(False)
        self.fish.append(Fish(self, x))
        for p in self.pets:
            if p.state not in ("drag", "fall", "sleep", "game"):
                p.set_state("food", 400)

    def throw_ball(self):
        if self.hidden:
            self.set_hidden(False)
        for b in self.balls[:]:
            b.destroy()
        self.balls.append(Ball(self))
        for p in self.pets:
            if p.state not in ("drag", "fall", "game") and \
                    random.random() < 0.35 + 0.12 * p.sp["stats"]["Oyunculuk"]:
                p.set_state("play", 400)

    def gather(self):
        if self.hidden:
            self.set_hidden(False)
        l, t, r, b = self.area
        mid = (l + r) / 2
        for i, p in enumerate(self.pets):
            p.call_to(mid + (i - (len(self.pets) - 1) / 2) * p.W * 1.2)

    # -- dostlar arası etkileşim --
    def socialize(self):
        free = [p for p in self.pets if p.state in ("walk", "idle") and not p.social_cd]
        random.shuffle(free)
        for i, a in enumerate(free):
            for b in free[i + 1:]:
                if abs(a.surface - b.surface) < 4 * a.scale and abs(a.cx - b.cx) < (a.W + b.W) * 0.6:
                    self.meet(a, b)
                    return

    def meet(self, a, b):
        tired = a.energy < 45 and b.energy < 45
        kind = "nap" if tired else random.choice(["hello", "hello", "chase"])
        if kind == "chase":
            a.meet(b, "chase")
            b.meet(a, "flee")
        else:
            a.meet(b, kind)
            b.meet(a, kind)
        if kind != "nap":
            a.say(mood("meet", name=b.name))
        self.announce(self.store.meet(a.id, b.id))

    # -- mini oyun --
    def start_game(self, pet=None):
        if self.game:
            return
        if not self.pets:
            self.hub.toast(_("Önce bir dost sahiplen"))
            return
        if self.hidden:
            self.set_hidden(False)
        pet = pet or max(self.pets, key=lambda p: (p.level, p.xp))
        self.game = MiniGame(self, pet)
        self.hub.draw_static()

    def stop_game(self):
        if not self.game:
            return
        game, self.game = self.game, None
        score = game.finish()
        best = self.store.stats.get("game_best", 0)
        self.announce(self.store.set_max("game_best", score))
        title = _("Oyun bitti: {score} puan").format(score=score)
        body = _("Yeni rekor!") if score > best else _("Rekor: {best}").format(best=max(best, score))
        if not self.hub.toast(title, body):
            self.notify(title, body)
        game.pet.say(title)
        self.hub.draw_static()
        self.hub.refresh()

    # -- istatistik / başarımlar --
    def stat(self, key, n=1):
        self.announce(self.store.bump(key, n))

    def announce(self, achievements):
        for aid, title, desc, icon, goal, stat in achievements:
            text = _("Başarım: {title}").format(title=_(title))
            if not self.hub.toast(text, _(desc)):
                self.notify(text, _(desc))
        if achievements:
            self.hub.draw_nav()

    def on_level_up(self, pet):
        self.announce(self.store.set_max("max_level", pet.level))
        text = _("{name} {level}. seviyeye çıktı").format(name=pet.name, level=pet.level)
        if not self.hub.toast(text):
            self.notify(text, "")
        self.hub.refresh()

    def on_evolve(self, pet):
        stage = _(pet.stage[1]).lower()
        text = _("{name} artık {stage}!").format(name=pet.name, stage=stage)
        if not self.hub.toast(text):
            self.notify(text, "")

    def notify_hungry(self, pet):
        self.notify(_("{name} acıktı").format(name=pet.name), _("Mama vermek için tepsideki ikona sağ tıkla."))

    def notify(self, title, body):
        if self.tray and self.settings["notify"] and not self.root.winfo_viewable():
            try:
                self.tray.notify(body or title, title)
            except Exception:
                pass

    # -- güncelleme --
    def check_update(self):
        if self.closed:
            return
        if self.settings["updates"]:
            threading.Thread(target=self._fetch_latest, daemon=True).start()
        self.root.after(6 * 3600 * 1000, self.check_update)

    def _fetch_latest(self):
        try:
            req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/releases/latest",
                                         headers={"User-Agent": APP_ID, "Accept": "application/vnd.github+json"})
            with urllib.request.urlopen(req, timeout=8) as r:
                data = json.load(r)
            tag, url = data.get("tag_name", ""), data.get("html_url", "")
            if version_tuple(tag) > version_tuple(__version__):
                self.jobs.put(lambda: self.on_update(tag, url))
        except Exception:
            pass

    def on_update(self, tag, url):
        first = self.update is None
        self.update = (tag, url)
        self.hub.draw_status()
        if first:
            text = _("Yeni sürüm: {tag}").format(tag=tag)
            if not self.hub.toast(text, _("Ayarlar sayfasından indirebilirsin.")):
                self.notify(text, _("İndirmek için uygulamayı aç."))

    def open_update(self):
        webbrowser.open(self.update[1] if self.update else f"https://github.com/{REPO}/releases")

    # -- ayarlar --
    def set_setting(self, key, value):
        self.settings[key] = value
        if key == "size":
            self.respawn()
        elif key == "autostart":
            winapi.set_autostart(APP_ID, value)
            self.settings[key] = winapi.get_autostart(APP_ID)
        elif key == "bubbles" and not value:
            for p in self.pets:
                p.bubble.hide()
        elif key == "seasons":
            self.seasons.refresh()
        elif key == "updates" and value:
            threading.Thread(target=self._fetch_latest, daemon=True).start()
        elif key == "lang":
            i18n.set_lang(value)
            self.root.title(_(APP_NAME))
            self.hub.rebuild()
            if self.tray:
                self.tray.title = _(APP_NAME)
                self.tray.update_menu()
        self.save()

    # -- pencere / görünürlük --
    def show_hub(self, page=None, wardrobe=None):
        root = self.root
        first = not getattr(self, "_shown", False)
        root.deiconify()
        if first:
            self._shown = True
            root.update_idletasks()
            l, t, r, b = self.area
            w, h = root.winfo_reqwidth(), root.winfo_reqheight()
            root.geometry(f"+{l + (r - l - w) // 2}+{t + max(0, (b - t - h) // 2)}")
            winapi.dark_title_bar(root, C["bg"])
        if page:
            self.hub.show(page)
        else:
            self.hub.refresh()
        if wardrobe:
            self.hub.open_wardrobe(wardrobe)
        root.lift()
        root.focus_force()

    def set_hidden(self, hidden):
        if hidden:
            self.stop_game()
        self.hidden = hidden
        for p in self.pets:
            p.set_visible(not hidden)
        for obj in self.fish + self.balls:
            obj.win.withdraw() if hidden else obj.win.deiconify()
        self.seasons.refresh()
        if self.tray:
            self.tray.update_menu()
        self.hub.draw_status()

    # -- sistem tepsisi --
    def start_tray(self):
        if not pystray:
            return
        Item = pystray.MenuItem

        def do(fn):
            return lambda icon, item: self.jobs.put(fn)

        menu = pystray.Menu(
            Item(lambda item: _("{app}'nı aç").format(app=_(APP_NAME)), do(self.show_hub), default=True),
            Item(lambda item: _("Dostları göster"), do(lambda: self.set_hidden(not self.hidden)),
                 checked=lambda item: not self.hidden),
            pystray.Menu.SEPARATOR,
            Item(lambda item: _("Mama ver"), do(self.drop_fish)),
            Item(lambda item: _("Top at"), do(self.throw_ball)),
            Item(lambda item: _("Hepsini çağır"), do(self.gather)),
            Item(lambda item: _("Mama Yağmuru oyna"), do(self.start_game)),
            pystray.Menu.SEPARATOR,
            Item(lambda item: _("Çıkış"), do(self.quit)),
        )
        self.tray = pystray.Icon(APP_ID, gfx.make_logo(64), _(APP_NAME), menu)
        threading.Thread(target=self.tray.run, daemon=True).start()

    # -- döngüler --
    def loop(self):
        if self.closed:
            return
        self.t += 1
        while not self.jobs.empty():
            self.jobs.get()()
            if self.closed:
                return
        if self.t % 125 == 0:                                      # ekran düzeni değiştiyse
            old = self.bounds
            self.refresh_screens()
            if self.bounds != old:
                self.seasons.refresh()
        if not self.hidden:
            if self.settings["walk_windows"] and self.pets and self.t % 12 == 0:
                self.platforms = winapi.window_platforms(self.pid, self.bounds)
            if self.t % 10 == 0 and len(self.pets) > 1:
                self.socialize()
            try:
                for obj in self.fish + self.balls + self.pets:
                    obj.tick()
                if self.game:
                    self.game.tick()
                self.seasons.tick()
            except tk.TclError:
                pass
        self.root.after(TICK_MS, self.loop)

    def second(self):
        if self.closed:
            return
        for p in self.pets:
            p.second()
        if self.pets and not self.hidden:
            self.store.stats["playtime"] = self.store.stats.get("playtime", 0) + 1
            if time.localtime().tm_hour < 5:
                self.announce(self.store.set_max("night", 1))
        now = int(time.time())
        if now % 20 == 0:
            self.save()
        if now % 60 == 0:
            self.seasons.refresh()
        self.hub.on_second()
        self.root.after(1000, self.second)

    def save(self):
        self.store.save([p.to_dict() for p in self.pets])

    def quit(self):
        self.stop_game()
        self.closed = True
        self.save()
        if self.tray:
            self.tray.stop()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


def main():
    winapi.enable_dpi_awareness()
    if winapi.already_running(APP_ID + "_tek_kopya"):
        r = tk.Tk()
        r.withdraw()
        messagebox.showinfo(APP_NAME, f"{APP_NAME} zaten açık.\nGizli simgelerdeki pati ikonuna tıkla.")
        r.destroy()
        return
    winapi.set_app_id(APP_ID)
    App().run()
