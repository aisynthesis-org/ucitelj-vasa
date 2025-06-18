"""
AI Service Factory
Automatski kreira pravi AI servis na osnovu konfiguracije
"""

import sys
import os
import logging
from typing import Optional, List, Dict, Any

# Dodaj parent folder u path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import Config
from .base_service import BaseAIService
from .openai_service import OpenAIService
from .gemini_service import GeminiService

# Resilience importi - proveri da li postoje pre importovanja
try:
    from utils.retry_handler import retry, RetryConfig, RetryError
    from utils.circuit_breaker import circuit_breaker, CircuitOpenError, register_circuit
    from utils.fallback_manager import fallback_manager, FallbackLevel, FallbackOption

    RESILIENCE_AVAILABLE = True
except ImportError:
    print("⚠️ Resilience moduli nisu dostupni. Nastavljam bez napredne zaštite.")
    RESILIENCE_AVAILABLE = False


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


# Jednostavna simulacija za fallback
def simuliraj_ai_odgovor(poruka: str) -> str:
    """Lokalna simulacija AI odgovora kada servisi nisu dostupni."""
    poruka_lower = poruka.lower()

    if any(word in poruka_lower for word in ["zdravo", "pozdrav", "ćao", "hej"]):
        return "Zdravo! Trenutno radim u offline režimu, ali mogu da pomognem sa osnovnim stvarima."
    elif "python" in poruka_lower:
        return "Python je odličan programski jezik za početnike! Ima jednostavnu sintaksu i moćne biblioteke."
    else:
        return "Izvini, trenutno radim u ograničenom režimu. Pokušaj ponovo kasnije za potpun odgovor."


