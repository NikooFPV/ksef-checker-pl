"""
Konfiguracja KSeF Checker – ustawienia i lista sprawdzeń.
Plik jest tworzony automatycznie przy pierwszym uruchomieniu.
"""
import json, os, datetime

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")

# Definicja wszystkich dostępnych sprawdzeń
ALL_CHECKS = [
    # id, domyślnie włączone, kategoria, opis
    ("pending_ksef",            True,  "Kompletność",  "Dokumenty KSeF czekające na pobranie"),
    ("missing_purchases",       True,  "Kompletność",  "Niezaksięgowane zakupy z KSeF"),
    ("missing_sales",           True,  "Kompletność",  "Niezaksięgowana sprzedaż z KSeF"),
    ("partial_booking",         True,  "Kompletność",  "Tylko w KSIEGA lub tylko w VATZAKUPY"),
    ("partial_booking_sales",   True,  "Kompletność",  "Tylko w KSIEGA lub tylko w VATSPRZEDAZ"),
    ("amounts_vs_vat",          True,  "Kwoty",        "Kwoty zakupów: KSeF vs VATZAKUPY"),
    ("amounts_vs_ksiega",       True,  "Kwoty",        "Kwoty zakupów: KSeF vs KSIEGA"),
    ("sales_amounts",           True,  "Kwoty",        "Kwoty sprzedaży: KSeF vs VATSPRZEDAZ"),
    ("sales_amounts_vs_ksiega", True,  "Kwoty",        "Kwoty sprzedaży: KSeF vs KSIEGA"),
    ("advance_invoices",        True,  "Korekty",      "Faktury zaliczkowe i rozliczeniowe (Zal/Roz)"),
    ("date_shift_purchases",    True,  "Daty",         "Zakupy w złym miesiącu (VATZAKUPY)"),
    ("date_shift_sales",        True,  "Daty",         "Sprzedaż w złym miesiącu (VATSPRZEDAZ)"),
    ("date_shift_purchases_ksiega", True, "Daty",      "Zakupy ujęte w KSIEGA poza oknem M..M+3"),
    ("no_ksef_number",          True,  "Jakość",       "Zakupy bez numeru KSeF"),
    ("no_ksef_number_sales",    True,  "Jakość",       "Sprzedaż bez numeru KSeF"),
    ("ksiega_only",             True,  "Jakość",       "Wpisy tylko w KSIEGA (ZUS, opłaty)"),
    ("ksiega_only_sales",       True,  "Jakość",       "Przychody tylko w KSIEGA (bez VATSPRZEDAZ)"),
    ("duplicates_vat",          True,  "Jakość",       "Duplikaty faktur w VATZAKUPY"),
    ("duplicates_vatsp",        True,  "Jakość",       "Duplikaty faktur w VATSPRZEDAZ"),
    ("corrections_purchases",   True,  "Korekty",      "Niezaksięgowane korekty zakupów"),
    ("corrections_sales",       True,  "Korekty",      "Niezaksięgowane korekty sprzedaży"),
    ("nip_mismatch",            True,  "Compliance",   "Błędny NIP kontrahenta (KSeF vs rejestr)"),
    ("vat_deadline",            True,  "Compliance",   "Termin odliczenia VAT przekroczony (>90 dni)"),
    ("split_payment",           True,  "Compliance",   "Split payment (MPP) – próg 15 000 zł"),
    ("foreign_currency",        True,  "Compliance",   "Faktury walutowe (nie-PLN)"),
    ("nip_name_inconsistency",  False, "Jakość",       "Ten sam NIP, różne nazwy firmy"),
]

DEFAULTS = {
    "enabled_checks": {cid: enabled for cid, enabled, _, _ in ALL_CHECKS},
    "theme": "dark",
    "left_panel_width": 430,
    "default_period": "month",  # "all" | "month"
    "cutoff_days": 3,           # ile dni od końca zakresu ignorujemy jako "za świeże"
    "amount_tolerance": 0.05,   # tolerancja różnic kwotowych w zł
    "ksef_no_threshold": 15.0,  # % zakupów bez KSeF triggering warning
}

def load() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            # merge with defaults so new keys are added automatically
            cfg = dict(DEFAULTS)
            cfg.update(saved)
            cfg["enabled_checks"] = dict(DEFAULTS["enabled_checks"])
            cfg["enabled_checks"].update(saved.get("enabled_checks", {}))
            return cfg
        except Exception:
            pass
    return dict(DEFAULTS)

def save(cfg: dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


# ── historia analiz ───────────────────────────────────────────────────────────
HISTORY_FILE   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history.json")
MAX_HISTORY    = 40     # maks. liczba wpisów
MAX_ROWS_SAVED = 300    # maks. wierszy na sprawdzenie (oszczędność miejsca)

def load_history() -> list:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_history(mdb_path: str, res: dict):
    history = load_history()
    checks_trimmed = []
    for chk in res.get("checks", []):
        c = dict(chk)
        c["rows"] = c.get("rows", [])[:MAX_ROWS_SAVED]
        checks_trimmed.append(c)
    entry = {
        "path":      mdb_path,
        "filename":  os.path.basename(mdb_path),
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "period":    res.get("period", "?"),
        "status":    res.get("status", "ok"),
        "summary":   res.get("summary", {}),
        "checks":    checks_trimmed,
    }
    # ta sama baza + ten sam okres → nadpisz zamiast duplikować
    history = [h for h in history
               if not (h["path"] == mdb_path and h["period"] == entry["period"])]
    history.insert(0, entry)
    history = history[:MAX_HISTORY]
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def delete_history_entry(idx: int):
    history = load_history()
    if 0 <= idx < len(history):
        history.pop(idx)
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception:
            pass


# ── oznaczenia wierszy ("do sprawdzenia") ─────────────────────────────────────
MARKS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "marks.json")

def load_marks() -> dict:
    if os.path.exists(MARKS_FILE):
        try:
            with open(MARKS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def get_marks(mdb_path: str, check_id: str) -> set:
    return set(load_marks().get(mdb_path or "", {}).get(check_id, []))

def toggle_mark(mdb_path: str, check_id: str, row_key: str) -> bool:
    """Przełącz oznaczenie wiersza. Zwraca True jeśli teraz zaznaczony."""
    marks = load_marks()
    bucket = marks.setdefault(mdb_path or "", {}).setdefault(check_id, [])
    if row_key in bucket:
        bucket.remove(row_key)
        marked = False
    else:
        bucket.append(row_key)
        marked = True
    try:
        with open(MARKS_FILE, "w", encoding="utf-8") as f:
            json.dump(marks, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
    return marked

def clear_marks(mdb_path: str, check_id: str):
    marks = load_marks()
    marks.get(mdb_path or "", {}).pop(check_id, None)
    try:
        with open(MARKS_FILE, "w", encoding="utf-8") as f:
            json.dump(marks, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
