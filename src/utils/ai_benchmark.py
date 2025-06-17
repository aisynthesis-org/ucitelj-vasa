"""
AI Benchmark sistem
Poredi performanse različitih AI servisa
"""

import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from ai_services.ai_factory import AIServiceFactory
from utils.config import Config
from utils.performance_tracker import tracker
from utils.optimization_profiles import profile_manager, ProfileType


class AIBenchmark:
    """Benchmark sistem za poređenje AI servisa."""

    # Test pitanja grupisana po kategorijama
    TEST_QUESTIONS = {
        "simple": [
            "Šta je Python?",
            "Koliko je 15 + 27?",
            "Koji je glavni grad Srbije?"
        ],
        "code": [
            "Napiši Python funkciju koja vraća faktorijel broja",
            "Kako da sortiram listu u Python-u?",
            "Objasni razliku između list i tuple"
        ],
        "complex": [
            "Objasni koncept rekurzije sa primerom",
            "Koje su prednosti objektno-orijentisanog programiranja?",
            "Kako funkcioniše garbage collection u Python-u?"
        ],
        "creative": [
            "Napiši kratku priču o programeru početniku",
            "Osmisli analogiju za objasnšnjenje API-ja",
            "Opiši budunost AI tehnologije"
        ]
    }

    def __init__(self):
        """Inicijalizuje benchmark sistem."""
        self.results_dir = Path(__file__).parent.parent.parent / "data" / "benchmarks"
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.current_results = []

    def run_single_test(self, provider: str, question: str,
                       category: str, profile: Optional[ProfileType] = None) -> Dict[str, Any]:
        """
        Pokreće pojedinačni test.

        Args:
            provider: AI provider za testiranje
            question: Test pitanje
            category: Kategorija pitanja
            profile: Opcioni profil za optimizaciju

        Returns:
            Rezultati testa
        """
        try:
            # Promeni provider ako treba
            original_provider = Config.AI_PROVIDER
            if Config.AI_PROVIDER != provider:
                Config.AI_PROVIDER = provider
                AIServiceFactory.reset()

            # Dobij servis
            service = AIServiceFactory.get_service()

            # Primeni profil ako je dat
            if profile:
                settings = profile_manager.apply_profile(
                    profile,
                    service.get_current_settings()
                )
                service.apply_settings(settings)

            # Meri vreme
            start_time = time.time()

            # Pozovi AI
            response = service.pozovi_ai(question)

            # Kraj merenja
            duration = time.time() - start_time

            # Vrati na originalni provider
            if original_provider != provider:
                Config.AI_PROVIDER = original_provider
                AIServiceFactory.reset()

            return {
                "provider": provider,
                "question": question,
                "category": category,
                "profile": profile.value if profile else "default",
                "response": response,
                "response_length": len(response),
                "duration": round(duration, 3),
                "success": True,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            # Vrati na originalni provider
            if original_provider != provider:
                Config.AI_PROVIDER = original_provider
                AIServiceFactory.reset()

            return {
                "provider": provider,
                "question": question,
                "category": category,
                "profile": profile.value if profile else "default",
                "response": None,
                "response_length": 0,
                "duration": 0,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def run_category_benchmark(self, category: str, providers: List[str]) -> List[Dict]:
        """
        Pokreće benchmark za celu kategoriju.

        Args:
            category: Kategorija pitanja za testiranje
            providers: Lista providera za testiranje

        Returns:
            Lista rezultata
        """
        results = []
        questions = self.TEST_QUESTIONS.get(category, [])

        print(f"\n🏃 Pokrećem benchmark za kategoriju: {category.upper()}")
        print("=" * 60)

        for question in questions:
            print(f"\n📝 Pitanje: {question}")

            # Analiziraj koje profile treba
            suggested_profile = profile_manager.analyze_question(question)

            for provider in providers:
                print(f"   🤖 Testiram {provider}...", end="", flush=True)

                # Test sa default postavkama
                result_default = self.run_single_test(provider, question, category)
                results.append(result_default)

                # Test sa optimizovanim profilom
                result_optimized = self.run_single_test(
                    provider, question, category, suggested_profile
                )
                results.append(result_optimized)

                print(f" ✓ ({result_default['duration']}s default, "
                     f"{result_optimized['duration']}s optimized)")

            # Pauza između pitanja
            time.sleep(0.5)

        return results

    def run_full_benchmark(self) -> str:
        """
        Pokreće kompletan benchmark test.

        Returns:
            Putanja do fajla sa rezultatima
        """
        print("\n🚀 POKRETANJE KOMPLETNOG BENCHMARK TESTA")
        print("=" * 60)

        # Proveri koji provideri su dostupni
        available_providers = []
        if Config.OPENAI_API_KEY:
            available_providers.append("openai")
        if Config.GEMINI_API_KEY:
            available_providers.append("gemini")

        if len(available_providers) < 2:
            print("⚠️ Potrebna su oba API ključa za poređenje!")
            return ""

        print(f"✅ Testiram: {', '.join(p.upper() for p in available_providers)}")

        # Pokreni testove za sve kategorije
        all_results = []
        for category in self.TEST_QUESTIONS.keys():
            category_results = self.run_category_benchmark(category, available_providers)
            all_results.extend(category_results)
            self.current_results.extend(category_results)

        # Sačuvaj rezultate
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.results_dir / f"benchmark_{timestamp}.json"

        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Benchmark završen! Rezultati sačuvani u: {results_file}")

        # Generiši izveštaj
        self.generate_report(all_results)

        return str(results_file)

    def generate_report(self, results: List[Dict[str, Any]]):
        """
        Generiše izveštaj na osnovu rezultata.

        Args:
            results: Lista rezultata benchmark-a
        """
        print("\n📊 BENCHMARK IZVEŠTAJ")
        print("=" * 60)

        # Grupiši po providerima
        provider_stats = {}

        for result in results:
            if not result["success"]:
                continue

            provider = result["provider"]
            profile = result["profile"]

            if provider not in provider_stats:
                provider_stats[provider] = {
                    "default": {"times": [], "lengths": []},
                    "optimized": {"times": [], "lengths": []}
                }

            mode = "default" if profile == "default" else "optimized"
            provider_stats[provider][mode]["times"].append(result["duration"])
            provider_stats[provider][mode]["lengths"].append(result["response_length"])

        # Prikaži statistiku
        for provider, stats in provider_stats.items():
            print(f"\n🤖 {provider.upper()}")

            for mode in ["default", "optimized"]:
                if stats[mode]["times"]:
                    avg_time = sum(stats[mode]["times"]) / len(stats[mode]["times"])
                    avg_length = sum(stats[mode]["lengths"]) / len(stats[mode]["lengths"])

                    print(f"\n   {mode.upper()} MODE:")
                    print(f"   - Prosečno vreme: {avg_time:.2f}s")
                    print(f"   - Prosečna dužina: {avg_length:.0f} karaktera")
                    print(f"   - Najbrži odgovor: {min(stats[mode]['times']):.2f}s")
                    print(f"   - Najsporiji odgovor: {max(stats[mode]['times']):.2f}s")

        # Preporuke
        print("\n💡 PREPORUKE NA OSNOVU BENCHMARK-A:")

        # Pronađi najbolje za svaku kategoriju
        category_winners = {}
        for result in results:
            if result["success"] and result["profile"] != "default":
                cat = result["category"]
                if cat not in category_winners:
                    category_winners[cat] = {"provider": result["provider"],
                                           "time": result["duration"]}
                elif result["duration"] < category_winners[cat]["time"]:
                    category_winners[cat] = {"provider": result["provider"],
                                           "time": result["duration"]}

        for cat, winner in category_winners.items():
            print(f"   - {cat.capitalize()} pitanja: {winner['provider'].upper()}")


# Test funkcionalnost
if __name__ == "__main__":
    print("🧪 Test AI Benchmark Sistema")
    print("=" * 50)

    benchmark = AIBenchmark()

    # Test pojedinačnog pitanja
    print("\n1️⃣ Test pojedinačnog pitanja:")
    result = benchmark.run_single_test(
        Config.AI_PROVIDER,
        "Šta je rekurzija?",
        "test"
    )
    print(f"Provider: {result['provider']}")
    print(f"Trajanje: {result['duration']}s")
    print(f"Dužina odgovora: {result['response_length']} karaktera")

    # Samo ako imamo oba providera
    if Config.OPENAI_API_KEY and Config.GEMINI_API_KEY:
        print("\n2️⃣ Pokrećem mini benchmark...")
        # Smanji broj pitanja za test
        benchmark.TEST_QUESTIONS = {
            "simple": ["Šta je Python?"],
            "code": ["Kako da sortiram listu?"]
        }
        benchmark.run_full_benchmark()
