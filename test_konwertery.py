import csv
import io
import json
import platform
import subprocess
import sys
import tempfile
import unittest

from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import konwertery


class TestKonwertera(unittest.TestCase):
    def setUp(self):
        self.katalog_tymczasowy = tempfile.TemporaryDirectory()
        self.addCleanup(self.katalog_tymczasowy.cleanup)

        self.katalog = Path(self.katalog_tymczasowy.name)

    def utworz_plik(self, nazwa, tekst):
        plik = self.katalog / nazwa
        plik.write_text(tekst, encoding="utf-8")
        return plik

    def test_csv_na_json_polskie_znaki_i_pusta_wartosc(self):
        wejscie = self.utworz_plik(
            "dane.csv",
            "imie;miasto;opis\nŁukasz;Łódź;\n",
        )

        wyjscie = self.katalog / "wynik.json"

        konwertery.konwertuj(wejscie, wyjscie)

        dane = json.loads(
            wyjscie.read_text(encoding="utf-8")
        )

        self.assertEqual(
            dane,
            [
                {
                    "imie": "Łukasz",
                    "miasto": "Łódź",
                    "opis": "",
                }
            ],
        )

        self.assertEqual(
            list(dane[0]),
            ["imie", "miasto", "opis"],
        )

    def test_json_na_csv_bom_separator_i_kolejnosc(self):
        wejscie = self.utworz_plik(
            "dane.json",
            json.dumps(
                [
                    {
                        "miasto": "Łódź",
                        "imie": "Żaneta",
                        "opis": None,
                    }
                ],
                ensure_ascii=False,
            ),
        )

        wyjscie = self.katalog / "wynik.csv"

        konwertery.konwertuj(wejscie, wyjscie)

        self.assertTrue(
            wyjscie.read_bytes().startswith(b"\xef\xbb\xbf")
        )

        with wyjscie.open(
            encoding="utf-8-sig",
            newline="",
        ) as plik:
            wiersze = list(csv.reader(plik, delimiter=";"))

        self.assertEqual(
            wiersze,
            [
                ["miasto", "imie", "opis"],
                ["Łódź", "Żaneta", ""],
            ],
        )

    def test_csv_json_csv_zachowuje_tresc(self):
        wejscie = self.utworz_plik(
            "dane.csv",
            'imie,opis\nŁukasz,"Lubi muzykę, książki i sport"\n',
        )

        json_plik = self.katalog / "posredni.json"
        csv_plik = self.katalog / "powrot.csv"

        konwertery.konwertuj(wejscie, json_plik)
        konwertery.konwertuj(json_plik, csv_plik)

        oryginal = list(
            csv.reader(
                io.StringIO(
                    wejscie.read_text(encoding="utf-8")
                ),
                delimiter=",",
            )
        )

        wynik = list(
            csv.reader(
                io.StringIO(
                    csv_plik.read_text(encoding="utf-8-sig")
                ),
                delimiter=";",
            )
        )

        self.assertEqual(wynik, oryginal)

    def test_bledny_json_nie_tworz_wyniku(self):
        wejscie = self.utworz_plik(
            "bledny.json",
            '[{"imie": "Jan",}]',
        )

        wyjscie = self.katalog / "wynik.csv"

        with self.assertRaisesRegex(ValueError, "Błędny JSON"):
            konwertery.konwertuj(wejscie, wyjscie)

        self.assertFalse(wyjscie.exists())

    def test_csv_powtorzone_naglowki(self):
        wejscie = self.utworz_plik(
            "bledny.csv",
            "imie;imie\nJan;Adam\n",
        )

        with self.assertRaises(ValueError):
            konwertery.konwertuj(
                wejscie,
                self.katalog / "wynik.json",
            )

    def test_csv_nieprawidlowa_liczba_kolumn(self):
        wejscie = self.utworz_plik(
            "bledny.csv",
            "imie;miasto\nJan;Opole;dodatkowa\n",
        )

        with self.assertRaises(ValueError):
            konwertery.konwertuj(
                wejscie,
                self.katalog / "wynik.json",
            )

    def test_json_rozne_klucze(self):
        wejscie = self.utworz_plik(
            "bledny.json",
            '[{"imie": "Jan"}, {"miasto": "Opole"}]',
        )

        with self.assertRaises(ValueError):
            konwertery.konwertuj(
                wejscie,
                self.katalog / "wynik.csv",
            )

    def test_json_zagniezdzone_dane(self):
        wejscie = self.utworz_plik(
            "bledny.json",
            '[{"imie": "Jan", "adres": {"miasto": "Opole"}}]',
        )

        with self.assertRaises(ValueError):
            konwertery.konwertuj(
                wejscie,
                self.katalog / "wynik.csv",
            )

    def test_brak_pliku_wejsciowego(self):
        with self.assertRaises(ValueError):
            konwertery.konwertuj(
                self.katalog / "nie_istnieje.csv",
                self.katalog / "wynik.json",
            )

    def test_brak_katalogu_docelowego(self):
        wejscie = self.utworz_plik(
            "dane.csv",
            "imie\nJan\n",
        )

        with self.assertRaises(ValueError):
            konwertery.konwertuj(
                wejscie,
                self.katalog / "brak_katalogu" / "wynik.json",
            )

    def test_nieobslugiwana_para(self):
        wejscie = self.utworz_plik(
            "dane.csv",
            "imie\nJan\n",
        )

        with self.assertRaises(ValueError):
            konwertery.konwertuj(
                wejscie,
                self.katalog / "wynik.pdf",
            )

    def test_dostepne_formaty(self):
        self.assertEqual(
            konwertery.dostepne_formaty("DANE.CSV"),
            [".json"],
        )

        self.assertEqual(
            konwertery.dostepne_formaty("dane.json"),
            [".csv"],
        )

        self.assertEqual(
            set(konwertery.dostepne_formaty("dokument.docx")),
            {".txt", ".pdf"},
        )

        self.assertEqual(
            konwertery.dostepne_formaty("dokument.pdf"),
            [".docx"],
        )

        self.assertEqual(
            konwertery.dostepne_formaty("obraz.jpg"),
            [],
        )

    def test_blokada_nadpisania(self):
        wejscie = self.utworz_plik(
            "dane.csv",
            "imie\nJan\n",
        )

        wyjscie = self.utworz_plik(
            "wynik.json",
            "POPRZEDNIA ZAWARTOSC",
        )

        with self.assertRaises(ValueError):
            konwertery.konwertuj(wejscie, wyjscie)

        self.assertEqual(
            wyjscie.read_text(encoding="utf-8"),
            "POPRZEDNIA ZAWARTOSC",
        )

    def test_nadpisanie_po_zgodzie(self):
        wejscie = self.utworz_plik(
            "dane.csv",
            "imie\nJan\n",
        )

        wyjscie = self.utworz_plik(
            "wynik.json",
            "POPRZEDNIA ZAWARTOSC",
        )

        konwertery.konwertuj(
            wejscie,
            wyjscie,
            nadpisz=True,
        )

        self.assertEqual(
            json.loads(wyjscie.read_text(encoding="utf-8")),
            [{"imie": "Jan"}],
        )

    def test_blad_nie_niszczy_poprzedniego_wyniku(self):
        wejscie = self.utworz_plik(
            "bledny.json",
            '[{"imie": "Jan",}]',
        )

        wyjscie = self.utworz_plik(
            "wynik.csv",
            "POPRZEDNIA ZAWARTOSC",
        )

        with self.assertRaises(ValueError):
            konwertery.konwertuj(
                wejscie,
                wyjscie,
                nadpisz=True,
            )

        self.assertEqual(
            wyjscie.read_text(encoding="utf-8"),
            "POPRZEDNIA ZAWARTOSC",
        )

    def test_txt_docx_txt_polskie_znaki_i_akapity(self):
        from docx import Document

        tekst = (
            "Pierwszy akapit: Łódź.\n"
            "\n"
            "Trzeci akapit: Żaneta i książki."
        )

        wejscie = self.utworz_plik("tekst.txt", tekst)
        docx_plik = self.katalog / "dokument.docx"
        txt_plik = self.katalog / "odczyt.txt"

        konwertery.konwertuj(wejscie, docx_plik)

        dokument = Document(str(docx_plik))

        self.assertEqual(
            [akapit.text for akapit in dokument.paragraphs],
            tekst.split("\n"),
        )

        konwertery.konwertuj(docx_plik, txt_plik)

        self.assertEqual(
            txt_plik.read_text(encoding="utf-8"),
            tekst,
        )

    def test_uszkodzony_docx(self):
        wejscie = self.utworz_plik(
            "uszkodzony.docx",
            "To nie jest dokument Word.",
        )

        wyjscie = self.katalog / "wynik.txt"

        with self.assertRaises(ValueError):
            konwertery.konwertuj(wejscie, wyjscie)

        self.assertFalse(wyjscie.exists())

    def test_blad_narzedzia_zewnetrznego(self):
        wejscie = self.utworz_plik(
            "dokument.docx",
            "Dane zastępcze do testu obsługi procesu.",
        )

        wyjscie = self.katalog / "wynik.pdf"

        wynik_procesu = subprocess.CompletedProcess(
            args=[],
            returncode=1,
            stdout="",
            stderr="Nie można uruchomić Microsoft Word.",
        )

        with (
            patch.object(konwertery.sys, "platform", "win32"),
            patch.object(
                konwertery.subprocess,
                "run",
                return_value=wynik_procesu,
            ) as uruchom,
        ):
            with self.assertRaisesRegex(
                ValueError,
                "Nie można uruchomić Microsoft Word",
            ):
                konwertery.konwertuj(wejscie, wyjscie)

            self.assertFalse(
                uruchom.call_args.kwargs["shell"]
            )

        self.assertFalse(wyjscie.exists())

    def test_limit_czasu_procesu(self):
        wejscie = self.utworz_plik(
            "dokument.docx",
            "Dane zastępcze do testu limitu czasu.",
        )

        wyjscie = self.katalog / "wynik.pdf"

        with (
            patch.object(konwertery.sys, "platform", "win32"),
            patch.object(
                konwertery.subprocess,
                "run",
                side_effect=subprocess.TimeoutExpired(
                    cmd=["proces_testowy"],
                    timeout=90,
                ),
            ),
        ):
            with self.assertRaisesRegex(
                ValueError,
                "90 sekund",
            ):
                konwertery.konwertuj(wejscie, wyjscie)

        self.assertFalse(wyjscie.exists())

    def test_brak_uprawnien_do_zapisu(self):
        wejscie = self.utworz_plik(
            "dane.csv",
            "imie\nJan\n",
        )

        wyjscie = self.katalog / "wynik.json"

        def odmow_zapisu(zrodlo, cel):
            raise PermissionError("Brak uprawnień do zapisu.")

        with patch.dict(
            konwertery.KONWERTERY,
            {(".csv", ".json"): odmow_zapisu},
        ):
            with self.assertRaises(PermissionError):
                konwertery.konwertuj(wejscie, wyjscie)

        self.assertFalse(wyjscie.exists())


