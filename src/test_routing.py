"""
Test scenariji za request routing sistem
"""

import requests
import json
from typing import Dict, Any


BASE_URL = "http://localhost:8000"


def test_request_types():
    """Testira prepoznavanje tipova zahteva."""
    print("\n🧪 TEST 1: Prepoznavanje tipova zahteva")
    print("=" * 50)

    test_cases = [
        {
            "pitanje": "Napiši funkciju za sortiranje liste u Python-u",
            "expected_type": "code"
        },
        {
            "pitanje": "Zašto mi ovaj kod baca IndexError?",
            "expected_type": "debug"
        },
        {
            "pitanje": "Objasni mi šta je rekurzija",
            "expected_type": "explain"
        },
        {
            "pitanje": "Zdravo, kako si?",
            "expected_type": "chat"
        }
    ]

    for test in test_cases:
        response = requests.post(
            f"{BASE_URL}/pitaj",
            json=test
        )

        if response.status_code == 200:
            data = response.json()
            detected_type = data.get("tip_zahteva", "unknown")

            print(f"\nPitanje: '{test['pitanje'][:50]}...'")
            print(f"Očekivan tip: {test['expected_type']}")
            print(f"Detektovan tip: {detected_type}")
            print(f"Provider: {data.get('provider', {}).get('selected', 'N/A')}")

            if detected_type == test["expected_type"]:
                print("✅ Tačno prepoznat tip!")
            else:
                print("❌ Pogrešan tip")
        else:
            print(f"❌ Greška: {response.status_code}")


def test_structured_requests():
    """Testira strukturirane zahteve."""
    print("\n🧪 TEST 2: Strukturirani zahtevi")
    print("=" * 50)

    structured = {
        "pitanje": "Implementiraj bubble sort algoritam",
        "tip": "code",
        "context": {
            "programming_language": "python",
            "user_level": "beginner"
        },
        "preferences": {
            "temperature": 0.3,
            "max_tokens": 300
        }
    }

    response = requests.post(f"{BASE_URL}/pitaj", json=structured)

    if response.status_code == 200:
        data = response.json()

        print(f"\nStrukturiran zahtev poslat")
        print(f"Tip: {data.get('tip_zahteva')}")
        print(f"Provider: {data.get('provider', {}).get('selected')}")
        print(f"Razlog: {data.get('provider', {}).get('reason')}")
        print(f"Optimizacija: {data.get('optimizacija')}")

        if "context" in data:
            print(f"Kontekst prepoznat: {data['context']}")
    else:
        print(f"❌ Greška: {response.status_code}")
        print(response.json())


def test_provider_override():
    """Testira override providera."""
    print("\n🧪 TEST 3: Override providera")
    print("=" * 50)

    # Test sa forsiranim providerom
    response = requests.post(
        f"{BASE_URL}/pitaj",
        json={"pitanje": "Šta je Python?"},
        params={"force_provider": "gemini"}
    )

    if response.status_code == 200:
        data = response.json()
        selected = data.get("provider", {}).get("selected")
        strategy = data.get("provider", {}).get("strategy")

        print(f"\nForsiran provider: gemini")
        print(f"Korišćen provider: {selected}")
        print(f"Strategija: {strategy}")

        if selected == "gemini" and strategy == "override":
            print("✅ Override radi!")
        else:
            print("❌ Override ne radi")


def test_routing_strategies():
    """Testira različite routing strategije."""
    print("\n🧪 TEST 4: Routing strategije")
    print("=" * 50)

    strategies = ["static", "performance", "loadbalance", "hybrid"]

    for strategy in strategies:
        # Promeni strategiju
        response = requests.post(
            f"{BASE_URL}/routing/strategy",
            params={"strategy_name": strategy}
        )

        if response.status_code == 200:
            print(f"\n📋 Strategija: {strategy}")

            # Testiraj sa istim pitanjem
            test_response = requests.post(
                f"{BASE_URL}/pitaj",
                json={"pitanje": "Napiši hello world program"}
            )

            if test_response.status_code == 200:
                data = test_response.json()
                provider = data.get("provider", {}).get("selected")
                reason = data.get("provider", {}).get("reason")

                print(f"  Provider: {provider}")
                print(f"  Razlog: {reason}")


def test_request_types_endpoint():
    """Testira endpoint za tipove zahteva."""
    print("\n🧪 TEST 5: Request types endpoint")
    print("=" * 50)

    response = requests.get(f"{BASE_URL}/request-types")

    if response.status_code == 200:
        data = response.json()

        print(f"\nPodržano tipova: {data['total']}")
        print("\nTipovi:")

        for req_type in data["supported_types"]:
            print(f"\n  {req_type['type']}:")
            print(f"    Opis: {req_type['description']}")
            print(f"    Preferirani: {req_type['preferred_provider']}")


def test_routing_statistics():
    """Testira routing statistiku."""
    print("\n🧪 TEST 6: Routing statistika")
    print("=" * 50)

    # Prvo generiši neke zahteve
    test_questions = [
        "Kako da sortiram listu?",
        "Napiši funkciju za fibonacci",
        "Debug ovaj kod",
        "Objasni closure",
        "Zdravo!"
    ]

    for q in test_questions:
        requests.post(f"{BASE_URL}/pitaj", json={"pitanje": q})

    # Dobij statistiku
    response = requests.get(f"{BASE_URL}/routing/stats")

    if response.status_code == 200:
        stats = response.json()

        print(f"\nUkupno zahteva: {stats.get('total_requests', 0)}")
        print(f"Trenutna strategija: {stats.get('current_strategy')}")
        print(f"Dostupni provideri: {stats.get('available_providers')}")

        if "providers" in stats:
            print("\nPo providerima:")
            for provider, count in stats["providers"].items():
                print(f"  {provider}: {count}")

        if "request_types" in stats:
            print("\nPo tipovima:")
            for req_type, count in stats["request_types"].items():
                print(f"  {req_type}: {count}")


if __name__ == "__main__":
    print("🚀 ROUTING SYSTEM TEST SUITE")
    print("=" * 60)

    print("\n⚠️  Proveri da li je server pokrenut na http://localhost:8000")
    input("Pritisni ENTER za početak testiranja...")

    try:
        # Proveri da li server radi
        health = requests.get(f"{BASE_URL}/health")
        if health.status_code != 200:
            print("❌ Server ne odgovara!")
            exit(1)

        # Pokreni testove
        test_request_types()
        test_structured_requests()
        test_provider_override()
        test_routing_strategies()
        test_request_types_endpoint()
        test_routing_statistics()

        print("\n✅ Svi testovi završeni!")

    except requests.exceptions.ConnectionError:
        print("❌ Ne mogu da se povežem sa serverom!")
        print("   Pokreni server sa: python src/web_api/run_server.py")
    except Exception as e:
        print(f"❌ Neočekivana greška: {e}")
