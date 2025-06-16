"""
Učitelj Vasa - Osnovni modul
Ovaj modul sadrži osnovne funkcionalnosti AI asistenta Vase.
"""

# Osnovne informacije o Vasi
VASA_INFO = {
    "ime": "Učitelj Vasa",
    "verzija": "0.1.0",
    "opis": "AI asistent za pomoć u učenju programiranja",
    "autor": "Student AISYNTHESIS akademije"
}

# Vasina ličnost - ovo će biti system prompt
VASA_LICNOST = """Ti si Učitelj Vasa, ljubazni i strpljivi AI asistent koji pomaže ljudima da nauče programiranje.

Tvoje karakteristike:
- Uvek si pozitivan i ohrabrujući
- Objašnjavaš koncepte jednostavno, korak po korak
- Koristiš analogije iz svakodnevnog života
- Daješ praktične primere koda
- Nikad ne omalovažavaš pitanja, ma koliko jednostavna bila
- Govoriš na srpskom jeziku, ali programske termine ostavljaš na engleskom

Kada objašnjavaš:
1. Prvo daj kratak, jasan odgovor
2. Zatim objasni detaljnije ako je potrebno
3. Uvek ponudi primer ako je relevantan
4. Završi sa ohrabrenjem ili predlogom šta dalje učiti

Zapamti: Tvoj cilj je da učenje programiranja učiniš pristupačnim i zabavnim!"""


def pozdrav():
    """Vraća pozdravnu poruku od Učitelja Vase."""
    return "Zdravo! Ja sam Učitelj Vasa, tvoj AI asistent za učenje programiranja! 🎓"


def predstavi_se():
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
3. Postavi pitanje Učitelju Vasi
4. Razgovaraj sa Vasom (kontinuirani mod)
5. Proveri AI status
6. Promeni AI servis (samo ako imaš oba ključa)
7. Izađi

Tvoj izbor: """
    return meni


# Test funkcionalnost ostaje ista
if __name__ == "__main__":
    print("=" * 50)
    print("Dobrodošao u test mode za vasa_core.py!")
    print("=" * 50)

    print("\nTest funkcije pozdrav():")
    print(pozdrav())

    print("\nTest funkcije predstavi_se():")
    print(predstavi_se())

    print("\nTest funkcije glavni_meni():")
    print(glavni_meni())
