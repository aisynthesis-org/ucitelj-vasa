"""
Test scenariji za resilience funkcionalnosti
Simulira različite failure scenario
"""

import time
import random
from ai_services.ai_factory import AIServiceFactory
from utils.config import Config


def simulate_network_issues():
    """Simulira probleme sa mrežom."""
    print("\n🧪 TEST 1: Simulacija mrežnih problema")
    print("=" * 50)

    # Kreiraj resilient servis
    service = AIServiceFactory.create_resilient_service()

    # Simuliraj više poziva sa povremenim greškama
    for i in range(5):
        print(f"\nPokušaj {i + 1}:")

        # Random da li će raditi
        if random.random() < 0.6:  # 60% šanse za grešku
            # Privremeno "pokvari" servis
            original_key = Config.get_api_key()
            Config.OPENAI_API_KEY = "invalid_key"
            Config.GEMINI_API_KEY = "invalid_key"

        try:
            response = service.pozovi_ai("Šta je Python?")
            print(f"✅ Odgovor: {response[:100]}...")
        except Exception as e:
            print(f"❌ Greška: {e}")
        finally:
            # Vrati pravi ključ
            if 'original_key' in locals():
                if Config.AI_PROVIDER == "openai":
                    Config.OPENAI_API_KEY = original_key
                else:
                    Config.GEMINI_API_KEY = original_key

        time.sleep(1)


def test_circuit_breaker():
    """Testira circuit breaker funkcionalnost."""
    print("\n🧪 TEST 2: Circuit Breaker test")
    print("=" * 50)

    service = AIServiceFactory.create_resilient_service()

    # Forsiraj greške
    original_key = Config.get_api_key()
    if Config.AI_PROVIDER == "openai":
        Config.OPENAI_API_KEY = "invalid"
    else:
        Config.GEMINI_API_KEY = "invalid"

    print("Forsiram greške da aktiviram circuit breaker...")

    for i in range(6):
        print(f"\nPoziv {i + 1}:")
        try:
            response = service.pozovi_ai("Test")
            print(f"Odgovor: {response}")
        except Exception as e:
            print(f"Status: {type(e).__name__}")

    # Vrati ključ i čekaj recovery
    if Config.AI_PROVIDER == "openai":
        Config.OPENAI_API_KEY = original_key
    else:
        Config.GEMINI_API_KEY = original_key

    print("\n⏰ Čekam 35 sekundi za recovery timeout...")
    time.sleep(35)

    print("\nPokušavam ponovo nakon recovery perioda:")
    try:
        response = service.pozovi_ai("Test nakon recovery")
        print(f"✅ Uspeh: {response}")
    except Exception as e:
        print(f"❌ Još uvek ne radi: {e}")


def test_graceful_degradation():
    """Testira graceful degradation."""
    print("\n🧪 TEST 3: Graceful Degradation")
    print("=" * 50)

    # Sačuvaj originalne ključeve
    orig_openai = Config.OPENAI_API_KEY
    orig_gemini = Config.GEMINI_API_KEY

    # Ukloni sve API ključeve
    Config.OPENAI_API_KEY = None
    Config.GEMINI_API_KEY = None

    print("Svi API ključevi uklonjeni - testiram degraded mode...")

    try:
        service = AIServiceFactory.create_resilient_service()

        test_messages = [
            "Zdravo!",
            "Imam problem sa kodom",
            "Kako da naučim Python?",
            "Random poruka"
        ]

        for msg in test_messages:
            print(f"\nPoruka: '{msg}'")
            response = service.pozovi_ai(msg)
            print(f"Odgovor: {response}")

    finally:
        # Vrati ključeve
        Config.OPENAI_API_KEY = orig_openai
        Config.GEMINI_API_KEY = orig_gemini


if __name__ == "__main__":
    print("🚀 RESILIENCE TEST SUITE")
    print("=" * 60)

    # Proveri da li je bar jedan servis konfigurisan
    if not (Config.OPENAI_API_KEY or Config.GEMINI_API_KEY):
        print("❌ Potreban je bar jedan API ključ za testiranje!")
        exit(1)

    # Pokreni testove
    simulate_network_issues()
    test_circuit_breaker()
    test_graceful_degradation()

    print("\n✅ Svi testovi završeni!")
