"""
Performance Tracker za AI servise
Meri i analizira performanse različitih AI servisa
"""

import time
import json
import statistics
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from functools import wraps
import os


class PerformanceTracker:
    """Prati performanse AI servisa."""

    def __init__(self, data_file: str = "ai_performance_data.json"):
        """
        Inicijalizuje tracker sa putanjom do fajla za čuvanje podataka.

        Args:
            data_file: Ime fajla za čuvanje podataka
        """
        # Kreiraj data folder ako ne postoji
        self.data_dir = Path(__file__).parent.parent.parent / "data"
        self.data_dir.mkdir(exist_ok=True)

        self.data_file = self.data_dir / data_file
        self.current_metrics = {}
        self.load_data()

    def load_data(self):
        """Učitava postojeće podatke iz fajla."""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.all_metrics = json.load(f)
            except Exception as e:
                print(f"⚠️ Greška pri učitavanju podataka: {e}")
                self.all_metrics = []
        else:
            self.all_metrics = []

    def save_data(self):
        """Čuva podatke u fajl."""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.all_metrics, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Greška pri čuvanju podataka: {e}")

    def start_tracking(self, provider: str, model: str, operation: str):
        """
        Počinje praćenje performansi.

        Args:
            provider: AI provider (openai, gemini)
            model: Model koji se koristi
            operation: Tip operacije (chat, completion, etc)
        """
        tracking_id = f"{provider}_{model}_{int(time.time()*1000)}"
        self.current_metrics[tracking_id] = {
            "provider": provider,
            "model": model,
            "operation": operation,
            "start_time": time.time(),
            "timestamp": datetime.now().isoformat()
        }
        return tracking_id

    def end_tracking(self, tracking_id: str,
                    success: bool = True,
                    response_length: int = 0,
                    error: Optional[str] = None,
                    additional_data: Optional[Dict] = None):
        """
        Završava praćenje i čuva metrike.

        Args:
            tracking_id: ID praćenja
            success: Da li je poziv bio uspešan
            response_length: Dužina odgovora u karakterima
            error: Opis greške ako nije uspešno
            additional_data: Dodatni podaci za čuvanje
        """
        if tracking_id not in self.current_metrics:
            return

        metrics = self.current_metrics[tracking_id]
        end_time = time.time()

        # Izračunaj trajanje
        duration = end_time - metrics["start_time"]

        # Dopuni metrike
        metrics.update({
            "duration_seconds": round(duration, 3),
            "success": success,
            "response_length": response_length,
            "error": error,
            "tokens_per_second": round(response_length / duration, 2) if duration > 0 else 0
        })

        # Dodaj dodatne podatke ako postoje
        if additional_data:
            metrics.update(additional_data)

        # Sačuvaj u listu svih metrika
        self.all_metrics.append(metrics)
        self.save_data()

        # Ukloni iz trenutnih
        del self.current_metrics[tracking_id]

        return metrics

    def track_call(self, provider: str, model: str):
        """
        Dekorator za automatsko praćenje AI poziva.

        Args:
            provider: AI provider
            model: Model koji se koristi

        Returns:
            Dekorator funkcija
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Počni praćenje
                tracking_id = self.start_tracking(provider, model, func.__name__)

                try:
                    # Pozovi originalnu funkciju
                    result = func(*args, **kwargs)

                    # Završi praćenje - uspešno
                    self.end_tracking(
                        tracking_id,
                        success=True,
                        response_length=len(result) if isinstance(result, str) else 0
                    )

                    return result

                except Exception as e:
                    # Završi praćenje - neuspešno
                    self.end_tracking(
                        tracking_id,
                        success=False,
                        error=str(e)
                    )
                    raise

            return wrapper
        return decorator

    def get_provider_stats(self, provider: str) -> Dict[str, Any]:
        """
        Vraća statistiku za određeni provider.

        Args:
            provider: Ime providera

        Returns:
            Dict sa statistikama
        """
        provider_metrics = [m for m in self.all_metrics
                          if m.get("provider") == provider and m.get("success")]

        if not provider_metrics:
            return {
                "provider": provider,
                "total_calls": 0,
                "avg_duration": 0,
                "avg_tokens_per_second": 0,
                "success_rate": 0
            }

        durations = [m["duration_seconds"] for m in provider_metrics]
        tokens_per_sec = [m["tokens_per_second"] for m in provider_metrics]

        total_calls = len(self.all_metrics)
        successful_calls = len(provider_metrics)

        return {
            "provider": provider,
            "total_calls": total_calls,
            "successful_calls": successful_calls,
            "avg_duration": round(statistics.mean(durations), 3),
            "min_duration": round(min(durations), 3),
            "max_duration": round(max(durations), 3),
            "avg_tokens_per_second": round(statistics.mean(tokens_per_sec), 2),
            "success_rate": round(successful_calls / total_calls * 100, 1) if total_calls > 0 else 0
        }

    def compare_providers(self) -> str:
        """
        Poredi performanse svih providera.

        Returns:
            Formatiran string sa poređenjem
        """
        providers = set(m["provider"] for m in self.all_metrics)

        if not providers:
            return "📊 Nema dovoljno podataka za poređenje."

        report = "📊 POREĐENJE AI SERVISA\n"
        report += "=" * 60 + "\n\n"

        for provider in sorted(providers):
            stats = self.get_provider_stats(provider)

            report += f"🤖 {provider.upper()}\n"
            report += f"   Ukupno poziva: {stats['total_calls']}\n"
            report += f"   Uspešnih: {stats['successful_calls']}\n"
            report += f"   Prosečno vreme: {stats['avg_duration']}s\n"
            report += f"   Min/Max vreme: {stats['min_duration']}s / {stats['max_duration']}s\n"
            report += f"   Brzina: ~{stats['avg_tokens_per_second']} karaktera/s\n"
            report += f"   Uspešnost: {stats['success_rate']}%\n\n"

        return report

    def get_recommendations(self) -> Dict[str, str]:
        """
        Daje preporuke na osnovu analize performansi.

        Returns:
            Dict sa preporukama za različite scenarije
        """
        providers = set(m["provider"] for m in self.all_metrics)

        if len(providers) < 2:
            return {
                "general": "Potrebno je više podataka sa oba servisa za preporuke."
            }

        # Analiziraj performanse
        stats = {p: self.get_provider_stats(p) for p in providers}

        # Pronađi najbrži i najstabilniji
        fastest = min(stats.items(), key=lambda x: x[1]["avg_duration"])[0]
        most_stable = max(stats.items(), key=lambda x: x[1]["success_rate"])[0]

        recommendations = {
            "brzi_odgovori": f"Koristi {fastest.upper()} - najbrži prosečni odgovor",
            "stabilnost": f"Koristi {most_stable.upper()} - najbolja uspešnost",
            "eksperimentisanje": "Gemini - besplatan za neograničeno testiranje",
            "produkcija": "OpenAI - industrijski standard sa najboljom dokumentacijom"
        }

        return recommendations


# Globalni tracker instance
tracker = PerformanceTracker()


# Test funkcionalnost
if __name__ == "__main__":
    print("🧪 Test Performance Tracker-a")
    print("=" * 50)

    # Simuliraj nekoliko poziva
    for i in range(3):
        provider = "openai" if i % 2 == 0 else "gemini"

        # Start tracking
        tid = tracker.start_tracking(provider, "test-model", "test_operation")

        # Simuliraj poziv
        time.sleep(0.5 + i * 0.2)

        # End tracking
        tracker.end_tracking(tid, success=True, response_length=100 + i * 50)

    # Prikaži statistiku
    print("\n" + tracker.compare_providers())

    # Prikaži preporuke
    print("💡 PREPORUKE:")
    for scenario, recommendation in tracker.get_recommendations().items():
        print(f"   {scenario}: {recommendation}")
