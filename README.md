# Konwerter plików — laboratoria 2–5

Autor: Maciej Jankowski

## Cel projektu

Aplikacja desktopowa do konwersji plików CSV, JSON, TXT, DOCX i PDF.
Działa w okienku Tkinter oraz w terminalu.
Logika konwersji jest oddzielona od interfejsu.

## Wymagania

- Python 3.13 z Tkinter.
- Biblioteki python-docx oraz pywin32.
- Windows i zainstalowany desktopowy Microsoft Word do DOCX ↔ PDF.

Instalacja bibliotek:

```powershell
py -m pip install -r requirements.txt
```

## Uruchomienie okienka

W terminalu otwartym w katalogu projektu wykonaj:

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

Przykładowe polecenia:

```powershell
py main.py dane.csv wynik.json
py main.py wynik.json wynik.csv
py main.py tekst.txt dokument.docx
py main.py dokument.docx odczyt.txt
py main.py dokument.docx dokument.pdf
py main.py dokument.pdf dokument_odtworzony.docx
```

Jeżeli plik wynikowy już istnieje, dodaj opcję --nadpisz:

```powershell
py main.py dane.csv wynik.json --nadpisz
```

Ścieżki zawierające spacje należy umieścić w cudzysłowach:

```powershell
py main.py "moj dokument.docx" "moj dokument.pdf"
```

## Obsługiwane konwersje

| Wejście | Wyjście | Narzędzie | Ograniczenia |
|---|---|---|---|
| CSV | JSON | csv, json | Wartości komórek stają się tekstem |
| JSON | CSV | json, csv | Płaska lista obiektów o tych samych kluczach; utrata typów danych |
| TXT | DOCX | python-docx | Każda linia staje się akapitem |
| DOCX | TXT | python-docx | Tylko zwykłe akapity głównej treści |
| DOCX | PDF | Microsoft Word przez pywin32 | Wymaga desktopowego Worda na Windows |
| PDF | DOCX | Microsoft Word przez pywin32 | Możliwe zmiany układu i formatowania; brak gwarancji OCR |

## Zasady danych CSV i JSON

- Wejście CSV i JSON jest odczytywane w UTF-8, również z BOM.
- Wynikowy JSON jest zapisywany w UTF-8.
- Wynikowy CSV jest zapisywany w UTF-8 z BOM.
- Obsługiwane separatory wejściowego CSV to przecinek, średnik i tabulator.
- Separator jest wybierany na podstawie największej liczby pól
  w nagłówku odczytanym dla każdego z tych separatorów.
- Przy remisie pierwszeństwo ma przecinek, następnie średnik i tabulator.
- Nietypowe nagłówki zawierające różne separatory mogą być niejednoznaczne.
- Wynikowy CSV używa średnika jako separatora kolumn.
- Pierwszy rekord CSV zawiera unikalne, niepuste nagłówki.
- Każdy niepusty rekord musi mieć tyle pól co nagłówek.
- CSV musi zawierać przynajmniej jeden rekord danych.
- JSON musi być niepustą listą niepustych obiektów
  o identycznym zestawie kluczy.
- Zagnieżdżone obiekty i listy nie są obsługiwane.
- Kolejność kolumn pochodzi z CSV lub pierwszego obiektu JSON.
- Wartości CSV są zapisywane w JSON jako tekst.
- JSON null jest zapisywany jako pusta komórka CSV.
- CSV nie zachowuje typów danych JSON ani różnicy między null i pustym tekstem.

Przykładowa akceptowana struktura JSON:

```json
[
  {
    "imie": "Łukasz",
    "miasto": "Łódź",
    "opis": ""
  },
  {
    "imie": "Anna",
    "miasto": "Kraków",
    "opis": "Przykładowy rekord"
  }
]
```

## Zasady i ograniczenia dokumentów

- Wejściowy TXT musi mieć kodowanie UTF-8, opcjonalnie z BOM.
- Wynikowy TXT jest zapisywany w UTF-8.
- TXT → DOCX: każda linia tekstu staje się osobnym akapitem.
- DOCX → TXT: odczytywane są akapity głównej treści dokumentu.
  Obrazy, tabele, nagłówki i stopki nie są przenoszone.
- DOCX → PDF: eksport wykonuje Microsoft Word.
- PDF → DOCX: Word przekształca PDF w dokument DOCX.
  Układ stron, tabele i formatowanie mogą się zmienić.
