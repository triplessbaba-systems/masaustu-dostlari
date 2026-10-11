"""Mevsim efektleri: kışın kar, sonbaharda yaprak, ilkbaharda çiçek, yaz gecelerinde ateşböceği."""
import math
import random
import time

from . import winapi
from .desktop import transparent_window

COUNTS = {"snow": 28, "leaf": 16, "petal": 18, "firefly": 12}


def current_season():
    now = time.localtime()
    if now.tm_mon in (12, 1, 2):
        return "snow"
    if now.tm_mon in (10, 11):
        return "leaf"
    if now.tm_mon in (3, 4, 5):
        return "petal"
    if now.tm_hour >= 21 or now.tm_hour < 5:
        return "firefly"
    return None


class SeasonFx:
    """Tüm ekranları kaplayan, tıklamaları geçiren şeffaf bir katman."""

    def __init__(self, app):
        self.app = app
        self.kind = None
        self.box = None
        self.win = None
        self.parts = []

    def refresh(self):
        app = self.app
        kind = current_season() if app.settings["seasons"] and not app.hidden else None
        if kind != self.kind or (kind and self.box != app.bounds):
            self.clear()
            if kind:
                self.build(kind)

    def clear(self):
        if self.win is not None:
            self.win.destroy()
        self.win, self.kind, self.parts = None, None, []

    def build(self, kind):
        app = self.app
        self.kind, self.box = kind, app.bounds
        l, t, r, b = self.box
        self.win, self.c = transparent_window(app.root, r - l, b - t)
        self.win.geometry(f"+{l}+{t}")
        self.win.update_idletasks()
        winapi.click_through(self.win)
        img = app.effect(kind, max(2, app.s // 2 + (1 if kind == "leaf" else 0)))
        for _ in range(COUNTS[kind]):
            x, y = random.uniform(0, r - l), random.uniform(0, b - t)
            item = self.c.create_image(x, y, image=img)
            self.parts.append(dict(item=item, x=x, y=y, phase=random.uniform(0, 6.28),
                                   vy=random.uniform(0.6, 1.6) * app.s / 4,
                                   amp=random.uniform(0.3, 1.2) * app.s / 4))

    def tick(self):
        if self.win is None:
            return
        l, t, r, b = self.box
        firefly = self.kind == "firefly"
        for p in self.parts:
            p["phase"] += 0.05
            if firefly:
                p["x"] += math.cos(p["phase"] * 0.7) * p["amp"]
                p["y"] += math.sin(p["phase"]) * p["amp"] * 0.6
                p["x"] %= (r - l)
                p["y"] = min(max(p["y"], (b - t) * 0.3), b - t - 10)
            else:
                p["y"] += p["vy"]
                p["x"] += math.sin(p["phase"]) * p["amp"]
                if p["y"] > self.app.floor_at(l + p["x"]) - t:
                    p["y"], p["x"] = -10, random.uniform(0, r - l)
            self.c.coords(p["item"], p["x"], p["y"])
