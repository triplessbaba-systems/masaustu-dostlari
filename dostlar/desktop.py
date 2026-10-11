"""Masaüstünde yaşayan nesneler: dostlar, mama, top ve konuşma balonları."""
import math
import random
import time
import tkinter as tk

from .sprites import MOOD_LINES, SPECIES
from .store import xp_needed

KEY = "#ff00ff"      # bu renk pencerede şeffaf olur

STATUS_TEXT = {
    "walk": "Geziyor", "idle": "Dinleniyor", "sleep": "Uyuyor", "happy": "Mutlu",
    "eat": "Yemek yiyor", "fall": "Havada", "drag": "Havada", "chase": "İmleci kovalıyor",
    "food": "Mamaya koşuyor", "play": "Top oynuyor",
}


def transparent_window(root, w, h):
    win = tk.Toplevel(root)
    win.overrideredirect(True)
    win.attributes("-topmost", True)
    win.attributes("-transparentcolor", KEY)
    win.config(bg=KEY)
    c = tk.Canvas(win, width=w, height=h, bg=KEY, highlightthickness=0, bd=0)
    c.pack()
    return win, c


def clamp(v, lo=0.0, hi=100.0):
    return max(lo, min(hi, v))


# --- Konuşma balonu -------------------------------------------------------------------
class Bubble:
    def __init__(self, app):
        self.app = app
        self.win = None
        self.life = 0
        self.w = self.h = 0

    def show(self, text):
        img = self.app.bubble_img(text)
        if self.win is None:
            self.win, self.c = transparent_window(self.app.root, 10, 10)
            self.item = self.c.create_image(0, 0, anchor="nw")
        self.w, self.h = img.width(), img.height()
        self.c.config(width=self.w, height=self.h)
        self.c.itemconfig(self.item, image=img)
        self.life = 75
        if not self.app.hidden:
            self.win.deiconify()

    def follow(self, pet):
        if self.win is None or self.life <= 0:
            return
        self.life -= 1
        if self.life == 0:
            self.win.withdraw()
            return
        hx, hy = pet.head_pos()
        self.win.geometry(f"+{int(pet.x + hx - self.w / 2)}+{int(pet.y + hy - self.h - pet.app.s)}")

    def hide(self):
        self.life = 0
        if self.win is not None:
            self.win.withdraw()

    def destroy(self):
        if self.win is not None:
            self.win.destroy()
            self.win = None


# --- Mama ---------------------------------------------------------------------------
class Fish:
    def __init__(self, app, x=None):
        self.app = app
        s = app.s
        self.w, self.h = 12 * s, 7 * s
        self.win, c = transparent_window(app.root, self.w, self.h)
        c.create_image(0, 0, anchor="nw", image=app.effect("fish", s))
        l, t, r, b = app.area
        self.x = float(x - self.w / 2 if x is not None else random.randint(l + self.w, r - 2 * self.w))
        self.x = min(max(self.x, l), r - self.w)
        self.y = float(t)
        self.vy = 0.0
        self.landed = False
        self.place()

    @property
    def cx(self):
        return self.x + self.w / 2

    def tick(self):
        if not self.landed:
            ground = self.app.area[3] - self.h
            self.vy += 0.3 * self.app.s
            self.y += self.vy
            if self.y >= ground:
                self.y, self.landed = ground, True
            self.place()

    def place(self):
        self.win.geometry(f"+{int(self.x)}+{int(self.y)}")

    def destroy(self):
        self.win.destroy()
        if self in self.app.fish:
            self.app.fish.remove(self)


# --- Top ----------------------------------------------------------------------------
class Ball:
    def __init__(self, app):
        self.app = app
        s = app.s
        self.size = 8 * s
        self.win, c = transparent_window(app.root, self.size, self.size)
        c.create_image(0, 0, anchor="nw", image=app.effect("ball", s))
        l, t, r, b = app.area
        self.x = float(random.randint(l + 100, r - 100 - self.size))
        self.y = float(t)
        self.vx = random.choice([-1, 1]) * s * random.uniform(0.5, 1.5)
        self.vy = 0.0
        self.idle = 0
        self.place()

    @property
    def cx(self):
        return self.x + self.size / 2

    def near_floor(self):
        return self.y + self.size >= self.app.area[3] - 4 * self.app.s

    def kick(self, direction):
        s = self.app.s
        self.vx = direction * s * random.uniform(2.5, 4.5)
        self.vy = -s * random.uniform(2.5, 4.5)
        self.idle = 0

    def tick(self):
        s = self.app.s
        l, t, r, b = self.app.area
        floor = b - self.size
        self.vy += 0.35 * s
        self.x += self.vx
        self.y += self.vy
        if self.x < l or self.x > r - self.size:
            self.x = min(max(self.x, l), r - self.size)
            self.vx = -self.vx * 0.7
        if self.y >= floor:
            self.y = floor
            self.vy = -self.vy * 0.55 if self.vy > 1.5 * s else 0.0
            self.vx *= 0.96
        self.idle += 1
        if self.idle > 25 * 60:                  # bir dakika kimse oynamazsa kaybolur
            self.destroy()
            return
        self.place()

    def place(self):
        self.win.geometry(f"+{int(self.x)}+{int(self.y)}")

    def destroy(self):
        self.win.destroy()
        if self in self.app.balls:
            self.app.balls.remove(self)


