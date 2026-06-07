import tkinter as tk
from tkinter import ttk, filedialog
import threading, os, sys, base64, io, webbrowser
import pandas as pd

VERSION     = "1.0.4"
GITHUB_REPO = "NikooFPV/ksef-checker-pl"
GITHUB_API  = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
GITHUB_URL  = f"https://github.com/{GITHUB_REPO}/releases/latest"

def _ver_tuple(v):
    try: return tuple(int(x) for x in v.lstrip("v").split("."))
    except: return (0,)

import config as cfg_module
from config import ALL_CHECKS

# ── logo (base64 PNG — brak zewnętrznych plików) ─────────────────────────────
_LOGO_48 = "R0lGODdhMAAwAIIAAP////Dw8L6+vrS0tPuSPCIiIhoaGgAAACwAAAAAMAAwAEAI/wANCBxIsKDBgwgTGizAsGGBABAjSpw4wKHFixYJYnw4saPHiBsxDtz4sWQAAihTpgxZYCRGkxFVogSQEgBNmQQyumTJkyHOlRsP9hxKdOFLmBEHKFVKtOFOixIFSJ1KlarEpk8dIoX4syvKi1kbbj2J8+ZPsAWbqg2qUODaom3fynWY9ujWpXLDMhwbYKlfrG7t8r0K1wDJiFUTTyU8VC9HiIqpesUpMvDFqJEnE7Bp9itdy1CRluXcWaVOw3N9agZ6GnRqtW1Rv64cu7bt20Jn81Soe63R3rAd82Wa17XYsX99G9+L3G9FwLJDD2bcU/h06ruXPw4QOTF2ltavQ1GEfhhyd6tkWYcMv3V1TtrluZ937/l0/PmTS6ONrlW0V86UfcbfcTDJBKBNXdknmEmjlaYeQ441Rd97Cr7mHlvaySVTdhoBV1huHu6H24gkBgQAOw=="
_LOGO_256 = "R0lGODdhAAEAAYIAAP////Dw8L6+vrS0tPuSPCIiIhoaGhISEiwAAAAAAAEAAUAI/wANCBxIsKDBgwgTKlzIsKHDhxAjSpxIsaLFixgzatzIsaPHjyA3FhhJsqTJkyhTqlzJsqXLlzBjypwZsqbBmThz6tzJs6dPnjYl/hxKtKjRo0hTBiWYtKnTp1CjKv0otWSAq1izat3KtavXr2C7Dhg7tqrZniLPjgzLtq3bt1nJyp07QK3dlhjvFoDLt69fuoAD69V7Ua/fw4jBBl7MuOzgp4XvJp5M+Wrjy5jrPh4a2W7lz6BDB9jM2aJh0ahTwyX9s7NavwJiy55Nu7bt27hz69aNmLVP12dVCx/u1Tda05KJK1duHChyz3x3S59OvbqAAASya9/Ovbv37+C73/8Fbna5eazh06tfz359U/JVo1ufT19A+/v48+s/ULri6fOf6SfggNsBYKCBBG7Hn07wSSVffRDSluCE7B1o4YUXJrigTA1GBWBiFIbYHYYkWiiighw+99qHh51IQIkmfgcjjC5+d8CGLnUIFYuIuTjjjzPWuN6NKfqXHI8tCqkdkBkqyR6RNOnYnG9OVjnhjTgWmdeUXKZk5Zc2YnmcR12WuRKYIWKZ5ZhLmemmS2oKqaaakC310Jt45qmSnTbp6edZfAYq6KCEFmrooYgmquiijGr056MrNRoopJQ+JilClWaqp6Gadqppn+UhCZpmniLF0ZGiUrZYqURtCV2qqmb/5hirURr5KqyJycoYrSxJ6RSuseoqK68j+doUsMh+xaqxSSXr7FbLqhjcs9SOViqzSD0Y4bbcXtdXtLauWK2z4FL0n1vdphvhV0JOie1R44KGJoVSvWsUbOrma9+8867J5kTnxusVvwSH56+WAKMqcFYFD8ikhjnZW1Rf+lrX8H1MxkghlDBJTNTCDCvZZIUZI+gkxzlKGyrI2IVY8oHZvWwymijjpXJ8LKMnpMwkXkyAmDF5PFTOW335o8/aAV1ruMQ+hXS/SkecVtNVPZ1m1DuBSvVdB1idNJ1Hcbq1m3OWDfZ4l9409toIpw0S22W6LffcdNdt991476333nz3/+3334AHLijcnQruEOGIlwR44ozbPHfjkC+daOSUS11o5ZhnzWfmnP9LZuegO9eRuERzRVboJ51KeulaAYZ6sRkpzDpWjYXu6uqzW5YZ50L/lPtWws7aeO8+/d568HIxTnxPxseFvOtsL89T87Q/vyvV0u9Eve7WX8Zr9jptv1y5Cd8qvmrkCyX7+aKlH1HA7Ld/7c0Oxo/+/EyvbL/8noKfk7YVC+Bt/OI+iMCPLQJMYG0OU8A7rW9/lGng4R4IwcRIsCEHRKACFeiX9uTJfzgB4AYTGDKCbQaEM6kgV7z2HUDRz0MqZCF+oIJCmdhPhiEy1Qt3BJcRQgiH7WrVDv+fQjEfUgeIX2rNEH/1OySmBwAiOljHlnis2TkRPDSCmOXMRUGwGBE3VxzRywRUs5fUMCYi/GJswligMV5Jcuoz38LCyLMTlbFXVGxWzqwExfzUUU5SRMkZYUK0nZVIPTL70h33lMds7dFlJRNjJGkWyNQ1El6FFBHP3Ai1SppkkC8pnSE32bOGLZKR+cOZKEVGSp9hLWWprB/r+Jixp70Sllx8HUvQNDJbntJxsdSlSdgISE9GKnbCdAkxr/RLM04tmS1ZJn5uiROqQBMmXZMmd+bUn7ddUybZdCI3izKpb+LkRqYcZ9jEZs6elK09ZqOmDhfVTuXRrZ7EWhw+/WT/OAzu0y79DKhAB0rQghr0oAhNqEIXytCGOvShEI2oRCdK0Ypa9KIYzahGVffPOlG0oydUKEjjJtCRftCfJv3T3lJauLqx9ILsfOn3GCXTrSmqptG7HE4JN6idJq6cPkVcm4IKuZoQlXLePGrkrKnK5gnvdZ/Tn/GSJ0yOSvV3dKmqo3CXO8Ggbqtcnd31QIfMsLLOe5273bSotzveXfJe29NV5kDpEvEFr3J0bYldkbfUt04srtYbnl8/Btju/XSwQyts90i1tryyZK+LPV1jEes7xUb2qTMNJg/ZetmsNs2xK4FsZ+eST8oWz7KjpSr+cmlWFRJwteVrrWv5AtOF/2Rwtt+CbRxli1u31FYht+3tW36bkOAKty3ExVQXj8uW5B7EuMwFi3PVJsfo+la374OudauDXQNqd7tcmW5BoAteaHXXgdUNixoDyMDzTjC9X1mvAF/bP9Myr4fyrRh9W6pZIhYxv9zqjXv9Cd/ydkW8TPmugbGC4IGQd8FXabBAHgxhCRuAwgu2MIaxAmB1tYVeXQKtStLYYQitMImsEXFKSFxi+lzlaYNRMUrw1eL6tEyGALXv9HpLTLPI+CSz1aZ2ovJjk8RQyNzxKGvXyj4kpycpRbZK/JysHmPCMbsF9kqNwUhl9hglyiRhcYu7nB8h9peJb9lybci8HyWeuf+KYpYvm8n4Gx1rr4lzJpDnsMzbcTkZZmnS3Jv1OEskl1KL1bRz+KyozaMRqJmoXPJVQdboSbY50YN2JH47XGlLX7ptfGZyW2q8zD8OCNKWzDQm01ziUnMS0VNUNVzjrEA2JjKKViYJmNfyyCve2o6g9m6WneXrV9sx1wXY9V56PUr8mLpGqNa1ov/H7BMd+onGhjaylZ1Ja2cRi78+2banHcJqJ6iW3gl3laINO1n/lWWQfLW6rcTuZJM7heYmUB3nTe9xu5uw+dY3KR3NL3kK8t427LYmB37IgtXb3v9OrMIXzvCZEczgB494ZSfu7YG7EtntlnRTAx7vbBf84RDQF7ksV8lKdH8c5CGPrahJTvEg+XKLMjcnmBpuNYxHOuc6z/OpUS5thBNO6NP0+c9VHnSkV5noiivrP52eHqUfU+odpXp3zsagZ4JU6z+zOh6t+nWni33sZB9pOKmszj1jPaVO5nqdkyrTtYtT7nM36k7t3nO85z0oROX7xf3u5s0dFUtgMptTYnp4xDOzbESenFJPEs/Kx9OF9Jx8pdym+U25tPMkzRvofRO40aMtoKaPfEJT302Jst6ZG4297GdP+9rb/va4z73ud8/73u8tIAA7"

def _logo_photoimage(b64: str):
    """Base64 GIF → tk.PhotoImage (GIF obsługiwany natywnie przez Tk)."""
    return tk.PhotoImage(data=b64)

# ── mapowanie id sprawdzenia → kategoria (do grupowania na liście wyników)
_CAT_MAP  = {cid: cat for cid, _, cat, _ in ALL_CHECKS}
_CAT_ORDER = list(dict.fromkeys(cat for _, _, cat, _ in ALL_CHECKS))

# ── colours & fonts ───────────────────────────────────────────────────────────
BG    = "#1a1a1a"; BG2 = "#222222"; BG3 = "#2a2a2a"; BG4 = "#333333"
ACCENT= "#fb923c"; A2  = "#86efac"; WARN= "#fbbf24"; ERR = "#f87171"
OK    = "#86efac"; TXT = "#f0f0f0"; TXT2= "#a0a0a0"; TXT3= "#606060"
BORDER= "#3d3d3d"
_SYS  = "Segoe UI"   # Windows system font (closest to SF Pro on Windows)
FB    = (_SYS, 11);  FS = (_SYS, 10);  FSM = (_SYS, 9)
FBIG  = (_SYS, 19, "bold"); FMED = (_SYS, 12, "bold")
BG_HOVER = "#2e2e2e"   # karta pod kursorem

MONTHS_PL = ["Styczeń","Luty","Marzec","Kwiecień","Maj","Czerwiec",
             "Lipiec","Sierpień","Wrzesień","Październik","Listopad","Grudzień"]

# ── database ──────────────────────────────────────────────────────────────────
def open_connection(mdb_path):
    try: import pyodbc
    except ImportError:
        raise RuntimeError("Brak pyodbc.\n\nUruchom:\n    python -m pip install pyodbc")
    for drv in [r"Microsoft Access Driver (*.mdb, *.accdb)",
                r"Microsoft Access Driver (*.mdb)"]:
        try:
            return pyodbc.connect(
                f"DRIVER={{{drv}}};DBQ={mdb_path};ExtendedAnsiSQL=1;",
                autocommit=True)
        except Exception: continue
    raise RuntimeError(
        "Brak sterownika Microsoft Access.\n\n"
        "Pobierz AccessDatabaseEngine_X64.exe:\n"
        "https://www.microsoft.com/en-us/download/details.aspx?id=54920")

