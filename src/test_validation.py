"""
Test scenariji za Pydantic validaciju
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"


def test_simple_validation():
    """Testira osnovnu validaciju pitanja."""
    print("\n🧪 TEST 1: Osnovna validacija")
    print("=" * 50)

    test_cases = [
        {
            "name": "Validno pitanje",
            "data": {"pitanje": "Kako da sortiram listu?"},
            "should_pass": True
        },
        {
            "name": "Prazno pitanje",
            "data": {"pitanje": "   "},
            "should_pass": False
        },
        {
            "name": "Bez pitanja",
            "data": {},
            "should_pass": False
        },
        {
            "name": "Predugačko pitanje",
            "data": {"pitanje": "x" * 2001},
            "should_pass": False
        }
    ]

    for test in test_cases:
        response = requests.post(f"{BASE_URL}/pitaj", json=test["data"])

        print(f"\n{test['name']}:")
        print(f"  Status: {response.status_code}")

        if test["should_pass"]:
            if response.status_code == 200:
                print("  ✅ Prošao kako je očekivano")
            else:
                print("  ❌ Trebalo je da prođe!")
                print(f"  Greška: {response.json()}")
        else:
            if response.status_code == 422:
                print("  ✅ Validacija radila kako treba")
                error = response.json()
                print(f"  Detalj: {error.get('detail', 'N/A')}")
            else:
                print("  ❌ Trebalo je da failuje!")


def test_structured_validation():
    """Testira strukturiranu validaciju."""
    print("\n🧪 TEST 2: Strukturirana validacija")
    print("=" * 50)

    # Validan strukturiran zahtev
    valid_request = {
        "pitanje": "Debug ovaj Python kod",
        "tip": "debug",
        "context": {
            "programming_language": "python",
            "code_snippet": "def test():\n    return None",
            "user_level": "beginner"
        },
        "preferences": {
            "temperature": 0.3,
            "response_style": "detailed",
            "include_examples": True
        }
    }

    response = requests.post(f"{BASE_URL}/pitaj", json=valid_request)

    if response.status_code == 200:
        data = response.json()
        print("✅ Strukturiran zahtev prošao")
        print(f"  Tip: {data.get('tip_zahteva')}")
        print(f"  Kontekst korišćen: {data.get('context_used')}")
        print(f"  Optimizacija: {data.get('optimization')}")
    else:
        print(f"❌ Greška: {response.status_code}")
        print(response.json())

    # Test sa nevalidnim context
    invalid_context = valid_request.copy()
    invalid_context["context"]["user_level"] = "super-expert"  # Nije valjan enum

    response = requests.post(f"{BASE_URL}/pitaj", json=invalid_context)
    print(f"\nNevalidan user level:")
    print(f"  Status: {response.status_code}")
    if response.status_code == 422:
        print("  ✅ Validacija uhvatila grešku")

    # Test sa nevalidnim preferences
    invalid_prefs = valid_request.copy()
    invalid_prefs["preferences"]["temperature"] = 3.0  # Preko maksimuma

    response = requests.post(f"{BASE_URL}/pitaj", json=invalid_prefs)
    print(f"\nNevalidna temperatura:")
    print(f"  Status: {response.status_code}")
    if response.status_code == 422:
        print("  ✅ Validacija uhvatila grešku")


def test_validation_endpoint():
    """Testira /validate-request endpoint."""
    print("\n🧪 TEST 3: Validation endpoint")
    print("=" * 50)

    test_request = {
        "pitanje": "Zašto ovaj kod ne radi?",
        "context": {
            "programming_language": "python"
        }
    }

    response = requests.post(f"{BASE_URL}/validate-request", json=test_request)

    if response.status_code == 200:
        analysis = response.json()
        print("✅ Validacija analize:")
        print(f"  Detektovan tip: {analysis['analysis']['detected_type']}")
        print(f"  Kontekst kompletan: {analysis['analysis']['context_complete']}")

        if analysis['analysis']['context_warnings']:
            print(f"  Upozorenja: {analysis['analysis']['context_warnings']}")

        if analysis['suggestions']:
            print(f"  Sugestije: {analysis['suggestions']}")
    else:
        print(f"❌ Greška: {response.status_code}")


def test_response_validation():
    """Testira da li response odgovara modelu."""
    print("\n🧪 TEST 4: Response validacija")
    print("=" * 50)

    response = requests.post(
        f"{BASE_URL}/pitaj",
        json={"pitanje": "Test validacije response-a"}
    )

    if response.status_code == 200:
        data = response.json()

        # Proveri da li postoje sva očekivana polja
        expected_fields = [
            "pitanje", "odgovor", "tip_zahteva",
            "provider", "optimization", "response_time_ms"
        ]

        missing = [f for f in expected_fields if f not in data]

        if not missing:
            print("✅ Sva polja prisutna u response-u")

            # Proveri strukture
            if isinstance(data.get("provider"), dict):
                provider_fields = ["selected", "reason", "strategy"]
                provider_ok = all(f in data["provider"] for f in provider_fields)
                print(f"  Provider info kompletna: {'✅' if provider_ok else '❌'}")

            if isinstance(data.get("optimization"), dict):
                opt_fields = ["temperature", "max_tokens", "adjusted_for_type"]
                opt_ok = all(f in data["optimization"] for f in opt_fields)
                print(f"  Optimization info kompletna: {'✅' if opt_ok else '❌'}")

        else:
            print(f"❌ Nedostaju polja: {missing}")
    else:
        print(f"❌ Request failed: {response.status_code}")


def test_provider_schemas():
    """Testira provider-specific scheme."""
    print("\n🧪 TEST 5: Provider schemas")
    print("=" * 50)

    # Ovaj test bi trebalo da bude endpoint, ali možemo simulirati
    print("📌 Provider-specific schemas bi trebalo da budu dostupne kroz API")
    print("   Predlog: GET /providers/{provider}/schema")

    # Test provider info sa capabilities
    response = requests.get(f"{BASE_URL}/providers")

    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Dostupni provideri: {len(data['providers'])}")

        for provider in data['providers']:
            print(f"\n  {provider['display_name']}:")
            print(f"    Ime: {provider['name']}")
            print(f"    Features: {provider.get('features', [])}")


def run_all_tests():
    """Pokreće sve testove."""
    print("🚀 PYDANTIC VALIDATION TEST SUITE")
    print("=" * 60)

    print("\n⚠️  Proveri da li je server pokrenut na http://localhost:8000")
    input("Pritisni ENTER za početak testiranja...")

    try:
        # Proveri da li server radi
        health = requests.get(f"{BASE_URL}/health")
        if health.status_code != 200:
            print("❌ Server ne odgovara!")
            return

        test_simple_validation()
        test_structured_validation()
        test_validation_endpoint()
        test_response_validation()
        test_provider_schemas()

        print("\n✅ Svi testovi završeni!")

    except requests.exceptions.ConnectionError:
        print("❌ Ne mogu da se povežem sa serverom!")
        print("   Pokreni server sa: python src/web_api/run_server.py")
    except Exception as e:
        print(f"❌ Neočekivana greška: {e}")


if __name__ == "__main__":
    run_all_tests()
