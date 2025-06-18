"""
Fallback Manager za Učitelja Vasu
Upravlja rezervnim strategijama kada glavni servisi ne rade
"""

from typing import List, Callable, Any, Optional, Dict
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from utils.retry_handler import SmartRetry, RetryConfig
from utils.circuit_breaker import CircuitOpenError


class FallbackLevel(Enum):
    """Nivoi fallback strategije."""
    PRIMARY = "primary"  # Glavni servis
    SECONDARY = "secondary"  # Rezervni servis
    TERTIARY = "tertiary"  # Lokalna alternativa
    EMERGENCY = "emergency"  # Poslednja linija odbrane


@dataclass
class FallbackOption:
    """Definiše jednu fallback opciju."""
    name: str
    level: FallbackLevel
    handler: Callable
    description: str
    degradation_message: Optional[str] = None


class FallbackChain:
    """
    Lanac fallback opcija koji se izvršavaju redom.
    """

    def __init__(self, name: str):
        """
        Inicijalizuje fallback lanac.

        Args:
            name: Ime lanca (za logovanje)
        """
        self.name = name
        self.options: List[FallbackOption] = []
        self.execution_history = []

    def add_option(self, option: FallbackOption):
        """Dodaje opciju u lanac."""
        self.options.append(option)
        # Sortiraj po nivou (PRIMARY=0, SECONDARY=1, itd)
        self.options.sort(key=lambda x: list(FallbackLevel).index(x.level))

    def execute(self, *args, **kwargs) -> Any:
        """
        Izvršava lanac - pokušava opcije redom dok jedna ne uspe.

        Args:
            *args: Argumenti za handler funkcije
            **kwargs: Imenovani argumenti

        Returns:
            Rezultat prve uspešne opcije

        Raises:
            Exception: Ako nijedna opcija ne uspe
        """
        errors = []
        start_time = datetime.now()

        for i, option in enumerate(self.options):
            try:
                print(f"\n🔄 Pokušavam {option.level.value}: {option.name}")

                # Pozovi handler
                result = option.handler(*args, **kwargs)

                # Uspeh! Zapamti u istoriji
                self.execution_history.append({
                    "time": datetime.now(),
                    "option": option.name,
                    "level": option.level.value,
                    "success": True,
                    "attempt_number": i + 1,
                    "total_time": (datetime.now() - start_time).total_seconds()
                })

                # Ako nije primary, obavesti korisnika o degradaciji
                if option.level != FallbackLevel.PRIMARY and option.degradation_message:
                    print(f"ℹ️ {option.degradation_message}")

                return result

            except Exception as e:
                errors.append((option.name, str(e)))
                print(f"   ❌ {option.name} neuspešan: {str(e)[:50]}...")

                # Zapamti neuspeh
                self.execution_history.append({
                    "time": datetime.now(),
                    "option": option.name,
                    "level": option.level.value,
                    "success": False,
                    "error": str(e),
                    "attempt_number": i + 1
                })

        # Sve opcije neuspešne
        error_summary = "\n".join([f"  - {name}: {err}" for name, err in errors])
        raise Exception(
            f"Sve fallback opcije za '{self.name}' su neuspešne:\n{error_summary}"
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Vraća statistiku korišćenja fallback opcija."""
        stats = {
            "total_executions": len(self.execution_history),
            "by_level": {},
            "success_rate": 0
        }

        if not self.execution_history:
            return stats

        # Računaj statistiku po nivou
        for level in FallbackLevel:
            level_calls = [h for h in self.execution_history if h["level"] == level.value]
            if level_calls:
                successful = sum(1 for h in level_calls if h["success"])
                stats["by_level"][level.value] = {
                    "total": len(level_calls),
                    "successful": successful,
                    "rate": (successful / len(level_calls)) * 100
                }

        # Ukupna stopa uspeha
        total_success = sum(1 for h in self.execution_history if h["success"])
        stats["success_rate"] = (total_success / len(self.execution_history)) * 100

        return stats


class FallbackManager:
    """
    Centralizovani manager za sve fallback strategije.
    """

    def __init__(self):
        self.chains: Dict[str, FallbackChain] = {}
        self.smart_retry = SmartRetry()

    def create_chain(self, name: str) -> FallbackChain:
        """Kreira novi fallback lanac."""
        chain = FallbackChain(name)
        self.chains[name] = chain
        return chain

    def get_chain(self, name: str) -> Optional[FallbackChain]:
        """Vraća postojeći lanac."""
        return self.chains.get(name)

    def execute_with_fallback(
            self,
            chain_name: str,
            *args,
            retry_config: Optional[RetryConfig] = None,
            **kwargs
    ) -> Any:
        """
        Izvršava lanac sa retry logikom.

        Args:
            chain_name: Ime lanca za izvršavanje
            *args: Argumenti za handler funkcije
            retry_config: Konfiguracija za retry
            **kwargs: Imenovani argumenti

        Returns:
            Rezultat izvršavanja
        """
        chain = self.chains.get(chain_name)
        if not chain:
            raise ValueError(f"Nepoznat fallback lanac: {chain_name}")

        # Ako nema retry config, samo izvrši lanac
        if not retry_config:
            return chain.execute(*args, **kwargs)

        # Inače, koristi smart retry
        success, result = self.smart_retry.execute_with_retry(
            chain.execute,
            args=args,
            kwargs=kwargs,
            config=retry_config
        )

        if success:
            return result
        else:
            raise result  # result je Exception u slučaju neuspeha

    def get_health_report(self) -> str:
        """Generiše izveštaj o zdravlju sistema."""
        report = "🏥 FALLBACK SISTEM - ZDRAVSTVENI IZVEŠTAJ\n"
        report += "=" * 60 + "\n\n"

        if not self.chains:
            report += "Nema konfigurisanih fallback lanaca.\n"
            return report

        for name, chain in self.chains.items():
            stats = chain.get_statistics()

            report += f"📊 Lanac: {name}\n"
            report += f"   Ukupno izvršavanja: {stats['total_executions']}\n"
            report += f"   Stopa uspeha: {stats['success_rate']:.1f}%\n"

            if stats['by_level']:
                report += "   Po nivoima:\n"
                for level, level_stats in stats['by_level'].items():
                    report += f"     - {level}: {level_stats['successful']}/{level_stats['total']} "
                    report += f"({level_stats['rate']:.1f}%)\n"

            report += "\n"

        return report


# Globalni fallback manager
fallback_manager = FallbackManager()


# Pomocne funkcije za brže kreiranje opcija
def create_ai_fallback_chain(
        openai_handler: Callable,
        gemini_handler: Callable,
        simulation_handler: Callable,
        static_response: str = "Izvini, trenutno ne mogu da odgovorim. Pokušaj ponovo kasnije."
) -> FallbackChain:
    """
    Kreira standardni AI fallback lanac.

    Args:
        openai_handler: Funkcija za OpenAI poziv
        gemini_handler: Funkcija za Gemini poziv
        simulation_handler: Funkcija za lokalnu simulaciju
        static_response: Poslednji fallback odgovor

    Returns:
        Konfigurisani FallbackChain
    """
    chain = fallback_manager.create_chain("ai_response")

    # Primary - OpenAI
    chain.add_option(FallbackOption(
        name="OpenAI API",
        level=FallbackLevel.PRIMARY,
        handler=openai_handler,
        description="Glavni AI servis"
    ))

    # Secondary - Gemini
    chain.add_option(FallbackOption(
        name="Google Gemini",
        level=FallbackLevel.SECONDARY,
        handler=gemini_handler,
        description="Rezervni AI servis",
        degradation_message="Koristim rezervni AI servis (Gemini)"
    ))

    # Tertiary - Lokalna simulacija
    chain.add_option(FallbackOption(
        name="Lokalna simulacija",
        level=FallbackLevel.TERTIARY,
        handler=simulation_handler,
        description="Offline simulacija",
        degradation_message="AI servisi nisu dostupni - koristim lokalnu simulaciju"
    ))

    # Emergency - Statički odgovor
    chain.add_option(FallbackOption(
        name="Statički odgovor",
        level=FallbackLevel.EMERGENCY,
        handler=lambda *args, **kwargs: static_response,
        description="Predefinisan odgovor",
        degradation_message="Svi servisi su trenutno nedostupni"
    ))

    return chain


# Test funkcionalnost
if __name__ == "__main__":
    print("🧪 Test Fallback Manager-a")
    print("=" * 50)


    # Simuliraj različite servise
    def primary_service(msg):
        """Uvek pada."""
        raise ConnectionError("Primary service down")


    def secondary_service(msg):
        """Pada prva 2 puta."""
        if not hasattr(secondary_service, 'count'):
            secondary_service.count = 0
        secondary_service.count += 1

        if secondary_service.count <= 2:
            raise TimeoutError("Secondary service timeout")
        return f"Secondary odgovor na: {msg}"


    def backup_service(msg):
        """Uvek radi."""
        return f"Backup odgovor na: {msg}"


    # Kreiraj lanac
    chain = fallback_manager.create_chain("test_chain")

    chain.add_option(FallbackOption(
        "Primary", FallbackLevel.PRIMARY, primary_service, "Glavni servis"
    ))

    chain.add_option(FallbackOption(
        "Secondary", FallbackLevel.SECONDARY, secondary_service, "Rezervni servis",
        "Koristim rezervni servis"
    ))

    chain.add_option(FallbackOption(
        "Backup", FallbackLevel.TERTIARY, backup_service, "Backup servis",
        "Koristim backup - ograničene mogućnosti"
    ))

    # Test izvršavanja
    print("Test 1: Prvi pokušaj")
    try:
        result = chain.execute("Test poruka 1")
        print(f"✅ Rezultat: {result}")
    except Exception as e:
        print(f"❌ Greška: {e}")

    print("\nTest 2: Drugi pokušaj")
    try:
        result = chain.execute("Test poruka 2")
        print(f"✅ Rezultat: {result}")
    except Exception as e:
        print(f"❌ Greška: {e}")

    print("\nTest 3: Treći pokušaj")
    try:
        result = chain.execute("Test poruka 3")
        print(f"✅ Rezultat: {result}")
    except Exception as e:
        print(f"❌ Greška: {e}")

    # Prikaži statistiku
    print("\n" + fallback_manager.get_health_report())
