"""
AI Service Factory
Automatski kreira pravi AI servis na osnovu konfiguracije
"""

import sys
import os
from typing import Optional

# Dodaj parent folder u path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import Config
from .base_service import BaseAIService
from .openai_service import OpenAIService
from .gemini_service import GeminiService


class AIServiceFactory:
    """Factory klasa za kreiranje AI servisa."""

    _instance: Optional[BaseAIService] = None

    @classmethod
    def get_service(cls, force_new: bool = False) -> BaseAIService:
        """
        Vraća instancu AI servisa na osnovu konfiguracije.
        Koristi Singleton pattern za efikasnost.

        Args:
            force_new: Ako je True, kreira novu instancu

        Returns:
            Instanca AI servisa (OpenAI ili Gemini)

        Raises:
            ValueError: Ako je AI_PROVIDER nepoznat
        """
        # Ako već imamo instancu i ne tražimo novu, vrati postojeću
        if cls._instance is not None and not force_new:
            return cls._instance

        # Kreiraj novu instancu na osnovu providera
        provider = Config.AI_PROVIDER.lower()

        print(f"\n🏭 AI Factory: Kreiram {provider.upper()} servis...")

        if provider == 'openai':
            cls._instance = OpenAIService()
        elif provider == 'gemini':
            cls._instance = GeminiService()
        else:
            raise ValueError(
                f"Nepoznat AI provider: {provider}. "
                f"Dozvoljeni: 'openai', 'gemini'"
            )

        print(f"✅ {provider.upper()} servis uspešno kreiran!\n")
        return cls._instance

    @classmethod
    def reset(cls):
        """Resetuje factory (korisno za testiranje)."""
        cls._instance = None
        print("🔄 AI Factory resetovan")

    @classmethod
    def switch_provider(cls, new_provider: str) -> BaseAIService:
        """
        Prebacuje na drugi provider i vraća novi servis.

        Args:
            new_provider: 'openai' ili 'gemini'

        Returns:
            Nova instanca AI servisa
        """
        # Promeni provider u konfiguraciji
        Config.AI_PROVIDER = new_provider

        # Resetuj postojeću instancu
        cls.reset()

        # Kreiraj i vrati novu
        return cls.get_service()


# Test funkcionalnosti
if __name__ == "__main__":
    print("🧪 Test AI Factory")
    print("=" * 50)

    try:
        # Test 1: Kreiraj servis na osnovu trenutne konfiguracije
        print(f"Trenutni provider: {Config.AI_PROVIDER}")
        service1 = AIServiceFactory.get_service()

        # Test 2: Proveri Singleton
        service2 = AIServiceFactory.get_service()
        print(f"\n🔍 Singleton test: service1 == service2? {service1 is service2}")

        # Test 3: Test poziva
        print("\n📤 Test poziv...")
        response = service1.pozovi_ai("Reci 'Zdravo' na srpskom")
        print(f"📥 Odgovor: {response}")

        # Test 4: Prebacivanje providera (samo ako imaš oba ključa)
        if Config.OPENAI_API_KEY and Config.GEMINI_API_KEY:
            drugi_provider = 'gemini' if Config.AI_PROVIDER == 'openai' else 'openai'
            print(f"\n🔄 Prebacujem na {drugi_provider}...")

            service3 = AIServiceFactory.switch_provider(drugi_provider)
            response2 = service3.pozovi_ai("Reci 'Cao' na srpskom")
            print(f"📥 Odgovor od {drugi_provider}: {response2}")

            # Vrati na originalni
            AIServiceFactory.switch_provider(Config.AI_PROVIDER)

    except Exception as e:
        print(f"❌ Factory test neuspešan: {e}")
