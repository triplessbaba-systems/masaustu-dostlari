"""Piksel art: hayvan kareleri, renk paletleri, tür bilgileri ve arayüz ikonları.

Tüm hayvanlar 20x16 piksel, sağa bakıyor, ayakları en alt satırda.
K: çizgi  O: ana renk  D: koyu ton  W: açık ton  E: göz  P: pembe  Y: gaga/ayak
"""

BASE_PALETTE = {
    "K": "#2b1d14", "E": "#1a1a1a", "P": "#ff8fab", "W": "#fff4e6", "Y": "#ffb703",
    "R": "#e63946", "B": "#5fa8d3", "L": "#cae9ff", "Z": "#4361ee", "S": "#ffffff",
}
BLANK = "." * 20


def patch(rows, *edits):
    """(satır, sütun, metin) düzenlemeleriyle yeni bir kare üret."""
    rows = list(rows)
    for r, c, txt in edits:
        rows[r] = rows[r][:c] + txt + rows[r][c + len(txt):]
    return rows


LEGS_A = ["...KOK.KOK..KOK.KOK.",
          "...KWK.KWK..KWK.KWK.",
          "...KKK.KKK..KKK.KKK."]
LEGS_B = ["....KOKKOK..KOKKOK..",
          "....KWKKWK..KWKKWK..",
          "....KKKKKK..KKKKKK.."]

# Kedi ---------------------------------------------------------------------------
CAT_BODY = [
    ".............K....K.",
    "............KPK..KPK",
    "............KOOOOOOK",
    "..K.........KOEOOEOK",
    ".KOK........KOEPPEOK",
    ".KOK........KWWWWWWK",
    ".KOK.KKKKKKKKWWWWWK.",
    "..KOOOOOOOOOOOWWWK..",
    "...KOODOOODOOOOWWK..",
    "...KOOOOOOOOOOOOOK..",
    "...KOODOOODOOOOOOK..",
    "...KOOOOOOOOOOOOOK..",
    "....KKKKKKKKKKKKK...",
]


def cat_frames():
    walk1 = CAT_BODY + LEGS_A
    closed = ((3, 12, "KOOOOOOK"), (4, 12, "KOKPPKOK"))
    return dict(
        walk1=walk1,
        walk2=CAT_BODY + LEGS_B,
        blink=patch(walk1, *closed),
        happy=patch(walk1, (3, 12, "KOKOOKOK"), (4, 12, "KPOPPOPK")),
        dangle=patch(walk1, (5, 12, "KWWKKWWK")),
        sleep=[BLANK] * 3 + patch(CAT_BODY, *closed),
    )


# Köpek --------------------------------------------------------------------------
DOG_BODY = [
    BLANK,
    "............KKKKK...",
    "...........KOOOOOK..",
    "..........KDDOOEOKK.",
    ".K........KDDOOOWWEK",
    "KOK.......KDDOOWWWWK",
    ".KOK.KKKKKKDKOOKKKK.",
    "..KOOOOOOOKDKOOOOK..",
    "...KOOOOOOOKOOOWWK..",
    "...KODDOOOOOOOWWWK..",
    "...KOODOOOODOOOWWK..",
    "...KOOOOOOOOOOOOOK..",
    "....KKKKKKKKKKKKK...",
]
DOG_TAIL_UP = ((3, 0, "..K."), (4, 0, ".KOK"), (5, 0, ".KOK"), (6, 0, "..KK"))


def dog_frames():
    walk1 = DOG_BODY + LEGS_A
    happy = patch(walk1, (3, 15, "K"), (6, 16, "PP"))
    return dict(
        walk1=walk1,
        walk2=patch(DOG_BODY + LEGS_B, *DOG_TAIL_UP),
        blink=patch(walk1, (3, 15, "D")),
        happy=happy,
        happy2=patch(happy, *DOG_TAIL_UP),      # kuyruk sallama
        dangle=patch(walk1, (6, 17, "P")),
        sleep=[BLANK] * 3 + patch(DOG_BODY, (3, 15, "D")),
    )