# --- Dost ---------------------------------------------------------------------------
class Pet:
    def __init__(self, app, data):
        self.app = app
        self.id = data["id"]
        self.species, self.color, self.name = data["species"], data["color"], data["name"]
        self.food, self.joy, self.energy = data["food"], data["joy"], data["energy"]
        self.xp, self.level, self.adopted = data["xp"], data["level"], data["adopted"]
        self.sp = SPECIES[self.species]

        s = app.s
        self.top_pad = 10 * s                 # kalp / Z efektleri için üst boşluk
        self.W, self.H = 20 * s, 16 * s + self.top_pad
        self.win, self.c = transparent_window(app.root, self.W, self.H)
        self.sprite = self.c.create_image(0, self.top_pad, anchor="nw")
        self.cur = None
        self.bubble = Bubble(app)

        l, t, r, b = app.area
        self.x = float(random.randint(l, r - self.W))
        self.y = float(t)
        self.facing = random.choice([-1, 1])
        self.vx = self.facing * s * 0.5
        self.vy = 0.0
        self.px, self.py = self.x, self.y
        self.speed = s * 0.5
        self.state, self.timer, self.t = "fall", 0, 0
        self.moving = self.airborne = False
        self.surface = b                      # üzerinde durduğu yüzeyin y'si
        self.on_window = False
        self.particles = []
        self.drag = None
        self.dragging = False
        self.kick_cd = 0
        self.last_pet = 0.0
        self.hungry_notified = False
        self.next_chat = random.randint(25 * 20, 25 * 60)

        self.c.bind("<ButtonPress-1>", self.on_press)
        self.c.bind("<B1-Motion>", self.on_motion)
        self.c.bind("<ButtonRelease-1>", self.on_release)
        self.c.bind("<Button-3>", self.on_right)
        self.place()
        if app.hidden:
            self.win.withdraw()

    def to_dict(self):
        return {"id": self.id, "species": self.species, "color": self.color, "name": self.name,
                "food": round(self.food, 2), "joy": round(self.joy, 2), "energy": round(self.energy, 2),
                "xp": self.xp, "level": self.level, "adopted": self.adopted}

    @property
    def status(self):
        text = STATUS_TEXT.get(self.state, "")
        if self.food < 25 and self.state not in ("eat", "food"):
            text += ", aç"
        return text

    # -- ihtiyaçlar (saniyede bir) --
    def second(self):
        sleeping = self.state == "sleep"
        self.food = clamp(self.food - (0.012 if sleeping else 0.02))
        self.joy = clamp(self.joy - (0.028 if self.food < 25 else 0.014))
        self.energy = clamp(self.energy + (0.12 if sleeping else -0.01))
        if self.food < 20 and not self.hungry_notified:
            self.hungry_notified = True
            self.say(random.choice(MOOD_LINES["hungry"]))
            self.app.notify_hungry(self)
        elif self.food > 50:
            self.hungry_notified = False

    def add_xp(self, n):
        self.xp += n
        while self.xp >= xp_needed(self.level):
            self.xp -= xp_needed(self.level)
            self.level += 1
            self.say(f"Seviye {self.level}!")
            self.spawn("star")
            self.app.on_level_up(self)

    # -- durumlar --
    def set_state(self, state, timer=0):
        self.state, self.timer = state, timer

    def choose(self):
        s, app = self.app.s, self.app
        settings = app.settings
        if app.fish:
            self.set_state("food", 400)
            return
        if app.balls and random.random() < 0.15 + 0.12 * self.sp["stats"]["Oyunculuk"]:
            self.set_state("play", 400)
            return
        hour = time.localtime().tm_hour
        night = settings["night_mode"] and (hour >= 23 or hour < 6)
        if (self.energy < 25 or night) and random.random() < 0.55:
            self.set_state("sleep", random.randint(400, 900))
            return
        r = random.random()
        if r < 0.42:
            self.facing = random.choice([-1, 1])
            self.speed = s * random.uniform(0.4, 0.8) * self.sp["speed"] * (0.6 if self.food < 25 else 1)
            self.set_state("walk", random.randint(50, 150))
        elif r < 0.64:
            self.set_state("idle", random.randint(40, 120))
        elif r < 0.76 and settings["chase_mouse"] and self.energy > 30:
            self.set_state("chase", random.randint(120, 250))
        elif r < 0.88:
            self.jump()
        elif random.random() < self.sp["stats"]["Uykuculuk"] / 5:
            self.set_state("sleep", random.randint(300, 700))
        else:
            self.set_state("idle", random.randint(40, 120))

    def jump(self):
        s = self.app.s
        self.vy = -s * random.uniform(2.5, 4)
        self.vx = self.facing * s * random.uniform(0.5, 1.5)
        self.energy = clamp(self.energy - 0.5)
        self.set_state("fall")

    def call_to(self, x):
        """Ekranın tepesinden belirli bir noktaya düşür."""
        l, t, r, b = self.app.area
        self.x = float(min(max(x - self.W / 2, l), r - self.W))
        self.y = float(t - self.top_pad)
        self.vx, self.vy = 0.0, 0.0
        self.on_window = False
        self.set_state("fall")

    # -- etkileşimler --
    def pet(self):
        if self.state == "sleep":
            self.say(random.choice(MOOD_LINES["woke"]))
        now = time.time()
        if now - self.last_pet > 0.4:             # tık spamı sayılmasın
            self.last_pet = now
            self.joy = clamp(self.joy + 6)
            self.add_xp(2)
            self.app.stat("pets")
            if random.random() < 0.25:
                self.say(random.choice(MOOD_LINES["happy"]))
        self.set_state("happy", 50)
        self.spawn("heart")

    def eat(self, fish):
        fish.destroy()
        self.food = clamp(self.food + 35)
        self.joy = clamp(self.joy + 4)
        self.add_xp(8)
        self.app.stat("feeds")
        self.set_state("eat", 40)

    def kick(self, ball):
        ball.kick(self.facing)
        self.kick_cd = 15
        self.joy = clamp(self.joy + 3)
        self.energy = clamp(self.energy - 2)
        self.add_xp(3)
        self.app.stat("kicks")

    def caught_mouse(self):
        self.joy = clamp(self.joy + 5)
        self.add_xp(4)
        self.app.stat("catches")
        self.set_state("happy", 50)
        self.spawn("heart")

    def say(self, text):
        if self.app.settings["bubbles"]:
            self.bubble.show(text)

    def chatter(self):
        if self.food < 25:
            line = random.choice(MOOD_LINES["hungry"])
        elif self.energy < 20:
            line = random.choice(MOOD_LINES["tired"])
        elif self.joy < 25:
            line = random.choice(MOOD_LINES["sad"])
        elif self.joy > 80 and random.random() < 0.3:
            line = random.choice(MOOD_LINES["happy"])
        else:
            line = random.choice(self.sp["lines"])
        self.say(line)

    def target(self):
        """(hedef x, ulaşılabilir mi) ya da None."""
        app = self.app
        if self.state == "chase":
            return app.root.winfo_pointerx(), True
        if self.state == "food" and app.fish:
            f = min(app.fish, key=lambda f: abs(f.cx - (self.x + self.W / 2)))
            return f.cx, f.landed
        if self.state == "play" and app.balls:
            return app.balls[0].cx, True
        return None

    # -- zemin / pencere platformları --
    def landing(self, prev_bottom, new_bottom):
        cx = self.x + self.W / 2
        floor = self.app.area[3]
        best = None
        if self.app.settings["walk_windows"]:
            margin = 2 * self.app.s
            for py, x0, x1 in self.app.platforms:
                if x0 + margin <= cx <= x1 - margin and prev_bottom - 1 <= py <= new_bottom:
                    if best is None or py < best:
                        best = py
        if best is None and new_bottom >= floor:
            best = floor
        return best

    def platform_near(self):
        if not self.app.settings["walk_windows"]:
            return None
        cx = self.x + self.W / 2
        best = None
        for py, x0, x1 in self.app.platforms:
            if x0 <= cx <= x1 and abs(py - self.surface) <= 12 * self.app.s:
                if best is None or abs(py - self.surface) < abs(best - self.surface):
                    best = py
        return best

    # -- ana döngü --
    def tick(self):
        s = self.app.s
        l, t, r, b = self.app.area
        self.t += 1
        self.moving = False
        if self.kick_cd:
            self.kick_cd -= 1

        # ayağının altındaki pencere kaybolduysa (taşındı / kapandı) düş
        if self.state not in ("drag", "fall"):
            if self.on_window:
                p = self.platform_near()
                if p is None:
                    self.on_window = False
                    self.vx, self.vy = self.facing * s * 0.6, 0.0
                    self.set_state("fall")
                else:
                    self.surface = p
            else:
                self.surface = b
        ground = self.surface - self.H
        st = self.state

        if st == "drag":
            self.vx = (self.x - self.px) * 0.8
            self.vy = (self.y - self.py) * 0.8
            self.px, self.py = self.x, self.y

        elif st == "fall":
            prev_bottom = self.y + self.H
            self.vy += 0.35 * s
            self.x += self.vx
            self.y += self.vy
            if self.x < l or self.x > r - self.W:
                self.x = min(max(self.x, l), r - self.W)
                self.vx = -self.vx * 0.5
            if self.y < t - self.top_pad:
                self.y, self.vy = t - self.top_pad, abs(self.vy) * 0.3
            if self.vy >= 0:
                land = self.landing(prev_bottom, self.y + self.H)
                if land is not None:
                    self.y = land - self.H
                    climbed = land < b
                    if climbed and not self.on_window:
                        self.app.stat("climbs")
                    self.on_window, self.surface = climbed, land
                    if self.vy > 3 * s:                       # sekme
                        self.vy, self.vx = -self.vy * 0.35, self.vx * 0.6
                    else:
                        self.vx = self.vy = 0
                        self.set_state("idle", random.randint(20, 50))

        elif st == "walk":
            self.y = ground
            self.x += self.facing * self.speed
            self.moving = True
            if self.x <= l or self.x >= r - self.W:
                self.x = min(max(self.x, l), r - self.W)
                self.facing *= -1
            self.timer -= 1
            if self.timer <= 0:
                self.choose()

        elif st in ("chase", "food", "play"):
            self.y = ground
            tgt = self.target()
            self.timer -= 1
            if tgt is None or self.timer <= 0:
                self.choose()
            else:
                tx, reachable = tgt
                dx = tx - (self.x + self.W / 2)
                close = abs(dx) < self.W * (0.35 if st == "play" else 0.3)
                if close and st == "chase":
                    self.caught_mouse()
                elif close and st == "food" and reachable:
                    self.eat(min(self.app.fish, key=lambda f: abs(f.cx - tx)))
                elif close and st == "play":
                    ball = self.app.balls[0]
                    if not self.on_window and ball.near_floor() and not self.kick_cd:
                        self.kick(ball)
                if not close or st == "play":
                    self.facing = 1 if dx > 0 else -1
                    mult = {"chase": 1.3, "food": 1.7, "play": 1.5}[st]
                    step = s * mult * self.sp["speed"] * (0.7 if self.energy < 20 else 1)
                    self.x += self.facing * min(abs(dx), step)
                    self.x = min(max(self.x, l), r - self.W)
                    self.moving = abs(dx) > 1

        else:  # idle, sleep, happy, eat
            self.y = ground
            if st == "happy":
                self.y -= abs(math.sin(self.t * 0.35)) * 3 * s
                if self.t % 10 == 0:
                    self.spawn("heart")
            elif st == "sleep" and self.t % 25 == 0:
                self.spawn("z")
            self.timer -= 1
            if st == "sleep" and self.energy >= 99:
                self.timer = min(self.timer, 0)
            if self.timer <= 0:
                if st == "eat":
                    self.pet()
                elif st == "sleep":
                    self.set_state("idle", 40)
                else:
                    self.choose()

        # tavşan ve kurbağa yürümez, zıplar
        self.airborne = False
        if self.moving and self.sp["hop"]:
            lift = math.sin((self.t % 14) / 14 * math.pi) * 3 * s
            self.y = ground - lift
            self.airborne = lift > s

        self.next_chat -= 1
        if self.next_chat <= 0:
            self.next_chat = random.randint(25 * 35, 25 * 90)
            if self.state not in ("sleep", "drag", "fall"):
                self.chatter()

        if self.t % 100 == 0:
            self.win.attributes("-topmost", True)
        self.update_particles()
        self.update_sprite()
        self.place()

    # -- çizim --
    def update_sprite(self):
        st = self.state
        frames = self.sp["frames"]
        if self.moving:
            if self.sp["hop"]:
                name = "walk2" if self.airborne else "walk1"
            else:
                name = "walk1" if (self.t // self.sp["step"]) % 2 == 0 else "walk2"
        elif st == "fall":
            name = "walk2" if self.vy < 0 else "dangle"
        elif st == "drag":
            name = "dangle"
        elif st == "sleep":
            name = "sleep"
        elif st == "happy":
            name = "happy2" if "happy2" in frames and (self.t // 3) % 2 else "happy"
        elif st == "eat":
            name = "happy" if (self.t // 5) % 2 == 0 else "walk1"
        else:
            name = "blink" if self.t % 70 < 4 else "walk1"
        key = (name, self.facing)
        if key != self.cur:
            img = self.app.img(self.species, self.color, name, self.facing, self.app.s)
            self.c.itemconfig(self.sprite, image=img)
            self.cur = key

    def head_pos(self):
        """Kafanın pencere içindeki konumu (piksel)."""
        s = self.app.s
        col, row = self.sp["sleep_head" if self.state == "sleep" else "head"]
        if self.facing == -1:
            col = 20 - col
        return col * s, self.top_pad + row * s

    def spawn(self, kind):
        s = self.app.s
        hx, hy = self.head_pos()
        item = self.c.create_image(hx + random.randint(-s, s), hy,
                                   image=self.app.effect(kind, max(2, s // 2)))
        self.particles.append([item, random.uniform(-0.3, 0.3) * s, 22])

    def update_particles(self):
        for p in self.particles[:]:
            self.c.move(p[0], p[1], -0.4 * self.app.s)
            p[2] -= 1
            if p[2] <= 0:
                self.c.delete(p[0])
                self.particles.remove(p)

    def place(self):
        self.win.geometry(f"+{int(self.x)}+{int(self.y)}")
        self.bubble.follow(self)

    def set_visible(self, visible):
        if visible:
            self.win.deiconify()
        else:
            self.win.withdraw()
            self.bubble.hide()

    # -- fare --
    def on_press(self, e):
        self.drag = (e.x_root - self.x, e.y_root - self.y, e.x_root, e.y_root)
        self.dragging = False

    def on_motion(self, e):
        if not self.drag:
            return
        ox, oy, sx, sy = self.drag
        if not self.dragging and abs(e.x_root - sx) + abs(e.y_root - sy) > 6:
            self.dragging = True
            self.on_window = False
            self.set_state("drag")
            self.px, self.py = self.x, self.y
        if self.dragging:
            self.x, self.y = e.x_root - ox, e.y_root - oy
            self.place()

    def on_release(self, e):
        if self.dragging:
            s = self.app.s
            cap = 6 * s
            if math.hypot(self.vx, self.vy) > 3.5 * s:
                self.say(random.choice(MOOD_LINES["thrown"]))
                self.app.stat("throws")
            self.vx = max(-cap, min(cap, self.vx))
            self.vy = max(-cap, min(cap, self.vy))
            self.set_state("fall")
        else:
            self.pet()
        self.drag, self.dragging = None, False

    def on_right(self, e):
        app = self.app
        m = app.menu
        m.delete(0, "end")
        m.add_command(label=f"{self.name} (seviye {self.level})", state="disabled")
        m.add_separator()
        m.add_command(label="Sev", command=self.pet)
        m.add_command(label="Besle", command=lambda: app.drop_fish(self.x + self.W / 2))
        m.add_command(label="Top at", command=app.throw_ball)
        if self.state == "sleep":
            m.add_command(label="Uyandır", command=self.pet)
        else:
            m.add_command(label="Uyut", command=lambda: self.set_state("sleep", 800))
        m.add_command(label="Beni kovala", command=lambda: self.set_state("chase", 300))
        m.add_command(label="Zıplat", command=self.jump)
        m.add_separator()
        m.add_command(label="Dostlarımı aç...", command=lambda: app.show_hub("pets"))
        m.add_command(label="Kaldır", command=lambda: app.remove_pet(self))
        m.tk_popup(e.x_root, e.y_root)

    def destroy(self):
        self.bubble.destroy()
        self.win.destroy()
