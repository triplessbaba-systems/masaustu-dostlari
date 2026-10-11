"""Kayıt dosyası, istatistikler, başarımlar ve ayarlar."""
import json
import os
import sys
import time
import uuid

from .sprites import ACCESSORIES, DRAGON_UNLOCK, SPECIES

SAVE_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "MasaustuDostlari")
SAVE_FILE = os.path.join(SAVE_DIR, "hayvanlar.json")
# 1.0 sürümü kaydı programın yanındaki klasöre yazıyordu
LEGACY_FILE = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0] or ".")), "hayvanlar.json")

DEFAULT_SETTINGS = {
    "size": "M",            # S / M / L
    "bubbles": True,        # konuşma balonları
    "walk_windows": True,   # pencerelerin üstünde yürü
    "chase_mouse": True,    # imleci kovala
    "night_mode": True,     # gece daha çok uyu
    "notify": True,         # acıkınca bildirim
    "autostart": False,     # Windows ile başlat
    "seasons": True,        # mevsim efektleri
    "updates": True,        # güncellemeleri denetle
    "lang": "tr",           # tr / en
}

DEFAULT_STATS = {
    "adopted": 0, "species": [], "pets": 0, "feeds": 0, "throws": 0, "kicks": 0,
    "catches": 0, "climbs": 0, "max_level": 1, "max_active": 0, "night": 0, "playtime": 0,
    "meets": 0, "game_best": 0, "dressed": 0, "dragon": 0,
}

# kimlik, başlık, açıklama, ikon, hedef, istatistik
ACHIEVEMENTS = [
    ("ilk_dost",   "İlk Dost",            "İlk dostunu sahiplen.",                    "paw",     1,  "adopted"),
    ("kalabalik",  "Kalabalık Ev",        "Masaüstünde aynı anda 5 dost olsun.",      "home",    5,  "max_active"),
    ("koleksiyon", "Koleksiyoncu",        "8 farklı türden dost sahiplen.",           "star",    8,  "species"),
    ("sevgi",      "Sevgi Dolu",          "Dostlarını toplam 50 kez sev.",            "heart",   50, "pets"),
    ("asci",       "Aşçıbaşı",            "Dostlarını 25 kez besle.",                 "fish",    25, "feeds"),
    ("ucan",       "Uçan Dost",           "Bir dostunu tutup havaya fırlat.",         "arrow",   1,  "throws"),
    ("oyun",       "Oyun Zamanı",         "Dostların topa 20 kez vursun.",            "ball",    20, "kicks"),
    ("yakala",     "Yakala Beni",         "Dostların imlecini 10 kez yakalasın.",     "cursor",  10, "catches"),
    ("gezgin",     "Gezgin",              "Bir dostun bir pencerenin üstüne çıksın.", "window",  1,  "climbs"),
    ("dostluk",    "Can Dostlar",         "Dostların birbiriyle 10 kez buluşsun.",    "people",  10, "meets"),
    ("avci",       "Usta Avcı",           "Mama Yağmuru'nda 25 puan topla.",          "gamepad", 25, "game_best"),
    ("moda",       "Moda İkonu",          "Bir dostuna aksesuar tak.",                "hat",     1,  "dressed"),
    ("usta",       "Usta Bakıcı",         "Bir dostunu 5. seviyeye ulaştır.",         "trophy",  5,  "max_level"),
    ("efsane",     "Efsane",              "Bir dostunu 10. seviyeye ulaştır.",        "crown",   10, "max_level"),
    ("ejderha",    "Ejderha Terbiyecisi", "Nadir ejderhayı sahiplen.",                "flame",   1,  "dragon"),
    ("gece",       "Gece Kuşu",           "Gece yarısından sonra dostlarınla takıl.", "moon",    1,  "night"),
]


def xp_needed(level):
    return 40 + 30 * (level - 1)


def new_pet(species, color, name):
    return {"id": uuid.uuid4().hex[:8], "species": species, "color": color, "name": name,
            "food": 80.0, "joy": 80.0, "energy": 90.0, "xp": 0, "level": 1, "acc": None,
            "adopted": int(time.time())}


def _valid_pet(d):
    return (isinstance(d, dict) and d.get("species") in SPECIES
            and d.get("color") in SPECIES[d["species"]]["colors"]
            and isinstance(d.get("name"), str))