# Tavşan -------------------------------------------------------------------------
RABBIT_BODY = [
    "..............KK.KK.",
    ".............KPKKPK.",
    ".............KPKKPK.",
    ".............KOKKOK.",
    "............KOOOOOOK",
    "............KOOOEOOK",
    "............KOOOOOPK",
    ".....KKKKKKKKWWWWWK.",
    "...KKOOOOOOOOOWWWK..",
    "..KWKOOOOOOOOOOOOK..",
    "..KWWKOOOOOOOOOOOK..",
    "...KKOOOOOOOOOOOOK..",
    "....KKKKKKKKKKKKK...",
]
RABBIT_LEGS_A = ["....KOOK....KOK.....",
                 "...KWWWK....KWK.....",
                 "...KKKKK....KKK....."]
RABBIT_LEGS_B = ["....KOK.....KOK.....",
                 "...KWWK......KWK....",
                 "...KKKK......KKK...."]


def rabbit_frames():
    walk1 = RABBIT_BODY + RABBIT_LEGS_A
    return dict(
        walk1=walk1,
        walk2=RABBIT_BODY + RABBIT_LEGS_B,
        blink=patch(walk1, (5, 16, "O")),
        happy=patch(walk1, (5, 16, "K"), (6, 14, "P")),
        dangle=patch(RABBIT_BODY + RABBIT_LEGS_B, (6, 17, "K")),
        sleep=patch(walk1, (5, 16, "D"), (6, 14, "P")),
    )


# Penguen ------------------------------------------------------------------------
PENGUIN_BODY = [
    "......KKKKK.........",
    ".....KOOOOOK........",
    "....KOOOOOOOK.......",
    "....KOOOOWEOK.......",
    "....KOOOOOOOYYYK....",
    "....KOOOOWWWKK......",
    "...KOOOWWWWWWK......",
    "..KOKOOWWWWWWWK.....",
    "..KOKOOWWWWWWWK.....",
    "..KOKOOWWWWWWWK.....",
    "...KKOOWWWWWWWK.....",
    "....KOOWWWWWWWK.....",
    "....KOOOWWWWWK......",
    ".....KKKKKKKKK......",
]
PENGUIN_FEET_A = ["......KYYK.KYYK.....",
                  "......KKKK.KKKK....."]
PENGUIN_FEET_B = [".......KYYK.KYYK....",
                  ".......KKKK.KKKK...."]


def penguin_frames():
    walk1 = PENGUIN_BODY + PENGUIN_FEET_A
    return dict(
        walk1=walk1,
        walk2=PENGUIN_BODY + PENGUIN_FEET_B,
        blink=patch(walk1, (3, 9, "OO")),
        happy=patch(walk1, (3, 9, "OK"), (5, 8, "P")),
        dangle=patch(PENGUIN_BODY + PENGUIN_FEET_B, (4, 12, "YKY")),
        sleep=patch(walk1, (3, 9, "OK")),
    )


# Kurbağa ------------------------------------------------------------------------
FROG_BODY = [BLANK] * 5 + [
    "..........KKK.KKK...",
    ".........KWEWKWEWK..",
    "........KOOOOOOOOOK.",
    "......KKOOOOOOOOOOOK",
    ".....KOOOOOOOOOOKKKK",
    "....KOODOOOOOOOWWWK.",
    "...KOOOOODOOOOWWWWK.",
    "...KOODOOOOOOWWWWK..",
]
FROG_LEGS_A = ["..KOOOKKKKKKKKOOK...",
               ".KOOOOK......KOK....",
               "KDDDDK......KDDK...."]
FROG_LEGS_B = ["...KOOKKKKKKKKKOK...",
               "..KOOK.......KOK....",
               ".KDDK.........KDK..."]


def frog_frames():
    walk1 = FROG_BODY + FROG_LEGS_A
    return dict(
        walk1=walk1,
        walk2=FROG_BODY + FROG_LEGS_B,
        blink=patch(walk1, (6, 9, "KDDDKDDDK")),
        happy=patch(walk1, (6, 9, "KOKOKOKOK"), (9, 18, "PP")),
        dangle=patch(FROG_BODY + FROG_LEGS_B, (9, 16, "KPPK")),
        sleep=patch(walk1, (6, 9, "KDDDKDDDK")),
    )


