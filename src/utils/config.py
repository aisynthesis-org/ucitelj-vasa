"""
Centralizovana konfiguracija za Učitelja Vasu
Podržava OpenAI i Gemini API servise
"""

import os
from pathlib import Path
from typing import Optional, Literal
from dotenv import load_dotenv


# Učitaj .env fajl
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)


class Config:
    """Centralizovana konfiguracija aplikacije."""

    # Izbor AI servisa
    AI_PROVIDER: Literal['openai', 'gemini'] = os.getenv('AI_PROVIDER', 'openai')

    # OpenAI postavke
    OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL: str = os.getenv('OPENAI_MODEL', 'gpt-4.1')
    OPENAI_MAX_TOKENS: int = int(os.getenv('OPENAI_MAX_TOKENS', '150'))
    OPENAI_TEMPERATURE: float = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))

    # Gemini postavke
    GEMINI_API_KEY: Optional[str] = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL: str = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
    GEMINI_MAX_TOKENS: int = int(os.getenv('GEMINI_MAX_TOKENS', '150'))
    GEMINI_TEMPERATURE: float = float(os.getenv('GEMINI_TEMPERATURE', '0.7'))

    # App postavke
    APP_ENV: str = os.getenv('APP_ENV', 'development')
    DEBUG_MODE: bool = os.getenv('DEBUG_MODE', 'True').lower() == 'true'

    # Retry postavke
    MAX_RETRIES: int = int(os.getenv('MAX_RETRIES', '3'))
    RETRY_DELAY: float = float(os.getenv('RETRY_DELAY', '1'))

    @classmethod
    def validate(cls) -> bool:
        """Proverava da li su sve potrebne postavke učitane."""
        print(f"\n🔍 Provera konfiguracije za: {cls.AI_PROVIDER.upper()}")
        print("=" * 50)

        if cls.AI_PROVIDER == 'openai':
            if not cls.OPENAI_API_KEY:
                print("❌ GREŠKA: OPENAI_API_KEY nije postavljen!")
                print("\n💡 Opcije:")
                print("1. Dodaj OPENAI_API_KEY u .env fajl")
                print("2. Ili prebaci na Gemini: AI_PROVIDER=gemini")
                return False

            if not cls.OPENAI_API_KEY.startswith('sk-'):
                print("❌ GREŠKA: OPENAI_API_KEY ne izgleda ispravno!")
                print("   Trebalo bi da počinje sa 'sk-'")
                return False

        elif cls.AI_PROVIDER == 'gemini':
            if not cls.GEMINI_API_KEY:
                print("❌ GREŠKA: GEMINI_API_KEY nije postavljen!")
                print("\n💡 Opcije:")
                print("1. Dodaj GEMINI_API_KEY u .env fajl")
                print("2. Ili prebaci na OpenAI: AI_PROVIDER=openai")
                return False

            if not cls.GEMINI_API_KEY.startswith('AIza'):
                print("❌ GREŠKA: GEMINI_API_KEY ne izgleda ispravno!")
                print("   Trebalo bi da počinje sa 'AIza'")
                return False
        else:
            print(f"❌ GREŠKA: Nepoznat AI_PROVIDER: {cls.AI_PROVIDER}")
            print("   Dozvoljene vrednosti: 'openai' ili 'gemini'")
            return False

        # Ako je sve OK, prikaži info
        if cls.DEBUG_MODE:
            print(f"✅ {cls.AI_PROVIDER.upper()} konfiguracija učitana!")
            if cls.AI_PROVIDER == 'openai':
                print(f"   - Model: {cls.OPENAI_MODEL}")
                print(f"   - Max tokena: {cls.OPENAI_MAX_TOKENS}")
                print(f"   - Temperature: {cls.OPENAI_TEMPERATURE}")
            else:
                print(f"   - Model: {cls.GEMINI_MODEL}")
                print(f"   - Max tokena: {cls.GEMINI_MAX_TOKENS}")
                print(f"   - Temperature: {cls.GEMINI_TEMPERATURE}")
            print(f"   - Environment: {cls.APP_ENV}")

        return True

    @classmethod
    def get_api_key(cls) -> Optional[str]:
        """Vraća API ključ za trenutno izabrani servis."""
        if cls.AI_PROVIDER == 'openai':
            return cls.OPENAI_API_KEY
        else:
            return cls.GEMINI_API_KEY

    @classmethod
    def get_model(cls) -> str:
        """Vraća model za trenutno izabrani servis."""
        if cls.AI_PROVIDER == 'openai':
            return cls.OPENAI_MODEL
        else:
            return cls.GEMINI_MODEL

    @classmethod
    def mask_api_key(cls) -> str:
        """Vraća maskiranu verziju API ključa za prikaz."""
        key = cls.get_api_key()
        if not key:
            return "Not set"

        # Prikaži samo prvih 7 i poslednjih 4 karaktera
        if len(key) > 15:
            return f"{key[:7]}...{key[-4:]}"
        return "Invalid key"


# Primer korišćenja
if __name__ == "__main__":
    print("=" * 50)
    print("Test učitavanja konfiguracije")
    print("=" * 50)

    if Config.validate():
        print(f"\n📌 AI Servis: {Config.AI_PROVIDER.upper()}")
        print(f"📌 API Key (maskiran): {Config.mask_api_key()}")
        print(f"📌 Model: {Config.get_model()}")
    else:
        print("\n⚠️ Konfiguracija nije validna!")
        print("Prati instrukcije gore za podešavanje.")
