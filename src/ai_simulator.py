"""
Simulator AI API poziva
Ovaj modul simulira AI odgovore dok ne dobijemo pravi API ključ.
"""

import json
import random
import time
from typing import Dict, List


def simuliraj_ai_odgovor(poruka: str) -> str:
    """
    Simulira AI odgovor sa random kašnjenjem.
    U stvarnom API pozivu, ovo bi slalo zahtev OpenAI serveru.
    """
    # Simuliraj network kašnjenje
    vreme_odgovora = random.uniform(0.5, 2.0)
    print(f"🤔 Razmišljam... (simulacija {vreme_odgovora:.1f}s kašnjenja)")
    time.sleep(vreme_odgovora)

    # Simulirani odgovori za različite tipove pitanja
    odgovori = {
        "pozdrav": [
            "Zdravo! Kako mogu da ti pomognem danas sa učenjem programiranja?",
            "Pozdrav! Spreman sam da ti pomognem da savladaš Python!",
            "Hej! Drago mi je što si tu. Šta te zanima danas?"
        ],
        "python": [
            "Python je odličan izbor za početnike! Hajde da učimo korak po korak.",
            "Python sintaksa je vrlo čitljiva. Pokazaću ti na primerima.",
            "Divno pitanje o Python-u! Evo objašnjenja..."
        ],
        "default": [
            "Interesantno pitanje! Hajde da ga istražimo zajedno.",
            "Dobro pitanje! Evo kako bih ja to objasnio...",
            "Hmm, hajde da razmislimo o tome korak po korak."
        ]
    }

    # Jednostavna logika za izbor odgovora
    poruka_lower = poruka.lower()
    if any(rec in poruka_lower for rec in ["zdravo", "pozdrav", "hej", "ćao"]):
        kategorija = "pozdrav"
    elif "python" in poruka_lower or "programir" in poruka_lower:
        kategorija = "python"
    else:
        kategorija = "default"

    return random.choice(odgovori[kategorija])


def prikazi_api_strukturu(poruka: str) -> Dict:
    """
    Prikazuje kako bi izgledao pravi API poziv.
    Ovo je edukativno - pokazuje strukturu koju ćemo koristiti.
    """
    api_struktura = {
        "url": "https://api.openai.com/v1/chat/completions",
        "method": "POST",
        "headers": {
            "Authorization": "Bearer YOUR_API_KEY_HERE",
            "Content-Type": "application/json"
        },
        "body": {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "Ti si Učitelj Vasa, AI asistent za učenje programiranja."
                },
                {
                    "role": "user",
                    "content": poruka
                }
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }
    }
    return api_struktura


def demonstriraj_api_komunikaciju():
    """Demonstrira kako će izgledati komunikacija sa pravim API-jem."""
    print("\n" + "=" * 60)
    print("🎓 DEMONSTRACIJA API KOMUNIKACIJE")
    print("=" * 60)

    # Korisnikov unos
    test_poruka = "Objasni mi šta su promenljive u Python-u"
    print(f"\n📤 TVOJE PITANJE: {test_poruka}")

    # Prikaz API strukture
    print("\n📋 STRUKTURA API POZIVA:")
    api_data = prikazi_api_strukturu(test_poruka)
    print(json.dumps(api_data, indent=2, ensure_ascii=False))

    # Simulirani odgovor
    print("\n⏳ SLANJE ZAHTEVA...")
    odgovor = simuliraj_ai_odgovor(test_poruka)

    print(f"\n📥 AI ODGOVOR: {odgovor}")

    # Objašnjenje
    print("\n💡 ŠTA SE DESILO:")
    print("1. Pripremili smo pitanje u JSON formatu")
    print("2. Dodali smo API ključ u header (za autentifikaciju)")
    print("3. Poslali POST zahtev na OpenAI endpoint")
    print("4. Sačekali odgovor (simulirano kašnjenje)")
    print("5. Primili i prikazali AI odgovor")
    print("\n⚠️  Napomena: Ovo je simulacija. Sutra ćemo koristiti pravi API!")


if __name__ == "__main__":
    demonstriraj_api_komunikaciju()
