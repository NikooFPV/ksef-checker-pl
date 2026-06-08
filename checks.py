"""
Logika sprawdzeń KSeF Checker.
Każda funkcja check_* przyjmuje słownik d (z prepare()) i opcjonalnie cfg.
Zwraca dict: kind, title, detail, rows, explanation.
"""
import pandas as pd

MONTHS_PL = ["Styczeń","Luty","Marzec","Kwiecień","Maj","Czerwiec",
             "Lipiec","Sierpień","Wrzesień","Październik","Listopad","Grudzień"]

# ── helpers ───────────────────────────────────────────────────────────────────
def _clean(df):
    """astype str, replace None/nan."""
    return df.astype(str).replace({"None":"","nan":"","<NA>":""})

def rows_to_dicts(df):
    out = []
    for _, row in df.iterrows():
        d = {}
        for c in df.columns:
            v = row[c]
            try:
                if pd.isna(v): d[c]=""; continue
            except Exception: pass
            d[c] = f"{v:,.2f}" if isinstance(v, float) else str(v).strip()
        out.append(d)
    return out

def parse_dates(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce", dayfirst=False)
    return df

def sum_cols(df, cols):
    present = [c for c in cols if c in df.columns]
    if not present: return pd.Series(0.0, index=df.index)
    for c in present:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    return df[present].sum(axis=1)

def fmt(v):
    try: return f"{float(v):,.2f}"
    except: return str(v)

def ok(title, detail="", explanation=""):
    return dict(kind="ok", title=title, detail=detail, rows=[], explanation=explanation)

def err(title, detail="", rows=None, explanation=""):
    return dict(kind="error", title=title, detail=detail, rows=rows or [], explanation=explanation)

def warn(title, detail="", rows=None, explanation=""):
    return dict(kind="warning", title=title, detail=detail, rows=rows or [], explanation=explanation)

# ── VAT column definitions ────────────────────────────────────────────────────
NETTO_COLS    = ["NETTO23","NETTO8","NETTO5","NETTO22","NETTO7","NETTO3",
                 "NETTOZW23","NETTOZW8","NETTOZW5","ZAKUPY0"]
VAT_COLS      = ["VAT23","VAT8","VAT5","VAT22","VAT7","VAT3","VATZW23","VATZW8","VATZW5"]
NETTO_COLS_SP = ["NETTO23","NETTO8","NETTO5","NETTO22","NETTO7","NETTO3",
                 "KRAJOWA0","SPRZEDAZ_ZWOLNIONA"]
VAT_COLS_SP   = ["VAT23","VAT8","VAT5","VAT22","VAT7","VAT3"]  # PODATEK_NALEZNY is the SUM, not additive

# ── prepare: parse, filter, split ─────────────────────────────────────────────
QUARTER_MONTHS = {1:[1,2,3], 2:[4,5,6], 3:[7,8,9], 4:[10,11,12]}

def prepare(ksef, ksiega, vat, vatsp, month, year, cfg=None, quarter=None):
    cfg = cfg or {}
    tol = float(cfg.get("amount_tolerance", 0.05))
    cutoff_days = int(cfg.get("cutoff_days", 3))
    ksef_no_thr = float(cfg.get("ksef_no_threshold", 15.0))

    # parse
    ksef   = parse_dates(ksef,   ["ISSUE_DATE","INVOICING_DATE"])
    vat    = parse_dates(vat,    ["DATA_WYSTAWIENIA","DATA_UJECIA"])
    ksiega = parse_dates(ksiega, ["DATA","DATA_UJECIA"])
    if vatsp is not None:
        vatsp = parse_dates(vatsp, ["DATA_WYSTAWIENIA","DATA_SPRZEDAZY"])

    # DOWNLOADED filter (handles bool True/False from pyodbc)
    if "DOWNLOADED" in ksef.columns:
        dl = ksef["DOWNLOADED"].astype(str).str.strip().str.upper()
        ksef = ksef[dl.isin(["1","TRUE","YES","-1"])].copy()

    # numeric amounts
    for c in ["NET_AMOUNT","VAT_AMOUNT","GROSS_AMOUNT"]:
        ksef[c] = pd.to_numeric(ksef[c], errors="coerce")

    ksef_zak_all = ksef[ksef["DOCUMENT_TYPE"]=="2"].copy()
    ksef_spr_all = ksef[ksef["DOCUMENT_TYPE"]=="1"].copy()

    # period filter
    if quarter and year:
        months = QUARTER_MONTHS.get(quarter, [])
        def in_p(s): return s.dt.month.isin(months) & (s.dt.year==year)
        ksef_zak = ksef_zak_all[in_p(ksef_zak_all["ISSUE_DATE"])].copy()
        sd = ksef_spr_all["INVOICING_DATE"].fillna(ksef_spr_all["ISSUE_DATE"])
        ksef_spr  = ksef_spr_all[in_p(sd)].copy()
        vat_p     = vat[in_p(vat["DATA_UJECIA"])].copy()
        kd        = ksiega["DATA_UJECIA"].fillna(ksiega["DATA"])
        ksiega_p  = ksiega[in_p(kd)].copy()
        vatsp_p   = None
        if vatsp is not None:
            spd = vatsp["DATA_SPRZEDAZY"].fillna(vatsp["DATA_WYSTAWIENIA"])
            vatsp_p = vatsp[in_p(spd)].copy()
        use_cutoff = False
        # nadpisz month/year żeby date_shift checks mialy zakres
        month = None
    elif month and year:
        def in_p(s): return (s.dt.month==month) & (s.dt.year==year)
        ksef_zak = ksef_zak_all[in_p(ksef_zak_all["ISSUE_DATE"])].copy()
        sd = ksef_spr_all["INVOICING_DATE"].fillna(ksef_spr_all["ISSUE_DATE"])
        ksef_spr  = ksef_spr_all[in_p(sd)].copy()
        vat_p     = vat[in_p(vat["DATA_UJECIA"])].copy()
        kd        = ksiega["DATA_UJECIA"].fillna(ksiega["DATA"])
        ksiega_p  = ksiega[in_p(kd)].copy()
        vatsp_p   = None
        if vatsp is not None:
            spd = vatsp["DATA_SPRZEDAZY"].fillna(vatsp["DATA_WYSTAWIENIA"])
            vatsp_p = vatsp[in_p(spd)].copy()
        use_cutoff = False
    else:
        ksef_zak  = ksef_zak_all.copy()
        ksef_spr  = ksef_spr_all.copy()
        vat_p     = vat.copy()
        ksiega_p  = ksiega.copy()
        vatsp_p   = vatsp.copy() if vatsp is not None else None
        use_cutoff = True

    mn = ksef_zak["ISSUE_DATE"].min()
    mx = ksef_zak["ISSUE_DATE"].max()
    cutoff = (mx - pd.Timedelta(days=cutoff_days)) if use_cutoff and pd.notna(mx) else mx

    # precompute VAT sums (done once, reused by multiple checks)
    vat["_netto"] = sum_cols(vat, NETTO_COLS)
    vat["_vat"]   = sum_cols(vat, VAT_COLS)
    vat["WARTOSC_BRUTTO"] = pd.to_numeric(vat.get("WARTOSC_BRUTTO",0), errors="coerce").fillna(0)
    # ZAKUP50 bywa boolean (True/False) lub int (1/0) – normalizuj do 0/1
    if "ZAKUP50" in vat.columns:
        _z = vat["ZAKUP50"].astype(str).str.strip().str.upper()
        vat["ZAKUP50"] = _z.isin(["1", "TRUE", "YES", "-1"]).astype(int)
    else:
        vat["ZAKUP50"] = 0

    if vatsp is not None:
        vatsp["_netto"] = sum_cols(vatsp, NETTO_COLS_SP)
        vatsp["_vat"]   = sum_cols(vatsp, VAT_COLS_SP)
        vatsp["SPRZEDAZ_BRUTTO"] = pd.to_numeric(
            vatsp.get("SPRZEDAZ_BRUTTO",0), errors="coerce").fillna(0)

    # lookup sets – all periods (booking can cross months)
    def ksef_set(df, col="KSEF"):
        return set(df[df[col].notna()][col].str.strip()) if col in df.columns else set()

    all_ksiega_ksef = ksef_set(ksiega)
    all_vat_ksef    = ksef_set(vat)
    all_ksiega_r1   = ksef_set(ksiega[ksiega["RODZAJ"]=="1"])
    all_vatsp_ksef  = ksef_set(vatsp) if vatsp is not None else set()
    per_vat_ksef    = ksef_set(vat_p)
    per_ksiega_r2   = ksef_set(ksiega_p[ksiega_p["RODZAJ"]=="2"])

    return dict(
        ksef_zak=ksef_zak,       ksef_spr=ksef_spr,
        ksef_zak_all=ksef_zak_all, ksef_spr_all=ksef_spr_all,
        vat=vat,     vat_p=vat_p,
        vatsp=vatsp, vatsp_p=vatsp_p,
        ksiega=ksiega, ksiega_p=ksiega_p,
        all_ksiega_ksef=all_ksiega_ksef, all_vat_ksef=all_vat_ksef,
        all_ksiega_r1=all_ksiega_r1,     all_vatsp_ksef=all_vatsp_ksef,
        per_vat_ksef=per_vat_ksef,       per_ksiega_r2=per_ksiega_r2,
        cutoff=cutoff, use_cutoff=use_cutoff,
        month=month, year=year,
        tol=tol, ksef_no_thr=ksef_no_thr,
    )

# ── amount discrepancy helper ─────────────────────────────────────────────────
def _disc_tag(row, tol):
    t = []
    if abs(row.get("Δ_brutto",0)) > tol: t.append("brutto")
    if abs(row.get("Δ_netto",0))  > tol: t.append("netto")
    if abs(row.get("Δ_vat",0))    > tol: t.append("VAT/stawka")
    return ", ".join(t)

# ════════════════════════════════════════════════════════════════════════════════
# CHECKS
# ════════════════════════════════════════════════════════════════════════════════

def check_missing_purchases(d, cfg=None):
    zak = d["ksef_zak"]
    if d["use_cutoff"]: zak = zak[zak["ISSUE_DATE"] <= d["cutoff"]]
    missing = set(zak["KSEF_NUMBER"].dropna()) - d["all_ksiega_ksef"] - d["all_vat_ksef"]
    if not missing:
        return ok("Zakupy z KSeF: wszystkie zaksięgowane",
                  f"Sprawdzono {len(zak)} dokumentów.",
                  "Każda pobrana faktura zakupowa ma wpis w księdze i rejestrze VAT.")
    df = d["ksef_zak"][d["ksef_zak"]["KSEF_NUMBER"].isin(missing)][
        ["INVOICE_NUMBER","ISSUE_DATE","SELLER_NAME","SELLER_NIP",
         "NET_AMOUNT","VAT_AMOUNT","GROSS_AMOUNT"]].copy()
    df = df.sort_values("GROSS_AMOUNT", ascending=False)
    pos = df[df["GROSS_AMOUNT"]>0]["GROSS_AMOUNT"].sum()
    neg = df[df["GROSS_AMOUNT"]<0]["GROSS_AMOUNT"].sum()
    return err(f"Niezaksięgowane zakupy z KSeF: {len(missing)}",
               f"Faktury: {pos:,.2f} zł  |  Korekty: {neg:,.2f} zł",
               rows=rows_to_dicts(df.rename(columns={
                   "INVOICE_NUMBER":"Nr faktury","ISSUE_DATE":"Data wyst.",
                   "SELLER_NAME":"Sprzedawca","SELLER_NIP":"NIP",
                   "NET_AMOUNT":"Netto (KSeF)","VAT_AMOUNT":"VAT (KSeF)","GROSS_AMOUNT":"Brutto (KSeF)"})),
               explanation="Faktury pobrane z KSeF bez żadnego wpisu w KSIEGA ani VATZAKUPY. Wymagają ręcznego zaksięgowania.")

def check_missing_sales(d, cfg=None):
    spr = d["ksef_spr"]
    if d["use_cutoff"]: spr = spr[spr["ISSUE_DATE"] <= d["cutoff"]]
    missing = set(spr["KSEF_NUMBER"].dropna()) - d["all_ksiega_r1"] - d["all_vatsp_ksef"]
    if not missing:
        return ok("Sprzedaż z KSeF: wszystkie zaksięgowane",
                  f"Sprawdzono {len(spr)} dokumentów.",
                  "Każda faktura sprzedażowa ma wpis w księdze i rejestrze VAT.")
    df = d["ksef_spr"][d["ksef_spr"]["KSEF_NUMBER"].isin(missing)][
        ["INVOICE_NUMBER","ISSUE_DATE","BUYER_NAME",
         "NET_AMOUNT","VAT_AMOUNT","GROSS_AMOUNT"]].copy()
    df = df.sort_values("GROSS_AMOUNT", ascending=False)
    return err(f"Niezaksięgowana sprzedaż z KSeF: {len(missing)}",
               f"Łącznie: {df['GROSS_AMOUNT'].sum():,.2f} zł",
               rows=rows_to_dicts(df.rename(columns={
                   "INVOICE_NUMBER":"Nr faktury","ISSUE_DATE":"Data wyst.",
                   "BUYER_NAME":"Nabywca","NET_AMOUNT":"Netto (KSeF)",
                   "VAT_AMOUNT":"VAT (KSeF)","GROSS_AMOUNT":"Brutto (KSeF)"})),
               explanation="Faktury sprzedażowe z KSeF bez wpisu w księdze ani rejestrze VAT sprzedaży.")

def check_partial_booking(d, cfg=None):
    zak_nums = set(d["ksef_zak"]["KSEF_NUMBER"].dropna())
    w_k = (zak_nums & d["all_ksiega_ksef"]) - d["all_vat_ksef"]
    w_v = (zak_nums & d["all_vat_ksef"])    - d["all_ksiega_ksef"]
    if not w_k and not w_v:
        return ok("KSIEGA ↔ VATZAKUPY: spójne",
                  f"Wszystkie {len(d['per_ksiega_r2'])} wpisów zgodne.",
                  "Każdy zakup jest jednocześnie w księdze i rejestrze VAT.")
    rows = []
    for nums, problem in [(w_k,"Jest w KSIEGA — brak w VATZAKUPY"),
                          (w_v,"Jest w VATZAKUPY — brak w KSIEGA")]:
        for nr in nums:
            r = d["ksef_zak"][d["ksef_zak"]["KSEF_NUMBER"]==nr]
            if len(r):
                ri = r.iloc[0]
                rows.append({"Nr faktury":str(ri["INVOICE_NUMBER"]),
                             "Data":str(ri["ISSUE_DATE"])[:10],
                             "Sprzedawca":str(ri["SELLER_NAME"]),
                             "Brutto":fmt(ri["GROSS_AMOUNT"]),
                             "Problem":problem})
    parts = []
    if w_k: parts.append(f"W KSIEGA bez VAT: {len(w_k)}")
    if w_v: parts.append(f"W VAT bez KSIEGA: {len(w_v)}")
    return err(f"Niespójność KSIEGA ↔ VATZAKUPY: {len(rows)} faktur",
               " | ".join(parts), rows=rows,
               explanation="Faktura powinna być jednocześnie w KSIEGA i VATZAKUPY. Brak w jednym miejscu = niekompletne zaksięgowanie.")

def check_amounts_vs_vat(d, cfg=None):
    tol = d["tol"]
    booked = set(d["ksef_zak"]["KSEF_NUMBER"].dropna()) & d["all_ksiega_ksef"] & d["all_vat_ksef"]
    if not booked:
        return ok("Kwoty KSeF vs VATZAKUPY: brak danych", "Brak zaksięgowanych faktur.")
    ksef_b = d["ksef_zak"][d["ksef_zak"]["KSEF_NUMBER"].isin(booked)].copy()
    vat_b  = d["vat"][d["vat"]["KSEF"].isin(booked)][
        ["KSEF","WARTOSC_BRUTTO","_netto","_vat","ZAKUP50"]].copy()
    m = ksef_b.merge(vat_b, left_on="KSEF_NUMBER", right_on="KSEF", how="left")
    m["ZAKUP50"] = pd.to_numeric(m["ZAKUP50"], errors="coerce").fillna(0)
    m["Δ_brutto"] = (m["GROSS_AMOUNT"] - m["WARTOSC_BRUTTO"]).round(2)
    m["Δ_netto"]  = (m["NET_AMOUNT"]   - m["_netto"]).round(2)
    m["Δ_vat"]    = (m["VAT_AMOUNT"]   - m["_vat"]).round(2)

    # Stawka 0%: GROSS_AMOUNT w KSeF może być 0 gdy NET=brutto (zw./0%)
    zero_vat_ok = (
        (m["VAT_AMOUNT"].abs() < tol) &
        (m["Δ_netto"].abs() <= tol) &
        (m["Δ_vat"].abs()   <= tol)
    )
    # ZAKUP50=1: w rejestrze VAT tylko 50% netto/VAT – to prawidłowe
    zakup50_ok = (
        (m["ZAKUP50"] == 1) &
        ((m["NET_AMOUNT"] * 0.5 - m["_netto"]).abs() <= tol + 0.05) &
        ((m["VAT_AMOUNT"] * 0.5 - m["_vat"]).abs()   <= tol + 0.05)
    )
    disc = m[~zero_vat_ok & ~zakup50_ok & (
        (m["Δ_brutto"].abs()>tol)|(m["Δ_netto"].abs()>tol)|(m["Δ_vat"].abs()>tol))].copy()
    if disc.empty:
        return ok("Kwoty KSeF vs VATZAKUPY: zgodne",
                  f"Porównano {len(booked)} faktur.",
                  "Wszystkie kwoty netto/VAT/brutto zgodne między KSeF a rejestrem VAT.")
    disc["Rodzaj błędu"] = disc.apply(lambda r: _disc_tag(r, tol), axis=1)
    df = disc[["INVOICE_NUMBER","SELLER_NAME","NET_AMOUNT","VAT_AMOUNT","GROSS_AMOUNT",
               "_netto","_vat","WARTOSC_BRUTTO","Δ_netto","Δ_vat","Δ_brutto","Rodzaj błędu"]].copy()
    kind = "error" if disc["Δ_brutto"].abs().max()>1 else "warning"
    return dict(kind=kind,
        title=f"Niezgodności kwotowe zakupów (KSeF vs VAT): {len(disc)}",
        detail=(f"Σ Δbrutto: {disc['Δ_brutto'].abs().sum():,.2f} zł  |  "
                f"Σ Δnetto: {disc['Δ_netto'].abs().sum():,.2f} zł  |  "
                f"Σ ΔVAT: {disc['Δ_vat'].abs().sum():,.2f} zł"),
        rows=rows_to_dicts(df.rename(columns={
            "INVOICE_NUMBER":"Nr faktury","SELLER_NAME":"Sprzedawca",
            "NET_AMOUNT":"Netto (KSeF)","VAT_AMOUNT":"VAT (KSeF)","GROSS_AMOUNT":"Brutto (KSeF)",
            "_netto":"Netto (VAT rej.)","_vat":"VAT (VAT rej.)","WARTOSC_BRUTTO":"Brutto (VAT rej.)",
            "Δ_netto":"Δ Netto","Δ_vat":"Δ VAT","Δ_brutto":"Δ Brutto"})),
        explanation="'VAT/stawka' = poprawne brutto ale błędna stawka VAT w rejestrze.")

def check_amounts_vs_ksiega(d, cfg=None):
    tol = d["tol"]
    booked = set(d["ksef_zak"]["KSEF_NUMBER"].dropna()) & d["all_ksiega_ksef"]
    if not booked:
        return ok("Kwoty KSeF vs KSIEGA: brak danych", "Brak wspólnych wpisów.")
    ksef_b   = d["ksef_zak"][d["ksef_zak"]["KSEF_NUMBER"].isin(booked)].copy()
    ksiega_b = d["ksiega"][(d["ksiega"]["RODZAJ"]=="2") &
                            d["ksiega"]["KSEF"].isin(booked)].copy()
    kwota_cols = [c for c in ["ZAKUP","ZAKUP_KOSZTY","WYDATKI","WYDATKI_INNE","WYNAGRODZENIA"]
                  if c in ksiega_b.columns]
    for c in kwota_cols:
        ksiega_b[c] = pd.to_numeric(ksiega_b[c], errors="coerce").fillna(0)
    ksiega_b["_kwota"] = ksiega_b[kwota_cols].sum(axis=1)
    ksiega_b["PROCENT_KOSZTU"] = pd.to_numeric(
        ksiega_b.get("PROCENT_KOSZTU", 100), errors="coerce").fillna(100)
    m = ksef_b.merge(ksiega_b[["KSEF","_kwota","PROCENT_KOSZTU"]+kwota_cols],
                     left_on="KSEF_NUMBER", right_on="KSEF", how="left")
    m["_expected"] = (m["NET_AMOUNT"] * m["PROCENT_KOSZTU"] / 100).round(2)
    m["Δ_ksiega"]  = (m["_expected"] - m["_kwota"]).round(2)
    disc = m[m["Δ_ksiega"].abs() > tol].copy()
    if disc.empty:
        return ok("Kwoty KSeF vs KSIEGA: zgodne",
                  f"Porównano {len(m)} faktur.",
                  "Kwoty netto z KSeF zgodne z wartościami w księdze.")
    df = disc[["INVOICE_NUMBER","SELLER_NAME","NET_AMOUNT","_kwota","Δ_ksiega","PROCENT_KOSZTU"]].copy()
    return warn(f"Niezgodności kwotowe (KSeF vs KSIEGA): {len(disc)}",
                f"Suma różnic: {disc['Δ_ksiega'].abs().sum():,.2f} zł",
                rows=rows_to_dicts(df.rename(columns={
                    "INVOICE_NUMBER":"Nr faktury","SELLER_NAME":"Sprzedawca",
                    "NET_AMOUNT":"Netto (KSeF)","_kwota":"Kwota w KSIEGA",
                    "Δ_ksiega":"Różnica","PROCENT_KOSZTU":"% kosztu"})),
                explanation="Kwota netto w KSeF różni się od sumy kosztów w księdze. Uwzględniono % kosztu dla faktur z ograniczonym odliczeniem.")

def check_sales_amounts(d, cfg=None):
    tol = d["tol"]
    if d["vatsp"] is None:
        return ok("Kwoty sprzedaży: brak rejestru VATSPRZEDAZ")
    booked = set(d["ksef_spr"]["KSEF_NUMBER"].dropna()) & d["all_vatsp_ksef"]
    if not booked:
        return ok("Kwoty sprzedaży KSeF vs VATSPRZEDAZ: brak danych")
    ksef_b = d["ksef_spr"][d["ksef_spr"]["KSEF_NUMBER"].isin(booked)].copy()
    vsp_b  = d["vatsp"][d["vatsp"]["KSEF"].isin(booked)][
        ["KSEF","SPRZEDAZ_BRUTTO","_netto","_vat"]].copy()
    m = ksef_b.merge(vsp_b, left_on="KSEF_NUMBER", right_on="KSEF", how="left")
    m["Δ_brutto"] = (m["GROSS_AMOUNT"] - m["SPRZEDAZ_BRUTTO"]).round(2)
    m["Δ_netto"]  = (m["NET_AMOUNT"]   - m["_netto"]).round(2)
    m["Δ_vat"]    = (m["VAT_AMOUNT"]   - m["_vat"]).round(2)
    disc = m[(m["Δ_brutto"].abs()>tol)|(m["Δ_netto"].abs()>tol)|(m["Δ_vat"].abs()>tol)].copy()
    if disc.empty:
        return ok("Kwoty sprzedaży KSeF vs VATSPRZEDAZ: zgodne",
                  f"Porównano {len(booked)} faktur.",
                  "Wszystkie kwoty sprzedaży zgodne między KSeF a rejestrem.")
    disc["Rodzaj błędu"] = disc.apply(lambda r: _disc_tag(r, tol), axis=1)
    df = disc[["INVOICE_NUMBER","BUYER_NAME","NET_AMOUNT","VAT_AMOUNT","GROSS_AMOUNT",
               "_netto","_vat","SPRZEDAZ_BRUTTO","Δ_netto","Δ_vat","Δ_brutto","Rodzaj błędu"]].copy()
    kind = "error" if disc["Δ_brutto"].abs().max()>1 else "warning"
    return dict(kind=kind,
        title=f"Niezgodności kwotowe sprzedaży (KSeF vs VATSPRZEDAZ): {len(disc)}",
        detail=f"Σ Δbrutto: {disc['Δ_brutto'].abs().sum():,.2f} zł",
        rows=rows_to_dicts(df.rename(columns={
            "INVOICE_NUMBER":"Nr faktury","BUYER_NAME":"Nabywca",
            "NET_AMOUNT":"Netto (KSeF)","VAT_AMOUNT":"VAT (KSeF)","GROSS_AMOUNT":"Brutto (KSeF)",
            "_netto":"Netto (rej. sp.)","_vat":"VAT (rej. sp.)","SPRZEDAZ_BRUTTO":"Brutto (rej. sp.)",
            "Δ_netto":"Δ Netto","Δ_vat":"Δ VAT","Δ_brutto":"Δ Brutto"})),
        explanation="Porównanie netto/VAT/brutto sprzedaży między KSeF a rejestrem VATSPRZEDAZ.")

def _date_shift(ksef_df, reg_df, ksef_date_col, reg_date_col, reg_ksef_col,
                month, year, label_ksef, label_reg, name_col, amount_col):
    nums = set(ksef_df["KSEF_NUMBER"].dropna())
    booked = reg_df[reg_df[reg_ksef_col].isin(nums)].copy()
    wrong = booked[~((booked[reg_date_col].dt.month==month) &
                     (booked[reg_date_col].dt.year==year))].copy()
    if wrong.empty: return None
    m = ksef_df.merge(wrong[["KSEF_NUMBER" if reg_ksef_col=="KSEF_NUMBER" else reg_ksef_col,
                               reg_date_col]].rename(
        columns={reg_ksef_col:"KSEF_NUMBER"}),
        on="KSEF_NUMBER", how="inner")
    kd = ksef_df.get(ksef_date_col, ksef_df["ISSUE_DATE"])
    m2 = ksef_df[ksef_df["KSEF_NUMBER"].isin(wrong[reg_ksef_col])].copy()
    m2 = m2.merge(wrong[[reg_ksef_col,reg_date_col]],
                  left_on="KSEF_NUMBER", right_on=reg_ksef_col, how="inner")
    m2["Miesiąc KSeF"]    = m2["ISSUE_DATE"].dt.strftime("%m.%Y")
    m2["Miesiąc rejestr"] = m2[reg_date_col].dt.strftime("%m.%Y")
    return m2[["INVOICE_NUMBER",name_col,"Miesiąc KSeF","Miesiąc rejestr","GROSS_AMOUNT"]].copy()

def check_date_shift_purchases(d, cfg=None):
    if not (d["month"] and d["year"]): return None
    m, y = d["month"], d["year"]
    nums = set(d["ksef_zak"]["KSEF_NUMBER"].dropna())
    booked = d["vat"][d["vat"]["KSEF"].isin(nums)].copy()
    wrong = booked[~((booked["DATA_UJECIA"].dt.month==m)&(booked["DATA_UJECIA"].dt.year==y))]
    if wrong.empty:
        return ok(f"Daty zaksięgowania zakupów: prawidłowe",
                  f"Wszystkie zakupy ujęte w {MONTHS_PL[m-1]} {y}.",
                  "Daty wystawienia i ujęcia VAT zgodne z wybranym miesiącem.")
    merged = d["ksef_zak"].merge(
        wrong[["KSEF","DATA_UJECIA"]], left_on="KSEF_NUMBER", right_on="KSEF", how="inner")
    merged["Miesiąc KSeF"]    = merged["ISSUE_DATE"].dt.strftime("%m.%Y")
    merged["Miesiąc rejestr"] = merged["DATA_UJECIA"].dt.strftime("%m.%Y")
    df = merged[["INVOICE_NUMBER","SELLER_NAME","Miesiąc KSeF","Miesiąc rejestr","GROSS_AMOUNT"]].copy()
    return warn(f"Zakupy w złym miesiącu w VATZAKUPY: {len(df)}",
                f"Data wystawienia: {MONTHS_PL[m-1]} {y} → data ujęcia VAT różna",
                rows=rows_to_dicts(df.rename(columns={
                    "INVOICE_NUMBER":"Nr faktury","SELLER_NAME":"Sprzedawca","GROSS_AMOUNT":"Brutto"})),
                explanation="Zakupy powinny być ujmowane wg daty wystawienia. Faktura wpadła do innego miesiąca w rejestrze VAT.")

def check_date_shift_sales(d, cfg=None):
    if not (d["month"] and d["year"]): return None
    if d["vatsp"] is None or "KSEF" not in d["vatsp"].columns: return None
    m, y = d["month"], d["year"]
    vatsp = d["vatsp"].copy()
    vatsp["_sp"] = vatsp["DATA_SPRZEDAZY"].fillna(vatsp["DATA_WYSTAWIENIA"])
    nums = set(d["ksef_spr"]["KSEF_NUMBER"].dropna())
    booked = vatsp[vatsp["KSEF"].isin(nums)].copy()
    wrong = booked[~((booked["_sp"].dt.month==m)&(booked["_sp"].dt.year==y))]
    if wrong.empty:
        return ok(f"Daty zaksięgowania sprzedaży: prawidłowe",
                  f"Wszystkie faktury sprzedaży ujęte w {MONTHS_PL[m-1]} {y}.",
                  "Daty sprzedaży zgodne z wybranym miesiącem.")
    merged = d["ksef_spr"].merge(
        wrong[["KSEF","_sp"]], left_on="KSEF_NUMBER", right_on="KSEF", how="inner")
    sd = merged["INVOICING_DATE"].fillna(merged["ISSUE_DATE"])
    merged["Miesiąc KSeF"]    = sd.dt.strftime("%m.%Y")
    merged["Miesiąc rejestr"] = merged["_sp"].dt.strftime("%m.%Y")
    df = merged[["INVOICE_NUMBER","BUYER_NAME","Miesiąc KSeF","Miesiąc rejestr","GROSS_AMOUNT"]].copy()
    return warn(f"Sprzedaż w złym miesiącu w VATSPRZEDAZ: {len(df)}",
                f"Data sprzedaży: {MONTHS_PL[m-1]} {y} → data w rejestrze różna",
                rows=rows_to_dicts(df.rename(columns={
                    "INVOICE_NUMBER":"Nr faktury","BUYER_NAME":"Nabywca","GROSS_AMOUNT":"Brutto"})),
                explanation="Sprzedaż ujmujemy wg daty sprzedaży. Faktura wpadła do innego miesiąca.")

def check_no_ksef_number(d, cfg=None):
    vat = d["vat_p"]
    bez = vat[vat["KSEF"].isna()|(vat["KSEF"].str.strip()=="")]
    pct = len(bez)/len(vat)*100 if len(vat) else 0
    thr = d["ksef_no_thr"]
    sample = bez[["NUMER","DATA_WYSTAWIENIA","FIRMA","WARTOSC_BRUTTO"]].head(100).copy()
    rows = rows_to_dicts(sample.rename(columns={
        "NUMER":"Nr faktury","DATA_WYSTAWIENIA":"Data","FIRMA":"Kontrahent","WARTOSC_BRUTTO":"Brutto"}))
    kind = "warning" if pct > thr else "ok"
    return dict(kind=kind,
        title=f"Zakupy bez numeru KSeF: {len(bez)} ({pct:.1f}%)",
        detail="Faktury ręczne, zagraniczne lub spoza KSeF.",
        rows=rows if kind=="warning" else [],
        explanation="Wysoki odsetek może oznaczać, że część faktur nie jest pobierana automatycznie z KSeF.")

def check_ksiega_only(d, cfg=None):
    ks = d["ksiega_p"]
    bez = ks[(ks["RODZAJ"]=="2")&(ks["KSEF"].isna()|(ks["KSEF"].str.strip()==""))].copy()
    vat_numery = set(d["vat_p"]["NUMER"].dropna().str.strip())
    tylko = bez[~bez["NUMER"].str.strip().isin(vat_numery)].copy()
    if tylko.empty:
        return ok("Wpisy tylko w KSIEGA: brak",
                  "Wszystkie wpisy mają odpowiednik w rejestrze VAT.",
                  "Wszystkie wpisy zakupowe mają odpowiednik w VATZAKUPY.")
    cols_s = [c for c in ["NUMER","DATA","OPIS","FIRMA","NIP",
                           "ZAKUP","ZAKUP_KOSZTY","WYDATKI","WYNAGRODZENIA","RAZEM_WYDATKI"]
              if c in tylko.columns]
    df = tylko[cols_s].copy()
    for c in ["ZAKUP","ZAKUP_KOSZTY","WYDATKI","WYNAGRODZENIA","RAZEM_WYDATKI"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).round(2)
    total = df["RAZEM_WYDATKI"].sum() if "RAZEM_WYDATKI" in df.columns else 0
    return warn(f"Wpisy tylko w KSIEGA (bez rejestru VAT): {len(tylko)}",
                f"Łącznie: {total:,.2f} zł  |  Opłaty bankowe, ZUS, wynagrodzenia itp.",
                rows=rows_to_dicts(df),
                explanation="Wydatki w księdze bez faktury VAT: opłaty bankowe, ZUS, ubezpieczenia, amortyzacja, wynagrodzenia.")

def check_duplicates_vat(d, cfg=None):
    v = d["vat_p"]
    v2 = v[v["KSEF"].notna()&(v["KSEF"].str.strip()!="")]
    dups = v2[v2.duplicated(subset=["KSEF"], keep=False)].copy()
    if dups.empty:
        return ok("Duplikaty w VATZAKUPY: brak",
                  "Każdy numer KSeF występuje dokładnie raz.",
                  "Brak zduplikowanych faktur w rejestrze VAT zakupów.")
    df = dups[["NUMER","DATA_WYSTAWIENIA","FIRMA","WARTOSC_BRUTTO","KSEF"]].sort_values("KSEF")
    return err(f"Duplikaty w VATZAKUPY: {len(dups)} wpisów ({dups['KSEF'].nunique()} faktur)",
               "Ten sam numer KSeF zaksięgowany więcej niż raz.",
               rows=rows_to_dicts(df.rename(columns={
                   "NUMER":"Nr faktury","DATA_WYSTAWIENIA":"Data",
                   "FIRMA":"Kontrahent","WARTOSC_BRUTTO":"Brutto","KSEF":"Nr KSeF"})),
               explanation="Duplikat w VATZAKUPY zawyży odliczony VAT i spowoduje błąd w JPK_VAT.")

def check_duplicates_vatsp(d, cfg=None):
    if d["vatsp_p"] is None or "KSEF" not in d["vatsp_p"].columns: return None
    v = d["vatsp_p"][d["vatsp_p"]["KSEF"].notna()&(d["vatsp_p"]["KSEF"].str.strip()!="")]
    dups = v[v.duplicated(subset=["KSEF"], keep=False)].copy()
    if dups.empty:
        return ok("Duplikaty w VATSPRZEDAZ: brak",
                  "Każdy numer KSeF sprzedaży występuje dokładnie raz.",
                  "Brak zduplikowanych faktur w rejestrze VAT sprzedaży.")
    df = dups[["NUMER","DATA_WYSTAWIENIA","FIRMA","SPRZEDAZ_BRUTTO","KSEF"]].copy()
    return err(f"Duplikaty w VATSPRZEDAZ: {len(dups)} wpisów",
               "Ten sam numer KSeF sprzedaży zaksięgowany więcej niż raz.",
               rows=rows_to_dicts(df.rename(columns={
                   "NUMER":"Nr faktury","DATA_WYSTAWIENIA":"Data",
                   "FIRMA":"Kontrahent","SPRZEDAZ_BRUTTO":"Brutto","KSEF":"Nr KSeF"})),
               explanation="Duplikat w VATSPRZEDAZ zawyży VAT należny i przychód.")

def check_corrections_purchases(d, cfg=None):
    zak = d["ksef_zak_all"]
    kor = zak[zak["GROSS_AMOUNT"] < 0].copy()
    if kor.empty:
        return ok("Korekty zakupów: brak lub wszystkie OK",
                  "Brak faktur korygujących zakupy w wybranym okresie.")
    niezaks = kor[~kor["KSEF_NUMBER"].isin(d["all_vat_ksef"]|d["all_ksiega_ksef"])]
    if niezaks.empty:
        return ok(f"Korekty zakupów: wszystkie zaksięgowane ({len(kor)})",
                  f"Suma korekt: {kor['GROSS_AMOUNT'].sum():,.2f} zł")
    df = niezaks[["INVOICE_NUMBER","ISSUE_DATE","SELLER_NAME",
                   "NET_AMOUNT","VAT_AMOUNT","GROSS_AMOUNT"]].copy()
    return err(f"Niezaksięgowane korekty zakupów: {len(niezaks)}",
               f"Suma: {niezaks['GROSS_AMOUNT'].sum():,.2f} zł",
               rows=rows_to_dicts(df.rename(columns={
                   "INVOICE_NUMBER":"Nr faktury","ISSUE_DATE":"Data",
                   "SELLER_NAME":"Sprzedawca","NET_AMOUNT":"Netto",
                   "VAT_AMOUNT":"VAT","GROSS_AMOUNT":"Brutto"})),
               explanation="Faktury korygujące (ujemne) z KSeF nie zostały zaksięgowane. Zawyżają odliczony VAT i koszty.")

def check_corrections_sales(d, cfg=None):
    spr = d["ksef_spr_all"]
    if "INVOICE_TYPE" in spr.columns:
        kor = spr[spr["INVOICE_TYPE"].str.strip().str.upper().isin(["KOR","KOREKTA"])].copy()
    else:
        kor = spr[spr["GROSS_AMOUNT"] < 0].copy()
    if kor.empty:
        return ok("Korekty sprzedaży: brak lub wszystkie OK",
                  "Brak faktur korygujących sprzedaż w wybranym okresie.")
    niezaks = kor[~kor["KSEF_NUMBER"].isin(d["all_vatsp_ksef"]|d["all_ksiega_r1"])]
    if niezaks.empty:
        return ok(f"Korekty sprzedaży: wszystkie zaksięgowane ({len(kor)})",
                  f"Suma korekt: {kor['GROSS_AMOUNT'].sum():,.2f} zł")
    df = niezaks[["INVOICE_NUMBER","ISSUE_DATE","BUYER_NAME",
                   "NET_AMOUNT","VAT_AMOUNT","GROSS_AMOUNT"]].copy()
    return err(f"Niezaksięgowane korekty sprzedaży: {len(niezaks)}",
               f"Suma: {niezaks['GROSS_AMOUNT'].sum():,.2f} zł",
               rows=rows_to_dicts(df.rename(columns={
                   "INVOICE_NUMBER":"Nr faktury","ISSUE_DATE":"Data",
                   "BUYER_NAME":"Nabywca","NET_AMOUNT":"Netto",
                   "VAT_AMOUNT":"VAT","GROSS_AMOUNT":"Brutto"})),
               explanation="Faktury korygujące sprzedaż nie zostały zaksięgowane. Zawyżają VAT należny i przychód.")

def check_nip_mismatch(d, cfg=None):
    booked = set(d["ksef_zak"]["KSEF_NUMBER"].dropna()) & d["all_vat_ksef"]
    if not booked:
        return ok("NIP kontrahentów: brak danych do porównania")
    def cn(s): return str(s).strip().replace("-","").replace(" ","").replace(".","")
    ksef_b = d["ksef_zak"][d["ksef_zak"]["KSEF_NUMBER"].isin(booked)][
        ["KSEF_NUMBER","INVOICE_NUMBER","SELLER_NAME","SELLER_NIP"]].copy()
    ksef_b["_nk"] = ksef_b["SELLER_NIP"].apply(cn)
    vat_b  = d["vat"][d["vat"]["KSEF"].isin(booked)][["KSEF","NIP"]].copy()
    vat_b["_nv"] = vat_b["NIP"].apply(cn)
    m = ksef_b.merge(vat_b, left_on="KSEF_NUMBER", right_on="KSEF", how="left")
    disc = m[(m["_nk"].str.len()==10)&(m["_nv"].str.len()==10)&(m["_nk"]!=m["_nv"])].copy()
    if disc.empty:
        return ok("NIP kontrahentów: zgodne",
                  f"Porównano {len(booked)} faktur — brak różnic.",
                  "NIP sprzedawcy w KSeF zgodny z NIP w rejestrze VAT.")
    df = disc[["INVOICE_NUMBER","SELLER_NAME","SELLER_NIP","NIP"]].copy()
    return err(f"Błędny NIP kontrahenta: {len(df)} faktur",
               "NIP w KSeF różni się od NIP wpisanego w VATZAKUPY.",
               rows=rows_to_dicts(df.rename(columns={
                   "INVOICE_NUMBER":"Nr faktury","SELLER_NAME":"Sprzedawca",
                   "SELLER_NIP":"NIP (KSeF)","NIP":"NIP (rejestr)"})),
               explanation="Błędny NIP w rejestrze VAT powoduje odrzucenie JPK. Należy poprawić NIP w VATZAKUPY.")

def check_vat_deadline(d, cfg=None):
    vat = d["vat_p"].copy()
    vat["_wys"]  = pd.to_datetime(vat["DATA_WYSTAWIENIA"], errors="coerce", dayfirst=False)
    vat["_gap"]  = (vat["DATA_UJECIA"] - vat["_wys"]).dt.days
    late = vat[(vat["_gap"]>90)&vat["KSEF"].notna()&(vat["KSEF"].str.strip()!="")].copy()
    if late.empty:
        return ok("Termin odliczenia VAT: prawidłowy",
                  "Brak faktur ujętych po upływie 90 dni od wystawienia.",
                  "Wszystkie faktury ujęto w rejestrze w terminie ustawowym.")
    late["Dni opóźnienia"] = late["_gap"].astype(int)
    df = late[["NUMER","DATA_WYSTAWIENIA","DATA_UJECIA","FIRMA","WARTOSC_BRUTTO","Dni opóźnienia"]].copy()
    df["DATA_WYSTAWIENIA"] = df["DATA_WYSTAWIENIA"].astype(str).str[:10]
    df["DATA_UJECIA"]      = df["DATA_UJECIA"].astype(str).str[:10]
    total_vat = late["_vat"].sum() if "_vat" in late.columns else 0
    return err(f"Faktury po terminie odliczenia VAT (>90 dni): {len(late)}",
               f"Ryzyko utraty prawa do odliczenia. Kwota VAT: {total_vat:,.2f} zł",
               rows=rows_to_dicts(df.rename(columns={
                   "NUMER":"Nr faktury","DATA_WYSTAWIENIA":"Data wyst.",
                   "DATA_UJECIA":"Data ujęcia","FIRMA":"Kontrahent","WARTOSC_BRUTTO":"Brutto"})),
               explanation="Art. 86 ust. 11 ustawy o VAT: prawo do odliczenia w okresie wystawienia lub 3 kolejnych miesiącach. Przekroczenie = utrata prawa lub konieczność korekty.")

def check_split_payment(d, cfg=None):
    vat = d["vat_p"].copy()
    if "SPLIT_PAYMENT" not in vat.columns:
        return ok("Split payment (MPP): brak kolumny w bazie")
    vat["WARTOSC_BRUTTO"] = pd.to_numeric(vat["WARTOSC_BRUTTO"], errors="coerce").fillna(0)
    vat["SPLIT_PAYMENT"]  = pd.to_numeric(vat["SPLIT_PAYMENT"],  errors="coerce").fillna(0)
    big_no  = vat[(vat["WARTOSC_BRUTTO"]>=15000)&(vat["SPLIT_PAYMENT"]==0)].copy()
    rows = []
    for _, r in big_no.iterrows():
        rows.append({"Nr faktury":str(r.get("NUMER","")),
                     "Kontrahent":str(r.get("FIRMA","")),
                     "Brutto":f"{r['WARTOSC_BRUTTO']:,.2f}",
                     "MPP":"NIE",
                     "Uwaga":"Faktura ≥15 000 zł — brak oznaczenia MPP"})
    if not rows:
        return ok("Split payment (MPP): prawidłowy",
                  f"Sprawdzono {len(vat)} faktur — brak nieprawidłowości.",
                  "Oznaczenia MPP zgodne z progiem 15 000 zł brutto.")
    return err(f"Brak oznaczenia MPP dla faktur ≥15 000 zł: {len(rows)}",
               f"Wartość: {big_no['WARTOSC_BRUTTO'].sum():,.2f} zł",
               rows=rows,
               explanation="MPP obowiązkowy dla faktur ≥15 000 zł brutto z towarów/usług z zał. 15 ustawy o VAT (art. 108a ust. 1a).")

def check_foreign_currency(d, cfg=None):
    if "CURRENCY_IDENTIFIER" not in d["ksef_zak"].columns: return None
    fz = d["ksef_zak"][d["ksef_zak"]["CURRENCY_IDENTIFIER"].str.strip().str.upper()!="PLN"].copy()
    fs = d["ksef_spr"][d["ksef_spr"]["CURRENCY_IDENTIFIER"].str.strip().str.upper()!="PLN"].copy() \
        if "CURRENCY_IDENTIFIER" in d["ksef_spr"].columns else pd.DataFrame()
    all_f = pd.concat([fz, fs], ignore_index=True) if not fs.empty else fz
    if all_f.empty:
        return ok("Faktury walutowe: brak","Wszystkie faktury w PLN.")
    df = all_f[["INVOICE_NUMBER","ISSUE_DATE","SELLER_NAME",
                 "CURRENCY_IDENTIFIER","NET_AMOUNT","GROSS_AMOUNT"]].copy()
    return warn(f"Faktury walutowe (nie-PLN): {len(all_f)}",
                f"Waluty: {', '.join(all_f['CURRENCY_IDENTIFIER'].unique())}",
                rows=rows_to_dicts(df.rename(columns={
                    "INVOICE_NUMBER":"Nr faktury","ISSUE_DATE":"Data",
                    "SELLER_NAME":"Wystawca","CURRENCY_IDENTIFIER":"Waluta",
                    "NET_AMOUNT":"Netto (oryg.)","GROSS_AMOUNT":"Brutto (oryg.)"})),
                explanation="Faktury walutowe wymagają przeliczenia na PLN wg kursu NBP z dnia poprzedzającego wystawienie.")

def check_nip_name_inconsistency(d, cfg=None):
    vat = d["vat_p"].copy()
    if "NIP" not in vat.columns or "FIRMA" not in vat.columns: return None
    vat["_nc"] = vat["NIP"].str.replace(r"\D","",regex=True).str.strip()
    v = vat[vat["_nc"].str.len()==10].copy()
    grp = v.groupby("_nc")["FIRMA"].nunique()
    multi = grp[grp>1].index.tolist()
    if not multi:
        return ok("Spójność NIP↔Nazwa: prawidłowa",
                  "Każdy NIP ma jedną nazwę firmy w rejestrze.",
                  "Brak kontrahentów z tym samym NIP ale różnymi nazwami.")
    rows = []
    for nip in multi[:50]:
        names = v[v["_nc"]==nip]["FIRMA"].unique()
        rows.append({"NIP":nip, "Liczba nazw":str(len(names)),
                     "Nazwy w rejestrze":" | ".join(str(n) for n in names[:5])})
    return warn(f"Ten sam NIP, różne nazwy firmy: {len(multi)} kontrahentów",
                "Możliwe literówki w nazwie lub zmiana nazwy firmy.",
                rows=rows,
                explanation="Ten sam NIP pod różnymi nazwami — możliwa literówka, zmiana nazwy lub błąd przy wprowadzaniu.")

# ── registry: id → function ───────────────────────────────────────────────────
CHECK_REGISTRY = {
    "missing_purchases":      ("Sprawdzam niezaksięgowane zakupy…",    check_missing_purchases),
    "missing_sales":          ("Sprawdzam niezaksięgowaną sprzedaż…",  check_missing_sales),
    "partial_booking":        ("Sprawdzam spójność KSIEGA↔VAT…",       check_partial_booking),
    "amounts_vs_vat":         ("Sprawdzam kwoty zakupów vs VAT…",       check_amounts_vs_vat),
    "amounts_vs_ksiega":      ("Sprawdzam kwoty zakupów vs KSIEGA…",    check_amounts_vs_ksiega),
    "sales_amounts":          ("Sprawdzam kwoty sprzedaży…",            check_sales_amounts),
    "date_shift_purchases":   ("Sprawdzam daty zakupów…",               check_date_shift_purchases),
    "date_shift_sales":       ("Sprawdzam daty sprzedaży…",             check_date_shift_sales),
    "no_ksef_number":         ("Sprawdzam zakupy bez nr KSeF…",         check_no_ksef_number),
    "ksiega_only":            ("Sprawdzam wpisy tylko w KSIEGA…",       check_ksiega_only),
    "duplicates_vat":         ("Sprawdzam duplikaty zakupów…",          check_duplicates_vat),
    "duplicates_vatsp":       ("Sprawdzam duplikaty sprzedaży…",        check_duplicates_vatsp),
    "corrections_purchases":  ("Sprawdzam korekty zakupów…",            check_corrections_purchases),
    "corrections_sales":      ("Sprawdzam korekty sprzedaży…",          check_corrections_sales),
    "nip_mismatch":           ("Sprawdzam NIP kontrahentów…",           check_nip_mismatch),
    "vat_deadline":           ("Sprawdzam termin odliczenia VAT…",      check_vat_deadline),
    "split_payment":          ("Sprawdzam split payment (MPP)…",        check_split_payment),
    "foreign_currency":       ("Sprawdzam faktury walutowe…",           check_foreign_currency),
    "nip_name_inconsistency": ("Sprawdzam spójność NIP↔Nazwa…",        check_nip_name_inconsistency),
}

def run_all(ksef, ksiega, vat, vatsp, month, year, cfg=None, prog_cb=None, quarter=None):
    def prog(msg):
        if prog_cb: prog_cb(msg)

    cfg = cfg or {}
    enabled = cfg.get("enabled_checks", {})

    prog("Przygotowuję dane…")
    d = prepare(ksef, ksiega, vat, vatsp, month, year, cfg, quarter=quarter)

    results = []
    for cid, (msg, fn) in CHECK_REGISTRY.items():
        if not enabled.get(cid, True): continue
        prog(msg)
        try:
            r = fn(d, cfg)
            if r is not None:
                r["id"] = cid
                results.append(r)
        except Exception as e:
            results.append(warn(f"Błąd sprawdzenia: {cid}", str(e)))

    mn = d["ksef_zak"]["ISSUE_DATE"].min()
    mx = d["ksef_zak"]["ISSUE_DATE"].max()
    summary = {
        "ksef_total":  len(d["ksef_zak"]) + len(d["ksef_spr"]),
        "ksef_zakup":  len(d["ksef_zak"]),
        "ksef_sprz":   len(d["ksef_spr"]),
        "ksiega":      len(d["ksiega_p"]),
        "vatzakupy":   len(d["vat_p"]),
        "vatsprzedaz": len(d["vatsp_p"]) if d["vatsp_p"] is not None else 0,
        "date_from":   mn.strftime("%d.%m.%Y") if pd.notna(mn) else "?",
        "date_to":     mx.strftime("%d.%m.%Y") if pd.notna(mx) else "?",
    }
    errors   = sum(1 for r in results if r["kind"]=="error")
    warnings = sum(1 for r in results if r["kind"]=="warning")
    status   = "error" if errors else ("warning" if warnings else "ok")
    if quarter and year:
        period_label = f"Q{quarter} {year}  ({', '.join(MONTHS_PL[m-1] for m in QUARTER_MONTHS[quarter])})"
    elif month and year:
        period_label = f"{MONTHS_PL[month-1]} {year}"
    else:
        period_label = "Cały zakres"
    return {"status":status, "checks":results, "summary":summary, "period": period_label}
