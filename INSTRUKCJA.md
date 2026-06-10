# KSeF Checker — Instrukcja użytkownika

**Wersja 1.5.0**

---

## Spis treści

1. [Opis programu](#1-opis-programu)
2. [Wymagania i instalacja](#2-wymagania-i-instalacja)
3. [Interfejs główny](#3-interfejs-główny)
4. [Przeprowadzenie analizy](#4-przeprowadzenie-analizy)
5. [Opis sprawdzeń](#5-opis-sprawdzeń)
6. [Praca z wynikami](#6-praca-z-wynikami)
7. [Analiza wielu baz jednocześnie](#7-analiza-wielu-baz-jednocześnie-batch)
8. [Historia analiz](#8-historia-analiz)
9. [Eksport do Excel](#9-eksport-do-excel)
10. [Oznaczanie faktur do sprawdzenia](#10-oznaczanie-faktur-do-sprawdzenia)
11. [Ustawienia](#11-ustawienia)
12. [Aktualizacje](#12-aktualizacje)
13. [Najczęstsze pytania](#13-najczęstsze-pytania)

---

## 1. Opis programu

**KSeF Checker** to narzędzie do weryfikacji spójności danych między bazą KSeF a bazą księgową programu **Mała Księgowość** (plik `.mdb`). Program automatycznie wykrywa rozbieżności między fakturami pobranymi z Krajowego Systemu e-Faktur a zapisami w:

- **KSIEGA** — księdze przychodów i rozchodów
- **VATZAKUPY** — rejestrze VAT zakupów
- **VATSPRZEDAZ** — rejestrze VAT sprzedaży

Program nie modyfikuje żadnych danych — działa wyłącznie w trybie odczytu.

---

## 2. Wymagania i instalacja

### Wymagania systemowe

- Windows 10 / 11 (64-bit)
- Microsoft Access Database Engine 2016 (64-bit)

### Instalacja

**Wariant A — z Access Database Engine (dla nowych instalacji)**

Pobierz i uruchom `KSeF_Checker_Installer_z_AccessEngine.exe`. Instalator automatycznie zainstaluje sterownik Microsoft Access jeśli nie jest jeszcze obecny w systemie.

**Wariant B — bez Access Database Engine (jeśli sterownik już jest zainstalowany)**

Pobierz i uruchom `KSeF_Checker_Installer.exe`.

> **Uwaga:** Jeśli masz zainstalowany pakiet Microsoft Office (32-bit), sterownik Access musi być w tej samej wersji bitowej co Office. W razie konfliktu skontaktuj się z administratorem IT.

### Jak sprawdzić czy sterownik jest zainstalowany

1. Otwórz **Panel sterowania → Programy → Programy i funkcje**
2. Szukaj pozycji „Microsoft Access Database Engine 2016"

---

## 3. Interfejs główny

```
┌─────────────────────────────────────────────────────────────────────┐
│  [Logo]  KSeF Checker  v1.5.0      [🌙 Ciemny]  [🕐 Historia]  [⚙] │
├─────────────────────────────────────────────────────────────────────┤
│  [📂 Otwórz MDB]  | Cały | Miesiąc | Kwartał |  ▼Mies ▼Rok  [▶ Sprawdź] [↓ Excel]  │
├──────────────────────────────┬──────────────────────────────────────┤
│  [Wszystkie][Kompletność]... │                                       │
│  ─────────────────────────── │   Panel szczegółów                   │
│  KOMPLETNOŚĆ            ✗ 2  │                                       │
│  ✗ Niezaksięgowane zakupy 5  │   ← Kliknij sprawdzenie              │
│  ✓ Sprzedaż zaksięgowana     │      aby zobaczyć szczegóły          │
│  ...                         │                                       │
└──────────────────────────────┴──────────────────────────────────────┘
```

### Elementy interfejsu

| Element | Opis |
|---------|------|
| **Pasek nagłówka** | Logo, nazwa i wersja programu. Przyciski: przełącznik motywu, historia, ustawienia |
| **Pasek narzędzi** | Wybór pliku MDB, selektor okresu, przyciski Sprawdź i Eksport |
| **Filtry kategorii** | Szybki podgląd wybranej grupy sprawdzeń (2 rzędy przycisków) |
| **Panel lewy** | Lista wszystkich sprawdzeń pogrupowanych kategoriami z kolorowymi kartami |
| **Panel prawy** | Szczegóły wybranego sprawdzenia — tabela z listą nieprawidłowości |

### Motywy

Kliknij przycisk **☀️ Jasny** / **🌙 Ciemny** w prawym górnym rogu, aby przełączyć między ciemnym a jasnym motywem. Wybór jest zapamiętywany.

---

## 4. Przeprowadzenie analizy

### Krok 1 — Otwórz plik bazy danych

Kliknij przycisk **📂 Otwórz plik MDB** i wskaż plik bazy danych programu Mała Księgowość (rozszerzenie `.mdb`).

### Krok 2 — Wybierz okres analizy

Program oferuje trzy tryby analizy:

| Tryb | Kiedy używać |
|------|-------------|
| **Cały** | Sprawdzenie całej bazy — wszystkich dostępnych danych |
| **Miesiąc** | Analiza konkretnego miesiąca (np. Maj 2024) — najczęstszy tryb |
| **Kwartał** | Analiza kwartalnych deklaracji VAT (Q1–Q4) |

Wybierz tryb klikając odpowiedni przycisk, następnie ustaw miesiąc/kwartał i rok.

### Krok 3 — Uruchom analizę

Kliknij **▶ Sprawdź**. Program:
1. Łączy się z bazą MDB
2. Wczytuje tabele KSEF_DOCUMENT, KSIEGA, VATZAKUPY, VATSPRZEDAZ
3. Przeprowadza 19 sprawdzeń
4. Wyświetla wyniki na liście po lewej

Czas analizy: zazwyczaj 2–10 sekund w zależności od rozmiaru bazy.

### Krok 4 — Przeglądaj wyniki

- **Karty zielone (✓)** — brak nieprawidłowości
- **Karty żółte (⚠)** — ostrzeżenia wymagające weryfikacji
- **Karty czerwone (✗)** — błędy wymagające korekty

Kliknij kartę, aby zobaczyć szczegóły w panelu po prawej.

---

## 5. Opis sprawdzeń

Sprawdzenia są pogrupowane w 6 kategorii.

---

### 📋 Kompletność

#### Niezaksięgowane zakupy z KSeF
Wykrywa faktury zakupowe pobrane z KSeF, które nie mają żadnego wpisu ani w KSIEGA, ani w VATZAKUPY.

**Dlaczego to błąd?** Faktura z KSeF, której nie ma w księgach, nie pomniejsza podatku VAT ani kosztów.

**Co zrobić?** Zaksięgować fakturę w programie Mała Księgowość.

---

#### Niezaksięgowana sprzedaż z KSeF
Wykrywa faktury sprzedażowe z KSeF bez wpisu w KSIEGA lub VATSPRZEDAZ.

**Co zrobić?** Uzupełnić księgowanie sprzedaży.

---

#### Niespójność KSIEGA ↔ VATZAKUPY
Wykrywa faktury, które są w księdze ale nie ma ich w rejestrze VAT zakupów (lub odwrotnie).

**Dlaczego to błąd?** Faktura powinna być jednocześnie w obu miejscach — brak w jednym = niekompletne zaksięgowanie.

---

### 💰 Kwoty

#### Niezgodności kwotowe — KSeF vs VATZAKUPY
Porównuje kwoty netto, VAT i brutto między dokumentem KSeF a wpisem w rejestrze VAT zakupów.

**Uwaga:** Program automatycznie obsługuje faktury z 50% odliczeniem (ZAKUP50) i faktury zwolnione z VAT.

**Kolumny w wynikach:**
- `Netto (KSeF)` / `Netto (VAT rej.)` — kwota netto z obu źródeł
- `Δ Netto` / `Δ VAT` / `Δ Brutto` — różnica (0,00 = zgodne)
- `Rodzaj błędu` — które pole się różni

---

#### Niezgodności kwotowe — KSeF vs KSIEGA
Porównuje kwotę netto z KSeF z sumą kosztów w księdze. Uwzględnia kolumnę `% kosztu` (np. 75% dla samochodu).

---

#### Niezgodności kwotowe sprzedaży — KSeF vs VATSPRZEDAZ
Porównuje kwoty faktur sprzedażowych z KSeF z rejestrem VAT sprzedaży.

---

### 📅 Daty

#### Zakupy ujęte poza dopuszczalnym oknem (VATZAKUPY)
Sprawdza, czy data ujęcia faktury zakupowej w rejestrze VAT mieści się w **tym samym lub 3 kolejnych miesiącach** od daty wystawienia (art. 86 ust. 11 ustawy o VAT).

**Uwaga:** Ujęcie w M+1, M+2, M+3 jest w pełni legalne i **nie jest flagowane** jako błąd. Flagowane są tylko ujęcia **wstecz** (przed miesiącem wystawienia) lub **po upływie 3 miesięcy**.

---

#### Sprzedaż w złym miesiącu (VATSPRZEDAZ)
Sprawdza, czy faktury sprzedażowe są ujęte w rejestrze VAT w tym samym miesiącu, co data sprzedaży/wystawienia.

---

### 🔍 Jakość

#### Zakupy bez numeru KSeF
Wyświetla faktury w rejestrze VAT zakupów, które nie mają przypisanego numeru KSeF. Typowo są to:
- Faktury ręczne (papierowe)
- Faktury zagraniczne (spoza systemu KSeF)
- Dokumenty wewnętrzne (np. noty)

Sprawdzenie staje się ostrzeżeniem, gdy odsetek takich faktur przekroczy próg ustawiony w Ustawieniach (domyślnie 15%).

---

#### Wpisy tylko w KSIEGA (ZUS, opłaty, wynagrodzenia)
Pokazuje wydatki w księdze, które nie mają odpowiednika w rejestrze VAT — np. składki ZUS, opłaty bankowe, wynagrodzenia, amortyzacja. To jest **normalny** rodzaj wydatku, więc sprawdzenie zwraca ostrzeżenie (nie błąd), by ułatwić weryfikację kompletności.

---

#### Duplikaty w VATZAKUPY
Wykrywa faktury zakupowe, których numer KSeF występuje w rejestrze VAT więcej niż raz. Duplikat zawyża odliczony VAT i powoduje błąd w pliku JPK_VAT.

---

#### Duplikaty w VATSPRZEDAZ
Jak wyżej, dla rejestru VAT sprzedaży.

---

### ✂️ Korekty

#### Niezaksięgowane korekty zakupów
Wykrywa faktury korygujące (ujemne) z KSeF, które nie zostały zaksięgowane. Niezaksięgowana korekta zawyża odliczony VAT i koszty.

---

#### Niezaksięgowane korekty sprzedaży
Analogicznie dla faktur korygujących sprzedaż.

---

### ⚖️ Compliance

#### Błędny NIP kontrahenta
Porównuje NIP sprzedawcy w dokumencie KSeF z NIP wpisanym w rejestrze VAT zakupów. Niezgodny NIP powoduje odrzucenie pliku JPK przez urząd skarbowy.

---

#### Przekroczony termin odliczenia VAT (>3 miesiące)
Wykrywa faktury, gdzie czas między datą wystawienia a datą ujęcia w rejestrze VAT przekracza **3 miesiące kalendarzowe** (art. 86 ust. 11 ustawy o VAT). Po upływie terminu prawo do odliczenia VAT wygasa lub wymaga korekty deklaracji.

Wynik zawiera kolumnę **Miesięcy po terminie** informującą o skali przekroczenia.

---

#### Split payment (MPP) — faktury ≥ 15 000 zł
Wskazuje faktury zakupowe o wartości brutto ≥ 15 000 zł bez oznaczenia MPP w rejestrze VAT.

> **Ważne:** MPP jest obowiązkowy wyłącznie dla towarów i usług z **Załącznika 15** do ustawy o VAT. Program nie ma dostępu do kodów PKWiU, więc nie może samodzielnie stwierdzić obowiązku — wynik to **ostrzeżenie** do weryfikacji, nie jednoznaczny błąd.

---

#### Faktury walutowe (nie-PLN)
Informuje o fakturach wystawionych w walutach obcych, które wymagają przeliczenia na PLN według kursu NBP z dnia poprzedzającego wystawienie (art. 31a ustawy o VAT).

---

#### Ten sam NIP, różne nazwy firmy
Wykrywa kontrahentów, którym przypisano ten sam NIP pod różnymi nazwami w rejestrze VAT — możliwe literówki, zmiany nazwy firmy lub błędy przy wprowadzaniu.

---

## 6. Praca z wynikami

### Filtry kategorii

Na górze lewego panelu znajdują się przyciski filtrów:

```
[ Wszystkie ][ Kompletność ][ Kwoty ][ Daty ]
[ Jakość ][ Korekty ][ Compliance ]
```

Kliknięcie kategorii pokazuje tylko jej sprawdzenia i automatycznie zaznacza pierwszy błąd/ostrzeżenie z tej grupy.

---

### Sortowanie tabeli

W panelu szczegółów (prawa strona):
- **Kliknij nagłówek kolumny** — sortuje rosnąco (↑), ponowne kliknięcie malejąco (↓)
- **Przyciski „Sortuj:"** obok licznika wierszy — szybki dostęp do sortowania po dacie lub kwocie

---

### Popup szczegółów faktury

**Dwuklik na wierszu** otwiera okno ze szczegółowym porównaniem danych z trzech źródeł:

```
┌─────────────────────────────────────────────────────┐
│  FV/2024/001  ·  15.03.2024                     [✕] │
│  ABC Sp. z o.o.   NIP: 1234567890                   │
├──────────────────────────────────────────────────────┤
│  ┌──────────┐        ┌───────────────┐              │
│  │  KSeF   │  ⟷    │  Rejestr VAT  │              │
│  │         │  Δ Brutto:  50.00      │              │
│  │  Netto  │  Δ Netto:   40.65     │              │
│  │ 1 230,00│  Δ VAT:      9.35     │              │
│  │  VAT    │        │  Netto        │              │
│  │   282,90│        │    189.35     │              │
│  │  Brutto │        │  Brutto       │              │
│  │ 1 512,90│        │  1 462.90     │              │
│  └──────────┘        └───────────────┘              │
└──────────────────────────────────────────────────────┘
```

Wartości Δ zaznaczone na **czerwono** oznaczają rozbieżność. Wartość `0,00` oznacza zgodność.

---

## 7. Analiza wielu baz jednocześnie (Batch)

Zakładka **Wiele baz (batch)** pozwala sprawdzić kilka firm jednocześnie.

### Jak używać

1. Kliknij **＋ Dodaj bazy MDB** — wybierz wiele plików naraz (Ctrl+klik)
2. Ustaw wspólny okres analizy
3. Kliknij **▶ Sprawdź wszystkie**
4. Wyniki pojawią się w tabeli z podsumowaniem per firma

### Tabela wyników zawiera

| Kolumna | Opis |
|---------|------|
| Baza | Nazwa pliku MDB |
| Status | ✓ OK / ⚠ ostrzeżenia / ✗ błędy |
| Błędy | Liczba błędów |
| Ostrzeżenia | Liczba ostrzeżeń |
| KSeF | Łączna liczba dokumentów KSeF |
| Zakupy / Sprzedaż | Liczba faktur zakupowych/sprzedażowych |
| Okres | Analizowany okres |

### Eksport zbiorczy

Po zakończeniu analizy kliknij **↓ Excel zbiorczy** — plik zawiera:
- Arkusz **Podsumowanie zbiorcze** — jedna linia per firma
- Arkusz **Wszystkie błędy** — pełna lista problemów
- Arkusz **✉ Do sprawdzenia** — checklist do przekazania klientom

### Otwarcie firmy w trybie szczegółowym

**Dwuklik na wierszu** w tabeli zbiorczej otwiera tę bazę w zakładce **Pojedyncza baza** i automatycznie uruchamia analizę.

---

## 8. Historia analiz

Kliknij **🕐 Historia** w nagłówku programu, aby zobaczyć poprzednie analizy.

- Wyniki są zapisywane automatycznie po każdej analizie
- Przechowywanych jest do **40** ostatnich wpisów
- Dla tej samej bazy i okresu poprzedni wynik jest **nadpisywany**

### Wczytywanie z historii

Kliknij **Otwórz** przy wybranym wpisie — program wczyta zapisane wyniki **bez ponownej analizy** bazy. Przydatne gdy baza MDB jest niedostępna (np. klient zdalny).

---

## 9. Eksport do Excel

Kliknij **↓ Excel** w pasku narzędzi po zakończeniu analizy.

### Zawartość pliku

**Arkusz „Raport"** — tabela problemów z kolumnami:
- Typ (BŁĄD / OSTRZEŻENIE)
- Sprawdzenie
- Liczba rekordów
- Szczegóły
- Wyjaśnienie prawne

**Arkusz „Szczegóły"** — wszystkie wiersze z nieprawidłowościami, pogrupowane według sprawdzenia. Zawiera pełne dane faktur (numery, daty, kwoty, kontrahenci).

Nazwa pliku jest generowana automatycznie: `KSeF_NazwaFirmy_Maj_2024.xlsx`

---

## 10. Oznaczanie faktur do sprawdzenia

Podczas przeglądania wyników możesz oznaczać faktury, które wymagają poprawki w programie księgowym.

### Jak oznaczać

- **Prawy klik** na wierszu → wiersz zmienia kolor na **zielony** (oznaczono)
- **Prawy klik ponownie** → odznaczenie
- **Przycisk „Odznacz wszystkie"** — pojawia się gdy coś jest zaznaczone

### Licznik oznaczeń

Nad tabelą widoczny jest licznik `✓ N zaznaczonych` aktualizowany na bieżąco.

### Trwałość oznaczeń

Oznaczenia są zapisywane w pliku `marks.json` w folderze programu. Są przypisane do konkretnego pliku MDB i konkretnego sprawdzenia — przeżywają zamknięcie i ponowne otwarcie programu.

**Typowy przepływ pracy:**
1. Uruchom analizę dla miesiąca
2. Otwórz program Mała Księgowość obok
3. W KSeF Checker oznaczaj faktury prawym klikiem w miarę ich poprawiania w Mała Księgowość
4. Po zakończeniu uruchom analizę ponownie — liczba błędów powinna spaść do zera

---

## 11. Ustawienia

Kliknij **⚙ Ustawienia** w prawym górnym rogu.

### Zakładka „Sprawdzenia"

Włącz lub wyłącz poszczególne sprawdzenia. Użyj przycisków:
- **Zaznacz wszystkie** — włącz wszystkie
- **Odznacz wszystkie** — wyłącz wszystkie
- **Przywróć domyślne** — wróć do ustawień fabrycznych

### Zakładka „Parametry"

| Parametr | Domyślnie | Opis |
|----------|-----------|------|
| Tolerancja różnic kwotowych | 0,05 zł | Różnice poniżej tej wartości są ignorowane (zaokrąglenia) |
| Próg ostrzeżenia „brak KSeF" | 15% | Przy jakim odsetku faktur bez numeru KSeF wyświetlić ostrzeżenie |
| Dni bufora dla „cały zakres" | 3 dni | Ile ostatnich dni ignorować jako „za świeże do zaksięgowania" |

### Sprawdzanie aktualizacji

W oknie Ustawień kliknij **🔔 Sprawdź aktualizacje**, aby ręcznie sprawdzić dostępność nowej wersji.

---

## 12. Aktualizacje

Program **automatycznie sprawdza dostępność aktualizacji** przy każdym uruchomieniu (raz dziennie).

Gdy dostępna jest nowa wersja, w górnej części okna pojawia się baner:

```
🔔 Dostępna nowa wersja v1.x.x  —  [  Aktualizuj  ]  [✕]
```

### Proces aktualizacji

1. Kliknij **Aktualizuj**
2. Postęp pobierania jest widoczny na pasku
3. Może pojawić się **okno kontroli konta użytkownika (UAC)** — kliknij **Tak**
4. Po instalacji kliknij **🔄 Uruchom ponownie**
5. Program automatycznie uruchamia nową wersję

> Program nie zamyka się podczas pobierania — można pracować do momentu kliknięcia „Uruchom ponownie".

---

## 13. Najczęstsze pytania

**Q: Program wyświetla błąd „Brak sterownika Microsoft Access"**

A: Zainstaluj sterownik ze strony Microsoft lub użyj instalatora z sufiksem `_z_AccessEngine`. Jeśli masz 32-bitowy Microsoft Office, musisz użyć 32-bitowej wersji sterownika — skontaktuj się z administratorem IT.

---

**Q: Faktura jest w KSeF ale program pokazuje ją jako niezaksięgowaną, choć ją zaksięgowałem**

A: Sprawdź czy numer KSeF w Mała Księgowość zgadza się dokładnie z numerem w KSeF (bez dodatkowych spacji). Możliwa przyczyna to literówka lub brak numeru KSeF przy ręcznym wprowadzaniu faktury.

---

**Q: Program pokazuje błędy „niezaksięgowane korekty" dla starych faktur sprzed roku**

A: Sprawdzenie korekt działa w zakresie wybranego okresu. Jeśli stare korekty nie powinny być księgowane (np. sporne faktury), możesz wyłączyć to sprawdzenie w Ustawieniach.

---

**Q: Część faktur ma status „zły miesiąc" choć je zaksięgowałem w kolejnym miesiącu**

A: Ujęcie faktury zakupowej w M+1, M+2 lub M+3 jest **legalne** (art. 86 ust. 11 ustawy o VAT) i program tego **nie flaguje**. Jeśli widzisz ostrzeżenie, faktura jest ujęta albo wstecz (przed miesiącem wystawienia), albo po upływie 3 miesięcy.

---

**Q: Co znaczy „Δ Brutto = 50,00 zł"?**

A: Kwota brutto w KSeF różni się od kwoty w rejestrze VAT o 50,00 zł. Może to oznaczać: błędną wartość przy ręcznym wpisie, zaokrąglenie lub zaksięgowanie innej faktury pod tym numerem KSeF.

---

**Q: Analiza jest bardzo wolna**

A: Przy dużych bazach (kilka tysięcy faktur) analiza może trwać do 30 sekund. Dla trybu „Cały zakres" na dużej bazie czas może być dłuższy — wybierz konkretny miesiąc dla szybszego działania.

---

**Q: Gdzie są zapisywane ustawienia i historia?**

A: W folderze instalacji programu (domyślnie `C:\Program Files\KSeF Checker\`):
- `settings.json` — ustawienia programu
- `history.json` — historia analiz (maks. 40 wpisów)
- `marks.json` — oznaczenia faktur „do sprawdzenia"

---

*KSeF Checker | github.com/NikooFPV/ksef-checker-pl*
