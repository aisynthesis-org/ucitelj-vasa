"""
Glavni program za Učitelja Vasu
Ovo je ulazna tačka za pokretanje AI asistenta.
"""

from vasa_core import pozdrav, predstavi_se, glavni_meni
from ai_simulator import simuliraj_ai_odgovor, demonstriraj_api_komunikaciju


def pokreni_vasu():
    """Pokreće glavnu petlju programa Učitelj Vasa."""
    print("\n" + "🎓" * 25)
    print(pozdrav())
    print("🎓" * 25 + "\n")

    # Glavna petlja programa
    while True:
        print("\nŠta želiš da uradiš?")
        print("1. Pozdravi me")
        print("2. Predstavi se")
        print("3. Postavi pitanje AI-ju (simulacija)")
        print("4. Vidi kako API funkcioniše")
        print("5. Izađi")
        print("\nTvoj izbor: ", end="")

        izbor = input().strip()

        if izbor == "1":
            print("\n" + pozdrav() + "\n")
        elif izbor == "2":
            print("\n" + predstavi_se() + "\n")
        elif izbor == "3":
            print("\n💬 Postavi mi bilo koje pitanje o programiranju:")
            pitanje = input().strip()
            if pitanje:
                odgovor = simuliraj_ai_odgovor(pitanje)
                print(f"\n🤖 Učitelj Vasa: {odgovor}")
            else:
                print("\n❌ Nisi uneo pitanje.")
        elif izbor == "4":
            demonstriraj_api_komunikaciju()
        elif izbor == "5":
            print("\nHvala što si koristio Učitelja Vasu! Vidimo se! 👋")
            break
        else:
            print("\n❌ Nepoznata opcija. Pokušaj ponovo.\n")

    print("\nProgram završen.")


if __name__ == "__main__":
    pokreni_vasu()