# --- Türler -------------------------------------------------------------------------
SPECIES = {
    "kedi": dict(
        title="Kedi", frames=cat_frames(), speed=1.0, hop=False, step=4,
        head=(16, 0), sleep_head=(16, 3),
        desc="Meraklı ve biraz uykucu. İmlecini görünce dayanamaz, hemen peşine düşer.",
        traits=["Meraklı", "Uykucu", "Avcı"],
        stats={"Hız": 3, "Oyunculuk": 3, "Uykuculuk": 5},
        lines=["Miyav!", "Mırrr...", "Fare nerede?", "Pati pati", "Miyaav?"],
        names=["Tarçın", "Pamuk", "Duman", "Boncuk", "Zeytin", "Fıstık", "Mırmır", "Paşa"],
        colors={
            "Turuncu": {"O": "#f4a259", "D": "#d9822b", "W": "#fff4e6"},
            "Siyah":   {"O": "#3b3b48", "D": "#2a2a34", "W": "#f0f0f0", "K": "#101014", "E": "#c7f464"},
            "Gri":     {"O": "#a3acb9", "D": "#7b8796", "W": "#ffffff", "K": "#2a2f38"},
            "Beyaz":   {"O": "#f7f7f7", "D": "#dcdcdc", "W": "#ffffff", "K": "#3a3a44", "E": "#3d8bd9"},
            "Tekir":   {"O": "#b07d4f", "D": "#6f4a2f", "W": "#f6e7d2"},
        }),
    "kopek": dict(
        title="Köpek", frames=dog_frames(), speed=1.3, hop=False, step=3,
        head=(14, 1), sleep_head=(14, 4),
        desc="Enerjik ve sadık. Topu görünce yerinde duramaz, masaüstünün en hızlısı.",
        traits=["Sadık", "Enerjik", "Oyuncu"],
        stats={"Hız": 5, "Oyunculuk": 5, "Uykuculuk": 2},
        lines=["Hav hav!", "Top atar mısın?", "Kuyruğum sallanıyor!", "Hav!", "Gezelim mi?"],
        names=["Karabaş", "Çomar", "Bobi", "Lokum", "Max", "Fındık", "Kontes", "Rex"],
        colors={
            "Altın":      {"O": "#e9b872", "D": "#c98f45", "W": "#fff4e0"},
            "Çikolata":   {"O": "#7b4b2a", "D": "#4e2f1a", "W": "#d9b38c", "K": "#22140b"},
            "Dalmaçyalı": {"O": "#fafafa", "D": "#222222", "W": "#ffffff", "K": "#333333"},
            "Husky":      {"O": "#5a5f6b", "D": "#3a3e47", "W": "#ffffff", "K": "#1b1d22", "E": "#4ea8de"},
        }),
    "tavsan": dict(
        title="Tavşan", frames=rabbit_frames(), speed=1.1, hop=True, step=4,
        head=(16, 0), sleep_head=(16, 0),
        desc="Yumuşacık ve tez canlı. Hiç yürümez, nereye giderse zıplayarak gider.",
        traits=["Zıpzıp", "Yumuşak", "Tatlı"],
        stats={"Hız": 4, "Oyunculuk": 4, "Uykuculuk": 3},
        lines=["Havuç var mı?", "Zıp zıp!", "Burnum kaşınıyor", "Hop!"],
        names=["Havuç", "Pofuduk", "Bulut", "Ponpon", "Zıpzıp", "Kar Tanesi"],
        colors={
            "Beyaz": {"O": "#f8f8f8", "D": "#e0e0e0", "W": "#ffffff", "K": "#3a3a44", "E": "#e63946"},
            "Kahve": {"O": "#a47551", "D": "#7d5a3c", "W": "#f1e3d3"},
            "Gri":   {"O": "#b8b8c4", "D": "#8d8d9b", "W": "#f4f4f8", "K": "#2f2f3a"},
        }),
    "penguen": dict(
        title="Penguen", frames=penguin_frames(), speed=0.55, hop=False, step=6,
        head=(8, 0), sleep_head=(8, 0),
        desc="Sakin ve paytak. Hiç acele etmez ama gittiği her yere neşe götürür.",
        traits=["Sakin", "Paytak", "Soğukkanlı"],
        stats={"Hız": 1, "Oyunculuk": 3, "Uykuculuk": 3},
        lines=["Buz gibi!", "Paytak paytak...", "Balık?", "Brr!"],
        names=["Pingu", "Buzlu", "Frak", "Tıpış", "Kutup", "Paytak"],
        colors={
            "Klasik": {"O": "#2d3142", "D": "#1f2230", "W": "#ffffff", "K": "#11131a", "E": "#11131a"},
            "Mavi":   {"O": "#4f86c6", "D": "#3a6aa3", "W": "#f0f7ff", "K": "#1d2f4a", "Y": "#f4a261"},
            "Pembe":  {"O": "#ff8fab", "D": "#e56b8a", "W": "#fff0f5", "K": "#5a2a3a", "Y": "#ffd166",
                       "P": "#e63946"},
        }),
    "kurbaga": dict(
        title="Kurbağa", frames=frog_frames(), speed=0.9, hop=True, step=4,
        head=(13, 4), sleep_head=(13, 4),
        desc="Gölet sever, zıplamayı daha da çok sever. Ne zaman vıraklayacağı belli olmaz.",
        traits=["Zıplayan", "Gürültücü", "Neşeli"],
        stats={"Hız": 3, "Oyunculuk": 4, "Uykuculuk": 2},
        lines=["Vırak!", "Sinek gördüm!", "Vıraaak", "Hop hop!"],
        names=["Vırak", "Kurbi", "Yaprak", "Zıpır", "Bezelye", "Nilüfer"],
        colors={
            "Yeşil":   {"O": "#7bc950", "D": "#4c9a2a", "W": "#e9f5c9", "K": "#1f3a12"},
            "Mavi":    {"O": "#3a86ff", "D": "#1d4ed8", "W": "#cfe3ff", "K": "#0b1f4d"},
            "Turuncu": {"O": "#ff9f1c", "D": "#e76f51", "W": "#ffe8c2", "K": "#4a2108"},
        }),
}
SPECIES_ORDER = ["kedi", "kopek", "tavsan", "penguen", "kurbaga"]

