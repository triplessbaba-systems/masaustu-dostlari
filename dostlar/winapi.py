"""Windows'a özel yardımcılar: DPI, ekran alanı, pencere platformları, otomatik başlatma."""
import ctypes
import os
import sys
from ctypes import wintypes

user32 = ctypes.windll.user32
dwmapi = ctypes.windll.dwmapi

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                ("right", ctypes.c_long), ("bottom", ctypes.c_long)]


def enable_dpi_awareness():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            user32.SetProcessDPIAware()
        except Exception:
            pass


def dpi_scale():
    try:
        return user32.GetDpiForSystem() / 96
    except Exception:
        return 1.0


def work_area():
    """Görev çubuğu hariç kullanılabilir ekran alanı (sol, üst, sağ, alt)."""
    r = RECT()
    if user32.SystemParametersInfoW(48, 0, ctypes.byref(r), 0):
        return r.left, r.top, r.right, r.bottom
    return None


class MONITORINFO(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.DWORD), ("rcMonitor", RECT), ("rcWork", RECT), ("dwFlags", wintypes.DWORD)]


_MonitorEnumProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HMONITOR, wintypes.HDC,
                                      ctypes.POINTER(RECT), wintypes.LPARAM)


def monitors():
    """Tüm ekranların kullanılabilir alanları; ana ekran ilk sırada."""
    found = []

    def cb(hmon, hdc, rect, _):
        info = MONITORINFO()
        info.cbSize = ctypes.sizeof(MONITORINFO)
        if user32.GetMonitorInfoW(hmon, ctypes.byref(info)):
            w = info.rcWork
            found.append(((w.left, w.top, w.right, w.bottom), bool(info.dwFlags & 1)))
        return True

    try:
        user32.EnumDisplayMonitors(None, None, _MonitorEnumProc(cb), 0)
    except Exception:
        return []
    found.sort(key=lambda m: not m[1])
    return [area for area, primary in found]


def click_through(tk_window):
    """Pencereyi fare tıklamalarına tamamen geçirgen yap (mevsim efektleri için)."""
    try:
        hwnd = user32.GetParent(tk_window.winfo_id()) or tk_window.winfo_id()
        style = user32.GetWindowLongW(hwnd, -20)
        user32.SetWindowLongW(hwnd, -20, style | 0x80000 | 0x20 | 0x80)   # LAYERED | TRANSPARENT | TOOLWINDOW
    except Exception:
        pass


def set_app_id(app_id):
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except Exception:
        pass


_mutex = None


def already_running(name):
    """Aynı anda iki kopya açılmasın."""
    global _mutex
    try:
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        _mutex = k32.CreateMutexW(None, False, name)
        return ctypes.get_last_error() == 183   # ERROR_ALREADY_EXISTS
    except Exception:
        return False


def dark_title_bar(tk_window, caption_hex=None):
    """Windows 10/11 başlık çubuğunu koyu yap (Win11'de rengini de ayarla)."""
    try:
        hwnd = user32.GetParent(tk_window.winfo_id())
        on = ctypes.c_int(1)
        dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(on), 4)
        if caption_hex:
            r, g, b = (int(caption_hex[i:i + 2], 16) for i in (1, 3, 5))
            color = ctypes.c_int(r | g << 8 | b << 16)
            dwmapi.DwmSetWindowAttribute(hwnd, 35, ctypes.byref(color), 4)
    except Exception:
        pass


# --- Pencerelerin üst kenarları (dostlar bunların üstünde yürür) -------------------
_EnumProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
_IGNORED_CLASSES = {"Progman", "WorkerW", "Shell_TrayWnd", "Shell_SecondaryTrayWnd"}


def _visible_windows(own_pid):
    """Z sırasına göre (üstteki önce) görünür pencerelerin dikdörtgenleri."""
    rects = []
    cls = ctypes.create_unicode_buffer(64)

    def cb(hwnd, _):
        if not user32.IsWindowVisible(hwnd) or user32.IsIconic(hwnd):
            return True
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value == own_pid:
            return True
        cloaked = ctypes.c_int(0)
        dwmapi.DwmGetWindowAttribute(hwnd, 14, ctypes.byref(cloaked), 4)
        if cloaked.value or user32.GetWindowTextLengthW(hwnd) == 0:
            return True
        if user32.GetWindowLongW(hwnd, -20) & 0x80:          # WS_EX_TOOLWINDOW
            return True
        user32.GetClassNameW(hwnd, cls, 64)
        if cls.value in _IGNORED_CLASSES:
            return True
        r = RECT()
        if dwmapi.DwmGetWindowAttribute(hwnd, 9, ctypes.byref(r), ctypes.sizeof(r)) != 0:
            user32.GetWindowRect(hwnd, ctypes.byref(r))
        rects.append((r.left, r.top, r.right, r.bottom, bool(user32.IsZoomed(hwnd))))
        return True

    user32.EnumWindows(_EnumProc(cb), 0)
    return rects


def _subtract(segments, a, b):
    out = []
    for s0, s1 in segments:
        if b <= s0 or a >= s1:
            out.append((s0, s1))
            continue
        if a > s0:
            out.append((s0, a))
        if b < s1:
            out.append((b, s1))
    return out


def window_platforms(own_pid, area, min_len=80):
    """Üzerinde yürünebilecek pencere üst kenarları: [(y, x0, x1), ...].

    Üstteki pencerelerin kapattığı kısımlar çıkarılır, böylece dostlar
    başka bir pencerenin altında kalan kenarlara çıkmaz.
    """
    try:
        rects = _visible_windows(own_pid)
    except Exception:
        return []
    l, t, r, b = area
    plats = []
    for i, (x0, y, x1, y1, zoomed) in enumerate(rects):
        if zoomed or x1 - x0 < 150 or y1 - y < 60 or y <= t + 40 or y >= b - 40:
            continue
        segs = [(max(x0, l), min(x1, r))]
        for ox0, oy0, ox1, oy1, _ in rects[:i]:
            if oy0 <= y <= oy1:
                segs = _subtract(segs, ox0, ox1)
        plats += [(y, s0, s1) for s0, s1 in segs if s1 - s0 >= min_len]
    return plats


# --- Windows ile başlat -------------------------------------------------------------
def _launch_command():
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    pyw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    return f'"{pyw}" "{os.path.abspath(sys.argv[0])}"'


def get_autostart(name):
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as k:
            winreg.QueryValueEx(k, name)
            return True
    except OSError:
        return False


def set_autostart(name, enabled):
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as k:
            if enabled:
                winreg.SetValueEx(k, name, 0, winreg.REG_SZ, _launch_command())
            else:
                try:
                    winreg.DeleteValue(k, name)
                except FileNotFoundError:
                    pass
        return True
    except OSError:
        return False
