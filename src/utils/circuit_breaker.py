"""
Circuit Breaker za Učitelja Vasu
Štiti sistem od kaskadnih padova
"""

import time
from enum import Enum
from typing import Callable, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import functools


class CircuitState(Enum):
    """Stanja Circuit Breaker-a."""
    CLOSED = "closed"  # Normalno stanje - pozivi prolaze
    OPEN = "open"  # Otvoreno - blokira pozive
    HALF_OPEN = "half_open"  # Testira oporavak


@dataclass
class CircuitStats:
    """Statistika za Circuit Breaker."""
    success_count: int = 0
    failure_count: int = 0
    consecutive_failures: int = 0
    last_failure_time: Optional[datetime] = None
    state_changes: list = field(default_factory=list)

    def record_success(self):
        """Beleži uspešan poziv."""
        self.success_count += 1
        self.consecutive_failures = 0

    def record_failure(self):
        """Beleži neuspešan poziv."""
        self.failure_count += 1
        self.consecutive_failures += 1
        self.last_failure_time = datetime.now()

    def get_failure_rate(self) -> float:
        """Računa stopu neuspeha."""
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.0
        return (self.failure_count / total) * 100


class CircuitBreaker:
    """
    Circuit Breaker implementacija.

    Štiti sistem tako što prekida pozive kada servis nije dostupan.
    """

    def __init__(
            self,
            name: str,
            failure_threshold: int = 5,
            recovery_timeout: float = 60.0,
            expected_exception: type = Exception,
            success_threshold: int = 2
    ):
        """
        Inicijalizuje Circuit Breaker.

        Args:
            name: Ime circuit-a (za logovanje)
            failure_threshold: Broj grešaka pre otvaranja
            recovery_timeout: Vreme čekanja pre testiranja (sekunde)
            expected_exception: Tip greške koji se očekuje
            success_threshold: Broj uspešnih poziva za zatvaranje
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.success_threshold = success_threshold

        self.state = CircuitState.CLOSED
        self.stats = CircuitStats()
        self.half_open_success_count = 0
        self.state_changed_at = datetime.now()

    def _should_attempt_reset(self) -> bool:
        """Proverava da li je vreme za pokušaj reseta."""
        return (
                self.state == CircuitState.OPEN and
                datetime.now() > self.state_changed_at + timedelta(seconds=self.recovery_timeout)
        )

    def _record_state_change(self, new_state: CircuitState, reason: str):
        """Beleži promenu stanja."""
        old_state = self.state
        self.state = new_state
        self.state_changed_at = datetime.now()

        self.stats.state_changes.append({
            "time": self.state_changed_at,
            "from": old_state.value,
            "to": new_state.value,
            "reason": reason
        })

        # Prikaži promenu
        emoji = {"closed": "✅", "open": "🔴", "half_open": "🟡"}
        print(f"\n🔌 Circuit '{self.name}' promenio stanje:")
        print(f"   {emoji[old_state.value]} {old_state.value.upper()} → "
              f"{emoji[new_state.value]} {new_state.value.upper()}")
        print(f"   Razlog: {reason}\n")

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Poziva funkciju kroz circuit breaker.

        Args:
            func: Funkcija za pozivanje
            *args: Pozicioni argumenti
            **kwargs: Imenovani argumenti

        Returns:
            Rezultat funkcije

        Raises:
            CircuitOpenError: Ako je circuit otvoren
            Exception: Originalna greška funkcije
        """
        # Proveri da li treba pokušati reset
        if self._should_attempt_reset():
            self._record_state_change(
                CircuitState.HALF_OPEN,
                f"Pokušaj oporavka nakon {self.recovery_timeout}s"
            )
            self.half_open_success_count = 0

        # Ako je OPEN, odbij poziv
        if self.state == CircuitState.OPEN:
            self.stats.record_failure()
            raise CircuitOpenError(
                f"Circuit '{self.name}' je otvoren zbog previše grešaka. "
                f"Pokušaj ponovo za {self._time_until_retry():.0f} sekundi."
            )

        # Pokušaj poziv
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result

        except self.expected_exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Obrađuje uspešan poziv."""
        self.stats.record_success()

        if self.state == CircuitState.HALF_OPEN:
            self.half_open_success_count += 1

            if self.half_open_success_count >= self.success_threshold:
                self._record_state_change(
                    CircuitState.CLOSED,
                    f"Servis oporavljen nakon {self.success_threshold} uspešnih poziva"
                )

    def _on_failure(self):
        """Obrađuje neuspešan poziv."""
        self.stats.record_failure()

        if self.state == CircuitState.HALF_OPEN:
            self._record_state_change(
                CircuitState.OPEN,
                "Test oporavka neuspešan"
            )

        elif (self.state == CircuitState.CLOSED and
              self.stats.consecutive_failures >= self.failure_threshold):
            self._record_state_change(
                CircuitState.OPEN,
                f"Prekoračen prag od {self.failure_threshold} uzastopnih grešaka"
            )

    def _time_until_retry(self) -> float:
        """Vraća sekunde do sledećeg pokušaja."""
        if self.state != CircuitState.OPEN:
            return 0.0

        elapsed = (datetime.now() - self.state_changed_at).total_seconds()
        return max(0, self.recovery_timeout - elapsed)

    def get_status(self) -> dict:
        """Vraća trenutni status circuit breaker-a."""
        return {
            "name": self.name,
            "state": self.state.value,
            "stats": {
                "success_count": self.stats.success_count,
                "failure_count": self.stats.failure_count,
                "failure_rate": f"{self.stats.get_failure_rate():.1f}%",
                "consecutive_failures": self.stats.consecutive_failures
            },
            "time_until_retry": self._time_until_retry() if self.state == CircuitState.OPEN else None
        }

    def reset(self):
        """Ručno resetuje circuit breaker."""
        self._record_state_change(
            CircuitState.CLOSED,
            "Ručni reset"
        )
        self.stats = CircuitStats()
        self.half_open_success_count = 0


class CircuitOpenError(Exception):
    """Greška kada je circuit otvoren."""
    pass


def circuit_breaker(
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception,
        success_threshold: int = 2
):
    """
    Dekorator za dodavanje circuit breaker zaštite.

    Args:
        failure_threshold: Broj grešaka pre otvaranja
        recovery_timeout: Vreme oporavka u sekundama
        expected_exception: Tip greške koji se prati
        success_threshold: Broj uspešnih poziva za zatvaranje
    """

    def decorator(func: Callable) -> Callable:
        # Kreiraj circuit breaker za ovu funkciju
        cb = CircuitBreaker(
            name=func.__name__,
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            expected_exception=expected_exception,
            success_threshold=success_threshold
        )

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return cb.call(func, *args, **kwargs)

        # Dodaj metodu za pristup circuit breaker-u
        wrapper.circuit_breaker = cb

        return wrapper

    return decorator


# Globalni registar svih circuit breaker-a
circuit_registry = {}


def register_circuit(name: str, circuit: CircuitBreaker):
    """Registruje circuit breaker u globalni registar."""
    circuit_registry[name] = circuit


def get_all_circuits_status() -> str:
    """Vraća status svih registrovanih circuit breaker-a."""
    if not circuit_registry:
        return "Nema registrovanih circuit breaker-a."

    status = "🔌 STATUS SVIH CIRCUIT BREAKER-A\n"
    status += "=" * 50 + "\n\n"

    for name, circuit in circuit_registry.items():
        info = circuit.get_status()
        state_emoji = {
            "closed": "✅",
            "open": "🔴",
            "half_open": "🟡"
        }

        status += f"{state_emoji[info['state']]} {name}: {info['state'].upper()}\n"
        status += f"   Uspešnih: {info['stats']['success_count']}\n"
        status += f"   Neuspešnih: {info['stats']['failure_count']}\n"
        status += f"   Stopa greške: {info['stats']['failure_rate']}\n"

        if info['time_until_retry']:
            status += f"   ⏰ Sledeći pokušaj za: {info['time_until_retry']:.0f}s\n"

        status += "\n"

    return status


# Test funkcionalnost
if __name__ == "__main__":
    print("🧪 Test Circuit Breaker-a")
    print("=" * 50)

    # Simulacija servisa koji pada
    fail_count = 0


    @circuit_breaker(failure_threshold=3, recovery_timeout=5.0)
    def unreliable_service():
        global fail_count
        fail_count += 1

        # Prva 4 poziva će pasti
        if fail_count <= 4:
            raise ConnectionError(f"Service unavailable (pokušaj {fail_count})")

        return f"Success nakon {fail_count} pokušaja!"


    # Registruj u globalni registar
    register_circuit("unreliable_service", unreliable_service.circuit_breaker)

    # Test scenario
    print("Simulacija servisa koji pada...\n")

    for i in range(10):
        try:
            result = unreliable_service()
            print(f"✅ Poziv {i + 1}: {result}")
        except CircuitOpenError as e:
            print(f"🔴 Poziv {i + 1}: {e}")
        except ConnectionError as e:
            print(f"❌ Poziv {i + 1}: {e}")

        # Pauza između poziva
        if i == 5:
            print("\n⏰ Čekam 6 sekundi da prođe recovery timeout...\n")
            time.sleep(6)
        else:
            time.sleep(0.5)

    # Prikaži finalni status
    print("\n" + get_all_circuits_status())