def uruchom_testy_z_raportem():
    zestaw = unittest.defaultTestLoader.loadTestsFromTestCase(
        TestKonwertera
    )

    bufor = io.StringIO()

    runner = unittest.TextTestRunner(
        stream=bufor,
        verbosity=2,
    )

    wynik = runner.run(zestaw)
    szczegoly = bufor.getvalue()

    raport = (
        "RAPORT TESTOW AUTOMATYCZNYCH\n"
        "Konwerter plikow\n\n"
        f"Data: {datetime.now().astimezone().isoformat()}\n"
        f"Python: {platform.python_version()}\n"
        f"System: {platform.platform()}\n\n"
        f"Liczba testow: {wynik.testsRun}\n"
        f"Niepowodzenia: {len(wynik.failures)}\n"
        f"Bledy: {len(wynik.errors)}\n"
        f"Pominiete: {len(wynik.skipped)}\n\n"
        "Testy procesu Worda korzystaja z symulacji.\n"
        "Rzeczywiste DOCX/PDF i GUI wymagaja testow recznych.\n\n"
        + szczegoly
    )

    sciezka = Path(__file__).resolve().with_name(
        "RAPORT_TESTOW_AUTOMATYCZNYCH.txt"
    )

    sciezka.write_text(raport, encoding="utf-8")

    print(szczegoly)
    print(f"Raport zapisano: {sciezka}")

    return 0 if wynik.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(uruchom_testy_z_raportem())