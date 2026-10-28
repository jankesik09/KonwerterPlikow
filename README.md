# Konwerter plików — Lab 2 i Lab 3

Autor: Maciej Jankowski

## Cel projektu
Aplikacja desktopowa do konwersji plików CSV, JSON, TXT, DOCX i PDF.
Działa w okienku Tkinter oraz w terminalu.
Logika konwersji jest oddzielona od interfejsu.

## Wymagania
- Python 3.13 z Tkinter.
- Windows i zainstalowany desktopowy Microsoft Word do DOCX ↔ PDF.
- Biblioteki python-docx oraz pywin32.

Instalacja bibliotek:

```powershell
py -m pip install -r requirements.txt
```

LibreOffice nie jest wymagany.

## Uruchomienie okienka

```powershell
py main.py
```

Obsługa:
1. Kliknij „Wybierz plik…”.
2. Wybierz plik wejściowy.
3. Wybierz katalog zapisu.
4. Wybierz format docelowy.
5. Kliknij „Konwertuj”.

Lista formatów docelowych zależy od rozszerzenia wejścia.
Wynik otrzymuje nazwę pliku wejściowego z nowym rozszerzeniem.
Przed nadpisaniem istniejącego pliku program pyta o zgodę.
Konwersja odbywa się w osobnym wątku, aby okienko pozostawało responsywne.

## Uruchomienie w terminalu

```powershell
py main.py dane.csv wynik.json
py main.py wynik.json wynik.csv
py main.py tekst.txt dokument.docx
py main.py dokument.docx odczyt.txt
py main.py dokument.docx dokument.pdf
py main.py dokument.pdf dokument_odtworzony.docx
```

Jeżeli plik wynikowy już istnieje, dodaj --nadpisz:

```powershell
py main.py dane.csv wynik.json --nadpisz
```

## Obsługiwane konwersje

| Wejście | Wyjście | Narzędzie |
|---|---|---|
| CSV | JSON | csv, json |
| JSON | CSV | json, csv |
| TXT | DOCX | python-docx |
| DOCX | TXT | python-docx |
| DOCX | PDF | Microsoft Word przez pywin32 |
| PDF | DOCX | Microsoft Word przez pywin32 |

## Zasady danych CSV i JSON
- Tekstowe wejście jest odczytywane w UTF-8, również z BOM.
- Wynikowy JSON jest zapisywany w UTF-8.
- Wynikowy CSV jest zapisywany w UTF-8 z BOM.
- Separator wejściowego CSV jest rozpoznawany spośród przecinka,
  średnika i tabulatora. Przy nietypowych danych rozpoznanie
  może być niejednoznaczne.
- Wynikowy CSV używa średnika jako separatora kolumn.
- Pierwszy wiersz CSV zawiera unikalne, niepuste nagłówki.
- CSV musi zawierać przynajmniej jeden rekord.
- JSON musi być niepustą listą niepustych obiektów
  o identycznym zestawie kluczy.
- Zagnieżdżone obiekty i listy nie są obsługiwane.
- Kolejność kolumn pochodzi z CSV lub pierwszego obiektu JSON.
- Wartości CSV są zapisywane w JSON jako tekst.
- JSON null jest zapisywany jako pusta komórka CSV.
- CSV nie zachowuje typów danych JSON ani różnicy między null
  i pustym tekstem.

## Zasady i ograniczenia dokumentów
- Wejściowy TXT musi mieć kodowanie UTF-8, opcjonalnie z BOM.
- Wynikowy TXT jest zapisywany w UTF-8.
- TXT → DOCX: każda linia tekstu staje się osobnym akapitem.
- DOCX → TXT: odczytywane są akapity głównej treści dokumentu.
  Obrazy, tabele, nagłówki i stopki nie są przenoszone.
- DOCX → PDF: eksport wykonuje Microsoft Word.
- PDF → DOCX: Word przekształca PDF w edytowalny dokument.
  Układ stron, tabele i formatowanie mogą się zmienić.
- PDF będący skanem nie gwarantuje uzyskania edytowalnego tekstu.
- Dokumenty chronione hasłem lub wymagające interakcji
  mogą nie zostać przekonwertowane.

## Narzędzie zewnętrzne
Microsoft Word jest uruchamiany automatycznie przez pywin32.
Skrypt word_pdf.py działa w osobnym procesie uruchamianym
przez subprocess.run().

Program:
- przekazuje argumenty jako listę, bez shell=True;
- sprawdza kod zakończenia procesu;
- ogranicza oczekiwanie do 90 sekund;
- zgłasza błąd, gdy Word nie może zostać uruchomiony;
- sprawdza istnienie i poprawność struktury pliku wynikowego;
- próbuje zamknąć dokument i własną instancję Worda po operacji.

Limit czasu kończy proces pomocniczy. Przy zawieszeniu automatyzacji
instancja Worda może pozostać uruchomiona.

## Walidacja i zapis
- Sprawdzane są istnienie wejścia i katalogu docelowego.
- Niedozwolone pary formatów są odrzucane.
- Plik wynikowy musi różnić się od wejściowego.
- Błędny JSON daje kontrolowany komunikat.
- Wynik konwersji powstaje najpierw w katalogu tymczasowym.
- Przy błędzie samej konwersji istniejący wynik pozostaje nienaruszony.
- GUI wymaga zgody na nadpisanie.
- Terminal wymaga opcji --nadpisz.

## Podział kodu
- main.py — okienko, wątek roboczy i obsługa terminala.
- konwertery.py — rejestr konwersji, walidacja i zapis.
- word_pdf.py — sterowanie Wordem dla DOCX ↔ PDF.
- requirements.txt — biblioteki wymagane przez projekt.
- dane.csv — przykładowe dane strukturalne.
- bledny.json — celowo niepoprawny JSON.
- tekst.txt — przykładowy tekst do konwersji.
- .gitignore — pliki pomijane przez Git.

## Testy ręczne
Potwierdzone podczas pracy nad projektem:
- CSV → JSON: działa.
- JSON → CSV: działa.
- TXT → DOCX: działa.
- DOCX → TXT: działa.
- DOCX → PDF: działa.
- PDF → DOCX: działa.
- Wybór pliku, katalogu i formatu w okienku: działa.
- Błędny JSON: kontrolowany komunikat błędu.

Przypadki do dodatkowego sprawdzenia:
- odmowa nadpisania istniejącego pliku;
- uszkodzony DOCX lub PDF;
- niedostępny Microsoft Word;
- przekroczenie limitu czasu.

## Dalszy rozwój
- Rozszerzenie obsługi formatów ODT.
- Automatyczne testy i rejestrowanie błędów.

## Historia pracy
- Lab 2: konwersje CSV ↔ JSON, GUI i lokalne repozytorium Git.
- Lab 3: konwersje TXT ↔ DOCX oraz DOCX ↔ PDF przez Microsoft Word.

Szczegółowa historia zmian jest przechowywana w repozytorium Git.

## Wykorzystane narzędzia
Python, Tkinter/ttk, csv, json, pathlib, argparse, subprocess,
tempfile, concurrent.futures, python-docx, pywin32 i Microsoft Word.

Kod przygotowany przy pomocy ChatGPT (OpenAI).

## Źródła
- https://docs.python.org/3/library/csv.html
- https://docs.python.org/3/library/json.html
- https://docs.python.org/3/library/tkinter.html
- https://docs.python.org/3/library/subprocess.html
- https://python-docx.readthedocs.io/
- https://github.com/mhammond/pywin32
- https://learn.microsoft.com/office/vba/api/word.document.exportasfixedformat
- https://learn.microsoft.com/office/vba/api/word.saveas2