MOOD_LINES = {
    "hungry": ["Acıktım!", "Mama?", "Karnım guruldadı..."],
    "tired": ["Uykum geldi...", "Esniyorum...", "Biraz kestireyim"],
    "sad": ["Biraz ilgi?", "Sıkıldım...", "Beni sever misin?"],
    "happy": ["Seni seviyorum!", "Çok mutluyum!", "♥ ♥ ♥"],
    "missed": ["Seni özledim!", "Neredeydin?", "Geri geldin!"],
    "thrown": ["Wiiii!", "Uçuyorum!", "Aaaa!"],
    "woke": ["Hı? Ne oldu?", "Uyuyordum...", "Günaydın!"],
}


def first_color(species):
    return next(iter(SPECIES[species]["colors"]))


def palette(species, color):
    return dict(BASE_PALETTE, **SPECIES[species]["colors"][color])


# --- Masaüstü efektleri -------------------------------------------------------------
EFFECTS = {
    "heart": [
        ".KK...KK.",
        "KRRK.KRRK",
        "KRSRKRRRK",
        "KRRRRRRRK",
        ".KRRRRRK.",
        "..KRRRK..",
        "...KRK...",
        "....K....",
    ],
    "z": [
        "ZZZZZ",
        "...Z.",
        "..Z..",
        ".Z...",
        "ZZZZZ",
    ],
    "fish": [
        "...KKKKK....",
        ".KKBBBBBK.KK",
        "KBEBBBBBBKBK",
        "KBBBBLBBBBBK",
        "KBBBBBBBBKBK",
        ".KKBBBBBK.KK",
        "...KKKKK....",
    ],
    "ball": [
        "..KKKK..",
        ".KRRSSK.",
        "KRRRRSSK",
        "KSSSSSSK",
        "KRRRRRRK",
        "KRRRRRRK",
        ".KRRRRK.",
        "..KKKK..",
    ],
    "star": [
        "...Y...",
        "...Y...",
        ".YYYYY.",
        "YYYSYYY",
        ".YYYYY.",
        "...Y...",
        "...Y...",
    ],
}

