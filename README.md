# KSeF Checker — weryfikator bazy MDB

## Wymagania (64-bit Python + 64-bit Office)

1. Python 3.8+ (64-bit) — https://www.python.org/downloads/
2. Microsoft Access Database Engine 2016 (64-bit):
   https://www.microsoft.com/en-us/download/details.aspx?id=54920
   → pobierz: AccessDatabaseEngine_X64.exe
3. Zainstaluj zależności:
   pip install pandas pyodbc

## Uruchomienie

   python app.py

## Co sprawdza

1. Niezaksięgowane zakupy z KSeF
2. Niezaksięgowana sprzedaż z KSeF
3. Niezgodności kwotowe (KSeF vs rejestr VAT)
4. Spójność KSIEGA ↔ VATZAKUPY
5. Faktury bez numeru KSeF

## Budowanie .exe

   pip install pyinstaller
   pyinstaller --onefile --windowed --name "KSeF Checker" app.py