def read_table(conn, name):
    try:
        df = pd.read_sql(f"SELECT * FROM [{name}]", conn)
        return df.astype(str).replace({"None":"","nan":"","<NA>":""})
    except Exception: return None

def list_tables(conn):
    return [t.table_name for t in conn.cursor().tables(tableType="TABLE")]

# ── analysis wrapper ──────────────────────────────────────────────────────────
def analyze_mdb(mdb_path, month=None, year=None, cfg=None, progress_cb=None):
    def prog(msg):
        if progress_cb: progress_cb(msg)
    prog("Łączę z bazą…")
    conn = open_connection(mdb_path)
    prog("Odczytuję strukturę…")
    tables = list_tables(conn)
    for req in ["_KSEF_DOCUMENT","KSIEGA","VATZAKUPY"]:
        if req not in tables:
            conn.close()
            return {"status":"error","checks":[{"kind":"error",
                "title":f"Nieobsługiwany format bazy — brak tabeli {req}.",
                "detail":"","rows":[],"explanation":""}],"summary":{},"period":"?"}
    prog("Wczytuję dane…")
    ksef   = read_table(conn, "_KSEF_DOCUMENT")
    ksiega = read_table(conn, "KSIEGA")
    vat    = read_table(conn, "VATZAKUPY")
    vatsp  = read_table(conn, "VATSPRZEDAZ") if "VATSPRZEDAZ" in tables else None
    conn.close()
    if ksef is None or ksiega is None or vat is None:
        return {"status":"error","checks":[{"kind":"error","title":"Błąd odczytu tabel.",
            "detail":"","rows":[],"explanation":""}],"summary":{},"period":"?"}
    from checks import run_all
    return run_all(ksef, ksiega, vat, vatsp, month, year,
                   cfg=cfg, prog_cb=progress_cb)