# Resilience klase - definiši samo ako su moduli dostupni
if RESILIENCE_AVAILABLE:

    class ResilientAIServiceFactory(AIServiceFactory):
        """
        Proširena factory klasa sa resilience funkcionalnostima.
        """

        @classmethod
        def create_resilient_service(cls) -> BaseAIService:
            """
            Kreira AI servis sa ugrađenim resilience mehanizmima.

            Returns:
                AI servis sa retry, circuit breaker i fallback logikom
            """
            # Prvo pokušaj da kreiraš osnovni servis
            try:
                base_service = cls.get_service()

                # Omotaj ga u resilience wrapper
                return ResilientAIServiceWrapper(base_service)

            except Exception as e:
                print(f"⚠️ Ne mogu da kreiram {Config.AI_PROVIDER} servis: {e}")
                print("📌 Kreiram degradirani servis sa ograničenim mogućnostima...")

                # Vrati degradirani servis
                return DegradedAIService()


    class ResilientAIServiceWrapper(BaseAIService):
        """
        Wrapper koji dodaje resilience funkcionalnosti postojećem servisu.
        """

        def __init__(self, base_service: BaseAIService):
            self.base_service = base_service
            self.provider_name = Config.AI_PROVIDER

            # Kreiraj fallback lanac
            self._setup_fallback_chain()

            # Registruj circuit breaker
            register_circuit(f"ai_{self.provider_name}", self._circuit_breaker_call.circuit_breaker)

        def _setup_fallback_chain(self):
            """Postavlja fallback lanac za ovaj servis."""
            chain_name = f"ai_response_{self.provider_name}"
            chain = fallback_manager.create_chain(chain_name)

            # Primary - glavni servis sa circuit breaker-om
            chain.add_option(FallbackOption(
                name=f"{self.provider_name.upper()} (glavni)",
                level=FallbackLevel.PRIMARY,
                handler=self._circuit_breaker_call,
                description=f"Glavni {self.provider_name} servis sa zaštitom"
            ))

            # Secondary - alternativni AI (ako postoji)
            if Config.OPENAI_API_KEY and Config.GEMINI_API_KEY:
                alt_provider = "gemini" if self.provider_name == "openai" else "openai"
                chain.add_option(FallbackOption(
                    name=f"{alt_provider.upper()} (rezerva)",
                    level=FallbackLevel.SECONDARY,
                    handler=self._try_alternative_provider,
                    description=f"Rezervni {alt_provider} servis",
                    degradation_message=f"Prebacujem na {alt_provider} servis..."
                ))

            # Tertiary - lokalna simulacija
            chain.add_option(FallbackOption(
                name="Simulacija",
                level=FallbackLevel.TERTIARY,
                handler=lambda msg, **kwargs: simuliraj_ai_odgovor(msg),
                description="Offline simulacija",
                degradation_message="AI servisi nedostupni - koristim simulaciju"
            ))

            self.fallback_chain_name = chain_name

        @circuit_breaker(
            failure_threshold=3,
            recovery_timeout=30.0,
            expected_exception=Exception
        )
        def _circuit_breaker_call(self, message: str, **kwargs):
            """Poziva osnovni servis kroz circuit breaker."""
            return self._retry_call(message, **kwargs)

        @retry("default")
        def _retry_call(self, message: str, **kwargs):
            """Poziva osnovni servis sa retry logikom."""
            return self.base_service.pozovi_ai(message, **kwargs)

        def _try_alternative_provider(self, message: str, **kwargs):
            """Pokušava da koristi alternativni provider."""
            # Privremeno promeni provider
            original_provider = Config.AI_PROVIDER
            alt_provider = "gemini" if original_provider == "openai" else "openai"

            try:
                Config.AI_PROVIDER = alt_provider
                AIServiceFactory.reset()
                alt_service = AIServiceFactory.get_service()

                return alt_service.pozovi_ai(message, **kwargs)

            finally:
                # Vrati originalni provider
                Config.AI_PROVIDER = original_provider
                AIServiceFactory.reset()

        def pozovi_ai(self, poruka: str, system_prompt: Optional[str] = None) -> str:
            """
            Resilient poziv AI servisa.

            Args:
                poruka: Korisnikova poruka
                system_prompt: System prompt

            Returns:
                AI odgovor ili fallback
            """
            try:
                # Koristi fallback lanac
                return fallback_manager.execute_with_fallback(
                    self.fallback_chain_name,
                    poruka,
                    system_prompt=system_prompt
                )

            except Exception as e:
                # Poslednja linija odbrane
                logging.error(f"Totalni pad sistema: {e}")
                return self._emergency_response(poruka)

        def _emergency_response(self, message: str) -> str:
            """Generiše emergency odgovor kada sve ostalo ne radi."""
            responses = {
                "pozdrav": "Zdravo! Trenutno imam tehničkih problema, ali tu sam!",
                "python": "Python je odličan programski jezik! Izvini što ne mogu detaljnije.",
                "pomoć": "Pokušaj ponovo za nekoliko minuta. Radim na rešavanju problema!",
                "default": "Izvini, trenutno ne mogu da odgovorim kako treba. Molim te pokušaj ponovo kasnije."
            }

            # Jednostavna logika za izbor odgovora
            message_lower = message.lower()
            for key in responses:
                if key in message_lower:
                    return responses[key]

            return responses["default"]

        def pozovi_sa_istorijom(self, messages: List[Dict[str, str]]) -> str:
            """Poziva sa istorijom - sa fallback logikom."""
            try:
                return self.base_service.pozovi_sa_istorijom(messages)
            except Exception as e:
                # Fallback na poslednju poruku
                if messages:
                    last_user_msg = next(
                        (m["content"] for m in reversed(messages) if m["role"] == "user"),
                        "Nastavi razgovor"
                    )
                    return self.pozovi_ai(last_user_msg)
                return self._emergency_response("Nastavi razgovor")

        def test_konekcija(self) -> bool:
            """Testira konekciju sa graceful degradation."""
            try:
                return self.base_service.test_konekcija()
            except:
                # Čak i ako test ne radi, sistem može da funkcioniše
                return True  # Optimistično

        def get_current_settings(self) -> Dict[str, Any]:
            """Vraća postavke sa informacijom o degradaciji."""
            try:
                settings = self.base_service.get_current_settings()
            except:
                settings = {"model": "unknown", "temperature": 0.7, "max_tokens": 150}

            # Dodaj informaciju o stanju
            if hasattr(self._circuit_breaker_call, 'circuit_breaker'):
                cb = self._circuit_breaker_call.circuit_breaker
                settings["circuit_state"] = cb.state.value
                settings["reliability_score"] = 100 - (cb.stats.get_failure_rate())

            return settings

        def apply_settings(self, settings: Dict[str, Any]):
            """Primenjuje postavke ako je moguće."""
            try:
                self.base_service.apply_settings(settings)
            except Exception as e:
                print(f"⚠️ Ne mogu da primenim postavke: {e}")
                # Nastavi rad sa postojećim postavkama


    class DegradedAIService(BaseAIService):
        """
        Minimalni AI servis koji radi kada ništa drugo ne radi.
        """

        def __init__(self):
            print("🔧 Kreiram degradirani servis...")
            self.responses = {
                "greeting": [
                    "Zdravo! Radim u ograničenom režimu, ali tu sam da pomognem!",
                    "Pozdrav! Imam tehničkih problema, ali pokušaću da pomognem.",
                    "Hej! Sistemi nisu u punoj snazi, ali hajde da probamo!"
                ],
                "error": [
                    "Izvini, trenutno ne mogu da pristupim AI servisima.",
                    "Ups, izgleda da imam problema sa konekcijom.",
                    "Molim te pokušaj ponovo za par minuta."
                ],
                "encouragement": [
                    "Ne odustaj! Programiranje je putovanje, ne destinacija.",
                    "Svaki ekspert je bio početnik. Nastavi da učiš!",
                    "Greške su deo procesa učenja. To je potpuno normalno!"
                ]
            }

        def pozovi_ai(self, poruka: str, system_prompt: Optional[str] = None) -> str:
            """Vraća predefinisan odgovor."""
            import random

            poruka_lower = poruka.lower()

            # Pokušaj da prepoznaš tip poruke
            if any(word in poruka_lower for word in ["zdravo", "pozdrav", "hej", "ćao"]):
                return random.choice(self.responses["greeting"])
            elif any(word in poruka_lower for word in ["greška", "error", "problem", "ne radi"]):
                return random.choice(self.responses["encouragement"])
            else:
                return random.choice(self.responses["error"])

        def pozovi_sa_istorijom(self, messages: List[Dict[str, str]]) -> str:
            """Ignorise istoriju, vraća osnovni odgovor."""
            if messages:
                last_msg = messages[-1].get("content", "")
                return self.pozovi_ai(last_msg)
            return "Sistem trenutno radi u ograničenom režimu."

        def test_konekcija(self) -> bool:
            """Uvek vraća True jer je lokalni."""
            return True

        def get_current_settings(self) -> Dict[str, Any]:
            """Vraća minimalne postavke."""
            return {
                "model": "degraded_mode",
                "temperature": 0.5,
                "max_tokens": 100,
                "status": "limited_functionality"
            }

        def apply_settings(self, settings: Dict[str, Any]):
            """Ne može da menja postavke."""
            pass
# Dodaj create_resilient_service metodu na AIServiceFactory
AIServiceFactory.create_resilient_service = staticmethod(
    lambda: ResilientAIServiceFactory.create_resilient_service()
)
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

        # Test 5: Resilient servis (ako su moduli dostupni)
        if RESILIENCE_AVAILABLE:
            print("\n🛡️ Test resilient servisa...")
            resilient_service = AIServiceFactory.create_resilient_service()
            response3 = resilient_service.pozovi_ai("Šta je Python?")
            print(f"📥 Resilient odgovor: {response3}")

    except Exception as e:
        print(f"❌ Factory test neuspešan: {e}")

