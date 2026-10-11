"""Piksel art: hayvan kareleri, renk paletleri, tür bilgileri ve arayüz ikonları.

Tüm hayvanlar 20x16 piksel, sağa bakıyor, ayakları en alt satırda.
K: çizgi  O: ana renk  D: koyu ton  W: açık ton  E: göz  P: pembe  Y: gaga/ayak
"""

BASE_PALETTE = {
    "K": "#2b1d14", "E": "#1a1a1a", "P": "#ff8fab", "W": "#fff4e6", "Y": "#ffb703",
    "R": "#e63946", "B": "#5fa8d3", "L": "#cae9ff", "Z": "#4361ee", "S": "#ffffff",
    # efekt ve aksesuar renkleri (türler bunları ezmez)
    "A": "#e76f51", "G": "#6a994e", "N": "#ff8fab", "C": "#ffd166", "M": "#7b2cbf",
    "H": "#2b2d42", "T": "#7f5539", "Q": "#8d99ae",
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


# Tilki --------------------------------------------------------------------------
FOX_BODY = [
    "..............K...K.",
    ".............KDK.KDK",
    ".............KOOOOOK",
    ".KK.........KOOEOOOK",
    "KWWK........KWWOOOOE",
    "KWOOK.......KWWWWWK.",
    "KOOOOKKKKKKKKWWWWK..",
    ".KOOODOOOOOOOOWWWK..",
    "..KKOOOOOOOOOOOWWK..",
    "...KOOOOOOOOOOOOOK..",
    "...KOOOOOOOOOOOOOK..",
    "...KDOOOOOOOOOOODK..",
    "....KKKKKKKKKKKKK...",
]
FOX_LEGS_A = ["...KDK.KDK..KDK.KDK.",
              "...KDK.KDK..KDK.KDK.",
              "...KKK.KKK..KKK.KKK."]
FOX_LEGS_B = ["....KDKKDK..KDKKDK..",
              "....KDKKDK..KDKKDK..",
              "....KKKKKK..KKKKKK.."]


def fox_frames():
    walk1 = FOX_BODY + FOX_LEGS_A
    return dict(
        walk1=walk1,
        walk2=FOX_BODY + FOX_LEGS_B,
        blink=patch(walk1, (3, 15, "D")),
        happy=patch(walk1, (3, 15, "K"), (4, 14, "P")),
        dangle=patch(walk1, (5, 15, "KK")),
        sleep=[BLANK] * 3 + patch(FOX_BODY, (3, 15, "D")),
    )


# Ördek --------------------------------------------------------------------------
DUCK_BODY = [BLANK] * 3 + [
    "............KKKK....",
    "...........KOOOOK...",
    "...........KOOOEOK..",
    "...........KOOOOOYYK",
    "...........KOOOOKKK.",
    ".K.........KOOOOK...",
    ".KK.KKKKKKKOOOOOK...",
    ".KOKOOOOOOOOOOOOOK..",
    "..KODDDDDDOOOOOOOK..",
    "..KOODDDDDOOOOOOOK..",
    "...KOOOOOOOOOOOOK...",
    "....KKKKKKKKKKKK....",
]
DUCK_FEET_A = ["......KYYK..KYYK...."]
DUCK_FEET_B = [".......KYYKKYYK....."]


def duck_frames():
    walk1 = DUCK_BODY + DUCK_FEET_A
    return dict(
        walk1=walk1,
        walk2=DUCK_BODY + DUCK_FEET_B,
        blink=patch(walk1, (5, 15, "D")),
        happy=patch(walk1, (5, 15, "K")),
        dangle=patch(DUCK_BODY + DUCK_FEET_B, (7, 16, "YY")),
        sleep=patch(walk1, (5, 15, "D")),
    )


# Hamster ------------------------------------------------------------------------
HAMSTER_BODY = [BLANK] * 6 + [
    "......KK.....KK.....",
    ".....KPKKKKKKPK.....",
    "....KOOOOOOOOOOK....",
    "...KOOOOOOOOEOOOK...",
    "...KOOOOOOOWWWWPK...",
    "..KOOOOOOOOWWWWWK...",
    "..KOOOOOOOOWWWWWK...",
    "..KDOOOOOOOWWWWK....",
    "...KKKKKKKKKKKKK....",
]
HAMSTER_LEGS_A = ["....KPK....KPK......"]
HAMSTER_LEGS_B = [".....KPK..KPK......."]


def hamster_frames():
    walk1 = HAMSTER_BODY + HAMSTER_LEGS_A
    return dict(
        walk1=walk1,
        walk2=HAMSTER_BODY + HAMSTER_LEGS_B,
        blink=patch(walk1, (9, 12, "D")),
        happy=patch(walk1, (9, 12, "K"), (10, 11, "P")),
        dangle=HAMSTER_BODY + HAMSTER_LEGS_B,
        sleep=patch(walk1, (9, 12, "D")),
    )


# Ejderha ------------------------------------------------------------------------
DRAGON_BODY = [
    "..............K..K..",
    ".............KYKKYK.",
    ".............KOOOOK.",
    "....KK......KOOOEOOK",
    "...KDDK.....KOOOOOOE",
    "..KDDDDK....KWWWWWK.",
    "..KDDDDDKKKKKWWWWK..",
    "KK.KDDDDOOOOOOWWWK..",
    "KOK.KOOOOOOOOOOWWK..",
    ".KOKKOOOOOOOOOOOOK..",
    "..KOOOOOOOOOOOOOOK..",
    "...KOOOOOOOOOOOOOK..",
    "....KKKKKKKKKKKKK...",
]
DRAGON_WING_UP = ((2, 3, "KK"), (3, 2, "KDDK"), (4, 2, "KDDDK"), (5, 2, "KDDDDK"))


def dragon_frames():
    walk1 = DRAGON_BODY + LEGS_A
    happy = patch(walk1, (3, 16, "K"))
    return dict(
        walk1=walk1,
        walk2=patch(DRAGON_BODY + LEGS_B, *DRAGON_WING_UP),
        blink=patch(walk1, (3, 16, "D")),
        happy=happy,
        happy2=patch(happy, *DRAGON_WING_UP),          # kanat çırpma
        dangle=patch(walk1, *DRAGON_WING_UP),
        sleep=patch(walk1, (3, 16, "D")),
    )


# --- Türler -------------------------------------------------------------------------
SPECIES = {
    "kedi": dict(
        title="Kedi", frames=cat_frames(), speed=1.0, hop=False, step=4,
        head=(16, 0), sleep_head=(16, 3), hat=(15.5, 2), sleep_dy=3,
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
        head=(14, 1), sleep_head=(14, 4), hat=(14.5, 1), sleep_dy=3,
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
        head=(16, 0), sleep_head=(16, 0), hat=(15.5, 4), sleep_dy=0,
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
        head=(8, 0), sleep_head=(8, 0), hat=(8, 0), sleep_dy=0,
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
        head=(13, 4), sleep_head=(13, 4), hat=(13.5, 5), sleep_dy=0,
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
    "tilki": dict(
        title="Tilki", frames=fox_frames(), speed=1.15, hop=False, step=3,
        head=(16, 0), sleep_head=(16, 3), hat=(16, 2), sleep_dy=3,
        desc="Kurnaz ve çevik. Kabarık kuyruğuyla ortalıkta sessizce dolaşır.",
        traits=["Kurnaz", "Çevik", "Sessiz"],
        stats={"Hız": 4, "Oyunculuk": 3, "Uykuculuk": 3},
        lines=["Hmm...", "Bir şey mi duydum?", "Kuyruğum kabarık!", "Psst!"],
        names=["Kızıl", "Kurnaz", "Ateş", "Çakıl", "Sincap", "Pırıl"],
        colors={
            "Kızıl": {"O": "#f08a4b", "D": "#9c4a1f", "W": "#fff5ea"},
            "Kutup": {"O": "#eef2f6", "D": "#9aa5b4", "W": "#ffffff", "K": "#3a3f4a"},
            "Gümüş": {"O": "#7b8291", "D": "#3f4450", "W": "#e5e7eb", "K": "#1d2027"},
        }),
    "ordek": dict(
        title="Ördek", frames=duck_frames(), speed=0.8, hop=False, step=4,
        head=(14, 3), sleep_head=(14, 3), hat=(13.5, 3), sleep_dy=0,
        desc="Neşeli ve geveze. Yürürken iki yana sallanır, gölet görünce dayanamaz.",
        traits=["Geveze", "Neşeli", "Meraklı"],
        stats={"Hız": 2, "Oyunculuk": 4, "Uykuculuk": 2},
        lines=["Vak vak!", "Vak?", "Su nerede?", "Vaaak!"],
        names=["Vakvak", "Limon", "Paytak", "Badi", "Tüy", "Dalgıç"],
        colors={
            "Beyaz": {"O": "#fdfdfd", "D": "#d6d6d6", "K": "#3a3a44"},
            "Civciv": {"O": "#ffd84d", "D": "#f2b705", "K": "#5a4300", "Y": "#ff8c1a"},
            "Kahve": {"O": "#b08968", "D": "#7f5539", "K": "#2e1d10"},
        }),
    "hamster": dict(
        title="Hamster", frames=hamster_frames(), speed=0.9, hop=False, step=2,
        head=(12, 6), sleep_head=(12, 6), hat=(10, 7), sleep_dy=0,
        desc="Minik ve tombul. Yanaklarını doldurur, küçük adımlarla hızlı hızlı koşar.",
        traits=["Minik", "Tombul", "Telaşlı"],
        stats={"Hız": 3, "Oyunculuk": 3, "Uykuculuk": 4},
        lines=["Çekirdek?", "Yanaklarım dolu!", "Tık tık tık", "Koşmam lazım!"],
        names=["Fındık", "Tombi", "Mısır", "Pamuk", "Çekirdek", "Bıcır"],
        colors={
            "Altın": {"O": "#e8a95b", "D": "#c98536", "W": "#fff1dc"},
            "Beyaz": {"O": "#f4f1ea", "D": "#d8d2c4", "W": "#ffffff", "K": "#3a3a44"},
            "Gri":   {"O": "#9aa0a6", "D": "#6b7178", "W": "#eef0f2", "K": "#2a2d33"},
        }),
    "ejderha": dict(
        title="Ejderha", frames=dragon_frames(), speed=1.1, hop=False, step=3, glide=True, rare=True,
        head=(16, 0), sleep_head=(16, 0), hat=(15.5, 2), sleep_dy=0,
        desc="Nadir bulunur. Zıpladığında kanatlarını açıp yavaşça süzülerek iner.",
        traits=["Nadir", "Süzülür", "Asil"],
        stats={"Hız": 4, "Oyunculuk": 4, "Uykuculuk": 4},
        lines=["Rawr!", "Kanatlarım hazır!", "Hazine nerede?", "Fsss..."],
        names=["Alev", "Kıvılcım", "Zümrüt", "Duman", "Yakut", "Gece"],
        colors={
            "Zümrüt": {"O": "#3fb37f", "D": "#2a7f5a", "W": "#d9f7c6", "Y": "#ffcf56"},
            "Ateş":   {"O": "#e4572e", "D": "#a63a1f", "W": "#ffd29d", "Y": "#ffd166"},
            "Gece":   {"O": "#4b3f8f", "D": "#2e2760", "W": "#c7b8ff", "Y": "#e0e0e0", "E": "#ffd166"},
        }),
}
SPECIES_ORDER = ["kedi", "kopek", "tavsan", "penguen", "kurbaga", "tilki", "ordek", "hamster", "ejderha"]
DRAGON_UNLOCK = 8          # ejderha için gereken başarım sayısı

# İngilizce metinler (Türkçe kayıt anahtarları değişmez)
SPECIES_EN = {
    "kedi": dict(title="Cat", desc="Curious and a little sleepy. Can't resist chasing your cursor.",
                 traits=["Curious", "Sleepy", "Hunter"], lines=["Meow!", "Purrr...", "Where's the mouse?", "Mrrp?"],
                 names=["Biscuit", "Shadow", "Mochi", "Pepper", "Olive", "Ginger"]),
    "kopek": dict(title="Dog", desc="Energetic and loyal. Goes wild for the ball, the fastest buddy around.",
                  traits=["Loyal", "Energetic", "Playful"],
                  lines=["Woof!", "Throw the ball?", "Tail is wagging!", "Walk?"],
                  names=["Buddy", "Max", "Rocky", "Cookie", "Bean", "Rex"]),
    "tavsan": dict(title="Bunny", desc="Soft and quick. Never walks, always hops.",
                   traits=["Hoppy", "Fluffy", "Sweet"], lines=["Got a carrot?", "Hop hop!", "My nose itches", "Hop!"],
                   names=["Carrot", "Fluff", "Cloud", "Pompom", "Snowflake", "Clover"]),
    "penguen": dict(title="Penguin", desc="Calm and waddly. Never in a hurry, but brings joy wherever it goes.",
                    traits=["Calm", "Waddly", "Cool"], lines=["Ice cold!", "Waddle waddle...", "Fish?", "Brr!"],
                    names=["Pingu", "Frost", "Tux", "Waddles", "Polar", "Pebble"]),
    "kurbaga": dict(title="Frog", desc="Loves ponds, loves hopping even more. You never know when it'll croak.",
                    traits=["Hopper", "Noisy", "Cheerful"], lines=["Ribbit!", "I saw a fly!", "Ribbiiit", "Hop hop!"],
                    names=["Ribbit", "Kermie", "Leaf", "Bubbles", "Pea", "Lily"]),
    "tilki": dict(title="Fox", desc="Clever and nimble. Sneaks around quietly with its fluffy tail.",
                  traits=["Clever", "Nimble", "Quiet"],
                  lines=["Hmm...", "Did I hear something?", "Fluffy tail!", "Psst!"],
                  names=["Rusty", "Scout", "Ember", "Pebble", "Maple", "Sly"]),
    "ordek": dict(title="Duck", desc="Cheerful and chatty. Wobbles side to side and can't resist a pond.",
                  traits=["Chatty", "Cheerful", "Curious"],
                  lines=["Quack quack!", "Quack?", "Where's the water?", "Quaaack!"],
                  names=["Quackers", "Lemon", "Waddle", "Puddle", "Feather", "Dabble"]),
    "hamster": dict(title="Hamster", desc="Tiny and chubby. Stuffs its cheeks and scurries around in tiny steps.",
                    traits=["Tiny", "Chubby", "Busy"],
                    lines=["Seeds?", "Cheeks are full!", "Tik tik tik", "Gotta run!"],
                    names=["Peanut", "Chubby", "Corn", "Nibbles", "Seed", "Squeak"]),
    "ejderha": dict(title="Dragon", desc="Rare. When it jumps, it spreads its wings and glides down slowly.",
                    traits=["Rare", "Glider", "Noble"],
                    lines=["Rawr!", "Wings ready!", "Where's the treasure?", "Fsss..."],
                    names=["Blaze", "Spark", "Emerald", "Smoke", "Ruby", "Nyx"]),
}
COLOR_EN = {
    "Turuncu": "Orange", "Siyah": "Black", "Gri": "Gray", "Beyaz": "White", "Tekir": "Tabby",
    "Altın": "Golden", "Çikolata": "Chocolate", "Dalmaçyalı": "Dalmatian", "Husky": "Husky",
    "Kahve": "Brown", "Klasik": "Classic", "Mavi": "Blue", "Pembe": "Pink", "Yeşil": "Green",
    "Kızıl": "Red", "Kutup": "Arctic", "Gümüş": "Silver", "Civciv": "Duckling",
    "Zümrüt": "Emerald", "Ateş": "Fire", "Gece": "Night",
}

# Seviyeye göre gelişim: (başlangıç seviyesi, ad, boyut çarpanı)
EVOLUTION = [(1, "Yavru", 0.75), (5, "Yetişkin", 1.0), (10, "Efsane", 1.0)]


def evolution(level):
    """Seviyenin gelişim aşaması: (sıra, ad, boyut çarpanı)."""
    stage = 0
    for i, (lvl, _, _) in enumerate(EVOLUTION):
        if level >= lvl:
            stage = i
    return (stage,) + EVOLUTION[stage][1:]

MOOD_LINES = {
    "hungry": ["Acıktım!", "Mama?", "Karnım guruldadı..."],
    "tired": ["Uykum geldi...", "Esniyorum...", "Biraz kestireyim"],
    "sad": ["Biraz ilgi?", "Sıkıldım...", "Beni sever misin?"],
    "happy": ["Seni seviyorum!", "Çok mutluyum!", "♥ ♥ ♥"],
    "missed": ["Seni özledim!", "Neredeydin?", "Geri geldin!"],
    "thrown": ["Wiiii!", "Uçuyorum!", "Aaaa!"],
    "woke": ["Hı? Ne oldu?", "Uyuyordum...", "Günaydın!"],
    "meet": ["Selam {name}!", "{name}! Oynayalım mı?", "Merhaba {name}"],
    "grow": ["Büyüdüm!", "Bak ne kadar büyüdüm!"],
    "legend": ["Efsane oldum!", "Artık bir efsaneyim!"],
}
MOOD_LINES_EN = {
    "hungry": ["I'm hungry!", "Food?", "My tummy is rumbling..."],
    "tired": ["I'm sleepy...", "Yawn...", "Quick nap?"],
    "sad": ["A little attention?", "I'm bored...", "Do you love me?"],
    "happy": ["I love you!", "So happy!", "♥ ♥ ♥"],
    "missed": ["I missed you!", "Where were you?", "You're back!"],
    "thrown": ["Wheee!", "I'm flying!", "Aaaa!"],
    "woke": ["Huh? What?", "I was sleeping...", "Good morning!"],
    "meet": ["Hi {name}!", "{name}! Wanna play?", "Hello {name}"],
    "grow": ["I grew up!", "Look how big I got!"],
    "legend": ["I'm a legend now!", "Legendary!"],
}

# --- Aksesuarlar --------------------------------------------------------------------
# gereksinim: ("level", n) en yüksek dost seviyesi, ("ach", n) açık başarım sayısı, ("month", ay)
ACCESSORIES = {
    "silindir": dict(name="Silindir şapka", req=("level", 2), rows=[
        "..KKKK..",
        "..KHHK..",
        "..KHHK..",
        "..KNNK..",
        "KKKKKKKK",
    ]),
    "fiyonk": dict(name="Fiyonk", req=("level", 3), rows=[
        "KK...KK",
        "KNK.KNK",
        "KNNKNNK",
        "KNK.KNK",
        "KK...KK",
    ]),
    "cicek": dict(name="Çiçek", req=("level", 4), rows=[
        ".N.N.",
        "NNCNN",
        ".NNN.",
        "..G..",
    ]),
    "parti": dict(name="Parti şapkası", req=("ach", 6), rows=[
        "..C..",
        "..M..",
        ".MCM.",
        ".CMC.",
        "MCMCM",
    ]),
    "tac": dict(name="Taç", req=("level", 10), rows=[
        "C..C..C",
        "CC.C.CC",
        "CCCCCCC",
        "CRCNCRC",
    ]),
    "cadi": dict(name="Cadı şapkası", req=("month", 10), rows=[
        "...M...",
        "..MMM..",
        "..MMM..",
        ".MCCCM.",
        "MMMMMMM",
    ]),
    "noel": dict(name="Noel şapkası", req=("month", 12), rows=[
        ".....SS",
        "...RRRS",
        "..RRRR.",
        ".RRRRRR",
        "SSSSSSS",
    ]),
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
    "snow": [
        "..S..",
        "S.S.S",
        ".SSS.",
        "S.S.S",
        "..S..",
    ],
    "leaf": [
        "...AA",
        "..AAA",
        ".AAA.",
        "AAA..",
        "T....",
    ],
    "petal": [
        ".N.",
        "NNN",
        ".N.",
    ],
    "firefly": [
        ".C.",
        "CCC",
        ".C.",
    ],
    "rock": [
        ".KKKK.",
        "KQQQQK",
        "KQSQQK",
        "KQQQQK",
        ".KKKK.",
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
    "home": [
        "....X....",
        "...XXX...",
        "..XXXXX..",
        ".XXXXXXX.",
        "XXXXXXXXX",
        ".XXX.XXX.",
        ".XXX.XXX.",
    ],
    "hat": [
        "..XXXXX..",
        "..XXXXX..",
        "..XXXXX..",
        "..XXXXX..",
        "XXXXXXXXX",
    ],
    "flame": [
        "...X...",
        "..XX...",
        "..XXX..",
        ".XXXX.X",
        ".XXXXXX",
        "XXX.XXX",
        "XX...XX",
        ".XX.XX.",
    ],
    "gamepad": [
        ".XXXXXXXXX.",
        "XXX.XXXXXXX",
        "X...XXX.X.X",
        "XXX.XXXXXXX",
        "XXXXXXXXXXX",
        "XX.......XX",
    ],
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
