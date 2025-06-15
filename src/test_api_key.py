"""
Test skripta za proveru API ključa
Radi sa OpenAI i Gemini servisima
"""

import sys
from pathlib import Path

# Dodaj src folder u Python path
sys.path.append(str(Path(__file__).parent))

from utils.config import Config


def test_api_key_setup():
    """Testira da li je API ključ pravilno postavljen."""
    print("\n🔍 PROVERA PODEŠAVANJA API KLJUČA")
    print("=" * 50)

    # Korak 1: Proveri da li .env postoji
    env_path = Path(__file__).parent.parent / '.env'
    if not env_path.exists():
        print("❌ .env fajl ne postoji!")
        print(f"   Očekivana lokacija: {env_path}")
        return False

    print("✅ .env fajl pronađen")

    # Korak 2: Prikaži koji servis je izabran
    print(f"\n🤖 Izabrani AI servis: {Config.AI_PROVIDER.upper()}")

    # Korak 3: Proveri da li se učitava
    api_key = Config.get_api_key()
    if not api_key:
        print(f"❌ {Config.AI_PROVIDER.upper()} API ključ nije učitan!")
        print("\nMoguci razlozi:")
        print(f"1. Nisi dodao {Config.AI_PROVIDER.upper()}_API_KEY= u .env")
        print("2. Ima razmaka oko = znaka")
        print("3. Ključ je u navodnicima (ne treba)")
        return False

    print(f"✅ {Config.AI_PROVIDER.upper()} API ključ uspešno učitan")

    # Korak 4: Validacija formata
    if Config.AI_PROVIDER == 'openai':
        if not api_key.startswith('sk-'):
            print("⚠️  API ključ možda nije ispravan")
            print("   OpenAI ključevi počinju sa 'sk-'")
    else:  # gemini
        if not api_key.startswith('AIza'):
            print("⚠️  API ključ možda nije ispravan")
            print("   Gemini ključevi počinju sa 'AIza'")

    # Korak 5: Prikaži info
    print(f"\n📊 INFORMACIJE O KLJUČU:")
    print(f"   Servis: {Config.AI_PROVIDER.upper()}")
    print(f"   Dužina: {len(api_key)} karaktera")
    print(f"   Maskiran: {Config.mask_api_key()}")
    print(f"   Model: {Config.get_model()}")

    # Korak 6: Prikaži ostale postavke
    print(f"\n⚙️  OSTALE POSTAVKE:")
    if Config.AI_PROVIDER == 'openai':
        print(f"   Max tokena: {Config.OPENAI_MAX_TOKENS}")
        print(f"   Temperature: {Config.OPENAI_TEMPERATURE}")
    else:
        print(f"   Max tokena: {Config.GEMINI_MAX_TOKENS}")
        print(f"   Temperature: {Config.GEMINI_TEMPERATURE}")
    print(f"   Max pokušaja: {Config.MAX_RETRIES}")
    print(f"   Retry delay: {Config.RETRY_DELAY}s")

    # Korak 7: Troškovi
    if Config.AI_PROVIDER == 'openai':
        print("\n💰 TROŠKOVI:")
        print("   GPT-4.1: $0.0020 per 1K tokena (input)")
        print("   To znači: 1 milion tokena = $2.00")
        print("   Tvoj kredit od $5 = 2.5 miliona tokena!")
    else:
        print("\n💰 TROŠKOVI:")
        print("   Gemini 1.5 Flash: BESPLATNO!")
        print("   Limit: 60 zahteva po minuti")
        print("   15 miliona tokena po dan besplatno!")
        print("   Savršeno za učenje i eksperimentisanje!")

    print("\n✅ SVE JE SPREMNO ZA SUTRA!")
    print(f"   Učitelj Vasa može da koristi {Config.AI_PROVIDER.upper()} API 🎉")

    return True


def test_provider_switching():
    """Testira prebacivanje između servisa."""
    print("\n🔄 TEST PREBACIVANJA SERVISA")
    print("=" * 50)

    print("💡 Možeš lako prebaciti između servisa!")
    print("   Samo promeni AI_PROVIDER u .env fajlu:")
    print("   - AI_PROVIDER=openai")
    print("   - AI_PROVIDER=gemini")
    print("\nOstali kod ostaje isti!")


if __name__ == "__main__":
    # Pokreni testove
    success = test_api_key_setup()

    if success:
        test_provider_switching()

        print("\n💡 SLEDEĆI KORACI:")
        print("1. Sutra instaliramo biblioteke za izabrani servis")
        print("2. Pravimo wrapper funkciju za univerzalne pozive")
        print("3. Učitelj Vasa će progovoriti preko AI-ja!")
    else:
        print("\n❌ Ispravi greške pre nego što nastaviš!")
