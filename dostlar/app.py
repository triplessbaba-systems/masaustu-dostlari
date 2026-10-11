"""Uygulama: ana döngü, sistem tepsisi, kayıt ve her şeyi birbirine bağlayan parça."""
import os
import queue
import random
import threading
import time
import tkinter as tk
from tkinter import messagebox

from PIL import ImageTk

from . import APP_ID, APP_NAME, gfx, winapi
from .desktop import Ball, Fish, Pet, clamp
from .hub import C, Hub
from .sprites import BASE_PALETTE, EFFECTS, MOOD_LINES, SPECIES, palette
from .store import Store, new_pet

try:
    import pystray
except ImportError:          # pystray yoksa tepsi ikonu olmadan çalışır
    pystray = None

TICK_MS = 40                 # ~25 fps
SIZE_MULT = {"S": 0.75, "M": 1.0, "L": 1.35}


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.ui = winapi.dpi_scale()
        self.store = Store()
        self.settings = self.store.settings
        self.settings["autostart"] = winapi.get_autostart(APP_ID)
        self.area = winapi.work_area() or (0, 0, self.root.winfo_screenwidth(), self.root.winfo_screenheight())
        self.pid = os.getpid()
        self.cache = {}
        self.pets, self.fish, self.balls, self.platforms = [], [], [], []
        self.hidden = self.closed = False
        self.tray = None
        self.jobs = queue.Queue()             # tepsi thread'inden gelen işler
        self.menu = tk.Menu(self.root, tearoff=0)
        self.logo = ImageTk.PhotoImage(gfx.make_logo(64))
        self.root.iconphoto(True, self.logo)
        self.hub = Hub(self)

        away = max(0.0, time.time() - self.store.data["last_seen"])
        for d in self.store.data["pets"]:
            self.catch_up(d, away)
            self.pets.append(Pet(self, d))
        self.hub.refresh()
        if not self.pets:
            self.show_hub()
        elif away > 3 * 3600:
            self.root.after(3500, lambda: self.pets and random.choice(self.pets).say(
                random.choice(MOOD_LINES["missed"])))

        self.start_tray()
        self.t = 0
        self.root.after(TICK_MS, self.loop)
        self.root.after(1000, self.second)

    # -- ölçek ve görseller --
    @property
    def s(self):
        return max(2, round(4 * self.ui * SIZE_MULT.get(self.settings["size"], 1)))

    def img(self, species, color, frame, facing, scale):
        key = ("pet", species, color, frame, facing, scale)
        if key not in self.cache:
            rows = SPECIES[species]["frames"][frame]
            if facing == -1:
                rows = [row[::-1] for row in rows]
            self.cache[key] = ImageTk.PhotoImage(gfx.pixel_image(rows, palette(species, color), scale))
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
        self.announce(self.store.bump("adopted") + self.store.add_species(species)
                      + self.store.set_max("max_active", len(self.pets)))
        self.save()
        self.hub.refresh()

    def remove_pet(self, pet):
        if pet in self.pets:
            pet.destroy()
            self.pets.remove(pet)
            self.save()
            self.hub.refresh()
            if not self.pets:
                self.show_hub("adopt")

    def pet_by_id(self, pid):
        return next((p for p in self.pets if p.id == pid), None)

    def respawn(self):
        """Boyut değişince pencereleri yeni ölçekle baştan kur."""
        data = [p.to_dict() for p in self.pets]
        for p in self.pets:
            p.destroy()
        for obj in self.fish + self.balls:
            obj.win.destroy()
        self.fish, self.balls = [], []
        self.pets = [Pet(self, d) for d in data]

    def drop_fish(self, x=None):
        if self.hidden:
            self.set_hidden(False)
        self.fish.append(Fish(self, x))
        for p in self.pets:
            if p.state not in ("drag", "fall", "sleep"):
                p.set_state("food", 400)

    def throw_ball(self):
        if self.hidden:
            self.set_hidden(False)
        for b in self.balls[:]:
            b.destroy()
        self.balls.append(Ball(self))
        for p in self.pets:
            if p.state not in ("drag", "fall") and random.random() < 0.35 + 0.12 * p.sp["stats"]["Oyunculuk"]:
                p.set_state("play", 400)

    def gather(self):
        if self.hidden:
            self.set_hidden(False)
        l, t, r, b = self.area
        mid = (l + r) / 2
        for i, p in enumerate(self.pets):
            p.call_to(mid + (i - (len(self.pets) - 1) / 2) * p.W * 1.2)

    # -- istatistik / başarımlar --
    def stat(self, key, n=1):
        self.announce(self.store.bump(key, n))

    def announce(self, achievements):
        for aid, title, desc, icon, goal, stat in achievements:
            shown = self.hub.toast(f"Başarım: {title}", desc)
            if not shown:
                self.notify(f"Başarım açıldı: {title}", desc)
        if achievements:
            self.hub.draw_nav()

    def on_level_up(self, pet):
        self.announce(self.store.set_max("max_level", pet.level))
        text = f"{pet.name} {pet.level}. seviyeye çıktı"
        if not self.hub.toast(text):
            self.notify(text, "")
        self.hub.refresh()

    def notify_hungry(self, pet):
        self.notify(f"{pet.name} acıktı", "Mama vermek için tepsideki ikona sağ tıkla.")

    def notify(self, title, body):
        if self.tray and self.settings["notify"] and not self.root.winfo_viewable():
            try:
                self.tray.notify(body, title)
            except Exception:
                pass

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
        self.save()

    # -- pencere / görünürlük --
    def show_hub(self, page=None):
        root = self.root
        first = not root.winfo_viewable() and not getattr(self, "_shown", False)
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
        root.lift()
        root.focus_force()

    def set_hidden(self, hidden):
        self.hidden = hidden
        for p in self.pets:
            p.set_visible(not hidden)
        for obj in self.fish + self.balls:
            obj.win.withdraw() if hidden else obj.win.deiconify()
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
            Item(f"{APP_NAME}'nı aç", do(self.show_hub), default=True),
            Item("Dostları göster", do(lambda: self.set_hidden(not self.hidden)),
                 checked=lambda item: not self.hidden),
            pystray.Menu.SEPARATOR,
            Item("Mama ver", do(self.drop_fish)),
            Item("Top at", do(self.throw_ball)),
            Item("Hepsini çağır", do(self.gather)),
            pystray.Menu.SEPARATOR,
            Item("Çıkış", do(self.quit)),
        )
        self.tray = pystray.Icon(APP_ID, gfx.make_logo(64), APP_NAME, menu)
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
        if self.t % 125 == 0:                                      # görev çubuğu değiştiyse
            self.area = winapi.work_area() or self.area
        if not self.hidden:
            if self.settings["walk_windows"] and self.pets and self.t % 12 == 0:
                self.platforms = winapi.window_platforms(self.pid, self.area)
            try:
                for obj in self.fish + self.balls + self.pets:
                    obj.tick()
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
        if int(time.time()) % 20 == 0:
            self.save()
        self.hub.on_second()
        self.root.after(1000, self.second)

    def save(self):
        self.store.save([p.to_dict() for p in self.pets])

    def quit(self):
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
