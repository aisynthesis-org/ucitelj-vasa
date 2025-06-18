"""
Retry Handler za Učitelja Vasu
Implementira pametnu retry logiku sa exponential backoff
"""

import time
import random
import functools
from typing import Callable, Any, Optional, Tuple, Type
from datetime import datetime, timedelta


class RetryError(Exception):
    """Custom exception kada retry ne uspe nakon svih pokušaja."""

    def __init__(self, message: str, last_error: Optional[Exception] = None):
        super().__init__(message)
        self.last_error = last_error


class RetryConfig:
    """Konfiguracija za retry ponašanje."""

    def __init__(
            self,
            max_attempts: int = 3,
            initial_delay: float = 1.0,
            max_delay: float = 60.0,
            exponential_base: float = 2.0,
            jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter


# Globalne konfiguracije za različite scenarije
RETRY_CONFIGS = {
    "default": RetryConfig(max_attempts=3, initial_delay=1.0),
    "aggressive": RetryConfig(max_attempts=5, initial_delay=0.5),
    "conservative": RetryConfig(max_attempts=2, initial_delay=2.0),
    "api_rate_limit": RetryConfig(max_attempts=3, initial_delay=5.0, max_delay=30.0)
}


def calculate_delay(attempt: int, config: RetryConfig) -> float:
    """
    Računa koliko dugo da čeka pre sledećeg pokušaja.

    Args:
        attempt: Broj trenutnog pokušaja (počinje od 0)
        config: Retry konfiguracija

    Returns:
        Broj sekundi za čekanje
    """
    # Eksponencijalni backoff
    delay = min(
        config.initial_delay * (config.exponential_base ** attempt),
        config.max_delay
    )

    # Dodaj jitter ako je omogućen (random ±25%)
    if config.jitter:
        jitter_range = delay * 0.25
        delay = delay + random.uniform(-jitter_range, jitter_range)

    return max(0.1, delay)  # Minimum 0.1 sekunde


def should_retry(error: Exception) -> bool:
    """
    Određuje da li greška zaslužuje retry.

    Args:
        error: Exception koja se desila

    Returns:
        True ako treba pokušati ponovo, False inače
    """
    # Greške koje UVEK zaslužuju retry
    retry_errors = [
        "rate_limit", "rate limit",
        "timeout", "timed out",
        "connection", "network",
        "temporary", "unavailable",
        "429", "503", "502", "500"  # HTTP status kodovi
    ]

    error_str = str(error).lower()

    # Proveri da li poruka sadrži bilo koju od retry reči
    for retry_word in retry_errors:
        if retry_word in error_str:
            return True

    # Greške koje NIKAD ne zaslužuju retry
    no_retry_errors = [
        "invalid api key", "unauthorized",
        "insufficient_quota", "payment",
        "invalid request", "bad request"
    ]

    for no_retry_word in no_retry_errors:
        if no_retry_word in error_str:
            return False

    # Default: ne pokušavaj ponovo
    return False


def retry_with_config(config: RetryConfig):
    """
    Dekorator koji dodaje retry logiku funkciji.

    Args:
        config: RetryConfig objekat sa postavkama

    Returns:
        Dekorator funkcija
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_error = None

            for attempt in range(config.max_attempts):
                try:
                    # Pokušaj da pozoveš funkciju
                    result = func(*args, **kwargs)

                    # Ako je uspelo, vrati rezultat
                    if attempt > 0:
                        print(f"✅ Uspelo iz {attempt + 1}. pokušaja!")

                    return result

                except Exception as e:
                    last_error = e

                    # Proveri da li treba retry
                    if not should_retry(e):
                        print(f"❌ Greška ne zaslužuje retry: {str(e)[:100]}")
                        raise

                    # Ako je poslednji pokušaj, ne čekaj
                    if attempt == config.max_attempts - 1:
                        break

                    # Izračunaj delay
                    delay = calculate_delay(attempt, config)

                    print(f"⚠️ Pokušaj {attempt + 1}/{config.max_attempts} neuspešan: {str(e)[:50]}...")
                    print(f"⏳ Čekam {delay:.1f} sekundi pre sledećeg pokušaja...")

                    time.sleep(delay)

            # Svi pokušaji neuspešni
            raise RetryError(
                f"Neuspešno nakon {config.max_attempts} pokušaja",
                last_error
            )

        return wrapper

    return decorator


def retry(config_name: str = "default"):
    """
    Jednostavan dekorator koji koristi predefinisanu konfiguraciju.

    Args:
        config_name: Ime konfiguracije iz RETRY_CONFIGS

    Returns:
        Dekorator sa odgovarajućom konfiguracijom
    """
    config = RETRY_CONFIGS.get(config_name, RETRY_CONFIGS["default"])
    return retry_with_config(config)


class SmartRetry:
    """Napredniji retry sistem sa pamćenjem i statistikom."""

    def __init__(self):
        self.failure_history = {}  # Pamti greške po funkciji
        self.success_after_retry = {}  # Broji uspešne retry pokušaje

    def execute_with_retry(
            self,
            func: Callable,
            args: tuple = (),
            kwargs: dict = None,
            config: Optional[RetryConfig] = None
    ) -> Tuple[bool, Any]:
        """
        Izvršava funkciju sa retry logikom i vraća (success, result).

        Args:
            func: Funkcija za izvršavanje
            args: Pozicioni argumenti
            kwargs: Imenovani argumenti
            config: Retry konfiguracija

        Returns:
            Tuple (da li je uspelo, rezultat ili greška)
        """
        if kwargs is None:
            kwargs = {}

        if config is None:
            config = RETRY_CONFIGS["default"]

        func_name = func.__name__
        last_error = None

        for attempt in range(config.max_attempts):
            try:
                result = func(*args, **kwargs)

                # Uspeh!
                if attempt > 0:
                    # Zapamti da je retry pomogao
                    self.success_after_retry[func_name] = \
                        self.success_after_retry.get(func_name, 0) + 1
                    print(f"✅ {func_name} uspeo iz {attempt + 1}. pokušaja!")

                # Očisti istoriju grešaka za ovu funkciju
                if func_name in self.failure_history:
                    del self.failure_history[func_name]

                return True, result

            except Exception as e:
                last_error = e

                # Zapamti grešku
                if func_name not in self.failure_history:
                    self.failure_history[func_name] = []

                self.failure_history[func_name].append({
                    "time": datetime.now(),
                    "error": str(e),
                    "attempt": attempt + 1
                })

                # Proveri da li treba retry
                if not should_retry(e) or attempt == config.max_attempts - 1:
                    return False, e

                # Delay sa backoff
                delay = calculate_delay(attempt, config)
                print(f"⏳ Retry {func_name} za {delay:.1f}s...")
                time.sleep(delay)

        return False, last_error

    def get_reliability_score(self, func_name: str) -> float:
        """
        Vraća score pouzdanosti funkcije (0-100).

        Args:
            func_name: Ime funkcije

        Returns:
            Score od 0 do 100
        """
        if func_name not in self.failure_history:
            return 100.0  # Nema grešaka

        # Broj skorašnjih grešaka (poslednji sat)
        recent_errors = [
            err for err in self.failure_history[func_name]
            if err["time"] > datetime.now() - timedelta(hours=1)
        ]

        # Formula: 100 - (10 * broj_grešaka), minimum 0
        score = max(0, 100 - (10 * len(recent_errors)))

        # Bonus poeni za uspešne retry pokušaje
        retry_success = self.success_after_retry.get(func_name, 0)
        score = min(100, score + (retry_success * 5))

        return score


# Globalna instanca
smart_retry = SmartRetry()

# Test funkcionalnost
if __name__ == "__main__":
    print("🧪 Test Retry Handler-a")
    print("=" * 50)

    # Simulacija funkcije koja ponekad ne radi
    call_count = 0


    @retry("default")
    def flaky_function():
        global call_count
        call_count += 1

        if call_count < 3:
            raise ConnectionError(f"Network timeout (pokušaj {call_count})")

        return f"Uspeh nakon {call_count} pokušaja!"


    # Test
    try:
        result = flaky_function()
        print(f"\n✅ Rezultat: {result}")
    except RetryError as e:
        print(f"\n❌ Retry neuspešan: {e}")
        print(f"   Poslednja greška: {e.last_error}")

    # Test smart retry
    print("\n" + "=" * 50)
    print("Test Smart Retry sistema:")


    def another_flaky_function(threshold: int):
        import random
        if random.random() < 0.6:  # 60% šanse za grešku
            raise TimeoutError("API timeout")
        return "Success!"


    # Pokreni nekoliko puta
    for i in range(5):
        success, result = smart_retry.execute_with_retry(
            another_flaky_function,
            args=(i,)
        )
        print(f"Pokušaj {i + 1}: {'Uspeh' if success else 'Neuspeh'}")
        time.sleep(0.5)

    # Prikaži statistiku
    print(f"\nPouzdanost funkcije: {smart_retry.get_reliability_score('another_flaky_function'):.1f}%")
