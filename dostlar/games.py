"""Mama Yağmuru: dostunu fareyle yönet, yukarıdan düşen mamaları yakala."""
import random

from .desktop import clamp, transparent_window
from .i18n import _

DURATION = 30            # saniye
FPS = 25

# tür, puan, olasılık
TREATS = [("fish", 1, 0.68), ("star", 3, 0.14), ("rock", -2, 0.18)]


class Treat:
    def __init__(self, game, x, kind, value, speed):
        self.game, self.kind, self.value = game, kind, value
        app = game.app
        img = app.effect(kind, app.s + (1 if kind == "star" else 0))
        self.w, self.h = img.width(), img.height()
        self.win, c = transparent_window(app.root, self.w, self.h)
        c.create_image(0, 0, anchor="nw", image=img)
        self.x, self.y = float(x - self.w / 2), float(game.area[1] - self.h)
        self.vy = speed
        self.place()

    def tick(self):
        pet = self.game.pet
        self.y += self.vy
        cx, bottom = self.x + self.w / 2, self.y + self.h
        if pet.x <= cx <= pet.x + pet.W and bottom >= pet.y + pet.top_pad + 3 * pet.scale:
            self.game.caught(self)
            return
        if bottom >= self.game.app.floor_at(cx):
            self.destroy()
            return
        self.place()

    def place(self):
        self.win.geometry(f"+{int(self.x)}+{int(self.y)}")

    def destroy(self):
        self.win.destroy()
        if self in self.game.treats:
            self.game.treats.remove(self)


class MiniGame:
    def __init__(self, app, pet):
        self.app, self.pet = app, pet
        self.area = app.monitor_at(pet.cx)
        self.score = 0
        self.ticks = 0
        self.countdown = 3 * FPS
        self.next_spawn = 0
        self.treats = []
        self.hud_text = None
        self.hud, self.hud_c = transparent_window(app.root, 10, 10)
        self.hud_item = self.hud_c.create_image(0, 0, anchor="nw")
        pet.state, pet.timer = "game", 0
        pet.on_window = False
        pet.bubble.show("3", life=FPS)
        self.update_hud(DURATION)

    def remaining(self):
        return max(0, DURATION - (self.ticks - 3 * FPS) // FPS)

    def update_hud(self, secs):
        text = _("Puan {score}   Süre {secs}").format(score=self.score, secs=secs)
        if text == self.hud_text:
            return
        self.hud_text = text
        img = self.app.bubble_img(text)
        self.hud_c.config(width=img.width(), height=img.height())
        self.hud_c.itemconfig(self.hud_item, image=img)
        l, t, r, b = self.area
        self.hud.geometry(f"+{int((l + r - img.width()) / 2)}+{t + 16}")

    def tick(self):
        self.ticks += 1
        if self.countdown > 0:
            self.countdown -= 1
            if self.countdown and self.countdown % FPS == 0:
                self.pet.bubble.show(str(self.countdown // FPS), life=FPS)
            elif self.countdown == 0:
                self.pet.bubble.show(_("Başla!"), life=FPS)
            return
        secs = self.remaining()
        if secs <= 0:
            self.app.stop_game()
            return
        self.next_spawn -= 1
        if self.next_spawn <= 0:
            progress = 1 - secs / DURATION
            self.next_spawn = int(random.randint(12, 22) * (1 - 0.4 * progress))
            r = random.random()
            for kind, value, chance in TREATS:
                if r < chance:
                    break
                r -= chance
            l, t, rr, b = self.area
            speed = self.app.s * (1.6 + 1.8 * progress) * random.uniform(0.85, 1.15)
            self.treats.append(Treat(self, random.randint(l + 40, rr - 40), kind, value, speed))
        for t in self.treats[:]:
            t.tick()
        self.update_hud(secs)

    def caught(self, treat):
        self.score = max(0, self.score + treat.value)
        self.pet.spawn("heart" if treat.value > 0 else "z")
        if treat.value < 0:
            self.pet.say(_("Ay!"))
        treat.destroy()

    def finish(self):
        """Oyunu kapat; ödülleri ver ve puanı döndür."""
        for t in self.treats[:]:
            t.destroy()
        self.hud.destroy()
        pet = self.pet
        pet.state, pet.timer = "idle", 40
        if self.countdown == 0 and self.score:
            pet.joy = clamp(pet.joy + 10)
            pet.energy = clamp(pet.energy - 8)
            pet.add_xp(self.score)
        return self.score
