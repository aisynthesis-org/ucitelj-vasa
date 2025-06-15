"""
Učitelj Vasa - Osnovni modul
Ovaj modul sadrži osnovne funkcionalnosti AI asistenta Vase.
"""

# Osnovne informacije o Vasi
VASA_INFO = {
    "ime": "Učitelj Vasa",
    "verzija": "0.1.0",
    "opis": "AI asistent za pomoć u učenju programiranja",
    "autor": "Radoje AI SYNTHESIS akademija"
}


def pozdrav() -> str:
    """Vraća pozdravnu poruku od Učitelja Vase."""
    return f"Zdravo! Ja sam Učitelj Vasa, tvoj AI asistent za učenje programiranja! 🎓"


def predstavi_se() -> str:
    """Vraća detaljne informacije o Učitelju Vasi."""
    poruka = f"""
{VASA_INFO['ime']} - Verzija {VASA_INFO['verzija']}
{'=' * 50}
{VASA_INFO['opis']}

Stvorio: {VASA_INFO['autor']}
    """
    return poruka.strip()


def glavni_meni():
    """Prikazuje glavni meni sa opcijama."""
    meni = """
Šta želiš da uradiš?
1. Pozdravi me
2. Predstavi se
3. Izađi

Tvoj izbor: """
    return meni


if __name__ == "__main__":
    # Ovo se izvršava samo kada direktno pokreneš ovaj fajl
    print("=" * 50)
    print("Dobrodošao u test mode za vasa_core.py!")
    print("=" * 50)

    # Testiraj funkcije
    print("\nTest funkcije pozdrav():")
    print(pozdrav())

    print("\nTest funkcije predstavi_se():")
    print(predstavi_se())

    print("\nTest funkcije glavni_meni():")
    print(glavni_meni())