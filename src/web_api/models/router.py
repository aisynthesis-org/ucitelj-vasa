"""
Provider Router za Učitelja Vasu
Inteligentno rutiranje zahteva ka najboljim AI providerima
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import random

from web_api.models.request_types import RequestType, StructuredRequest
from utils.config import Config
from utils.performance_tracker import tracker
from utils.circuit_breaker import circuit_registry


class RoutingStrategy:
    """Bazna klasa za routing strategije."""

    def select_provider(
        self,
        request: StructuredRequest,
        available_providers: List[str]
    ) -> str:
        """
        Bira provider za zahtev.

        Args:
            request: Strukturiran zahtev
            available_providers: Lista dostupnih providera

        Returns:
            Ime izabranog providera
        """
        raise NotImplementedError


class StaticRoutingStrategy(RoutingStrategy):
    """Statička routing strategija bazirana na tipu zahteva."""

    def __init__(self, rules: Optional[Dict[RequestType, str]] = None):
        """
        Inicijalizuje sa pravilima rutiranja.

        Args:
            rules: Mapa tip -> provider
        """
        self.rules = rules or self._default_rules()

    def _default_rules(self) -> Dict[RequestType, str]:
        """Vraća default pravila rutiranja."""
        return {
            RequestType.CHAT: "gemini",
            RequestType.CODE_GENERATION: "openai",
            RequestType.CODE_DEBUG: "openai",
            RequestType.CONCEPT_EXPLAIN: "gemini",
            RequestType.CODE_REVIEW: "openai",
            RequestType.TRANSLATION: "openai",
            RequestType.OPTIMIZATION: "openai"
        }

    def select_provider(
        self,
        request: StructuredRequest,
        available_providers: List[str]
    ) -> str:
        """Bira provider prema statičkim pravilima."""
        preferred = self.rules.get(request.request_type)

        # Ako preferirani provider nije dostupan, uzmi prvi dostupan
        if preferred and preferred in available_providers:
            return preferred

        return available_providers[0] if available_providers else "openai"


class PerformanceRoutingStrategy(RoutingStrategy):
    """Routing baziran na performansama providera."""

    def __init__(self, metric: str = "latency"):
        """
        Inicijalizuje sa metrikom za poređenje.

        Args:
            metric: "latency", "success_rate", ili "cost"
        """
        self.metric = metric

    def select_provider(
        self,
        request: StructuredRequest,
        available_providers: List[str]
    ) -> str:
        """Bira provider sa najboljim performansama."""
        if not available_providers:
            return "openai"

        if len(available_providers) == 1:
            return available_providers[0]

        # Dobij performanse iz tracker-a
        scores = {}

        for provider in available_providers:
            if self.metric == "latency":
                # Manji je bolji
                avg_latency = self._get_average_latency(provider)
                scores[provider] = -avg_latency if avg_latency else 0
            elif self.metric == "success_rate":
                # Veći je bolji
                scores[provider] = self._get_success_rate(provider)
            else:
                # Default skor
                scores[provider] = 0

        # Vrati provider sa najboljim skorom
        return max(scores.items(), key=lambda x: x[1])[0]

    def _get_average_latency(self, provider: str) -> float:
        """Dobija prosečnu latenciju providera."""
        # Ovo bi trebalo da čita iz tracker-a
        # Za sada vraćamo simulirane vrednosti
        simulated = {
            "openai": 1.5,
            "gemini": 0.8
        }
        return simulated.get(provider, 2.0)

    def _get_success_rate(self, provider: str) -> float:
        """Dobija stopu uspeha providera."""
        simulated = {
            "openai": 0.95,
            "gemini": 0.92
        }
        return simulated.get(provider, 0.90)


class LoadBalancingStrategy(RoutingStrategy):
    """Round-robin load balancing između providera."""

    def __init__(self):
        self.last_selections = {}
        self.provider_counts = {}

    def select_provider(
        self,
        request: StructuredRequest,
        available_providers: List[str]
    ) -> str:
        """Bira sledeći provider u round-robin redosledu."""
        if not available_providers:
            return "openai"

        if len(available_providers) == 1:
            return available_providers[0]

        # Inicijalizuj brojače ako ne postoje
        for provider in available_providers:
            if provider not in self.provider_counts:
                self.provider_counts[provider] = 0

        # Nađi provider sa najmanje poziva
        min_count = min(self.provider_counts.values())
        candidates = [p for p in available_providers
                     if self.provider_counts.get(p, 0) == min_count]

        # Izaberi random između kandidata sa istim brojem
        selected = random.choice(candidates)
        self.provider_counts[selected] += 1

        return selected


class HybridRoutingStrategy(RoutingStrategy):
    """Kombinuje više strategija sa težinskim faktorima."""

    def __init__(self):
        self.static_strategy = StaticRoutingStrategy()
        self.performance_strategy = PerformanceRoutingStrategy()
        self.load_balance_strategy = LoadBalancingStrategy()

        # Težinski faktori (mogu se konfigurisati)
        self.weights = {
            "static": 0.5,
            "performance": 0.3,
            "load_balance": 0.2
        }

    def select_provider(
        self,
        request: StructuredRequest,
        available_providers: List[str]
    ) -> str:
        """Kombinuje strategije za finalni izbor."""
        if not available_providers:
            return "openai"

        if len(available_providers) == 1:
            return available_providers[0]

        # Dobij preporuke od svake strategije
        recommendations = {
            "static": self.static_strategy.select_provider(request, available_providers),
            "performance": self.performance_strategy.select_provider(request, available_providers),
            "load_balance": self.load_balance_strategy.select_provider(request, available_providers)
        }

        # Računaj skorove za svakog providera
        provider_scores = {}

        for strategy, provider in recommendations.items():
            weight = self.weights[strategy]
            if provider not in provider_scores:
                provider_scores[provider] = 0
            provider_scores[provider] += weight

        # Vrati provider sa najvećim skorom
        return max(provider_scores.items(), key=lambda x: x[1])[0]


class SmartProviderRouter:
    """Glavni router koji upravlja svim strategijama."""

    def __init__(self, strategy: Optional[RoutingStrategy] = None):
        """
        Inicijalizuje router.

        Args:
            strategy: Routing strategija (default: HybridRoutingStrategy)
        """
        self.strategy = strategy or HybridRoutingStrategy()
        self.routing_history = []

    def get_available_providers(self) -> List[str]:
        """Vraća listu trenutno dostupnih providera."""
        available = []

        # Proveri koji provideri imaju API ključeve
        if Config.OPENAI_API_KEY:
            # Proveri circuit breaker status
            cb_name = "ai_openai"
            if cb_name in circuit_registry:
                cb = circuit_registry[cb_name]
                if cb.state.value != "open":
                    available.append("openai")
            else:
                available.append("openai")

        if Config.GEMINI_API_KEY:
            cb_name = "ai_gemini"
            if cb_name in circuit_registry:
                cb = circuit_registry[cb_name]
                if cb.state.value != "open":
                    available.append("gemini")
            else:
                available.append("gemini")

        return available

    def route_request(
        self,
        request: StructuredRequest,
        override_provider: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Rutira zahtev ka odgovarajućem provideru.

        Args:
            request: Strukturiran zahtev
            override_provider: Opciono forsiraj provider

        Returns:
            Tuple (provider_name, routing_metadata)
        """
        # Ako je provider eksplicitno zadat
        if override_provider:
            metadata = {
                "strategy": "override",
                "reason": "Explicitly requested",
                "timestamp": datetime.now().isoformat()
            }
            self._record_routing(request, override_provider, metadata)
            return override_provider, metadata

        # Dobij dostupne providere
        available = self.get_available_providers()

        if not available:
            # Nema dostupnih providera
            metadata = {
                "strategy": "fallback",
                "reason": "No available providers",
                "timestamp": datetime.now().isoformat()
            }
            self._record_routing(request, "simulation", metadata)
            return "simulation", metadata

        # Koristi strategiju za izbor
        selected = self.strategy.select_provider(request, available)

        # Generiši metadata
        metadata = {
            "strategy": type(self.strategy).__name__,
            "available_providers": available,
            "request_type": request.request_type.value,
            "selected_reason": self._get_selection_reason(request, selected),
            "timestamp": datetime.now().isoformat()
        }

        # Zapamti routing odluku
        self._record_routing(request, selected, metadata)

        return selected, metadata

    def _get_selection_reason(
        self,
        request: StructuredRequest,
        selected: str
    ) -> str:
        """Generiše razlog izbora providera."""
        if isinstance(self.strategy, StaticRoutingStrategy):
            return f"Best for {request.request_type.value} requests"
        elif isinstance(self.strategy, PerformanceRoutingStrategy):
            return f"Best performance on {self.strategy.metric}"
        elif isinstance(self.strategy, LoadBalancingStrategy):
            return "Load balancing distribution"
        else:
            return "Hybrid strategy decision"

    def _record_routing(
        self,
        request: StructuredRequest,
        provider: str,
        metadata: Dict[str, Any]
    ):
        """Beleži routing odluku za analizu."""
        self.routing_history.append({
            "timestamp": datetime.now(),
            "request_type": request.request_type.value,
            "provider": provider,
            "metadata": metadata
        })

        # Ograniči istoriju na poslednjih 1000 zapisa
        if len(self.routing_history) > 1000:
            self.routing_history = self.routing_history[-1000:]

    def get_routing_statistics(self) -> Dict[str, Any]:
        """Vraća statistiku rutiranja."""
        if not self.routing_history:
            return {"message": "No routing history"}

        # Analiza po provideru
        provider_counts = {}
        type_counts = {}

        for record in self.routing_history:
            provider = record["provider"]
            req_type = record["request_type"]

            provider_counts[provider] = provider_counts.get(provider, 0) + 1
            type_counts[req_type] = type_counts.get(req_type, 0) + 1

        # Analiza po vremenu (poslednji sat)
        recent_records = [
            r for r in self.routing_history
            if r["timestamp"] > datetime.now() - timedelta(hours=1)
        ]

        return {
            "total_requests": len(self.routing_history),
            "providers": provider_counts,
            "request_types": type_counts,
            "recent_hour_count": len(recent_records),
            "strategy": type(self.strategy).__name__
        }


