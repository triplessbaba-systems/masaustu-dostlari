"""Dil desteği. Metinler Türkçe yazılır; İngilizce seçiliyse EN sözlüğünden çevrilir."""
import random

from .sprites import COLOR_EN, MOOD_LINES, MOOD_LINES_EN, SPECIES, SPECIES_EN

LANG = "tr"


def set_lang(lang):
    global LANG
    LANG = lang if lang in ("tr", "en") else "tr"


def _(text):
    return EN.get(text, text) if LANG == "en" else text


def sp_text(species, field):
    """Türün başlık, açıklama, özellik, replik ya da isim listesi."""
    if LANG == "en":
        return SPECIES_EN[species][field]
    return SPECIES[species][field]


def color_name(color):
    return COLOR_EN.get(color, color) if LANG == "en" else color


def mood(kind, **kw):
    lines = (MOOD_LINES_EN if LANG == "en" else MOOD_LINES)[kind]
    return random.choice(lines).format(**kw)


EN = {
    # genel
    "Masaüstü Dostları": "Desktop Buddies",
    "{app}'nı aç": "Open {app}",
    "Sahiplen": "Adopt", "Dostlarım": "My Buddies", "Başarımlar": "Achievements", "Ayarlar": "Settings",
    "Dil": "Language", "Dostları göster": "Show buddies", "Çıkış": "Quit", "Kapat": "Close", "Yok": "None",
    "Yeni sürüm: {tag}": "New version: {tag}", "{tag} indir": "Get {tag}",
    "Ayarlar sayfasından indirebilirsin.": "You can download it from Settings.",
    "İndirmek için uygulamayı aç.": "Open the app to download it.",
    # hızlı eylemler
    "Mama Ver": "Feed", "Top At": "Throw Ball", "Hepsini Çağır": "Call All", "Mama Yağmuru": "Snack Rain",
    "Oyunu Bitir": "End Game", "Masaüstüne balık yağdır": "Drop fish on the desktop",
    "Masaüstüne bir top bırak": "Drop a ball on the desktop", "Tüm dostlar ortada toplansın": "Gather everyone",
    "Düşen mamaları dostunla yakala": "Catch falling snacks with your buddy",
    "Mama Yağmuru'nu bitir": "End Snack Rain",
    # sahiplen
    "Tür": "Species", "Renk": "Color", "İsim": "Name", "Rastgele": "Random", "Rastgele isim": "Random name",
    "Hız": "Speed", "Oyunculuk": "Playfulness", "Uykuculuk": "Sleepiness",
    "{n} başarım": "{n} achievements", "Ejderha kilitli": "Dragon is locked",
    "{need} başarım gerekiyor, şu an {have} tane açık.": "Needs {need} achievements, you have {have}.",
    "{name} masaüstüne eklendi": "{name} joined your desktop",
    "Önce bir dost sahiplen": "Adopt a buddy first",
    # dostlarım
    "Henüz dostun yok.": "No buddies yet.", "Seviye {n}": "Level {n}", "Seviye {n}!": "Level {n}!",
    "Yavru": "Baby", "Yetişkin": "Adult", "Efsane": "Legend",
    "Besle": "Feed", "Sev": "Pet", "Uyut": "Sleep", "Uyandır": "Wake up", "Yanıma çağır": "Call over",
    "Aksesuar": "Accessory", "Aksesuar...": "Accessory...", "Aksesuar: {name}": "Accessory: {name}",
    "Kaldır": "Remove", "En iyi arkadaşı: {name} ({n} buluşma)": "Best friend: {name} ({n} meetups)",
    "Henüz bir arkadaşı yok": "No friends yet",
    "{name} masaüstünden kaldırılsın mı?\nSeviyesi ve ilerlemesi silinir.":
        "Remove {name} from the desktop?\nIts level and progress will be lost.",
    # durumlar
    "Geziyor": "Wandering", "Dinleniyor": "Resting", "Uyuyor": "Sleeping", "Mutlu": "Happy",
    "Yemek yiyor": "Eating", "Havada": "In the air", "İmleci kovalıyor": "Chasing the cursor",
    "Mamaya koşuyor": "Running for food", "Top oynuyor": "Playing ball",
    "Arkadaşını kovalıyor": "Chasing a friend", "Oyunda": "Playing a game", "aç": "hungry",
    # aksesuarlar
    "Silindir şapka": "Top hat", "Fiyonk": "Bow", "Çiçek": "Flower", "Parti şapkası": "Party hat",
    "Taç": "Crown", "Cadı şapkası": "Witch hat", "Noel şapkası": "Santa hat",
    "{month} ayında": "In {month}",
    "Ocak": "January", "Şubat": "February", "Mart": "March", "Nisan": "April", "Mayıs": "May",
    "Haziran": "June", "Temmuz": "July", "Ağustos": "August", "Eylül": "September", "Ekim": "October",
    "Kasım": "November", "Aralık": "December",
    # masaüstü menüsü
    "{name} (seviye {level} {title})": "{name} (level {level} {title})",
    "Oyunu bitir": "End game", "Top at": "Throw ball", "Beni kovala": "Chase me",
    "Mama Yağmuru oyna": "Play Snack Rain", "Dostlarımı aç...": "Open My Buddies...",
    "Mama ver": "Feed", "Hepsini çağır": "Call all",
    # mini oyun
    "Puan {score}   Süre {secs}": "Score {score}   Time {secs}", "Başla!": "Go!", "Ay!": "Ouch!",
    "Oyun bitti: {score} puan": "Game over: {score} points", "Yeni rekor!": "New record!",
    "Rekor: {best}": "Best: {best}",
    # bildirimler
    "Başarım: {title}": "Achievement: {title}", "{name} {level}. seviyeye çıktı": "{name} reached level {level}",
    "{name} artık {stage}!": "{name} is now {stage}!", "{name} acıktı": "{name} is hungry",
    "Mama vermek için tepsideki ikona sağ tıkla.": "Right-click the tray icon to feed.",
    # başarımlar sayfası
    "{done} / {total} açıldı": "{done} / {total} unlocked", "Rekor": "Best score", "Oyun süresi": "Playtime",
    "Mama": "Meals", "Sevgi": "Pets", "Tamamlandı": "Completed", "{h} sa {m} dk": "{h} h {m} min",
    "{m} dk": "{m} min",
    "İlk Dost": "First Buddy", "İlk dostunu sahiplen.": "Adopt your first buddy.",
    "Kalabalık Ev": "Full House", "Masaüstünde aynı anda 5 dost olsun.": "Have 5 buddies on the desktop at once.",
    "Koleksiyoncu": "Collector", "8 farklı türden dost sahiplen.": "Adopt buddies of 8 different species.",
    "Sevgi Dolu": "Full of Love", "Dostlarını toplam 50 kez sev.": "Pet your buddies 50 times in total.",
    "Aşçıbaşı": "Head Chef", "Dostlarını 25 kez besle.": "Feed your buddies 25 times.",
    "Uçan Dost": "Flying Buddy", "Bir dostunu tutup havaya fırlat.": "Grab a buddy and throw it in the air.",
    "Oyun Zamanı": "Playtime!", "Dostların topa 20 kez vursun.": "Have your buddies kick the ball 20 times.",
    "Yakala Beni": "Catch Me", "Dostların imlecini 10 kez yakalasın.": "Have your buddies catch the cursor 10 times.",
    "Gezgin": "Explorer", "Bir dostun bir pencerenin üstüne çıksın.": "Have a buddy climb onto a window.",
    "Can Dostlar": "Best Friends", "Dostların birbiriyle 10 kez buluşsun.": "Have your buddies meet 10 times.",
    "Usta Avcı": "Master Catcher", "Mama Yağmuru'nda 25 puan topla.": "Score 25 points in Snack Rain.",
    "Moda İkonu": "Fashion Icon", "Bir dostuna aksesuar tak.": "Put an accessory on a buddy.",
    "Usta Bakıcı": "Expert Keeper", "Bir dostunu 5. seviyeye ulaştır.": "Get a buddy to level 5.",
    "Bir dostunu 10. seviyeye ulaştır.": "Get a buddy to level 10.",
    "Ejderha Terbiyecisi": "Dragon Tamer", "Nadir ejderhayı sahiplen.": "Adopt the rare dragon.",
    "Gece Kuşu": "Night Owl", "Gece yarısından sonra dostlarınla takıl.": "Hang out with your buddies after midnight.",
    # ayarlar
    "Görünüm": "Appearance", "Davranış": "Behavior", "Sistem": "System", "Veri": "Data", "Hakkında": "About",
    "Dost boyutu": "Buddy size", "Masaüstündeki dostların ne kadar büyük görüneceği.": "How big buddies appear on the desktop.",
    "Küçük": "Small", "Orta": "Medium", "Büyük": "Large",
    "Konuşma balonları": "Speech bubbles", "Dostların ara sıra bir şeyler söylesin.": "Let buddies say things now and then.",
    "Mevsim efektleri": "Seasonal effects",
    "Kışın kar, sonbaharda yaprak, ilkbaharda çiçek yağsın.": "Snow in winter, leaves in autumn, petals in spring.",
    "Pencerelerin üstünde gez": "Walk on windows",
    "Dostlar açık pencerelerin üst kenarında yürüyebilsin.": "Buddies can walk along the top of open windows.",
    "İmleci kovala": "Chase the cursor", "Dostlar ara sıra farenin peşine düşsün.": "Buddies sometimes chase your mouse.",
    "Gece uykusu": "Night sleep", "Gece saatlerinde dostlar daha çok uyusun.": "Buddies sleep more at night.",
    "Windows ile başlat": "Start with Windows",
    "Bilgisayar açılınca dostların da uyansın.": "Wake your buddies up when the computer starts.",
    "Bildirimler": "Notifications",
    "Bir dostun acıkınca ya da başarım açılınca haber ver.": "Notify when a buddy is hungry or an achievement unlocks.",
    "Güncellemeleri denetle": "Check for updates", "Yeni sürüm çıkınca haber ver.": "Let me know when a new version is out.",
    "İlerlemeyi sıfırla": "Reset progress",
    "İstatistikleri ve başarımları sıfırlar. Dostların kalır.": "Resets stats and achievements. Your buddies stay.",
    "Sıfırla": "Reset", "Sürüm {v}, MIT lisansı": "Version {v}, MIT license",
    "Tüm istatistikler ve başarımlar sıfırlansın mı?\nDostların ve seviyeleri olduğu gibi kalır.":
        "Reset all stats and achievements?\nYour buddies and their levels stay as they are.",
    "İlerleme sıfırlandı": "Progress reset",
}