# --- Arayüz ikonları (tek renk piksel ikonlar, X: ana renk) ---------------------------
UI_ICONS = {
    "paw": [
        "..XX.XX..",
        "..XX.XX..",
        ".........",
        "XX.....XX",
        "XX.XXX.XX",
        "..XXXXX..",
        ".XXXXXXX.",
        ".XXXXXXX.",
        "..XX.XX..",
    ],
    "heart": [
        ".XX.XX.",
        "XXXXXXX",
        "XXXXXXX",
        ".XXXXX.",
        "..XXX..",
        "...X...",
    ],
    "fish": [
        "...XXXX...",
        ".XXXXXXX.X",
        "XX.XXXXXXX",
        "XXXXXXXXXX",
        ".XXXXXXX.X",
        "...XXXX...",
    ],
    "bolt": [
        "...XXX",
        "..XXX.",
        ".XXX..",
        "XXXXXX",
        "..XXX.",
        ".XXX..",
        ".XX...",
        "XX....",
    ],
    "trophy": [
        "XXXXXXXXX",
        "X.XXXXX.X",
        "X.XXXXX.X",
        ".XXXXXXX.",
        "..XXXXX..",
        "...XXX...",
        "....X....",
        "..XXXXX..",
    ],
    "gear": [
        "...X.X...",
        "..XXXXX..",
        ".XXXXXXX.",
        "XXX...XXX",
        ".XX...XX.",
        "XXX...XXX",
        ".XXXXXXX.",
        "..XXXXX..",
        "...X.X...",
    ],
    "ball": [
        "..XXXX..",
        ".XX..XX.",
        "XX.XX..X",
        "X.XXXX.X",
        "X.XXXX.X",
        "X..XX.XX",
        ".XX..XX.",
        "..XXXX..",
    ],
    "moon": [
        "..XXX...",
        ".XX.....",
        "XX......",
        "XX......",
        "XX.....X",
        "XXX...XX",
        ".XXXXXX.",
        "..XXXX..",
    ],
    "target": [
        "...XXX...",
        ".XX...XX.",
        ".X..X..X.",
        "X..XXX..X",
        ".X..X..X.",
        ".XX...XX.",
        "...XXX...",
    ],
    "x": [
        "X.....X",
        ".X...X.",
        "..X.X..",
        "...X...",
        "..X.X..",
        ".X...X.",
        "X.....X",
    ],
    "check": [
        ".......X",
        "......XX",
        "X....XX.",
        "XX..XX..",
        ".XXXX...",
        "..XX....",
    ],
    "sparkle": [
        "...X...",
        "...X...",
        "..XXX..",
        "XXXXXXX",
        "..XXX..",
        "...X...",
        "...X...",
    ],
    "star": [
        "....X....",
        "...XXX...",
        "XXXXXXXXX",
        ".XXXXXXX.",
        "..XXXXX..",
        "..XX.XX..",
        ".XX...XX.",
    ],
    "lock": [
        "..XXX..",
        ".X...X.",
        ".X...X.",
        "XXXXXXX",
        "XXX.XXX",
        "XXX.XXX",
        "XXXXXXX",
    ],
    "window": [
        "XXXXXXXXX",
        "XXXXXXXXX",
        "X.......X",
        "X.......X",
        "X.......X",
        "XXXXXXXXX",
    ],
    "arrow": [
        "...XXXXX",
        ".....XXX",
        "....X.XX",
        "...X...X",
        "..X.....",
        ".X......",
        "X.......",
    ],
    "cursor": [
        "X......",
        "XX.....",
        "XXX....",
        "XXXX...",
        "XXXXX..",
        "XXXXXX.",
        "XXX....",
        "X.XX...",
        "...XX..",
    ],
    "people": [
        ".XX...XX.",
        "XXXX.XXXX",
        ".XX...XX.",
        ".........",
        "XXXX.XXXX",
        "XXXX.XXXX",
    ],
    "crown": [
        "X...X...X",
        "XX.XXX.XX",
        "XXXXXXXXX",
        "XXXXXXXXX",
        ".XXXXXXX.",
    ],
    "power": [
        "...X...",
        ".X.X.X.",
        "X..X..X",
        "X.....X",
        "X.....X",
        ".X...X.",
        "..XXX..",
    ],
    "eye": [
        "..XXXXX..",
        ".X.....X.",
        "X...X...X",
        "X..XXX..X",
        "X...X...X",
        ".X.....X.",
        "..XXXXX..",
    ],
    "dice": [
        "XXXXXXX",
        "X.XXX.X",
        "XXXXXXX",
        "XXX.XXX",
        "XXXXXXX",
        "X.XXX.X",
        "XXXXXXX",
    ],
}
