import argparse
import csv
import sys
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from konwertery import dostepne_formaty, konwertuj


def uruchom_okno():
    okno = tk.Tk()
    okno.title("Konwerter plików — Lab 3")
    okno.geometry("760x410")
    okno.minsize(650, 410)

    plik_wejsciowy = tk.StringVar()
    katalog_zapisu = tk.StringVar()
    format_docelowy = tk.StringVar()

    status = tk.StringVar(
        value="Wybierz plik CSV, JSON, TXT, DOCX lub PDF."
    )

    wykonawca = ThreadPoolExecutor(max_workers=1)
    trwa_konwersja = False

    ramka = ttk.Frame(okno, padding=25)
    ramka.pack(fill="both", expand=True)
    ramka.columnconfigure(0, weight=1)

    def wybierz_plik():
        sciezka = filedialog.askopenfilename(
            parent=okno,
            title="Wybierz plik do konwersji",
            filetypes=[
                (
                    "Obsługiwane pliki",
                    "*.csv *.json *.txt *.docx *.pdf "
                    "*.CSV *.JSON *.TXT *.DOCX *.PDF"
                ),
                ("Pliki CSV", "*.csv"),
                ("Pliki JSON", "*.json"),
                ("Pliki tekstowe", "*.txt"),
                ("Dokumenty Word", "*.docx"),
                ("Dokumenty PDF", "*.pdf"),
                ("Wszystkie pliki", "*.*"),
            ],
        )

        if not sciezka:
            return

        plik_wejsciowy.set(sciezka)
        katalog_zapisu.set(str(Path(sciezka).parent))

        formaty = dostepne_formaty(sciezka)
        lista_formatow["values"] = formaty

        if formaty:
            format_docelowy.set(formaty[0])
            przycisk_konwersji["state"] = "normal"
            status.set("Gotowy do konwersji.")
        else:
            format_docelowy.set("")
            przycisk_konwersji["state"] = "disabled"
            status.set("Ten format nie jest obsługiwany.")

    def wybierz_katalog():
        sciezka = filedialog.askdirectory(
            parent=okno,
            title="Wybierz katalog zapisu",
        )

        if sciezka:
            katalog_zapisu.set(sciezka)

    def ustaw_stan_pracy(pracuje):
        stan = "disabled" if pracuje else "normal"

        przycisk_pliku["state"] = stan
        przycisk_katalogu["state"] = stan
        przycisk_konwersji["state"] = stan

        lista_formatow["state"] = (
            "disabled" if pracuje else "readonly"
        )

    def sprawdz_wynik(zadanie):
        nonlocal trwa_konwersja

        if not zadanie.done():
            okno.after(
                100,
                lambda: sprawdz_wynik(zadanie)
            )
            return

        trwa_konwersja = False
        ustaw_stan_pracy(False)

        try:
            wynik = zadanie.result()
        except Exception as blad:
            status.set("Konwersja nie powiodła się.")

            messagebox.showerror(
                "Błąd konwersji",
                str(blad),
                parent=okno,
            )
        else:
            status.set(f"Zapisano plik: {wynik.name}")

            messagebox.showinfo(
                "Gotowe",
                f"Konwersja zakończona.\n\nZapisano:\n{wynik}",
                parent=okno,
            )

    def wykonaj_konwersje():
        nonlocal trwa_konwersja

        if not plik_wejsciowy.get():
            messagebox.showerror(
                "Brak pliku",
                "Najpierw wybierz plik wejściowy.",
                parent=okno,
            )
            return

        if not katalog_zapisu.get() or not format_docelowy.get():
            messagebox.showerror(
                "Brak wyboru",
                "Wybierz katalog zapisu i format docelowy.",
                parent=okno,
            )
            return

        wejscie = Path(plik_wejsciowy.get())

        wyjscie = Path(katalog_zapisu.get()) / (
            wejscie.stem + format_docelowy.get()
        )

        nadpisz = False

        if wyjscie.exists():
            nadpisz = messagebox.askyesno(
                "Plik już istnieje",
                f"Czy nadpisać plik?\n\n{wyjscie}",
                parent=okno,
            )

            if not nadpisz:
                status.set(
                    "Anulowano. Możesz wybrać inny katalog."
                )
                return

        trwa_konwersja = True
        ustaw_stan_pracy(True)
        status.set("Trwa konwersja. Proszę czekać…")

        # Konwersja odbywa się poza głównym wątkiem GUI.
        zadanie = wykonawca.submit(
            konwertuj,
            wejscie,
            wyjscie,
            nadpisz,
        )

        okno.after(
            100,
            lambda: sprawdz_wynik(zadanie)
        )

    def zamknij_okno():
        if trwa_konwersja:
            messagebox.showinfo(
                "Trwa konwersja",
                "Poczekaj na zakończenie konwersji.",
                parent=okno,
            )
            return

        wykonawca.shutdown(wait=False)
        okno.destroy()

    ttk.Label(
        ramka,
        text="Konwerter plików",
        font=("Segoe UI", 20, "bold"),
    ).grid(
        row=0,
        column=0,
        columnspan=2,
        sticky="w",
    )

    ttk.Label(
        ramka,
        text="CSV ↔ JSON | TXT ↔ DOCX | DOCX ↔ PDF",

    ).grid(
        row=1,
        column=0,
        columnspan=2,
        sticky="w",
        pady=(4, 20),
    )

    ttk.Label(
        ramka,
        text="Plik wejściowy:",
    ).grid(row=2, column=0, sticky="w")

    ttk.Entry(
        ramka,
        textvariable=plik_wejsciowy,
        state="readonly",
    ).grid(
        row=3,
        column=0,
        sticky="ew",
        padx=(0, 12),
    )

    przycisk_pliku = ttk.Button(
        ramka,
        text="Wybierz plik…",
        command=wybierz_plik,
    )
    przycisk_pliku.grid(
        row=3,
        column=1,
        sticky="ew",
    )

    ttk.Label(
        ramka,
        text="Katalog zapisu:",
    ).grid(
        row=4,
        column=0,
        sticky="w",
        pady=(18, 0),
    )

    ttk.Entry(
        ramka,
        textvariable=katalog_zapisu,
        state="readonly",
    ).grid(
        row=5,
        column=0,
        sticky="ew",
        padx=(0, 12),
    )

    przycisk_katalogu = ttk.Button(
        ramka,
        text="Wybierz katalog…",
        command=wybierz_katalog,
    )
    przycisk_katalogu.grid(
        row=5,
        column=1,
        sticky="ew",
    )

    ttk.Label(
        ramka,
        text="Format docelowy:",
    ).grid(
        row=6,
        column=0,
        sticky="w",
        pady=(18, 0),
    )

    lista_formatow = ttk.Combobox(
        ramka,
        textvariable=format_docelowy,
        state="readonly",
        width=15,
    )
    lista_formatow.grid(
        row=7,
        column=0,
        sticky="w",
    )

    przycisk_konwersji = ttk.Button(
        ramka,
        text="Konwertuj",
        command=wykonaj_konwersje,
        state="disabled",
    )
    przycisk_konwersji.grid(
        row=7,
        column=1,
        sticky="ew",
    )

    ttk.Label(
        ramka,
        textvariable=status,
        wraplength=650,
    ).grid(
        row=8,
        column=0,
        columnspan=2,
        sticky="w",
        pady=(25, 0),
    )

    okno.protocol("WM_DELETE_WINDOW", zamknij_okno)
    okno.mainloop()


def main():
    if len(sys.argv) == 1:
        uruchom_okno()
        return 0

    parser = argparse.ArgumentParser(
        description="Konwerter CSV, JSON, TXT, DOCX i PDF"
    )

    parser.add_argument(
        "wejscie",
        help="Ścieżka pliku wejściowego"
    )

    parser.add_argument(
        "wyjscie",
        help="Ścieżka pliku wynikowego"
    )

    parser.add_argument(
        "--nadpisz",
        action="store_true",
        help="Zezwól na nadpisanie istniejącego pliku",
    )

    argumenty = parser.parse_args()

    try:
        wynik = konwertuj(
            argumenty.wejscie,
            argumenty.wyjscie,
            argumenty.nadpisz,
        )
    except (ValueError, OSError, UnicodeError, csv.Error) as blad:
        print(f"Błąd: {blad}", file=sys.stderr)
        return 1

    print(f"Zapisano: {wynik}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())