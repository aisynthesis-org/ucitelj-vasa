"""
Glavni program za Učitelja Vasu
Podržava OpenAI i Gemini AI servise
"""

from vasa_core import pozdrav, predstavi_se, glavni_meni
from ai_simulator import simuliraj_ai_odgovor, demonstriraj_api_komunikaciju
from utils.config import Config


def proveri_spremnost():
    """Proverava da li je sistem spreman za rad."""
    print("\n🔧 Provera sistema...")

    if Config.validate():
        print(f"✅ {Config.AI_PROVIDER.upper()} API ključ učitan: {Config.mask_api_key()}")
        return True
    else:
        print(f"\n⚠️  UPOZORENJE: {Config.AI_PROVIDER.upper()} API ključ nije podešen!")
        print("Možeš koristiti simulaciju, ali ne i pravi AI.")
        print("Pogledaj lekciju Dana 3 za instrukcije.")
        return False


def pokreni_vasu():
    """Pokreće glavnu petlju programa Učitelj Vasa."""
    # Proveri sistem
    api_dostupan = proveri_spremnost()

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
        print("5. Proveri API podešavanja")
        print("6. Izađi")
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
            print("\n" + "=" * 50)
            if api_dostupan:
                print(f"✅ TRENUTNO AKTIVAN: {Config.AI_PROVIDER.upper()}")
                print(f"📌 Ključ: {Config.mask_api_key()}")
                print(f"🎯 Model: {Config.get_model()}")

                if Config.AI_PROVIDER == 'openai':
                    print("💰 Tip: Plaćeni servis ($5 kredit)")
                else:
                    print("💰 Tip: Besplatan servis")

                # Proveri da li je konfigurisan i drugi servis
                print("\n🔄 DOSTUPNI SERVISI:")
                if Config.OPENAI_API_KEY:
                    status = "✅ AKTIVAN" if Config.AI_PROVIDER == 'openai' else "💤 Spreman"
                    print(f"   - OpenAI: {status}")
                if Config.GEMINI_API_KEY:
                    status = "✅ AKTIVAN" if Config.AI_PROVIDER == 'gemini' else "💤 Spreman"
                    print(f"   - Gemini: {status}")

                if Config.OPENAI_API_KEY and Config.GEMINI_API_KEY:
                    print("\n💡 TIP: Možeš prebaciti servis promenom AI_PROVIDER u .env!")
            else:
                print(f"❌ {Config.AI_PROVIDER.upper()} API ključ nije podešen.")
                print("Prati instrukcije iz Dana 3.")
            print("=" * 50)
        elif izbor == "6":
            print("\nHvala što si koristio Učitelja Vasu! Vidimo se! 👋")
            break
        else:
            print("\n❌ Nepoznata opcija. Pokušaj ponovo.\n")

    print("\nProgram završen.")


if __name__ == "__main__":
    pokreni_vasu()