- PDF będący skanem nie gwarantuje uzyskania edytowalnego tekstu.
- Dokumenty chronione hasłem lub wymagające interakcji
  mogą nie zostać przekonwertowane.

## Narzędzie zewnętrzne

Microsoft Word jest uruchamiany automatycznie przez pywin32.
Skrypt word_pdf.py działa w osobnym procesie uruchamianym
przez subprocess.run().

Program:

- przekazuje argumenty jako listę i używa shell=False;
- sprawdza kod zakończenia procesu;
- ogranicza oczekiwanie do 90 sekund;
- zgłasza błąd, gdy Word nie może zostać uruchomiony;
- sprawdza, czy wynik istnieje i nie jest pusty;
- sprawdza nagłówek wynikowego PDF;
- sprawdza, czy wynikowy DOCX można odczytać przez python-docx;
- próbuje zamknąć dokument i własną instancję Worda po operacji.

Przekroczenie limitu czasu kończy proces pomocniczy.
Przy zawieszeniu automatyzacji instancja Worda może pozostać uruchomiona.

## Walidacja i zapis

- Sprawdzane są istnienie wejścia i katalogu docelowego.
- Niedozwolone pary formatów są odrzucane.
- Plik wynikowy musi różnić się od wejściowego.
- Błędny JSON daje kontrolowany komunikat.
- Nieprawidłowa liczba kolumn CSV daje kontrolowany komunikat.
- Brak wymaganej biblioteki lub niedostępny Word daje komunikat błędu.
- Błędy zapisu są przekazywane do interfejsu lub terminala.
- Wynik konwersji powstaje najpierw w katalogu tymczasowym.
- Błąd samej konwersji nie niszczy istniejącego wyniku.
- GUI wymaga zgody na nadpisanie.
- Terminal wymaga opcji --nadpisz.

## Logowanie

Program zapisuje operacje i błędy do konwerter.log
w katalogu programu.

Log zawiera:

- datę i godzinę;
- poziom komunikatu;
- ścieżki wejścia i wyjścia;
- informację o powodzeniu;
- czas poprawnie zakończonej konwersji;
- szczegóły wyjątku w przypadku błędu.

Plik logu jest lokalny i jest pomijany przez Git.
Brak możliwości zapisania logu nie powinien przerywać samej konwersji.

## Podział projektu

| Plik | Zastosowanie |
|---|---|
| main.py | Okienko, wątek roboczy i obsługa terminala |
| konwertery.py | Rejestr konwersji, walidacja, zapis i logowanie |
| word_pdf.py | Sterowanie Wordem dla DOCX ↔ PDF |
| test_konwertery.py | Testy automatyczne i generowanie raportu |
| requirements.txt | Biblioteki wymagane przez projekt |
| README.md | Dokumentacja |
| dane.csv | Przykładowe dane tabelaryczne |
| bledny.json | Celowo niepoprawny JSON |
| tekst.txt | Przykładowy tekst do konwersji |
| RAPORT_TESTOW_AUTOMATYCZNYCH.txt | Wynik ostatniego uruchomienia testów |
| .gitignore | Pliki pomijane przez Git |

## Przykładowe dane i oczekiwane wyniki

- dane.csv → JSON: zachowane nazwy i kolejność kolumn,
  polskie znaki oraz wartości komórek.
- tekst.txt → DOCX: zachowany tekst, polskie znaki i podział na linie
  odwzorowany jako akapity.
- dokument.docx → PDF: otwieralny PDF zawierający treść dokumentu.
  Dokument można przygotować przez konwersję tekst.txt.
- bledny.json → CSV: kontrolowany błąd, brak nowego pliku wynikowego.

## Testy automatyczne

Uruchomienie:

```powershell
py test_konwertery.py
```

Zestaw zawiera 20 testów obejmujących:

- CSV → JSON i JSON → CSV;
- polskie znaki, puste wartości i kolejność kolumn;
- separator CSV oraz BOM;
- zachowanie treści po CSV → JSON → CSV;
- błędny JSON i niepoprawną strukturę danych;
- powtórzone nagłówki i nieprawidłową liczbę kolumn;
- brak pliku lub katalogu docelowego;
- nieobsługiwane pary i listę dostępnych formatów;
- blokadę nadpisania i zapis po zgodzie;
- ochronę poprzedniego wyniku przy błędzie konwersji;
- TXT → DOCX → TXT;
- uszkodzony DOCX;
- symulowany błąd procesu Worda;
- symulowane przekroczenie limitu czasu;
- symulowany brak uprawnień do zapisu.

