import csv
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import logging
import time


def csv_na_json(wejscie, wyjscie):
    tekst = wejscie.read_text(encoding="utf-8-sig")

    # Wybieramy separator na podstawie nagłówków.
    # Błędny wiersz danych nie wpływa na wybór separatora.
    separator = ","
    najwiecej_kolumn = 0

    for kandydat in (",", ";", "\t"):
        probny_czytnik = csv.reader(
            io.StringIO(tekst, newline=""),
            delimiter=kandydat,
            strict=True,
        )

        try:
            probne_naglowki = next(probny_czytnik, [])
        except csv.Error:
            continue

        if len(probne_naglowki) > najwiecej_kolumn:
            najwiecej_kolumn = len(probne_naglowki)
            separator = kandydat

    czytnik = csv.reader(
        io.StringIO(tekst, newline=""),
        delimiter=separator,
        strict=True,
    )

    naglowki = next(czytnik, None)

    if not naglowki or any(not nazwa.strip() for nazwa in naglowki):
        raise ValueError("CSV musi mieć niepuste nagłówki.")

    if len(set(naglowki)) != len(naglowki):
        raise ValueError("Nagłówki CSV nie mogą się powtarzać.")

    dane = []

    for wiersz in czytnik:
        if not wiersz:
            continue

        if len(wiersz) != len(naglowki):
            raise ValueError(
                f"Nieprawidłowa liczba kolumn przy linii "
                f"{czytnik.line_num}."
            )

        dane.append(dict(zip(naglowki, wiersz)))

    if not dane:
        raise ValueError("CSV musi zawierać przynajmniej jeden rekord.")

    wynik = json.dumps(dane, ensure_ascii=False, indent=4)
    wyjscie.write_text(wynik, encoding="utf-8")


def json_na_csv(wejscie, wyjscie):
    try:
        dane = json.loads(
            wejscie.read_text(encoding="utf-8-sig")
        )
    except json.JSONDecodeError as blad:
        raise ValueError(
            f"Błędny JSON: wiersz {blad.lineno}, "
            f"kolumna {blad.colno}."
        ) from blad

    if not isinstance(dane, list) or not dane:
        raise ValueError("JSON musi zawierać niepustą listę obiektów.")

    if not isinstance(dane[0], dict) or not dane[0]:
        raise ValueError("Każdy rekord musi być niepustym obiektem.")

    naglowki = list(dane[0].keys())

    if any(not nazwa.strip() for nazwa in naglowki):
        raise ValueError("Nazwy kolumn nie mogą być puste.")

    for numer, rekord in enumerate(dane, start=1):
        if not isinstance(rekord, dict):
            raise ValueError(f"Rekord {numer} nie jest obiektem.")

        if set(rekord.keys()) != set(naglowki):
            raise ValueError(
                f"Rekord {numer} ma inne kolumny niż pierwszy rekord."
            )

        for wartosc in rekord.values():
            if isinstance(wartosc, (dict, list)):
                raise ValueError(
                    "Zagnieżdżone obiekty i listy nie są obsługiwane."
                )

    with wyjscie.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as plik:
        zapis = csv.DictWriter(
            plik,
            fieldnames=naglowki,
            delimiter=";"
        )
        zapis.writeheader()
        zapis.writerows(dane)


def pobierz_document():
    try:
        from docx import Document
    except ImportError as blad:
        raise ValueError(
            "Brakuje biblioteki python-docx. "
            "W terminalu wykonaj: py -m pip install python-docx"
        ) from blad

    return Document


def txt_na_docx(wejscie, wyjscie):
    Document = pobierz_document()

    tekst = wejscie.read_text(encoding="utf-8-sig")
    dokument = Document()

    # Każda linia TXT staje się osobnym akapitem.
    for linia in tekst.split("\n"):
        dokument.add_paragraph(linia)

    dokument.save(str(wyjscie))


def docx_na_txt(wejscie, wyjscie):
    Document = pobierz_document()

    try:
        dokument = Document(str(wejscie))
    except Exception as blad:
        raise ValueError(
            "Nie można odczytać DOCX. "
            "Sprawdź, czy plik otwiera się w Wordzie."
        ) from blad

    # Odczyt zwykłych akapitów głównej treści dokumentu.
    tekst = "\n".join(
        akapit.text for akapit in dokument.paragraphs
    )

    wyjscie.write_text(tekst, encoding="utf-8")


