"""
Glavni program za Učitelja Vasu
Univerzalna podrška za OpenAI i Gemini
"""

# Dodaj src folder u Python path
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vasa_core import pozdrav, predstavi_se, glavni_meni, VASA_LICNOST
from ai_simulator import simuliraj_ai_odgovor
from utils.config import Config
from ai_services.ai_factory import AIServiceFactory
from ai_services.base_service import BaseAIService
from typing import Optional

# Globalna varijabla za AI servis
ai_service: Optional[BaseAIService] = None


def inicijalizuj_ai_servis():
    """Pokušava da kreira AI servis koristeći factory."""
    global ai_service

    try:
        if Config.validate():
            ai_service = AIServiceFactory.get_service()
            print(f"✅ {Config.AI_PROVIDER.upper()} servis uspešno pokrenut!")
            return True
    except Exception as e:
        print(f"⚠️ AI servis nije dostupan: {e}")
        print("Koristićemo simulaciju umesto pravog AI-ja.")

    return False


def postavi_pitanje_vasi(pitanje: str) -> str:
    """Postavlja pitanje Vasi koristeći AI ili simulaciju."""
    if ai_service:
        # Koristi pravi AI
        print(f"🤖 [Koristim {Config.AI_PROVIDER.upper()} AI model...]")
        return ai_service.pozovi_ai(pitanje, system_prompt=VASA_LICNOST)
    else:
        # Fallback na simulaciju
        print("🎭 [Koristim simulaciju...]")
        return simuliraj_ai_odgovor(pitanje)


def kontinuirani_razgovor():
    """Omogućava kontinuirani razgovor sa Vasom."""
    print("\n💬 KONTINUIRANI RAZGOVOR SA UČITELJEM VASOM")
    print("=" * 50)
    print("Možeš postavljati pitanja jedno za drugim.")
    print("Ukucaj 'kraj' ili 'exit' za povratak u glavni meni.\n")

    # Istorija razgovora za kontekst
    istorija = []

    # Dodaj system prompt u istoriju
    if ai_service:
        istorija.append({
            "role": "system",
            "content": VASA_LICNOST
        })

    while True:
        # Korisnikov unos
        pitanje = input("\n👤 Ti: ").strip()

        # Proveri da li korisnik želi da izađe
        if pitanje.lower() in ['kraj', 'exit', 'izlaz', 'nazad']:
            print("\n👋 Vraćam te u glavni meni...")
            break

        if not pitanje:
            print("❌ Molim te ukucaj pitanje.")
            continue

        # Dodaj pitanje u istoriju
        istorija.append({
            "role": "user",
            "content": pitanje
        })

        # Dobij odgovor
        if ai_service and len(istorija) > 1:  # Ima bar system + user poruku
            print("\n🤖 Učitelj Vasa: ", end="", flush=True)
            odgovor = ai_service.pozovi_sa_istorijom(istorija)
        else:
            print("\n🎭 Učitelj Vasa: ", end="", flush=True)
            odgovor = simuliraj_ai_odgovor(pitanje)

        print(odgovor)

        # Dodaj odgovor u istoriju
        istorija.append({
            "role": "assistant",
            "content": odgovor
        })

        # Ograniči istoriju na poslednjih 10 poruka + system prompt
        if len(istorija) > 11:
            istorija = [istorija[0]] + istorija[-10:]


def promeni_ai_servis():
    """Omogućava promenu AI servisa tokom rada."""
    print("\n🔄 PROMENA AI SERVISA")
    print("=" * 50)

    # Proveri da li su oba ključa dostupna
    if not (Config.OPENAI_API_KEY and Config.GEMINI_API_KEY):
        print("❌ Ne možeš menjati servis jer nemaš oba API ključa.")
        if not Config.OPENAI_API_KEY:
            print("   - OpenAI ključ nedostaje")
        if not Config.GEMINI_API_KEY:
            print("   - Gemini ključ nedostaje")
        return

    # Prikaži trenutni i dostupne
    print(f"Trenutno koristiš: {Config.AI_PROVIDER.upper()}")
    drugi = 'gemini' if Config.AI_PROVIDER == 'openai' else 'openai'

    print(f"\nDa li želiš da pređeš na {drugi.upper()}? (da/ne): ", end="")
    odgovor = input().strip().lower()

    if odgovor in ['da', 'd', 'yes', 'y']:
        global ai_service
        try:
            ai_service = AIServiceFactory.switch_provider(drugi)
            print(f"✅ Uspešno prebačeno na {drugi.upper()}!")
        except Exception as e:
            print(f"❌ Greška pri prebacivanju: {e}")


def pokreni_vasu():
    """Pokreće glavnu petlju programa Učitelj Vasa."""
    # Inicijalizuj AI servis
    ai_dostupan = inicijalizuj_ai_servis()

    print("\n" + "🎓" * 25)
    print(pozdrav())
    if ai_dostupan:
        provider_info = {
            'openai': "✨ Povezan sa OpenAI GPT - najpoznatiji AI model!",
            'gemini': "✨ Povezan sa Google Gemini - moćan i besplatan!"
        }
        print(provider_info.get(Config.AI_PROVIDER.lower(), "✨ AI je spreman!"))
    else:
        print("📚 Radim u offline modu sa simulacijom.")
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
            print("\n💭 Postavi mi bilo koje pitanje o programiranju:")
            pitanje = input("👤 Ti: ").strip()
            if pitanje:
                print("\n🤖 Učitelj Vasa: ", end="", flush=True)
                odgovor = postavi_pitanje_vasi(pitanje)
                print(odgovor)
            else:
                print("\n❌ Nisi uneo pitanje.")

        elif izbor == "4":
            kontinuirani_razgovor()

        elif izbor == "5":
            print("\n" + "=" * 50)
            print("📊 STATUS AI SERVISA")
            print("=" * 50)
            if ai_service:
                print(f"✅ Aktivan servis: {Config.AI_PROVIDER.upper()}")
                print(f"🤖 Model: {Config.get_model()}")
                print(
                    f"🔥 Temperature: {Config.OPENAI_TEMPERATURE if Config.AI_PROVIDER == 'openai' else Config.GEMINI_TEMPERATURE}")
                print(
                    f"📝 Max tokena: {Config.OPENAI_MAX_TOKENS if Config.AI_PROVIDER == 'openai' else Config.GEMINI_MAX_TOKENS}")

                # Troškovi
                if Config.AI_PROVIDER == 'openai':
                    print("\n💰 Troškovi: ~$0.002 po 1K tokena")
                else:
                    print("\n💰 Troškovi: BESPLATNO! (do 15M tokena dnevno)")
            else:
                print("❌ AI servis nije aktivan")
                print("📚 Koristi se simulacija")
            print("=" * 50)

        elif izbor == "6":
            promeni_ai_servis()

        elif izbor == "7":
            print("\nHvala što si koristio Učitelja Vasu! ")
            print("Nastavi sa učenjem i ne zaboravi - svaki ekspert je nekad bio početnik! 🌟")
            break

        else:
            print("\n❌ Nepoznata opcija. Pokušaj ponovo.\n")

    print("\nProgram završen. Srećno sa programiranjem! 👋")


if __name__ == "__main__":
    pokreni_vasu()