class Store:
    def __init__(self):
        self.data = self._load()

    # -- dosya --
    def _load(self):
        raw = None
        try:
            with open(SAVE_FILE, encoding="utf-8") as f:
                raw = json.load(f)
        except (OSError, ValueError):
            pass
        data = {"version": 3, "pets": [], "friends": {}, "stats": dict(DEFAULT_STATS, species=[]), "unlocked": [],
                "settings": dict(DEFAULT_SETTINGS), "last_seen": time.time()}
        if isinstance(raw, list):                       # v1 kaydı: sadece hayvan listesi
            raw = {"pets": raw}
        if isinstance(raw, dict):
            for d in raw.get("pets", []):
                if _valid_pet(d):
                    pet = new_pet(d["species"], d["color"], d["name"])
                    pet.update({k: v for k, v in d.items() if k in pet})
                    data["pets"].append(pet)
            data["stats"].update(raw.get("stats", {}))
            data["unlocked"] = list(raw.get("unlocked", []))
            data["friends"] = dict(raw.get("friends", {}))
            data["settings"].update({k: v for k, v in raw.get("settings", {}).items()
                                     if k in DEFAULT_SETTINGS})
            data["last_seen"] = raw.get("last_seen", time.time())
            data["legacy_checked"] = raw.get("legacy_checked", False)
        if not data.get("legacy_checked"):
            data["legacy_checked"] = True
            data["pets"] += self._legacy_pets()
        return data

    @staticmethod
    def _legacy_pets():
        if os.path.normcase(LEGACY_FILE) == os.path.normcase(SAVE_FILE):
            return []
        try:
            with open(LEGACY_FILE, encoding="utf-8") as f:
                raw = json.load(f)
        except (OSError, ValueError):
            return []
        return [new_pet(d["species"], d["color"], d["name"]) for d in raw if _valid_pet(d)] \
            if isinstance(raw, list) else []

    def save(self, pets):
        self.data["pets"] = pets
        self.data["last_seen"] = time.time()
        try:
            os.makedirs(SAVE_DIR, exist_ok=True)
            tmp = SAVE_FILE + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            os.replace(tmp, SAVE_FILE)
        except OSError:
            pass

    # -- kısayollar --
    @property
    def settings(self):
        return self.data["settings"]

    @property
    def stats(self):
        return self.data["stats"]

    @property
    def unlocked(self):
        return self.data["unlocked"]

    # -- istatistik + başarımlar --
    def bump(self, key, n=1):
        self.stats[key] = self.stats.get(key, 0) + n
        return self.check()

    def set_max(self, key, value):
        if value > self.stats.get(key, 0):
            self.stats[key] = value
        return self.check()

    def add_species(self, species):
        if species not in self.stats["species"]:
            self.stats["species"].append(species)
        return self.check()

    def progress(self, stat):
        v = self.stats.get(stat, 0)
        return len(v) if isinstance(v, list) else v

    def check(self):
        """Yeni açılan başarımların listesini döndür."""
        new = []
        for ach in ACHIEVEMENTS:
            aid, goal, stat = ach[0], ach[4], ach[5]
            if aid not in self.unlocked and self.progress(stat) >= goal:
                self.unlocked.append(aid)
                new.append(ach)
        return new

    # -- kilitler --
    def dragon_unlocked(self):
        return len(self.unlocked) >= DRAGON_UNLOCK

    def acc_unlocked(self, acc):
        kind, value = ACCESSORIES[acc]["req"]
        if kind == "level":
            return self.stats.get("max_level", 1) >= value
        if kind == "ach":
            return len(self.unlocked) >= value
        return time.localtime().tm_mon == value

    # -- arkadaşlık --
    def meet(self, a, b):
        key = "|".join(sorted((a, b)))
        self.data["friends"][key] = self.data["friends"].get(key, 0) + 1
        return self.bump("meets")

    def best_friend(self, pid):
        """(arkadaş kimliği, buluşma sayısı) ya da None."""
        best = None
        for key, n in self.data["friends"].items():
            ids = key.split("|")
            if pid in ids:
                other = ids[1] if ids[0] == pid else ids[0]
                if best is None or n > best[1]:
                    best = (other, n)
        return best

    def forget(self, pid):
        self.data["friends"] = {k: v for k, v in self.data["friends"].items() if pid not in k.split("|")}

    def reset_progress(self):
        self.data["stats"] = dict(DEFAULT_STATS, species=[])
        self.data["unlocked"] = []
