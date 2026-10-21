import csv
import io
import json
from pathlib import Path


def csv_na_json(plik):
    tekst = plik.read_text(encoding="utf-8-sig")

    try:
        separator = csv.Sniffer().sniff(
            tekst[:8192],
            delimiters=",;\t"
        )
    except csv.Error:
        separator = csv.excel

    czytnik = csv.reader(
        io.StringIO(tekst, newline=""),
        dialect=separator,
        strict=True
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

    return json.dumps(dane, ensure_ascii=False, indent=4)


def json_na_csv(plik):
    try:
        dane = json.loads(plik.read_text(encoding="utf-8-sig"))
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

    bufor = io.StringIO(newline="")

    zapis = csv.DictWriter(bufor, fieldnames=naglowki)
    zapis.writeheader()
    zapis.writerows(dane)

    return bufor.getvalue()


KONWERTERY = {
    (".csv", ".json"): csv_na_json,
    (".json", ".csv"): json_na_csv,
}


def dostepne_formaty(sciezka):
    rozszerzenie = Path(sciezka).suffix.lower()

    return [
        docelowy
        for wejsciowy, docelowy in KONWERTERY
        if wejsciowy == rozszerzenie
    ]


def konwertuj(wejscie, wyjscie, nadpisz=False):
    wejscie = Path(wejscie)
    wyjscie = Path(wyjscie)

    if not wejscie.is_file():
        raise ValueError("Plik wejściowy nie istnieje.")

    if not wyjscie.parent.is_dir():
        raise ValueError("Katalog zapisu nie istnieje.")

    if wejscie.resolve() == wyjscie.resolve():
        raise ValueError("Plik wynikowy musi różnić się od wejściowego.")

    para = (wejscie.suffix.lower(), wyjscie.suffix.lower())

    if para not in KONWERTERY:
        raise ValueError("Obsługiwane konwersje: CSV → JSON i JSON → CSV.")

    # Najpierw sprawdzamy dane, dopiero później zapisujemy wynik.
    wynik = KONWERTERY[para](wejscie)

    tryb = "w" if nadpisz else "x"

    with wyjscie.open(
        tryb,
        encoding="utf-8",
        newline=""
    ) as plik:
        plik.write(wynik)

    return wyjscie