import sys
from pathlib import Path


def konwersja_word(wejscie, wyjscie):
    try:
        import pythoncom
        import win32com.client
    except ImportError as blad:
        raise ValueError(
            "Brakuje biblioteki pywin32. "
            "Wykonaj: py -m pip install pywin32"
        ) from blad

    para = (wejscie.suffix.lower(), wyjscie.suffix.lower())

    if para not in {
        (".docx", ".pdf"),
        (".pdf", ".docx"),
    }:
        raise ValueError("Nieobsługiwana konwersja przez Word.")

    word = None
    dokument = None

    pythoncom.CoInitialize()

    try:
        try:
            word = win32com.client.DispatchEx("Word.Application")
        except Exception as blad:
            raise ValueError(
                "Nie można uruchomić Microsoft Word. "
                "Sprawdź, czy Word uruchamia się ręcznie."
            ) from blad

        word.Visible = False
        word.DisplayAlerts = 0
        word.AutomationSecurity = 3

        # Word może otworzyć PDF i przekształcić go
        # na edytowalny dokument.
        dokument = word.Documents.Open(
            FileName=str(wejscie.resolve()),
            ConfirmConversions=False,
            ReadOnly=True,
            AddToRecentFiles=False,
            Visible=False,
            NoEncodingDialog=True,
        )

        if wyjscie.suffix.lower() == ".pdf":
            dokument.ExportAsFixedFormat(
                OutputFileName=str(wyjscie.resolve()),
                ExportFormat=17,
                OpenAfterExport=False,
            )
        else:
            # 12 oznacza format DOCX.
            dokument.SaveAs2(
                FileName=str(wyjscie.resolve()),
                FileFormat=12,
                AddToRecentFiles=False,
            )

    finally:
        if dokument is not None:
            try:
                dokument.Close(SaveChanges=0)
            except Exception:
                pass

        if word is not None:
            try:
                word.Quit(SaveChanges=0)
            except Exception:
                pass

        dokument = None
        word = None
        pythoncom.CoUninitialize()


def main():
    if len(sys.argv) != 3:
        print(
            "Ten skrypt jest uruchamiany przez konwertery.py.",
            file=sys.stderr,
        )
        return 1

    wejscie = Path(sys.argv[1])
    wyjscie = Path(sys.argv[2])

    try:
        konwersja_word(wejscie, wyjscie)
    except Exception as blad:
        print(
            f"Błąd konwersji przez Word: {blad}",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())