# ── settings window ───────────────────────────────────────────────────────────
class SettingsWindow(tk.Toplevel):
    def __init__(self, parent, cfg, on_save, app_ref=None):
        super().__init__(parent)
        self.title("Ustawienia — KSeF Checker")
        self.geometry("680x580")
        self.configure(bg=BG)
        self.resizable(True, True)
        self._cfg = dict(cfg)
        self._on_save = on_save
        self._app_ref = app_ref
        self._vars = {}
        self._build()
        self.lift(); self.focus_force()

    def _build(self):
        # header
        hdr = tk.Frame(self, bg=BG2, pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text="⚙  Ustawienia", font=FMED, bg=BG2, fg=ACCENT, padx=16).pack(side="left")

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=12, pady=8)

        style = ttk.Style(self)
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=BG3, foreground=TXT2,
                        font=FS, padding=[12,4])
        style.map("TNotebook.Tab", background=[("selected",BG2)],
                  foreground=[("selected",ACCENT)])

        # ── Tab 1: Sprawdzenia ────────────────────────────────────────────
        tab_checks = tk.Frame(nb, bg=BG)
        nb.add(tab_checks, text="  Sprawdzenia  ")

        tk.Label(tab_checks,
                 text="Wybierz które sprawdzenia mają być wykonywane:",
                 font=FS, bg=BG, fg=TXT2, anchor="w").pack(fill="x", padx=12, pady=(8,4))

        # scrollable list
        cv = tk.Canvas(tab_checks, bg=BG, highlightthickness=0)
        sb = ttk.Scrollbar(tab_checks, orient="vertical", command=cv.yview)
        cv.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        cv.pack(side="left", fill="both", expand=True, padx=(12,0))
        inner = tk.Frame(cv, bg=BG)
        win_id = cv.create_window((0,0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.bind("<Configure>", lambda e: cv.itemconfig(win_id, width=e.width))
        cv.bind("<MouseWheel>", lambda e: cv.yview_scroll(-1*(e.delta//120),"units"))

        enabled = self._cfg.get("enabled_checks", {})
        current_cat = [None]

        for cid, default_on, cat, label in ALL_CHECKS:
            if cat != current_cat[0]:
                current_cat[0] = cat
                cat_frame = tk.Frame(inner, bg=BG3)
                cat_frame.pack(fill="x", pady=(8,2), padx=4)
                tk.Label(cat_frame, text=f"  {cat}", font=("Consolas",9,"bold"),
                         bg=BG3, fg=ACCENT, pady=3).pack(anchor="w")

            var = tk.BooleanVar(value=enabled.get(cid, default_on))
            self._vars[cid] = var
            row = tk.Frame(inner, bg=BG2)
            row.pack(fill="x", padx=4, pady=1)
            tk.Checkbutton(row, variable=var, bg=BG2, fg=TXT,
                           activebackground=BG2, selectcolor=BG3,
                           font=FS).pack(side="left")
            tk.Label(row, text=label, font=FS, bg=BG2, fg=TXT,
                     anchor="w").pack(side="left", padx=4)

        # bulk buttons
        btn_row = tk.Frame(tab_checks, bg=BG, pady=4)
        btn_row.pack(fill="x", padx=12)
        for lbl, cmd in [
            ("Zaznacz wszystkie", lambda: [v.set(True)  for v in self._vars.values()]),
            ("Odznacz wszystkie", lambda: [v.set(False) for v in self._vars.values()]),
            ("Przywróć domyślne", self._restore_defaults),
        ]:
            tk.Button(btn_row, text=lbl, font=FSM,
                      bg=BG4, fg=TXT,
                      activebackground=BG3, activeforeground=TXT,
                      relief="flat", padx=10, pady=4).pack(side="left", padx=2)
        # re-bind commands after creation (lambda issue workaround)
        btns = btn_row.winfo_children()
        btns[0].config(command=lambda: [v.set(True)  for v in self._vars.values()])
        btns[1].config(command=lambda: [v.set(False) for v in self._vars.values()])
        btns[2].config(command=self._restore_defaults)

        # ── Tab 2: Parametry ──────────────────────────────────────────────
        tab_params = tk.Frame(nb, bg=BG)
        nb.add(tab_params, text="  Parametry  ")

        params = [
            ("amount_tolerance",  "Tolerancja różnic kwotowych (zł):",
             "Różnice mniejsze niż ta wartość są ignorowane. Domyślnie: 0.05"),
            ("ksef_no_threshold", "Próg ostrzeżenia 'brak KSeF' (%):",
             "Jeśli więcej % zakupów nie ma numeru KSeF, wyświetl ostrzeżenie. Domyślnie: 15"),
            ("cutoff_days",       "Dni bufora dla 'cały zakres' (dni):",
             "Ile ostatnich dni ignorować jako 'za świeże do zaksięgowania'. Domyślnie: 3"),
        ]
        self._param_vars = {}
        for key, label, tip in params:
            f = tk.Frame(tab_params, bg=BG)
            f.pack(fill="x", padx=16, pady=8)
            tk.Label(f, text=label, font=FS, bg=BG, fg=TXT,
                     anchor="w", width=42).pack(side="left")
            var = tk.StringVar(value=str(self._cfg.get(key,
                cfg_module.DEFAULTS.get(key,""))))
            self._param_vars[key] = var
            tk.Entry(f, textvariable=var, font=FS, bg=BG3, fg=TXT,
                     insertbackground=TXT, relief="flat", width=10).pack(side="left")
            tk.Label(f, text=f"  ← {tip}", font=FSM,
                     bg=BG, fg=TXT3, anchor="w").pack(side="left")

        # ── bottom save/cancel + aktualizacje ────────────────────────────
        bot = tk.Frame(self, bg=BG2, pady=8)
        bot.pack(fill="x", side="bottom")
        tk.Button(bot, text="  Zapisz  ", font=FMED,
                  bg=ACCENT, fg="#111111",
                  activebackground="#ea7522", activeforeground="#f0f0f0",
                  relief="flat", padx=14, pady=5,
                  command=self._save).pack(side="right", padx=12)
        tk.Button(bot, text="  Anuluj  ", font=FB,
                  bg=BG3, fg=TXT,
                  activebackground=BG4, activeforeground=TXT,
                  relief="flat", padx=12, pady=5,
                  command=self.destroy).pack(side="right", padx=4)

        # przycisk sprawdzenia aktualizacji (lewa strona)
        self._upd_btn = tk.Button(bot, text="🔔  Sprawdź aktualizacje", font=FSM,
                  bg=BG3, fg=TXT,
                  activebackground=BG4, activeforeground=TXT,
                  relief="flat", padx=12, pady=5,
                  command=self._check_updates_now)
        self._upd_btn.pack(side="left", padx=12)
        self._upd_lbl = tk.Label(bot, text="", font=FSM, bg=BG2, fg=TXT2)
        self._upd_lbl.pack(side="left")

    def _check_updates_now(self):
        self._upd_btn.config(state="disabled")
        self._upd_lbl.config(text="Sprawdzam…", fg=TXT2)
        import threading
        def worker():
            import urllib.request, json
            try:
                req = urllib.request.Request(GITHUB_API,
                                             headers={"User-Agent": "KSeF-Checker"})
                with urllib.request.urlopen(req, timeout=6) as r:
                    data = json.loads(r.read())
                tag    = data.get("tag_name", "")
                dl_url = data.get("html_url", GITHUB_URL)
                if _ver_tuple(tag) > _ver_tuple(VERSION):
                    # szukaj URL instalatora
                    inst_url = None
                    for asset in data.get("assets", []):
                        if "installer" in asset["name"].lower():
                            inst_url = asset["browser_download_url"]
                            break
                    if not inst_url:
                        inst_url = dl_url
                    def _do_update(t=tag, u=inst_url):
                        self.destroy()
                        if self._app_ref:
                            self._app_ref._start_update(t, u)
                    self.after(0, lambda: (
                        self._upd_lbl.config(
                            text=f"Dostępna wersja {tag}!", fg=WARN),
                        self._upd_btn.config(
                            text="  Aktualizuj  ", state="normal",
                            bg=ACCENT, fg="#111111",
                            command=_do_update)
                    ))
                else:
                    self.after(0, lambda: (
                        self._upd_lbl.config(
                            text=f"Masz najnowszą wersję ({VERSION}) ✓", fg=OK),
                        self._upd_btn.config(state="normal")
                    ))
                # wyzeruj datę żeby przy starcie też sprawdzało
                self._cfg["last_update_check"] = ""
                cfg_module.save(self._cfg)
            except Exception:
                self.after(0, lambda: (
                    self._upd_lbl.config(text="Brak połączenia z internetem", fg=ERR),
                    self._upd_btn.config(state="normal")
                ))
        threading.Thread(target=worker, daemon=True).start()

    def _restore_defaults(self):
        defaults = cfg_module.DEFAULTS["enabled_checks"]
        for cid, var in self._vars.items():
            var.set(defaults.get(cid, True))

    def _save(self):
        self._cfg["enabled_checks"] = {cid: var.get() for cid, var in self._vars.items()}
        for key, var in self._param_vars.items():
            try:
                self._cfg[key] = float(var.get())
            except ValueError: pass
        cfg_module.save(self._cfg)
        self._on_save(self._cfg)
        self.destroy()

# ── batch processing tab ─────────────────────────────────────────────────────
class BatchTab(tk.Frame):
    """Zakładka do sprawdzania wielu baz MDB na raz."""

    def __init__(self, parent, cfg_getter, on_open_single=None, **kw):
        super().__init__(parent, bg=BG, **kw)
        self._cfg_getter = cfg_getter
        self._on_open_single = on_open_single  # callback(path, month, year)
        self._files = []      # list of (path, month, year)
        self._running = False
        self._results = []    # list of (path, res)
        self._build()

    def _build(self):
        # top controls
        ctrl = tk.Frame(self, bg=BG2, pady=10)
        ctrl.pack(fill="x")

        tk.Button(ctrl, text="＋  Dodaj bazy MDB", font=FMED,
                  bg=ACCENT, fg="#111111",
                  activebackground="#ea7522", activeforeground="#f0f0f0",
                  relief="flat", padx=14, pady=5,
                  command=self._add_files).pack(side="left", padx=12)

        tk.Button(ctrl, text="✕  Wyczyść listę", font=FSM,
                  bg=BG3, fg=TXT, activebackground=BG4,
                  relief="flat", padx=10, pady=5,
                  command=self._clear_list).pack(side="left", padx=4)

        tk.Frame(ctrl, bg=BORDER, width=1).pack(side="left", fill="y", padx=10)

        # period for batch
        tk.Label(ctrl, text="Okres:", font=FS, bg=BG2, fg=TXT).pack(side="left")
        self._period_var = tk.StringVar(value="month")
        tk.Radiobutton(ctrl, text="Cały", variable=self._period_var, value="all",
                       font=FS, bg=BG2, fg=TXT, selectcolor=ACCENT,
                       activebackground=BG2).pack(side="left", padx=(6,0))
        tk.Radiobutton(ctrl, text="Miesiąc:", variable=self._period_var, value="month",
                       font=FS, bg=BG2, fg=TXT, selectcolor=ACCENT,
                       activebackground=BG2).pack(side="left", padx=(8,0))

        import datetime; now = datetime.datetime.now()
        self._month_var = tk.StringVar(value=MONTHS_PL[now.month-1])
        self._year_var  = tk.StringVar(value=str(now.year))
        ttk.Combobox(ctrl, textvariable=self._month_var,
                     values=MONTHS_PL, state="readonly",
                     width=10, font=FS).pack(side="left", padx=3)
        tk.Spinbox(ctrl, from_=2020, to=2035,
                   textvariable=self._year_var, width=5, font=FS,
                   bg=BG3, fg=TXT, buttonbackground=BG3,
                   relief="flat").pack(side="left", padx=3)

        tk.Frame(ctrl, bg=BORDER, width=1).pack(side="left", fill="y", padx=10)

        self._run_btn = tk.Button(ctrl, text="▶  Sprawdź wszystkie", font=FMED,
                                   bg=A2, fg="#0a1f14",
                                   activebackground="#4ade80", activeforeground="#0a1f14",
                                   relief="flat", padx=14, pady=5,
                                   state="disabled", command=self._run_all)
        self._run_btn.pack(side="left", padx=4)

        self._export_btn = tk.Button(ctrl, text="↓  Eksport zbiorczy", font=FMED,
                                      bg=BG3, fg=TXT,
                                      activebackground=BG4,
                                      relief="flat", padx=12, pady=5,
                                      state="disabled", command=self._export_batch)
        self._export_btn.pack(side="left", padx=4)

        self._status = tk.Label(ctrl, text="", font=FS, bg=BG2, fg=TXT2)
        self._status.pack(side="left", padx=10)

        style = ttk.Style()
        style.configure("B.Horizontal.TProgressbar",
                        troughcolor=BG3, background=ACCENT,
                        bordercolor=BG3, lightcolor=ACCENT, darkcolor=ACCENT)
        self._prog = ttk.Progressbar(ctrl, style="B.Horizontal.TProgressbar",
                                      mode="determinate", length=180)

        # split: left=file list, right=results
        split = tk.Frame(self, bg=BG)
        split.pack(fill="both", expand=True)

        # LEFT – file queue
        left = tk.Frame(split, bg=BG, width=340)
        left.pack(side="left", fill="y"); left.pack_propagate(False)

        tk.Label(left, text="Kolejka plików", font=FSM,
                 bg=BG, fg=TXT2, anchor="w").pack(fill="x", padx=12, pady=(8,2))

        lsb = ttk.Scrollbar(left, orient="vertical")
        lsb.pack(side="right", fill="y")
        self._file_list = tk.Listbox(left, bg=BG2, fg=TXT, font=FSM,
                                      selectbackground=BG3, selectforeground=TXT,
                                      borderwidth=0, highlightthickness=0,
                                      yscrollcommand=lsb.set, activestyle="none")
        self._file_list.pack(side="left", fill="both", expand=True, padx=(8,0))
        lsb.config(command=self._file_list.yview)

        # right-click to remove
        self._file_list.bind("<Button-3>",
            lambda e: self._remove_file(self._file_list.nearest(e.y)))
        tk.Label(left, text="Prawy klik = usuń plik", font=FSM,
                 bg=BG, fg=TXT3, anchor="w").pack(fill="x", padx=12, pady=2)

        # divider
        tk.Frame(split, bg=BORDER, width=1).pack(side="left", fill="y")

        # RIGHT – results grid
        right = tk.Frame(split, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        tk.Label(right, text="Wyniki", font=FSM,
                 bg=BG, fg=TXT2, anchor="w").pack(fill="x", padx=12, pady=(8,2))

        rsb = ttk.Scrollbar(right, orient="vertical")
        rsb.pack(side="right", fill="y")
        hsb2 = ttk.Scrollbar(right, orient="horizontal")
        hsb2.pack(side="bottom", fill="x")

        cols = ("Baza", "Status", "Błędy", "Ostrzeżenia", "KSeF", "Zakupy", "Sprzedaż", "Okres")
        self._tree = ttk.Treeview(right, columns=cols, show="headings",
                                   yscrollcommand=rsb.set,
                                   xscrollcommand=hsb2.set)
        rsb.config(command=self._tree.yview)
        hsb2.config(command=self._tree.xview)
        self._tree.pack(side="left", fill="both", expand=True, padx=(8,0))

        widths = {"Baza":260,"Status":80,"Błędy":60,"Ostrzeżenia":90,
                  "KSeF":60,"Zakupy":70,"Sprzedaż":70,"Okres":100}
        for c in cols:
            self._tree.heading(c, text=c, anchor="w")
            self._tree.column(c, width=widths.get(c,80), minwidth=40, anchor="w")

        self._tree.tag_configure("error",   foreground=ERR)
        self._tree.tag_configure("warning", foreground=WARN)
        self._tree.tag_configure("ok",      foreground=OK)
        self._tree.tag_configure("running", foreground=ACCENT)
        self._tree.tag_configure("pending", foreground=TXT2)

        self._tree.bind("<Double-Button-1>", self._on_tree_dbl)

        tk.Label(right, text="ℹ  Dwuklik na wierszu = otwórz w zakładce Pojedyncza baza",
                 font=FSM, bg=BG, fg=TXT3, anchor="w").pack(
                 side="bottom", fill="x", padx=8, pady=2)

    # ── file management ───────────────────────────────────────────────────
    def _add_files(self):
        paths = filedialog.askopenfilenames(
            title="Wybierz bazy MDB",
            filetypes=[("Access Database","*.mdb *.MDB *.accdb"),
                       ("Wszystkie pliki","*.*")])
        for p in paths:
            if p not in [f[0] for f in self._files]:
                self._files.append((p, None, None))
                self._file_list.insert("end", os.path.basename(p))
        if self._files:
            self._run_btn.config(state="normal")

    def _remove_file(self, idx):
        if idx < 0 or idx >= len(self._files): return
        self._files.pop(idx)
        self._file_list.delete(idx)
        if not self._files: self._run_btn.config(state="disabled")

    def _clear_list(self):
        self._files.clear()
        self._file_list.delete(0, "end")
        self._tree.delete(*self._tree.get_children())
        self._results.clear()
        self._run_btn.config(state="disabled")
        self._export_btn.config(state="disabled")
        self._status.config(text="")

    # ── batch run ─────────────────────────────────────────────────────────
    def _run_all(self):
        if self._running: return
        self._running = True
        self._results.clear()
        self._tree.delete(*self._tree.get_children())
        self._export_btn.config(state="disabled")
        self._run_btn.config(state="disabled")

        month, year = None, None
        if self._period_var.get() == "month":
            try:
                month = MONTHS_PL.index(self._month_var.get()) + 1
                year  = int(self._year_var.get())
            except (ValueError, IndexError): pass

        # insert pending rows
        self._iids = []
        for path, _, _ in self._files:
            iid = self._tree.insert("", "end",
                values=(os.path.basename(path), "⏳ Czeka",
                        "–","–","–","–","–",
                        f"{MONTHS_PL[month-1]} {year}" if month else "Cały"),
                tags=("pending",))
            self._iids.append(iid)

        self._prog.config(maximum=len(self._files), value=0)
        self._prog.pack(side="left", padx=6)

        def worker():
            cfg = self._cfg_getter()
            for i, (path, _, _) in enumerate(self._files):
                iid = self._iids[i]
                self.after(0, lambda iid=iid: self._tree.item(iid,
                    values=(self._tree.item(iid,"values")[0],
                            "⟳ Sprawdzam","–","–","–","–","–",
                            self._tree.item(iid,"values")[7]),
                    tags=("running",)))
                self.after(0, lambda m=f"[{i+1}/{len(self._files)}] {os.path.basename(path)[:40]}…":
                           self._status.config(text=m, fg=TXT2))
                try:
                    res = analyze_mdb(path, month=month, year=year, cfg=cfg)
                    self._results.append((path, res))
                    s   = res.get("summary",{})
                    err = sum(1 for c in res["checks"] if c["kind"]=="error")
                    wrn = sum(1 for c in res["checks"] if c["kind"]=="warning")
                    if err:      tag, st = "error",   f"✗ {err} błędów"
                    elif wrn:    tag, st = "warning",  f"⚠ {wrn} ostrzeżeń"
                    else:        tag, st = "ok",       "✓ OK"
                    self.after(0, lambda iid=iid, tag=tag, st=st, s=s:
                               self._tree.item(iid,
                                   values=(self._tree.item(iid,"values")[0],
                                           st, err, wrn,
                                           s.get("ksef_total","?"),
                                           s.get("ksef_zakup","?"),
                                           s.get("ksef_sprz","?"),
                                           self._tree.item(iid,"values")[7]),
                                   tags=(tag,)))
                except Exception as e:
                    self._results.append((path, None))
                    msg = str(e)[:40]
                    self.after(0, lambda iid=iid, msg=msg:
                               self._tree.item(iid,
                                   values=(self._tree.item(iid,"values")[0],
                                           f"✗ Błąd: {msg}","–","–","–","–","–",
                                           self._tree.item(iid,"values")[7]),
                                   tags=("error",)))
                self.after(0, lambda i=i: self._prog.config(value=i+1))

            self.after(0, self._on_done)

        threading.Thread(target=worker, daemon=True).start()

    def _on_done(self):
        self._running = False
        self._run_btn.config(state="normal")
        self._prog.pack_forget()
        ok_n  = sum(1 for _,r in self._results if r and r.get("status")=="ok")
        err_n = sum(1 for _,r in self._results if r and r.get("status")=="error")
        wrn_n = sum(1 for _,r in self._results if r and r.get("status")=="warning")
        self._status.config(
            text=f"Gotowe: {ok_n}✓  {wrn_n}⚠  {err_n}✗  z {len(self._results)} baz",
            fg=ERR if err_n else (WARN if wrn_n else OK))
        if self._results:
            self._export_btn.config(state="normal")

    def _on_tree_dbl(self, e):
        """Dwuklik na wierszu → otwórz bazę w zakładce Pojedyncza baza."""
        item = self._tree.identify_row(e.y)
        if not item: return
        vals = self._tree.item(item, "values")
        # znajdź pełną ścieżkę na podstawie nazwy pliku (kolumna 0)
        bname = vals[0] if vals else ""
        path = next((p for p, *_ in self._files if os.path.basename(p) == bname), None)
        if not path and self._results:
            path = next((p for p, _ in self._results if os.path.basename(p) == bname), None)
        if not path or not self._on_open_single: return

        month, year = None, None
        if self._period_var.get() == "month":
            try:
                month = MONTHS_PL.index(self._month_var.get()) + 1
                year  = int(self._year_var.get())
            except (ValueError, IndexError): pass

        self._on_open_single(path, month, year)

    # ── batch export ──────────────────────────────────────────────────────
    def _export_batch(self):
        path = filedialog.asksaveasfilename(
            title="Zapisz raport zbiorczy",
            defaultextension=".xlsx",
            initialfile="KSeF_Raport_Zbiorczy.xlsx",
            filetypes=[("Excel","*.xlsx"),("Wszystkie pliki","*.*")])
        if not path: return
        try:
            _export_batch_excel(self._results, path)
            self._status.config(text=f"✓ Zapisano: {os.path.basename(path)}", fg=OK)
        except Exception as ex:
            self._status.config(text=f"✗ Błąd: {ex}", fg=ERR)


def _export_batch_excel(results, save_path):
    """Zbiorczy raport Excel dla wielu baz."""
    from openpyxl import Workbook
    from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    import os, datetime

    wb = Workbook(); wb.remove(wb.active)

    def fill(h): return PatternFill("solid", fgColor=h)
    def font(h, bold=False, sz=9): return Font(name="Segoe UI", color=h, bold=bold, size=sz)
    thin = Side(style="thin", color="3d3d3d")
    brd  = Border(left=thin, right=thin, top=thin, bottom=thin)

    # ── Arkusz 1: Podsumowanie zbiorcze ──────────────────────────────────
    ws = wb.create_sheet("Podsumowanie zbiorcze")
    ws.sheet_view.showGridLines = False

    ws.cell(1,1, f"KSeF Checker — Raport zbiorczy   |   {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}")
    ws.cell(1,1).font = font("fb923c", bold=True, sz=12)
    ws.cell(1,1).fill = fill("1a1a1a")
    ws.merge_cells("A1:J1")
    ws.row_dimensions[1].height = 24

    headers = ["Baza danych","Okres","Status","Błędy","Ostrzeżenia",
               "KSeF łącznie","Zakupy","Sprzedaż","Księga","VAT zakupy"]
    for j, h in enumerate(headers, 1):
        c = ws.cell(2, j, h)
        c.font  = font("86efac", bold=True)
        c.fill  = fill("2a2a2a")
        c.border = brd

    col_w = [45,15,18,8,12,12,10,10,10,12]
    for j, w in enumerate(col_w, 1):
        ws.column_dimensions[get_column_letter(j)].width = w

    kind_colors = {"ok":"86efac","warning":"fbbf24","error":"f87171"}

    for i, (path, res) in enumerate(results):
        row = i + 3
        bg = "222222" if i%2==0 else "1a1a1a"
        if res is None:
            for j in range(1, len(headers)+1):
                ws.cell(row,j,"" if j>1 else os.path.basename(path)).fill = fill(bg)
            ws.cell(row,3,"✗ Błąd odczytu").font = font("f87171")
            continue

        s    = res.get("summary",{})
        err  = sum(1 for c in res["checks"] if c["kind"]=="error")
        wrn  = sum(1 for c in res["checks"] if c["kind"]=="warning")
        stat = res.get("status","ok")
        fc   = kind_colors.get(stat,"f0f0f0")
        st   = "✓ OK" if stat=="ok" else (f"✗ {err} błędów" if stat=="error" else f"⚠ {wrn} ostrzeżeń")

        vals = [os.path.basename(path), res.get("period","?"), st,
                err or "", wrn or "",
                s.get("ksef_total","?"), s.get("ksef_zakup","?"),
                s.get("ksef_sprz","?"),  s.get("ksiega","?"), s.get("vatzakupy","?")]
        for j, v in enumerate(vals, 1):
            c = ws.cell(row, j, v)
            c.fill   = fill(bg)
            c.border = brd
            c.font   = font(fc if j==3 else "f0f0f0", bold=(j==3))

    # ── Arkusz 2: Wszystkie błędy (zbiorczo) ─────────────────────────────
    ws2 = wb.create_sheet("Wszystkie błędy")
    ws2.sheet_view.showGridLines = False
    hdrs2 = ["Baza","Rodzaj","Sprawdzenie","Liczba","Szczegóły"]
    for j, h in enumerate(hdrs2, 1):
        c = ws2.cell(1, j, h)
        c.font = font("86efac", bold=True)
        c.fill = fill("2a2a2a")
        c.border = brd
    ws2.column_dimensions["A"].width = 38
    ws2.column_dimensions["B"].width = 12
    ws2.column_dimensions["C"].width = 52
    ws2.column_dimensions["D"].width = 10
    ws2.column_dimensions["E"].width = 60

    row = 2
    for path, res in results:
        if not res: continue
        for chk in res["checks"]:
            if chk["kind"] not in ("error","warning"): continue
            bg = "222222" if row%2==0 else "1a1a1a"
            fc = "f87171" if chk["kind"]=="error" else "fbbf24"
            vals = [os.path.basename(path), chk["kind"].upper(),
                    chk["title"], len(chk.get("rows",[])),
                    chk.get("detail","")]
            for j, v in enumerate(vals, 1):
                c = ws2.cell(row, j, v)
                c.fill = fill(bg)
                c.border = brd
                c.font = font(fc if j in (2,3) else "a0a0a0")
            row += 1

    # ── Arkusz 3: Do sprawdzenia (checklisty per firma) ───────────────────
    ws3 = wb.create_sheet("✉ Do sprawdzenia")
    ws3.sheet_view.showGridLines = False
    ws3.cell(1,1,"Firma").font  = font("86efac", bold=True); ws3.cell(1,1).fill = fill("2a2a2a")
    ws3.cell(1,2,"Problem").font = font("86efac", bold=True); ws3.cell(1,2).fill = fill("2a2a2a")
    ws3.cell(1,3,"Pilność").font = font("86efac", bold=True); ws3.cell(1,3).fill = fill("2a2a2a")
    ws3.column_dimensions["A"].width = 38
    ws3.column_dimensions["B"].width = 55
    ws3.column_dimensions["C"].width = 12

    row = 2
    for path, res in results:
        if not res: continue
        name = os.path.splitext(os.path.basename(path))[0][:35]
        for chk in res["checks"]:
            if chk["kind"] == "ok": continue
            bg = "222222" if row%2==0 else "1a1a1a"
            fc = "f87171" if chk["kind"]=="error" else "fbbf24"
            ws3.cell(row,1,name).font  = font("f0f0f0"); ws3.cell(row,1).fill = fill(bg)
            ws3.cell(row,2,chk["title"]).font = font(fc); ws3.cell(row,2).fill = fill(bg)
            ws3.cell(row,3,chk["kind"].upper()).font = font(fc,bold=True); ws3.cell(row,3).fill = fill(bg)
            row += 1

    wb.save(save_path)


# ── okno pobierania aktualizacji ─────────────────────────────────────────────
class UpdateDialog(tk.Toplevel):
    def __init__(self, parent, app_root, version, installer_url):
        super().__init__(parent)
        self.title(f"Aktualizacja do {version}")
        self.geometry("440x170")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()
        self._app_root     = app_root
        self._version      = version
        self._installer_url = installer_url
        self._cancelled    = False
        self._build()
        self.lift(); self.focus_force()
        threading.Thread(target=self._download, daemon=True).start()

    def _build(self):
        tk.Label(self, text=f"Pobieranie KSeF Checker {self._version}",
                 font=FMED, bg=BG, fg=TXT, pady=14).pack()
        style = ttk.Style(self)
        style.configure("U.Horizontal.TProgressbar",
                        troughcolor=BG3, background=ACCENT,
                        bordercolor=BG3, lightcolor=ACCENT, darkcolor=ACCENT)
        self._prog = ttk.Progressbar(self, style="U.Horizontal.TProgressbar",
                                      length=380, mode="determinate")
        self._prog.pack(padx=30)
        self._lbl = tk.Label(self, text="Łączę z serwerem…",
                             font=FSM, bg=BG, fg=TXT2)
        self._lbl.pack(pady=10)
        tk.Button(self, text="Anuluj", font=FSM,
                  bg=BG3, fg=TXT, activebackground=BG4,
                  relief="flat", padx=12, pady=4,
                  command=self._cancel).pack()

    def _download(self):
        import urllib.request, tempfile
        try:
            tmp = tempfile.NamedTemporaryFile(suffix=".exe", delete=False)
            tmp_path = tmp.name
            tmp.close()

            def on_progress(count, block, total):
                if self._cancelled:
                    raise Exception("Anulowano")
                if total > 0:
                    pct  = min(100, count * block * 100 // total)
                    done = count * block / 1048576
                    tot  = total / 1048576
                    self.after(0, lambda p=pct, d=done, t=tot: (
                        self._prog.config(value=p),
                        self._lbl.config(text=f"{d:.1f} MB / {t:.1f} MB")))

            urllib.request.urlretrieve(self._installer_url, tmp_path, on_progress)

            self.after(0, lambda: self._lbl.config(
                text="Pobrano! Za chwilę uruchomi się instalator…", fg=OK))
            self.after(1000, lambda: self._run_installer(tmp_path))

        except Exception as e:
            if not self._cancelled:
                self.after(0, lambda: self._lbl.config(
                    text=f"Błąd: {e}", fg=ERR))

    def _run_installer(self, path):
        import subprocess, tempfile
        # BAT czeka aż stara wersja całkowicie się zamknie (i wyczyści temp PyInstallera)
        # zanim odpali installer — inaczej nowy EXE nie znajdzie python DLL
        bat = os.path.join(tempfile.gettempdir(), "ksef_update.bat")
        with open(bat, "w", encoding="utf-8") as f:
            f.write(
                "@echo off\n"
                "timeout /t 4 /nobreak >nul\n"
                f'"{path}" /SILENT /NORESTART\n'
                f'del "{bat}"\n'
            )
        subprocess.Popen(
            ["cmd", "/c", "start", "/min", "", bat],
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        # zamknij aplikację — bat odpali installer za 4 sekundy
        self.after(300, self._app_root.destroy)

    def _cancel(self):
        self._cancelled = True
        self.destroy()


# ── historia analiz ───────────────────────────────────────────────────────────
class HistoryWindow(tk.Toplevel):
    def __init__(self, parent, on_load):
        super().__init__(parent)
        self.title("Historia analiz — KSeF Checker")
        self.geometry("740x560")
        self.configure(bg=BG)
        self.resizable(True, True)
        self._parent   = parent
        self._on_load  = on_load
        self._history  = cfg_module.load_history()
        self._build()
        self.lift(); self.focus_force()

    def _build(self):
        for w in self.winfo_children(): w.destroy()

        # nagłówek
        hdr = tk.Frame(self, bg=BG2, pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🕐  Historia analiz", font=FMED,
                 bg=BG2, fg=ACCENT, padx=16).pack(side="left")
        tk.Label(hdr, text=f"{len(self._history)} zapisanych wyników",
                 font=FSM, bg=BG2, fg=TXT3).pack(side="left")
        if self._history:
            tk.Button(hdr, text="Wyczyść wszystko", font=FSM,
                      bg=BG3, fg=ERR, activebackground=BG4,
                      relief="flat", padx=10, pady=4,
                      command=self._clear_all).pack(side="right", padx=12)

        if not self._history:
            tk.Label(self,
                     text="Brak historii.\n\nUruchom analizę — wyniki zostaną tu zapisane automatycznie.",
                     font=FB, bg=BG, fg=TXT3, justify="center").pack(expand=True)
            return

        # przewijalna lista wpisów
        cv = tk.Canvas(self, bg=BG, highlightthickness=0)
        sb = ttk.Scrollbar(self, orient="vertical", command=cv.yview)
        cv.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        cv.pack(fill="both", expand=True, padx=8, pady=8)
        inner = tk.Frame(cv, bg=BG)
        wid = cv.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.bind("<Configure>",    lambda e: cv.itemconfig(wid, width=e.width))
        cv.bind("<MouseWheel>",   lambda e: cv.yview_scroll(-1*(e.delta//120), "units"))

        kc = {"ok": (OK,"✓"), "warning": (WARN,"⚠"), "error": (ERR,"✗")}

        for i, entry in enumerate(self._history):
            col, icon = kc.get(entry["status"], (TXT2, "·"))
            n_err = sum(1 for c in entry.get("checks",[]) if c["kind"]=="error")
            n_wrn = sum(1 for c in entry.get("checks",[]) if c["kind"]=="warning")
            s     = entry.get("summary", {})

            card = tk.Frame(inner, bg=BG2, cursor="hand2",
                            highlightbackground=col if entry["status"]!="ok" else BORDER,
                            highlightthickness=1)
            card.pack(fill="x", pady=2)

            # lewy pasek koloru
            tk.Frame(card, bg=col if entry["status"]!="ok" else BG4,
                     width=4).pack(side="left", fill="y")

            # treść
            content = tk.Frame(card, bg=BG2)
            content.pack(side="left", fill="both", expand=True, padx=10, pady=8)

            row1 = tk.Frame(content, bg=BG2)
            row1.pack(fill="x")
            tk.Label(row1, text=icon, font=(_SYS,10,"bold"),
                     bg=BG2, fg=col, width=2).pack(side="left")
            tk.Label(row1, text=entry["filename"], font=(_SYS,10,"bold"),
                     bg=BG2, fg=TXT, anchor="w").pack(side="left", fill="x", expand=True)
            ts = entry.get("timestamp","")[:16].replace("T", "  ")
            tk.Label(row1, text=ts, font=("Consolas",8),
                     bg=BG2, fg=TXT3).pack(side="right")

            row2 = tk.Frame(content, bg=BG2)
            row2.pack(fill="x", pady=(3,0))
            tk.Label(row2, text=f"📅  {entry.get('period','?')}",
                     font=FSM, bg=BG2, fg=TXT2).pack(side="left", padx=(20,10))
            if n_err:
                tk.Label(row2, text=f" ✗ {n_err} ", font=("Consolas",8,"bold"),
                         bg=ERR, fg="#111111").pack(side="left", padx=2)
            if n_wrn:
                tk.Label(row2, text=f" ⚠ {n_wrn} ", font=("Consolas",8,"bold"),
                         bg=WARN, fg="#111111").pack(side="left", padx=2)
            if not n_err and not n_wrn:
                tk.Label(row2, text="Wszystko OK", font=FSM,
                         bg=BG2, fg=OK).pack(side="left", padx=2)
            # statystyki KSeF
            ksef_total = s.get("ksef_total","?")
            tk.Label(row2, text=f"KSeF: {ksef_total}",
                     font=FSM, bg=BG2, fg=TXT3).pack(side="right", padx=8)

            # przyciski
            btn_col = tk.Frame(card, bg=BG2)
            btn_col.pack(side="right", padx=8, pady=8)
            tk.Button(btn_col, text="  Otwórz  ", font=FSM,
                      bg=ACCENT, fg="#111111",
                      activebackground="#ea7522", activeforeground="#f0f0f0",
                      relief="flat", padx=8, pady=4,
                      command=lambda e=entry: self._load(e)).pack(fill="x", pady=(0,4))
            tk.Button(btn_col, text="  Usuń  ", font=FSM,
                      bg=BG3, fg=TXT2,
                      activebackground=BG4, activeforeground=ERR,
                      relief="flat", padx=8, pady=4,
                      command=lambda idx=i: self._delete(idx)).pack(fill="x")

            # dwuklik na karcie też otwiera
            for w in card.winfo_children() + content.winfo_children() + \
                     row1.winfo_children() + row2.winfo_children():
                w.bind("<Double-Button-1>", lambda e, en=entry: self._load(en))
            card.bind("<Double-Button-1>", lambda e, en=entry: self._load(en))

        tk.Label(self, text="ℹ  Dwuklik lub przycisk Otwórz = wczytaj wyniki bez ponownej analizy",
                 font=FSM, bg=BG, fg=TXT3, anchor="w").pack(
                 fill="x", padx=12, pady=4)

    def _load(self, entry):
        self.destroy()
        self._on_load(entry)

    def _delete(self, idx):
        cfg_module.delete_history_entry(idx)
        self._history = cfg_module.load_history()
        self._build()

    def _clear_all(self):
        import os
        try: os.remove(cfg_module.HISTORY_FILE)
        except Exception: pass
        self._history = []
        self._build()


# ── main app ──────────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("KSeF Checker")
        self.geometry("1320x800")
        self.minsize(1000, 620)
        self.configure(bg=BG)
        self._cfg = cfg_module.load()
        self._checks = []
        self._selected = None
        self._last_res = None
        self._mdb_path = None
        # ikona okna
        try:
            self._logo_img256 = _logo_photoimage(_LOGO_256)
            self.iconphoto(True, self._logo_img256)
        except Exception:
            pass
        self._build()
        # sprawdź aktualizacje w tle (max raz dziennie)
        threading.Thread(target=self._check_updates, daemon=True).start()

    # ── aktualizacje ──────────────────────────────────────────────────────
    def _check_updates(self):
        import urllib.request, json, datetime
        today = datetime.date.today().isoformat()
        if self._cfg.get("last_update_check") == today:
            return
        try:
            req = urllib.request.Request(GITHUB_API,
                                         headers={"User-Agent": "KSeF-Checker"})
            with urllib.request.urlopen(req, timeout=5) as r:
                data = json.loads(r.read())
            tag   = data.get("tag_name", "")
            notes = data.get("body", "")[:300]
            # szukaj URL instalatora w assets
            installer_url = None
            for asset in data.get("assets", []):
                if "installer" in asset["name"].lower():
                    installer_url = asset["browser_download_url"]
                    break
            if not installer_url:
                installer_url = data.get("html_url", GITHUB_URL)
            if _ver_tuple(tag) > _ver_tuple(VERSION):
                self.after(0, lambda: self._show_update_banner(
                    tag, notes, installer_url))
            self._cfg["last_update_check"] = today
            cfg_module.save(self._cfg)
        except Exception:
            pass

    def _show_update_banner(self, tag, notes, installer_url):
        banner = tk.Frame(self, bg="#2b1a00", pady=0)
        banner.pack(fill="x", before=self._nb)
        left = tk.Frame(banner, bg="#2b1a00")
        left.pack(side="left", fill="x", expand=True, padx=12, pady=6)
        tk.Label(left, text=f"🔔  Dostępna nowa wersja  {tag}",
                 font=FMED, bg="#2b1a00", fg=WARN).pack(side="left")
        if notes:
            short = notes.split("\n")[0][:80]
            tk.Label(left, text=f"  —  {short}",
                     font=FSM, bg="#2b1a00", fg=TXT2).pack(side="left", padx=6)
        tk.Button(banner, text="  Aktualizuj  ", font=FSM,
                  bg=ACCENT, fg="#111111",
                  activebackground="#ea7522", activeforeground="#111111",
                  relief="flat", padx=10, pady=4,
                  command=lambda: self._start_update(tag, installer_url, banner)).pack(
                  side="right", padx=4, pady=6)
        tk.Button(banner, text="✕", font=FSM,
                  bg="#2b1a00", fg=TXT3,
                  activebackground="#3a2500", activeforeground=TXT,
                  relief="flat", padx=8, pady=4,
                  command=banner.destroy).pack(
                  side="right", padx=(0,4), pady=6)

    def _start_update(self, tag, installer_url, banner=None):
        if banner:
            banner.destroy()
        UpdateDialog(self, self, tag, installer_url)

    # ── layout ────────────────────────────────────────────────────────────
    def _build(self):
        # header
        hdr = tk.Frame(self, bg=BG2, height=60)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        try:
            self._logo_img48 = _logo_photoimage(_LOGO_48)
            tk.Label(hdr, image=self._logo_img48,
                     bg=BG2).pack(side="left", padx=(16,8), pady=6)
        except Exception:
            pass
        name_col = tk.Frame(hdr, bg=BG2)
        name_col.pack(side="left", pady=6)
        tk.Label(name_col, text="KSeF Checker", font=FBIG,
                 bg=BG2, fg=TXT).pack(anchor="w")
        tk.Label(name_col, text="weryfikator spójności bazy MDB",
                 font=(_SYS, 8), bg=BG2, fg=TXT3).pack(anchor="w")
        tk.Button(hdr, text="⚙  Ustawienia", font=FSM, bg=BG3, fg=TXT,
                  activebackground=BG4, activeforeground=TXT,
                  relief="flat", padx=12, pady=5,
                  command=self._open_settings).pack(side="right", padx=4, pady=8)
        tk.Button(hdr, text="🕐  Historia", font=FSM, bg=BG3, fg=TXT,
                  activebackground=BG4, activeforeground=TXT,
                  relief="flat", padx=12, pady=5,
                  command=self._open_history).pack(side="right", padx=4, pady=8)

        # notebook: single vs batch
        nb_style = ttk.Style(self); nb_style.theme_use("clam")
        nb_style.configure("App.TNotebook", background=BG2,
                           borderwidth=0, tabmargins=[0,0,0,0])
        nb_style.configure("App.TNotebook.Tab",
                           background=BG3, foreground=TXT2,
                           font=(_SYS, 9), padding=[16, 6],
                           borderwidth=0)
        nb_style.map("App.TNotebook.Tab",
                     background=[("selected", BG)],
                     foreground=[("selected", ACCENT)])
        nb = ttk.Notebook(self, style="App.TNotebook")
        nb.pack(fill="both", expand=True)

        # Tab 1: single file
        self._single_tab = tk.Frame(nb, bg=BG)
        nb.add(self._single_tab, text="  Pojedyncza baza  ")

        # Tab 2: batch
        self._nb = nb
        self._batch_tab = BatchTab(nb, cfg_getter=lambda: self._cfg,
                                   on_open_single=self._open_in_single)
        nb.add(self._batch_tab, text="  Wiele baz (batch)  ")

        # ── build single tab ──────────────────────────────────────────────
        parent = self._single_tab

        # toolbar
        tb = tk.Frame(parent, bg=BG3, pady=8)
        tb.pack(fill="x")

        self.file_lbl = tk.Label(tb, text="📂  Kliknij aby wybrać plik…", font=FS,
                                  bg=BG3, fg=TXT2, cursor="hand2")
        self.file_lbl.pack(side="left", padx=12)
        self.file_lbl.bind("<Button-1>", lambda e: self._pick_file())
        self.file_lbl.bind("<Enter>",
            lambda e: self.file_lbl.config(fg=ACCENT))
        self.file_lbl.bind("<Leave>",
            lambda e: self.file_lbl.config(
                fg=A2 if self._mdb_path else TXT2))
        tk.Frame(tb, bg=BORDER, width=1).pack(side="left", fill="y", padx=8)

        tk.Label(tb, text="Okres:", font=FS, bg=BG3, fg=TXT).pack(side="left", padx=(0,6))
        self.period_var = tk.StringVar(value=self._cfg.get("default_period","month"))
        # toggle-przyciski zamiast słabo widocznych radio-buttonów
        self._btn_all = tk.Button(tb, text="Cały", font=FS,
                                  relief="flat", padx=12, pady=4, cursor="hand2",
                                  command=lambda: (self.period_var.set("all"),
                                                   self._toggle_period()))
        self._btn_all.pack(side="left", padx=(0,1))
        self._btn_month = tk.Button(tb, text="Miesiąc", font=FS,
                                    relief="flat", padx=12, pady=4, cursor="hand2",
                                    command=lambda: (self.period_var.set("month"),
                                                     self._toggle_period()))
        self._btn_month.pack(side="left", padx=(0,6))

        import datetime; now = datetime.datetime.now()
        self.month_var = tk.StringVar(value=MONTHS_PL[now.month-1])
        self.year_var  = tk.StringVar(value=str(now.year))
        style = ttk.Style()
        style.configure("TB.TCombobox", fieldbackground=BG2, background=BG2,
                        foreground=TXT, selectbackground=BG3)
        self.month_cb = ttk.Combobox(tb, textvariable=self.month_var,
                                      values=MONTHS_PL, state="disabled",
                                      width=10, font=FS)
        self.month_cb.pack(side="left", padx=3)
        self.year_sp = tk.Spinbox(tb, from_=2020, to=2035,
                                   textvariable=self.year_var, width=5, font=FS,
                                   bg=BG2, fg=TXT,
                                   buttonbackground=BG3, insertbackground=TXT,
                                   relief="flat", state="disabled")
        self.year_sp.pack(side="left", padx=3)

        tk.Frame(tb, bg=BORDER, width=1).pack(side="left", fill="y", padx=8)

        self.btn = tk.Button(tb, text="▶  Sprawdź", font=FMED,
                              bg=ACCENT, fg="#111111",
                              activebackground="#ea7522", activeforeground="#f0f0f0",
                              relief="flat", padx=16, pady=5,
                              state="disabled", command=self._run)
        self.btn.pack(side="left", padx=4)

        self.export_btn = tk.Button(tb, text="↓  Excel", font=FMED,
                                     bg=A2, fg="#0a1f14",
                                     activebackground="#4ade80", activeforeground="#0a1f14",
                                     relief="flat", padx=12, pady=5,
                                     state="disabled", command=self._export)
        self.export_btn.pack(side="left", padx=4)

        self.status_lbl = tk.Label(tb, text="", font=FS, bg=BG3, fg=TXT)
        self.status_lbl.pack(side="left", padx=10)

        style = ttk.Style(self); style.theme_use("clam")
        style.configure("P.Horizontal.TProgressbar",
                        troughcolor=BG2, background=ACCENT,
                        bordercolor=BG2, lightcolor=ACCENT, darkcolor=ACCENT)
        style.configure("Treeview",
            background=BG2, foreground=TXT, fieldbackground=BG2,
            bordercolor=BORDER, borderwidth=0, rowheight=26,
            font=(_SYS, 9))
        style.configure("Treeview.Heading",
            background=BG3, foreground=TXT2, relief="flat",
            font=(_SYS, 9, "bold"), padding=[6, 5])
        style.map("Treeview",
            background=[("selected", BG4)],
            foreground=[("selected", ACCENT)])
        self.progress = ttk.Progressbar(tb, style="P.Horizontal.TProgressbar",
                                         mode="indeterminate", length=160)
        self._toggle_period()
        # results area for single tab

        # main split
        main = tk.Frame(parent, bg=BG)
        main.pack(fill="both", expand=True)

        # LEFT scrollable
        left_w = self._cfg.get("left_panel_width", 430)
        left = tk.Frame(main, bg=BG, width=left_w)
        left.pack(side="left", fill="y"); left.pack_propagate(False)

        left_sb = ttk.Scrollbar(left, orient="vertical")
        left_sb.pack(side="right", fill="y")
        self._left_cv = tk.Canvas(left, bg=BG, highlightthickness=0,
                                   yscrollcommand=left_sb.set)
        self._left_cv.pack(side="left", fill="both", expand=True)
        left_sb.config(command=self._left_cv.yview)

        self.list_frame = tk.Frame(self._left_cv, bg=BG)
        self._lcv_id = self._left_cv.create_window(
            (0,0), window=self.list_frame, anchor="nw")
        self.list_frame.bind("<Configure>",
            lambda e: self._left_cv.configure(scrollregion=self._left_cv.bbox("all")))
        self._left_cv.bind("<Configure>",
            lambda e: self._left_cv.itemconfig(self._lcv_id, width=e.width))
        self._left_cv.bind("<MouseWheel>",
            lambda e: self._left_cv.yview_scroll(-1*(e.delta//120),"units"))

        # divider
        tk.Frame(main, bg=BORDER, width=1).pack(side="left", fill="y")

        # RIGHT
        right = tk.Frame(main, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        self.detail_hdr = tk.Frame(right, bg=BG2, height=52)
        self.detail_hdr.pack(fill="x"); self.detail_hdr.pack_propagate(False)
        self.detail_title = tk.Label(self.detail_hdr,
            text="← Kliknij sprawdzenie aby zobaczyć szczegóły",
            font=FMED, bg=BG2, fg=TXT2, padx=16)
        self.detail_title.pack(side="left", pady=12)

        self.tree_frame = tk.Frame(right, bg=BG)
        self.tree_frame.pack(fill="both", expand=True, padx=8, pady=(0,8))

    def _open_in_single(self, path, month, year):
        """Otwórz bazę z batcha w zakładce Pojedyncza baza i uruchom analizę."""
        # przełącz zakładkę
        self._nb.select(self._single_tab)
        # ustaw plik
        self._mdb_path = path
        name = os.path.basename(path)
        short = name if len(name) <= 44 else name[:42] + "…"
        self.file_lbl.config(text=f"📂  {short}", fg=A2)
        self.btn.config(state="normal")
        self._clear_all()
        # ustaw okres
        if month and year:
            self.period_var.set("month")
            self.month_var.set(MONTHS_PL[month - 1])
            self.year_var.set(str(year))
        else:
            self.period_var.set("all")
        self._toggle_period()
        # odpal analizę
        self._run()

    def _toggle_period(self):
        is_month = self.period_var.get() == "month"
        self.month_cb.config(state="readonly" if is_month else "disabled")
        self.year_sp.config(state="normal"    if is_month else "disabled")
        # wygląd przycisków — aktywny = wypełniony kolorem akcentu
        self._btn_all.config(
            bg=BG4    if is_month else ACCENT,
            fg=TXT2   if is_month else "#111111",
            activebackground=BG3      if is_month else "#ea7522",
            activeforeground=TXT      if is_month else "#111111")
        self._btn_month.config(
            bg=ACCENT if is_month else BG4,
            fg="#111111" if is_month else TXT2,
            activebackground="#ea7522" if is_month else BG3,
            activeforeground="#111111" if is_month else TXT)

    def _open_settings(self):
        SettingsWindow(self, self._cfg, self._on_settings_saved, app_ref=self)

    def _on_settings_saved(self, new_cfg):
        self._cfg = new_cfg

    def _open_history(self):
        HistoryWindow(self, self._load_from_history)

    def _load_from_history(self, entry):
        """Wczytaj wyniki z historii bez ponownej analizy."""
        self._nb.select(self._single_tab)
        self._mdb_path = entry["path"]
        name  = entry["filename"]
        short = name if len(name) <= 44 else name[:42] + "…"
        self.file_lbl.config(text=f"🕐  {short}  (historia)", fg=TXT2)
        self.btn.config(state="normal")
        self._clear_all()

        # ustaw selektor okresu na podstawie zapisanego wpisu
        period = entry.get("period", "")
        month, year = None, None
        for mi, mname in enumerate(MONTHS_PL, 1):
            if mname in period:
                month = mi
                try: year = int(period.strip().split()[-1])
                except Exception: pass
                break

        if month and year:
            self.period_var.set("month")
            self.month_var.set(MONTHS_PL[month - 1])
            self.year_var.set(str(year))
        else:
            self.period_var.set("all")
        self._toggle_period()

        self._show_results(entry)

    def _pick_file(self):
        path = filedialog.askopenfilename(
            title="Wybierz plik MDB",
            filetypes=[("Access Database","*.mdb *.MDB *.accdb"),("Wszystkie pliki","*.*")])
        if not path: return
        self._mdb_path = path
        name = os.path.basename(path)
        short = name if len(name)<=44 else name[:42]+"…"
        self.file_lbl.config(text=f"📂  {short}", fg=A2)
        self.btn.config(state="normal")
        self._clear_all()

    def _run(self):
        self.btn.config(state="disabled")
        self.export_btn.config(state="disabled")
        self._clear_all()
        self.progress.pack(side="left", padx=6)
        self.progress.start(12)
        self.status_lbl.config(text="Analizuję…", fg=TXT2)

        month, year = None, None
        if self.period_var.get() == "month":
            try:
                month = MONTHS_PL.index(self.month_var.get()) + 1
                year  = int(self.year_var.get())
            except (ValueError, IndexError): pass

        cfg = dict(self._cfg)

        def worker():
            try:
                res = analyze_mdb(self._mdb_path, month=month, year=year,
                                   cfg=cfg, progress_cb=lambda m: self._set_status(m))
                self.after(0, lambda: self._show_results(res))
            except Exception as ex:
                msg = str(ex)
                self.after(0, lambda: self._show_error(msg))

        threading.Thread(target=worker, daemon=True).start()

    def _set_status(self, msg):
        self.after(0, lambda: self.status_lbl.config(text=msg))

    def _clear_all(self):
        for w in self.list_frame.winfo_children(): w.destroy()
        self._clear_detail()
        self._checks = []; self._selected = None; self._last_res = None

    def _clear_detail(self):
        for w in self.tree_frame.winfo_children(): w.destroy()
        self.detail_title.config(
            text="← Kliknij sprawdzenie aby zobaczyć szczegóły", fg=TXT3)

    def _show_error(self, msg):
        self.progress.stop(); self.progress.pack_forget()
        self.btn.config(state="normal")
        self.status_lbl.config(text="Błąd!", fg=ERR)
        tk.Label(self.list_frame, text=f"✗  {msg}", font=FB, bg=BG, fg=ERR,
                 wraplength=380, justify="left").pack(anchor="w", pady=10)

    # ── results ───────────────────────────────────────────────────────────
    def _show_results(self, res):
        self.progress.stop(); self.progress.pack_forget()
        self.btn.config(state="normal")
        self._last_res = res
        self.export_btn.config(state="normal")
        # zapisz do historii (tylko gdy pochodzi z prawdziwej analizy, nie z historii)
        if self._mdb_path and res.get("status"):
            cfg_module.save_history(self._mdb_path, res)

        s_map = {
            "ok":      ("✓ Spójna",  OK,   "#0d2b1a"),
            "warning": ("⚠ Ostrzeżenia", WARN, "#2b1e06"),
            "error":   ("✗ Błędy",   ERR,  "#2b0d0d"),
        }
        stxt, scol, sbg = s_map.get(res["status"], ("?", TXT2, BG3))
        period = res.get("period","")
        self.status_lbl.config(
            text=f"  {stxt}  {'·' if period else ''}  {period}  " if period else f"  {stxt}  ",
            fg=scol, bg=sbg, padx=2, pady=1)

        # summary strip
        s = res.get("summary",{})
        if s:
            sb = tk.Frame(self.list_frame, bg=BG2, pady=4)
            sb.pack(fill="x", pady=(0,10), padx=2)
            metrics = [
                ("KSeF",     s.get("ksef_total","?"), ACCENT),
                ("Zakupy",   s.get("ksef_zakup","?"),  A2),
                ("Sprzedaż", s.get("ksef_sprz","?"),   TXT),
                ("Księga",   s.get("ksiega","?"),       TXT),
                ("VAT zak.", s.get("vatzakupy","?"),    TXT),
            ]
            for lbl, val, chip_fg in metrics:
                chip = tk.Frame(sb, bg=BG4)
                chip.pack(side="left", padx=(0,6), pady=4)
                tk.Label(chip, text=str(val), font=("Consolas",13,"bold"),
                         bg=BG4, fg=chip_fg, padx=12, pady=2).pack()
                tk.Label(chip, text=lbl, font=(_SYS,8),
                         bg=BG4, fg=TXT3, padx=12, pady=3).pack()

        # check cards — grouped by category
        self._checks = res.get("checks",[])
        kc = {"ok":(OK,"✓"),"warning":(WARN,"⚠"),"error":(ERR,"✗")}
        _kind_cbg = {"ok": BG2, "warning": "#251d08", "error": "#231010"}

        # group checks by category, preserving original index for _select
        from collections import OrderedDict
        grouped: OrderedDict = OrderedDict()
        for i, chk in enumerate(self._checks):
            cat = _CAT_MAP.get(chk.get("id",""), "Inne")
            grouped.setdefault(cat, []).append((i, chk))

        def _cat_rank(c): return _CAT_ORDER.index(c) if c in _CAT_ORDER else 999
        sorted_groups = sorted(grouped.items(), key=lambda x: _cat_rank(x[0]))

        for cat_name, items in sorted_groups:
            n_err  = sum(1 for _, c in items if c["kind"]=="error")
            n_warn = sum(1 for _, c in items if c["kind"]=="warning")
            cat_col = ERR if n_err else (WARN if n_warn else TXT3)

            # ── category header ───────────────────────────────────────────
            cat_hdr = tk.Frame(self.list_frame, bg=BG)
            cat_hdr.pack(fill="x", padx=2, pady=(10,1))
            tk.Frame(cat_hdr, bg=cat_col, height=1).pack(fill="x")
            row_hdr = tk.Frame(cat_hdr, bg=BG)
            row_hdr.pack(fill="x", pady=(3,0))
            tk.Label(row_hdr, text=cat_name.upper(),
                     font=("Consolas",8,"bold"), bg=BG, fg=cat_col).pack(side="left", padx=4)
            if n_err or n_warn:
                badge_txt = "  ".join(
                    ([f"✗ {n_err}"] if n_err else []) +
                    ([f"⚠ {n_warn}"] if n_warn else []))
                tk.Label(row_hdr, text=badge_txt,
                         font=("Consolas",8), bg=BG, fg=cat_col).pack(side="right", padx=4)

            # ── cards in this category ────────────────────────────────────
            for i, chk in items:
                col, icon = kc.get(chk["kind"],(TXT2,"·"))
                n = len(chk.get("rows",[]))
                card_bg = _kind_cbg.get(chk["kind"], BG2)

                card = tk.Frame(self.list_frame, bg=BG,
                                highlightbackground=col if chk["kind"]!="ok" else BORDER,
                                highlightthickness=1, cursor="hand2")
                card.pack(fill="x", pady=2, padx=2)

                # left accent strip
                strip = tk.Frame(card, bg=col if chk["kind"]!="ok" else BG4, width=4)
                strip.pack(side="left", fill="y")
                setattr(self, f"_strip_{i}", strip)

                # content area
                inner = tk.Frame(card, bg=card_bg)
                inner.pack(side="left", fill="both", expand=True, padx=(10,10), pady=8)

                top = tk.Frame(inner, bg=card_bg)
                top.pack(fill="x")

                lbl_icon = tk.Label(top, text=icon, font=(_SYS,10,"bold"),
                                    bg=card_bg, fg=col, width=2)
                lbl_icon.pack(side="left")
                lbl_title = tk.Label(top, text=chk["title"], font=(_SYS,10,"bold"),
                                     bg=card_bg, fg=TXT if chk["kind"]=="ok" else col,
                                     anchor="w")
                lbl_title.pack(side="left", fill="x", expand=True)

                if n:
                    badge_bg = col if chk["kind"]!="ok" else BG4
                    badge_fg = "#1a1520" if chk["kind"]!="ok" else TXT3
                    tk.Label(top, text=f" {n} ", font=("Consolas",9,"bold"),
                             bg=badge_bg, fg=badge_fg).pack(side="right", padx=(4,0))

                if chk.get("detail"):
                    tk.Label(inner, text=chk["detail"], font=(_SYS,9),
                             bg=card_bg, fg=TXT2, anchor="w").pack(fill="x", pady=(3,0))

                # hover — check bounds to avoid flicker between child widgets
                def _hover_on(e, _in=inner, _tp=top, _bg=BG_HOVER):
                    _in.config(bg=_bg); _tp.config(bg=_bg)
                    for w in list(_tp.winfo_children()) + list(_in.winfo_children()):
                        try: w.config(bg=_bg)
                        except: pass

                def _hover_off(e, _in=inner, _tp=top, _bg=card_bg, _c=card):
                    rx = e.widget.winfo_rootx() + e.x - _c.winfo_rootx()
                    ry = e.widget.winfo_rooty() + e.y - _c.winfo_rooty()
                    if not (0 <= rx < _c.winfo_width() and 0 <= ry < _c.winfo_height()):
                        _in.config(bg=_bg); _tp.config(bg=_bg)
                        for w in list(_tp.winfo_children()) + list(_in.winfo_children()):
                            try: w.config(bg=_bg)
                            except: pass

                def on_click(e, idx=i): self._select(idx)

                for w in [card, strip, inner, top] + \
                          list(top.winfo_children()) + list(inner.winfo_children()):
                    w.bind("<Button-1>", on_click)
                    w.bind("<Enter>", _hover_on)
                    w.bind("<Leave>", _hover_off)

                setattr(self, f"_card_{i}", card)

        # auto-select first non-ok check
        first_bad = next((i for i,c in enumerate(self._checks) if c["kind"]!="ok"), None)
        if first_bad is not None:
            self.after(100, lambda: self._select(first_bad))

    def _select(self, idx):
        kc = {"ok":OK,"warning":WARN,"error":ERR}
        if self._selected is not None:
            prev = getattr(self, f"_card_{self._selected}", None)
            prev_strip = getattr(self, f"_strip_{self._selected}", None)
            if prev:
                kind = self._checks[self._selected]["kind"]
                prev.config(highlightbackground=kc.get(kind,TXT2) if kind!="ok" else BORDER,
                            highlightthickness=1)
            if prev_strip:
                kind = self._checks[self._selected]["kind"]
                prev_strip.config(bg=kc.get(kind, BG4) if kind!="ok" else BG4)
        self._selected = idx
        card = getattr(self, f"_card_{idx}", None)
        strip = getattr(self, f"_strip_{idx}", None)
        if card: card.config(highlightbackground=ACCENT, highlightthickness=2)
        if strip: strip.config(bg=ACCENT)
        self._show_detail(self._checks[idx])

    def _show_detail(self, chk):
        self._clear_detail()
        kc = {"ok":OK,"warning":WARN,"error":ERR}
        col  = kc.get(chk["kind"], TXT2)
        icon = {"ok":"✓","warning":"⚠","error":"✗"}.get(chk["kind"],"·")
        self.detail_title.config(text=f"{icon}  {chk['title']}", fg=col)

        if chk.get("explanation"):
            exp_box = tk.Frame(self.tree_frame, bg=BG3)
            exp_box.pack(fill="x", padx=8, pady=(4,4))
            tk.Frame(exp_box, bg=ACCENT, width=3).pack(side="left", fill="y")
            tk.Label(exp_box, text=f"  ℹ  {chk['explanation']}",
                     font=(_SYS,9), bg=BG3, fg=TXT2,
                     anchor="w", justify="left", wraplength=760,
                     padx=8, pady=7).pack(side="left", fill="x", expand=True)

        rows = chk.get("rows",[])
        if not rows:
            tk.Label(self.tree_frame,
                     text="✓  Brak nieprawidłowości w tej kategorii.",
                     font=FB, bg=BG, fg=OK).pack(anchor="w", pady=20, padx=12)
            return

        count_row = tk.Frame(self.tree_frame, bg=BG2)
        count_row.pack(fill="x", padx=8, pady=(4,4))
        tk.Label(count_row, text="Znaleziono:", font=(_SYS,9), bg=BG2, fg=TXT3).pack(side="left")
        tk.Label(count_row, text=f" {len(rows)} ", font=("Consolas",9,"bold"),
                 bg=WARN if chk["kind"]=="warning" else (ERR if chk["kind"]=="error" else OK),
                 fg="#111111").pack(side="left", padx=4)
        tk.Label(count_row, text="wierszy", font=(_SYS,9), bg=BG2, fg=TXT3).pack(side="left")

        cols = list(rows[0].keys())
        vsb = ttk.Scrollbar(self.tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(self.tree_frame, orient="horizontal")
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        tree = ttk.Treeview(self.tree_frame, columns=cols, show="headings",
                             yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)
        tree.pack(side="left", fill="both", expand=True)

        for c in cols:
            w = max(len(str(c)), max((len(str(r.get(c,"")or"")) for r in rows[:100]),default=0))
            px = min(w*8+20, 320)
            tree.heading(c, text=c, anchor="w")
            tree.column(c, width=px, minwidth=50, anchor="w", stretch=False)

        for row in rows:
            tree.insert("", "end",
                        values=tuple(str(row.get(c,"")or"") for c in cols))
        tree.bind("<MouseWheel>",
                  lambda e: tree.yview_scroll(-1*(e.delta//120),"units"))

        # double-click copies clicked cell to clipboard
        def on_dbl(e, _t=tree, _c=cols):
            item   = _t.identify_row(e.y)
            col_id = _t.identify_column(e.x)
            if not item or not col_id: return
            idx = int(col_id.replace("#","")) - 1
            if idx < 0 or idx >= len(_c): return
            val = _t.item(item, "values")[idx]
            if not val: return
            self.clipboard_clear()
            self.clipboard_append(val)
            self._set_status(f"\u2713 Skopiowano: {val[:60]}")
        tree.bind("<Double-Button-1>", on_dbl)

        tk.Label(self.tree_frame,
                 text="\u2139 Dwuklik na komórce = kopiuj do schowka",
                 font=FSM, bg=BG, fg=TXT3, anchor="e").pack(
                 side="bottom", fill="x", padx=8, pady=2)

    # ── export ────────────────────────────────────────────────────────────
    def _export(self):
        if not self._last_res: return
        import os
        default = os.path.splitext(os.path.basename(self._mdb_path))[0]
        period  = self._last_res.get("period","").replace(" ","_")
        path = filedialog.asksaveasfilename(
            title="Zapisz raport Excel",
            defaultextension=".xlsx",
            initialfile=f"KSeF_{default}_{period}.xlsx",
            filetypes=[("Excel","*.xlsx"),("Wszystkie pliki","*.*")])
        if not path: return
        try:
            _export_excel(self._last_res, self._mdb_path, path)
            self.status_lbl.config(
                text=f"✓ Zapisano: {os.path.basename(path)}", fg=OK)
        except Exception as ex:
            self.status_lbl.config(text=f"✗ Błąd: {ex}", fg=ERR)


# ── Excel export ──────────────────────────────────────────────────────────────
def _export_excel(res, mdb_path, save_path):
    from openpyxl import Workbook
    from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    import os, datetime

    wb = Workbook()
    wb.remove(wb.active)

    def fill(h): return PatternFill("solid", fgColor=h)
    def font(h, bold=False, size=9): return Font(name="Consolas", color=h, bold=bold, size=size)
    thin = Side(style="thin", color="2a2f45")
    brd  = Border(left=thin, right=thin, top=thin, bottom=thin)

    kind_map = {
        "ok":      ("2dd4a0","1e3a2f","✓"),
        "warning": ("f5a623","3a2e10","⚠"),
        "error":   ("f75f5f","3a1010","✗"),
    }

    # ── Podsumowanie ──────────────────────────────────────────────────────
    ws = wb.create_sheet("Podsumowanie")
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 44
    ws.column_dimensions["B"].width = 22

    for row_data, fgc, bgc in [
        (f"KSeF Checker — Raport weryfikacji", "2dd4a0", "0d1a2e"),
        (f"Baza: {os.path.basename(mdb_path)}", "8b90a8", "0d1a2e"),
        (f"Okres: {res.get('period','?')}",     "8b90a8", "0d1a2e"),
        (f"Wygenerowano: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}", "8b90a8", "0d1a2e"),
    ]:
        r = ws.max_row + (1 if ws.max_row > 1 else 0)
        ws.cell(r, 1, row_data).font = font(fgc, bold=(fgc=="2dd4a0"), size=12 if fgc=="2dd4a0" else 9)
        ws.cell(r, 1).fill = fill(bgc)
        ws.cell(r, 2).fill = fill(bgc)
        ws.merge_cells(f"A{r}:B{r}")

    ws.append([])
    s = res.get("summary",{})
    ws.cell(ws.max_row+1, 1, "Statystyki").font = font("2dd4a0", bold=True)
    ws.cell(ws.max_row, 1).fill = fill("1e3a2f")
    ws.cell(ws.max_row, 2).fill = fill("1e3a2f")
    for lbl, val in [
        ("KSeF dokumenty pobrane", s.get("ksef_total","?")),
        ("  z czego zakupy",       s.get("ksef_zakup","?")),
        ("  z czego sprzedaż",     s.get("ksef_sprz","?")),
        ("Wpisy w KSIEGA",         s.get("ksiega","?")),
        ("Wpisy w VATZAKUPY",      s.get("vatzakupy","?")),
        ("Wpisy w VATSPRZEDAZ",    s.get("vatsprzedaz","?")),
        ("Zakres dat",             f"{s.get('date_from','?')} – {s.get('date_to','?')}"),
    ]:
        r = ws.max_row + 1
        ws.cell(r, 1, lbl).font = font("e8eaf0")
        ws.cell(r, 2, str(val)).font = font("2dd4a0", bold=True)
        ws.cell(r, 2).alignment = Alignment(horizontal="right")

    ws.append([])
    r = ws.max_row + 1
    ws.cell(r, 1, "Wyniki sprawdzeń").font = font("e8eaf0", bold=True)
    ws.cell(r, 1).fill = fill("0d1a2e")
    ws.cell(r, 2, "Wierszy").font = font("e8eaf0", bold=True)
    ws.cell(r, 2).fill = fill("0d1a2e")
    ws.cell(r, 2).alignment = Alignment(horizontal="right")

    for chk in res.get("checks",[]):
        fgc, bgc, icon = kind_map.get(chk["kind"],("e8eaf0","181c27","·"))
        r = ws.max_row + 1
        ws.cell(r, 1, f"{icon}  {chk['title']}").font = font(fgc, bold=(chk["kind"]!="ok"))
        ws.cell(r, 1).fill = fill(bgc)
        n = len(chk.get("rows",[]))
        ws.cell(r, 2, n if n else "—").font = font(fgc, bold=True)
        ws.cell(r, 2).fill = fill(bgc)
        ws.cell(r, 2).alignment = Alignment(horizontal="right")
        if chk.get("detail"):
            r2 = ws.max_row + 1
            ws.cell(r2, 1, f"    {chk['detail']}").font = font("8b90a8", size=8)

    # ── Per-check sheets ──────────────────────────────────────────────────
    for chk in res.get("checks",[]):
        rows = chk.get("rows",[])
        title = chk["title"][:28].strip()
        for ch in ["\\","/","[","]","*","?",":"]: title = title.replace(ch,"")
        ws2 = wb.create_sheet(title)
        ws2.sheet_view.showGridLines = False
        fgc, bgc, icon = kind_map.get(chk["kind"],("e8eaf0","181c27","·"))

        ws2["A1"] = f"{icon}  {chk['title']}"
        ws2["A1"].font = Font(name="Consolas", color=fgc, bold=True, size=10)
        ws2["A1"].fill = fill(bgc)
        if chk.get("detail"):
            ws2["A2"] = chk["detail"]
            ws2["A2"].font = font("8b90a8", size=8)
            ws2["A2"].fill = fill("0d1a2e")
        if chk.get("explanation"):
            ws2["A3"] = chk["explanation"]
            ws2["A3"].font = font("8b90a8", size=8)
            ws2["A3"].fill = fill("0d1a2e")

        if not rows:
            ws2["A4"] = "✓ Brak nieprawidłowości."
            ws2["A4"].font = font("2dd4a0", bold=True)
            ws2.column_dimensions["A"].width = 50
            continue

        cols = list(rows[0].keys())
        if len(cols) > 1:
            for rn in [1,2,3]:
                try: ws2.merge_cells(start_row=rn,start_column=1,end_row=rn,end_column=len(cols))
                except: pass

        sr = 5
        for j, c in enumerate(cols, 1):
            cell = ws2.cell(sr, j, c)
            cell.font  = Font(name="Consolas", color="2dd4a0", bold=True, size=9)
            cell.fill  = fill("1e3a2f")
            cell.border = brd
            cell.alignment = Alignment(horizontal="left")

        for i, row in enumerate(rows):
            bg = "181c27" if i%2==0 else "1e2335"
            for j, c in enumerate(cols, 1):
                val = row.get(c,"") or ""
                try: val = float(val.replace(",","")) if val.replace(",","").replace(".","").replace("-","").isdigit() else val
                except: pass
                cell = ws2.cell(sr+1+i, j, val)
                cell.font   = font("e8eaf0")
                cell.fill   = fill(bg)
                cell.border = brd
                if isinstance(val, float):
                    cell.number_format = "#,##0.00"
                    cell.alignment = Alignment(horizontal="right")

        for j, c in enumerate(cols, 1):
            w = max(len(str(c)), max((len(str(r.get(c,"")or"")) for r in rows[:500]),default=0))
            ws2.column_dimensions[get_column_letter(j)].width = min(w+4, 55)

    # ── Do sprawdzenia (checklist for client) ────────────────────────────
    problems = [c for c in res.get("checks",[]) if c["kind"] in ("error","warning") and c.get("rows")]
    if problems:
        ws_todo = wb.create_sheet("✉ Do sprawdzenia", 0)  # first sheet
        ws_todo.sheet_view.showGridLines = False
        ws_todo.column_dimensions["A"].width = 6
        ws_todo.column_dimensions["B"].width = 38
        ws_todo.column_dimensions["C"].width = 18
        ws_todo.column_dimensions["D"].width = 16
        ws_todo.column_dimensions["E"].width = 50

        # header
        for col, txt in [(1,""), (2,"Problem"), (3,"Kategoria"), (4,"Liczba"), (5,"Szczegóły")]:
            cell = ws_todo.cell(1, col, txt)
            cell.font = Font(name="Segoe UI", color="f0f0f0", bold=True, size=10)
            cell.fill = fill("2a2a2a")
            cell.alignment = Alignment(horizontal="left", vertical="center")
        ws_todo.row_dimensions[1].height = 22

        # title above
        ws_todo.insert_rows(1)
        ws_todo.cell(1,1, f"Lista do weryfikacji — {os.path.basename(mdb_path)} — {res.get('period','?')}  |  Wygenerowano: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}")
        ws_todo.cell(1,1).font = Font(name="Segoe UI", color="fb923c", bold=True, size=11)
        ws_todo.cell(1,1).fill = fill("1a1a1a")
        ws_todo.merge_cells("A1:E1")
        ws_todo.row_dimensions[1].height = 24

        kind_icon = {"error":"✗","warning":"⚠"}
        kind_color = {"error":"f87171","warning":"fbbf24"}

        for i, chk in enumerate(problems, 1):
            row = i + 2
            ic = kind_icon.get(chk["kind"],"·")
            bg = "222222" if i%2==0 else "1a1a1a"
            fc = kind_color.get(chk["kind"],"f0f0f0")

            ws_todo.cell(row, 1, ic).font = Font(name="Segoe UI", color=fc, bold=True, size=11)
            ws_todo.cell(row, 1).fill = fill(bg)
            ws_todo.cell(row, 1).alignment = Alignment(horizontal="center", vertical="center")

            ws_todo.cell(row, 2, chk["title"]).font = Font(name="Segoe UI", color=fc, bold=True, size=9)
            ws_todo.cell(row, 2).fill = fill(bg)

            ws_todo.cell(row, 3, chk["kind"].upper()).font = Font(name="Segoe UI", color=fc, size=9)
            ws_todo.cell(row, 3).fill = fill(bg)

            ws_todo.cell(row, 4, len(chk.get("rows",[]))).font = Font(name="Segoe UI", color="a0a0a0", size=9)
            ws_todo.cell(row, 4).fill = fill(bg)
            ws_todo.cell(row, 4).alignment = Alignment(horizontal="center")

            exp = chk.get("explanation","") or chk.get("detail","")
            ws_todo.cell(row, 5, exp[:120]).font = Font(name="Segoe UI", color="a0a0a0", size=8)
            ws_todo.cell(row, 5).fill = fill(bg)
            ws_todo.row_dimensions[row].height = 18

        # checkbox column hint
        ws_todo.cell(2, 1).value = "Status"
        ws_todo.cell(2, 1).font = Font(name="Segoe UI", color="606060", size=8)

    wb.save(save_path)


if __name__ == "__main__":
    app = App()
    app.mainloop()