def konwersja_przez_word(wejscie, wyjscie):
    if sys.platform != "win32":
        raise ValueError(
            "Konwersja przez Microsoft Word wymaga Windows."
        )

    skrypt = Path(__file__).resolve().with_name("word_pdf.py")

    if not skrypt.is_file():
        raise ValueError(
            "Brakuje pliku word_pdf.py. "
            "Umieść go obok main.py i konwertery.py."
        )

    polecenie = [
        sys.executable,
        str(skrypt),
        str(wejscie.resolve()),
        str(wyjscie.resolve()),
    ]

    srodowisko = os.environ.copy()
    srodowisko["PYTHONIOENCODING"] = "utf-8"

    try:
        wynik = subprocess.run(
            polecenie,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=srodowisko,
            timeout=90,
            shell=False,
        )
    except subprocess.TimeoutExpired as blad:
        raise ValueError(
            "Word nie zakończył konwersji w ciągu 90 sekund. "
            "Sprawdź, czy nie oczekuje potwierdzenia "
            "lub aktywacji. Możesz też spróbować "
            "otworzyć plik ręcznie w Wordzie."
        ) from blad

    if wynik.returncode != 0:
        komunikat = (
            wynik.stderr.strip()
            or wynik.stdout.strip()
            or "Proces konwersji zakończył się błędem."
        )
        raise ValueError(komunikat)

    if not wyjscie.is_file() or wyjscie.stat().st_size == 0:
        raise ValueError("Word nie utworzył pliku wynikowego.")

    if wyjscie.suffix.lower() == ".pdf":
        with wyjscie.open("rb") as plik:
            if plik.read(5) != b"%PDF-":
                raise ValueError(
                    "Utworzony plik nie ma nagłówka PDF."
                )

    elif wyjscie.suffix.lower() == ".docx":
        Document = pobierz_document()

        try:
            Document(str(wyjscie))
        except Exception as blad:
            raise ValueError(
                "Word nie utworzył poprawnego dokumentu DOCX."
            ) from blad

KONWERTERY = {
    (".csv", ".json"): csv_na_json,
    (".json", ".csv"): json_na_csv,
    (".txt", ".docx"): txt_na_docx,
    (".docx", ".txt"): docx_na_txt,
    (".docx", ".pdf"): konwersja_przez_word,
    (".pdf", ".docx"): konwersja_przez_word,
}


def dostepne_formaty(sciezka):
    rozszerzenie = Path(sciezka).suffix.lower()

    return [
        docelowy
        for wejsciowy, docelowy in KONWERTERY
        if wejsciowy == rozszerzenie
    ]


def wykonaj_konwersje(wejscie, wyjscie, nadpisz=False):
    wejscie = Path(wejscie)
    wyjscie = Path(wyjscie)

    if not wejscie.is_file():
        raise ValueError("Plik wejściowy nie istnieje.")

    if not wyjscie.parent.is_dir():
        raise ValueError("Katalog zapisu nie istnieje.")

    if wejscie.resolve() == wyjscie.resolve():
        raise ValueError("Plik wynikowy musi różnić się od wejściowego.")

    para = (
        wejscie.suffix.lower(),
        wyjscie.suffix.lower()
    )

    if para not in KONWERTERY:
        raise ValueError("Wybrana konwersja nie jest obsługiwana.")

    if wyjscie.exists() and not nadpisz:
        raise ValueError(
            "Plik wynikowy już istnieje. "
            "Wybierz inną nazwę lub potwierdź nadpisanie."
        )

    try:
        # Wynik powstaje najpierw w katalogu tymczasowym.
        # Błąd konwersji nie niszczy poprzedniego wyniku.
        with tempfile.TemporaryDirectory(
            dir=str(wyjscie.parent)
        ) as katalog:
            tymczasowy = Path(katalog) / (
                "wynik" + wyjscie.suffix.lower()
            )

            KONWERTERY[para](wejscie, tymczasowy)

            if not tymczasowy.is_file():
                raise ValueError("Konwerter nie utworzył pliku.")

            if nadpisz:
                os.replace(tymczasowy, wyjscie)
            else:
                # Tryb xb blokuje przypadkowe nadpisanie.
                with wyjscie.open("xb") as cel:
                    try:
                        with tymczasowy.open("rb") as zrodlo:
                            shutil.copyfileobj(zrodlo, cel)
                    except Exception:
                        cel.close()
                        wyjscie.unlink(missing_ok=True)
                        raise

    except (ValueError, OSError, UnicodeError, csv.Error):
        raise
    except Exception as blad:
        raise ValueError(
            f"Konwersja nie powiodła się: {blad}"
        ) from blad

    return wyjscie

LOGGER = logging.getLogger("konwerter")
LOGGER.setLevel(logging.INFO)
LOGGER.propagate = False

if not LOGGER.handlers:
    handler = logging.FileHandler(
        Path(__file__).resolve().with_name("konwerter.log"),
        encoding="utf-8",
        delay=True,
    )

    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )
    )

    LOGGER.addHandler(handler)


def zapisz_log(poziom, komunikat, *argumenty, exc_info=False):
    try:
        LOGGER.log(
            poziom,
            komunikat,
            *argumenty,
            exc_info=exc_info,
        )
    except OSError:
        # Błąd zapisu logu nie powinien przerywać konwersji.
        pass


def konwertuj(wejscie, wyjscie, nadpisz=False):
    start = time.perf_counter()

    zapisz_log(
        logging.INFO,
        "START | %s -> %s | nadpisz=%s",
        wejscie,
        wyjscie,
        nadpisz,
    )

    try:
        wynik = wykonaj_konwersje(
            wejscie,
            wyjscie,
            nadpisz,
        )
    except Exception:
        zapisz_log(
            logging.ERROR,
            "BŁĄD | %s -> %s",
            wejscie,
            wyjscie,
            exc_info=True,
        )
        raise

    czas = time.perf_counter() - start

    zapisz_log(
        logging.INFO,
        "SUKCES | %s | czas=%.3f s",
        wynik,
        czas,
    )

    return wynik