Ostatnie potwierdzone uruchomienie: 20 testów, wynik OK.

Raport jest generowany automatycznie jako
RAPORT_TESTOW_AUTOMATYCZNYCH.txt.

Testy korzystają z katalogów tymczasowych.
Testy błędów procesu i uprawnień wykorzystują symulację.
Nie zastępują rzeczywistych prób DOCX ↔ PDF i testów GUI.

## Testy ręczne

Podczas pracy nad projektem potwierdzono działanie poniższych konwersji
w okienku oraz obsługę błędnego JSON:

| Przypadek | Oczekiwany wynik | Wynik |
|---|---|---|
| CSV → JSON | Zachowane dane, nazwy i kolejność kolumn oraz polskie znaki | Potwierdzono |
| JSON → CSV | Otwieralny CSV ze średnikiem i UTF-8 z BOM | Potwierdzono |
| TXT → DOCX | Zachowany tekst, polskie znaki i akapity | Potwierdzono |
| DOCX → TXT | Odczyt zwykłych akapitów głównej treści | Potwierdzono |
| DOCX → PDF | Otwieralny PDF z treścią dokumentu | Potwierdzono |
| PDF → DOCX | Otwieralny DOCX z treścią tekstowego PDF | Potwierdzono |
| Błędny JSON | Czytelny komunikat błędu bez awarii aplikacji | Potwierdzono |

Dodatkowe próby GUI obejmują odmowę nadpisania, wybór nieobsługiwanego
pliku JPG oraz sprawdzenie wpisu ERROR w konwerter.log po błędnej konwersji.
Testy automatyczne sprawdzają także ochronę przed nadpisaniem i dostępne formaty.

Głównym raportem testów jest RAPORT_TESTOW_AUTOMATYCZNYCH.txt.
Opis prób ręcznych znajduje się bezpośrednio w tym README;
osobny plik raportu ręcznego nie jest wymagany.

## Sprawdzenie w świeżym środowisku

Na komputerze z Windows, Pythonem 3.13 i desktopowym Wordem
wykonaj kolejno:

```powershell
py -3.13 -m venv .venv_test
.\.venv_test\Scripts\python.exe -m pip install -r requirements.txt
.\.venv_test\Scripts\python.exe test_konwertery.py
.\.venv_test\Scripts\python.exe main.py
```

Aktywowanie środowiska nie jest wymagane.

Po uruchomieniu okienka sprawdź również DOCX → PDF i PDF → DOCX.
Po wykonaniu próby dopisz jej rzeczywisty wynik w tej sekcji README.

## Historia pracy

- Lab 2: CSV ↔ JSON, dane przykładowe i lokalne repozytorium Git.
- Lab 3: TXT ↔ DOCX i DOCX ↔ PDF przez Microsoft Word.
- Lab 4: interfejs Tkinter/ttk, dynamiczne formaty,
  potwierdzanie nadpisania i praca w osobnym wątku;
  część funkcji GUI wykonano już we wcześniejszych etapach.
- Lab 5: testy automatyczne, raporty, logowanie
  i poprawa rozpoznawania separatora CSV.

Historia zmian jest przechowywana w lokalnym repozytorium Git.

## Dalszy rozwój

- Obsługa formatów ODT.
- Ręczny wybór separatora CSV przy niejednoznacznych nagłówkach.
- Rozszerzenie odczytu DOCX o tabele.
- Obsługa OCR dla skanów PDF.

## Wykorzystane narzędzia

Python, Tkinter/ttk, csv, json, pathlib, argparse, subprocess,
tempfile, shutil, concurrent.futures, logging, time,
unittest, unittest.mock, python-docx, pywin32 i Microsoft Word.

Kod przygotowany przy pomocy ChatGPT (OpenAI).

## Źródła

- https://docs.python.org/3/library/csv.html
- https://docs.python.org/3/library/json.html
- https://docs.python.org/3/library/tkinter.html
- https://docs.python.org/3/library/subprocess.html
- https://docs.python.org/3/library/logging.html
- https://docs.python.org/3/library/unittest.html
- https://python-docx.readthedocs.io/
- https://github.com/mhammond/pywin32
- https://learn.microsoft.com/office/vba/api/word.document.exportasfixedformat
- https://learn.microsoft.com/office/vba/api/word.saveas2