"""
Jednostavan monitoring skript za Učitelja Vasu API
"""

import requests
import time
from datetime import datetime


def check_api_status(base_url="http://localhost:8000"):
    """Proverava status API-ja i prikazuje rezultate."""
    print(f"\n{'=' * 60}")
    print(f"🔍 Učitelj Vasa API Monitor - {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'=' * 60}")

    # Proveri osnovni health
    try:
        response = requests.get(f"{base_url}/health", timeout=2)
        if response.status_code == 200:
            print("✅ API Server: ONLINE")
        else:
            print(f"⚠️  API Server: Status {response.status_code}")
    except:
        print("❌ API Server: OFFLINE")
        return

    # Proveri AI health
    try:
        response = requests.get(f"{base_url}/health/ai", timeout=5)
        data = response.json()
        status_icon = {
            "healthy": "✅",
            "degraded": "⚠️",
            "unavailable": "❌"
        }.get(data.get("status", "unknown"), "❓")

        print(f"{status_icon} AI Service: {data.get('status', 'unknown').upper()}")
        print(f"   Provider: {data.get('provider', 'N/A')}")
        if data.get("model"):
            print(f"   Model: {data.get('model')}")
    except:
        print("❌ AI Service: Ne mogu da proverim")

    # Proveri providere
    try:
        response = requests.get(f"{base_url}/providers", timeout=2)
        data = response.json()
        print(f"\n📡 Dostupni provideri:")
        for provider in data.get("providers", []):
            active = " (AKTIVAN)" if provider.get("is_active") else ""
            print(f"   • {provider.get('display_name', provider.get('name'))}{active}")
    except:
        print("❌ Ne mogu da dobijem listu providera")

    # Proveri statistike
    try:
        response = requests.get(f"{base_url}/providers/statistics", timeout=2)
        data = response.json()
        total = data.get("total_requests", 0)
        if total > 0:
            print(f"\n📊 Statistike:")
            print(f"   Ukupno zahteva: {total}")
            for provider, stats in data.get("providers", {}).items():
                print(f"   {provider}: {stats.get('success_rate', 0)}% uspešnih")
    except:
        pass  # Statistike nisu kritične


def monitor_loop(interval=10):
    """Pokreće monitoring u petlji."""
    print("🚀 Pokrećem monitoring Učitelja Vase...")
    print(f"   Provera svakih {interval} sekundi")
    print("   Pritisni Ctrl+C za prekid")

    try:
        while True:
            check_api_status()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring zaustavljen")


if __name__ == "__main__":
    # Možeš pokrenuti samo jednu proveru
    # check_api_status()

    # Ili monitoring petlju
    monitor_loop(interval=15)
