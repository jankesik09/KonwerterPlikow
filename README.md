# Konwerter plików — Lab 2

Autor: Maciej Jankowski

## Cel projektu
Aplikacja konwertuje CSV na JSON oraz JSON na CSV.
Działa w terminalu i ma dodatkowe okienko w Tkinter.

## Wymagania
Python 3.13 z Tkinter.
Brak dodatkowych pakietów do instalacji.

## Uruchomienie okienka
py main.py

## Uruchomienie w terminalu
py main.py dane.csv wynik.json
py main.py wynik.json wynik.csv

Jeżeli wynik już istnieje:
py main.py dane.csv wynik.json --nadpisz

## Obsługiwane konwersje
- CSV → JSON — działa.
- JSON → CSV — działa.

## Plan rozbudowy
- TXT → DOCX.
- DOCX → TXT.
- DOCX → PDF.
- ODT → PDF.

## Zasady danych
- Pliki wejściowe są odczytywane w UTF-8, również z BOM.
- Wynikowy JSON jest zapisywany w UTF-8.
- Wynikowy CSV jest zapisywany w UTF-8 z BOM, aby Excel poprawnie rozpoznawał polskie znaki.
- Odczyt CSV obsługuje przecinek, średnik i tabulator.
- Wynikowy CSV używa średnika jako separatora kolumn.
- Pierwszy wiersz CSV zawiera unikalne, niepuste nagłówki.
- CSV musi zawierać przynajmniej jeden rekord.
- JSON musi być niepustą listą obiektów o takich samych kluczach.
- Zagnieżdżone obiekty i listy nie są obsługiwane.
- Kolejność kolumn pochodzi z CSV lub pierwszego obiektu JSON.
- Wartości CSV są zapisywane w JSON jako tekst.
- JSON null jest zapisywany jako pusta komórka CSV.
- CSV nie zachowuje typów danych JSON.

## Podział kodu
- main.py — okienko i obsługa terminala.
- konwertery.py — konwersje i walidacja danych.

## Testy ręczne
- CSV → JSON: działa.
- JSON → CSV: działa.
- Wybór pliku i katalogu w okienku: działa.
- Błędny JSON: kontrolowany komunikat błędu.

## Wykorzystane narzędzia
Python, Tkinter, csv, json, pathlib, argparse.
Kod przygotowany przy pomocy ChatGPT (OpenAI).

## Źródła
https://docs.python.org/3/library/csv.html
https://docs.python.org/3/library/json.html
https://docs.python.org/3/library/tkinter.html