# Globalni router
smart_router = SmartProviderRouter()


# Test funkcionalnost
if __name__ == "__main__":
    print("🧪 Test Provider Router-a")
    print("=" * 50)

    from web_api.models.request_types import RequestAnalyzer

    # Test zahtevi
    test_requests = [
        "Napiši Python funkciju za sortiranje",
        "Objasni mi šta su closure",
        "Zdravo, kako si danas?",
        "Debug ovaj kod koji baca error",
        "Optimizuj ovu petlju"
    ]

    # Testiraj različite strategije
    strategies = [
        ("Static", StaticRoutingStrategy()),
        ("Performance", PerformanceRoutingStrategy()),
        ("LoadBalance", LoadBalancingStrategy()),
        ("Hybrid", HybridRoutingStrategy())
    ]

    for strategy_name, strategy in strategies:
        print(f"\n📋 Testiranje {strategy_name} strategije:")
        router = SmartProviderRouter(strategy)

        for req_text in test_requests[:3]:  # Samo prva 3 za kratak test
            # Kreiraj strukturiran zahtev
            structured = RequestAnalyzer.create_structured_request(req_text)

            # Rutiraj
            provider, metadata = router.route_request(structured)

            print(f"\n  Zahtev: '{req_text[:40]}...'")
            print(f"  Tip: {structured.request_type.value}")
            print(f"  Provider: {provider}")
            print(f"  Razlog: {metadata.get('selected_reason', 'N/A')}")

    # Prikaži statistiku
    print("\n📊 Routing statistika:")
    stats = router.get_routing_statistics()
    print(f"  Ukupno zahteva: {stats['total_requests']}")
    print(f"  Po providerima: {stats['providers']}")
