"""İngilizce çevirisi eksik metinleri listeler:  python tools/check_i18n.py"""
import ast
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dostlar import APP_NAME, desktop, hub, sprites, store  # noqa: E402
from dostlar.i18n import EN                                 # noqa: E402


def literal_calls():
    """Kodda _("...") ile çevrilen tüm sabit metinler."""
    found = set()
    for path in glob.glob(os.path.join(ROOT, "dostlar", "*.py")):
        tree = ast.parse(open(path, encoding="utf-8").read())
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "_"
                    and node.args and isinstance(node.args[0], ast.Constant)
                    and isinstance(node.args[0].value, str)):
                found.add(node.args[0].value)
    return found


def indirect():
    """Değişken üzerinden _() ile çevrilen metinler."""
    return {APP_NAME, *(label for _, label, _ in hub.NAV), *hub.PAGE_INFO.values(),
            *desktop.STATUS_TEXT.values(), *sprites.SPECIES["kedi"]["stats"],
            *(e[1] for e in sprites.EVOLUTION), *hub.MONTHS,
            *(a["name"] for a in sprites.ACCESSORIES.values()),
            *(a[1] for a in store.ACHIEVEMENTS), *(a[2] for a in store.ACHIEVEMENTS)}


if __name__ == "__main__":
    needed = (literal_calls() | indirect()) - {""}
    missing = sorted(needed - set(EN))
    unused = sorted(set(EN) - needed)
    for s in missing:
        print("EKSİK:", repr(s))
    for s in unused:
        print("KULLANILMIYOR:", repr(s))
    print(f"{len(needed)} metin, {len(missing)} eksik, {len(unused)} kullanılmıyor")
    sys.exit(1 if missing else 0)
