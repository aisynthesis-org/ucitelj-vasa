"""
Glavni program za Učitelja Vasu
Ovo je ulazna tačka za pokretanje AI asistenta.
"""

# Import našeg modula
from src.vasa_core import pozdrav, predstavi_se, glavni_meni


def pokreni_vasu():
    """Pokreće glavnu petlju programa Učitelj Vasa."""
    print("\n" + "🎓" * 25)
    print(pozdrav())
    print("🎓" * 25 + "\n")

    # Glavna petlja programa
    while True:
        print(glavni_meni())
        izbor = input().strip()

        if izbor == "1":
            print("\n" + pozdrav() + "\n")
        elif izbor == "2":
            print("\n" + predstavi_se() + "\n")
        elif izbor == "3":
            print("\nHvala što si koristio Učitelja Vasu! Vidimo se! 👋")
            break
        else:
            print("\n❌ Nepoznata opcija. Pokušaj ponovo.\n")

    print("\nProgram završen.")


# Pokreni program
if __name__ == "__main__":
    pokreni_vasu()
