"""
Glavni program za Učitelja Vasu
Sa podrškom za profilisanje i optimizaciju
"""

# Dodaj src folder u Python path
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vasa_core import pozdrav, predstavi_se, glavni_meni, VASA_LICNOST
from ai_simulator import simuliraj_ai_odgovor
from utils.config import Config
from utils.performance_tracker import tracker
from utils.optimization_profiles import profile_manager, ProfileType
from utils.ai_benchmark import AIBenchmark
from ai_services.ai_factory import AIServiceFactory
from ai_services.base_service import BaseAIService
from typing import Optional

# Dodaj ove importe nakon postojećih
from utils.circuit_breaker import get_all_circuits_status, CircuitOpenError
from utils.fallback_manager import fallback_manager
from utils.retry_handler import smart_retry

# Globalna varijabla za AI servis
ai_service: Optional[BaseAIService] = None
current_profile: Optional[ProfileType] = None


# Zameni postojeću inicijalizuj_ai_servis funkciju sa:
def inicijalizuj_ai_servis():
    """Pokušava da kreira resilient AI servis."""
    global ai_service

    print("\n🔧 Inicijalizujem AI servis sa naprednom zaštitom...")

    try:
        # Koristi resilient factory
        ai_service = AIServiceFactory.create_resilient_service()

        print(f"✅ {Config.AI_PROVIDER.upper()} servis pokrenut sa:")
        print("   ✓ Retry logikom (automatski pokušaji)")
        print("   ✓ Circuit breaker zaštitom")
        print("   ✓ Fallback strategijama")
        print("   ✓ Graceful degradation podrškom")

        # Test da li radi
        if ai_service.test_konekcija():
            print("   ✓ Konekcija stabilna!")
        else:
            print("   ⚠️ Konekcija nestabilna, ali sistem će pokušati da radi")

        return True

    except Exception as e:
        print(f"⚠️ Problem pri inicijalizaciji: {e}")
        print("📌 Sistem će raditi u degradiranom režimu")

        # Čak i ako inicijalizacija ne uspe, imamo degraded servis
        from ai_services.ai_factory import DegradedAIService
        ai_service = DegradedAIService()

        return False


# Dodaj novu opciju u glavni_meni_profilisanje funkciju:
def prikazi_sistem_zdravlje():
    """Prikazuje zdravlje i status svih resilience komponenti."""
    print("\n🏥 ZDRAVLJE SISTEMA")
    print("=" * 60)

    # Circuit breakers status
    print("\n" + get_all_circuits_status())

    # Fallback statistike
    print(fallback_manager.get_health_report())

    # Retry statistike
    if hasattr(ai_service, '_circuit_breaker_call'):
        cb = ai_service._circuit_breaker_call.circuit_breaker
        print(f"📊 Pouzdanost glavnog servisa: {100 - cb.stats.get_failure_rate():.1f}%")

    # Degradacija status
    if hasattr(ai_service, 'get_current_settings'):
        settings = ai_service.get_current_settings()
        if settings.get('status') == 'limited_functionality':
            print("\n⚠️ UPOZORENJE: Sistem radi u DEGRADIRANOM režimu!")
            print("   Funkcionalnosti su ograničene.")


def postavi_pitanje_vasi(pitanje: str, auto_optimize: bool = True) -> str:
    """
    Postavlja pitanje Vasi koristeći AI ili simulaciju.

    Args:
        pitanje: Korisnikovo pitanje
        auto_optimize: Da li automatski optimizovati postavke

    Returns:
        AI odgovor
    """
    global current_profile

    if ai_service:
        # Analiziraj pitanje i primeni profil ako treba
        if auto_optimize:
            suggested_profile = profile_manager.analyze_question(pitanje)

            # Prikaži koji profil se koristi
            profile_info = profile_manager.get_profile(suggested_profile)
            print(f"📋 [Koristim profil: {profile_info.name}]")

            # Primeni profil
            settings = profile_manager.apply_profile(
                suggested_profile,
                ai_service.get_current_settings()
            )
            ai_service.apply_settings(settings)
            current_profile = suggested_profile

            # Modifikuj system prompt sa addon-om
            modified_prompt = VASA_LICNOST + profile_info.system_prompt_addon
        else:
            modified_prompt = VASA_LICNOST

        # Koristi pravi AI
        print(f"🤖 [Koristim {Config.AI_PROVIDER.upper()} AI model...]")
        return ai_service.pozovi_ai(pitanje, system_prompt=modified_prompt)
    else:
        # Fallback na simulaciju
        print("🎭 [Koristim simulaciju...]")
        return simuliraj_ai_odgovor(pitanje)


def prikazi_performanse():
    """Prikazuje statistiku performansi."""
    print("\n" + tracker.compare_providers())

    # Prikaži preporuke
    recommendations = tracker.get_recommendations()
    if recommendations:
        print("💡 PREPORUKE NA OSNOVU ANALIZE:")
        for scenario, rec in recommendations.items():
            print(f"   • {scenario.replace('_', ' ').title()}: {rec}")


def upravljanje_profilima():
    """Omogućava upravljanje optimizacionim profilima."""
    while True:
        print("\n🎯 UPRAVLJANJE PROFILIMA")
        print("=" * 50)
        print(profile_manager.list_profiles())

        print("Opcije:")
        print("1. Testiraj profil sa prilagođenim pitanjem")
        print("2. Uporedi profile")
        print("3. Vrati se u glavni meni")

        izbor = input("\nTvoj izbor: ").strip()

        if izbor == "1":
            print("\nIzaberi profil (1-7): ", end="")
            try:
                profile_idx = int(input().strip()) - 1
                profile_type = list(ProfileType)[profile_idx]

                print(f"\nUnesi pitanje za testiranje: ", end="")
                test_pitanje = input().strip()

                if test_pitanje:
                    # Primeni profil i testiraj
                    odgovor = postavi_pitanje_vasi(test_pitanje, auto_optimize=False)

                    # Ručno primeni izabrani profil
                    settings = profile_manager.apply_profile(
                        profile_type,
                        ai_service.get_current_settings()
                    )
                    ai_service.apply_settings(settings)

                    print(f"\n🤖 Odgovor sa profilom '{profile_manager.get_profile(profile_type).name}':")
                    print(odgovor)

            except (ValueError, IndexError):
                print("❌ Nevaljan izbor profila.")

        elif izbor == "2":
            print("\nUnesi pitanje za poređenje: ", end="")
            test_pitanje = input().strip()

            if test_pitanje and ai_service:
                print("\n📊 POREĐENJE PROFILA")
                print("=" * 50)

                original_settings = ai_service.get_current_settings()

                for profile_type in [ProfileType.QUICK_ANSWER,
                                   ProfileType.DETAILED_EXPLANATION]:
                    profile = profile_manager.get_profile(profile_type)

                    # Primeni profil
                    settings = profile_manager.apply_profile(
                        profile_type,
                        original_settings
                    )
                    ai_service.apply_settings(settings)

                    print(f"\n🎯 {profile.name}:")
                    print(f"   Temperature: {settings['temperature']}")
                    print(f"   Max tokens: {settings['max_tokens']}")

                    # Dobij odgovor
                    modified_prompt = VASA_LICNOST + profile.system_prompt_addon
                    odgovor = ai_service.pozovi_ai(test_pitanje, modified_prompt)

                    print(f"   Odgovor ({len(odgovor)} karaktera):")
                    print(f"   {odgovor[:200]}..." if len(odgovor) > 200 else f"   {odgovor}")

                # Vrati originalne postavke
                ai_service.apply_settings(original_settings)

        elif izbor == "3":
            break
        else:
            print("❌ Nepoznata opcija.")


def pokreni_benchmark():
    """Pokreće benchmark testiranje."""
    print("\n🏁 BENCHMARK TESTIRANJE")
    print("=" * 50)

    if not (Config.OPENAI_API_KEY and Config.GEMINI_API_KEY):
        print("❌ Za benchmark su potrebna oba API ključa!")
        print("   Trenutno imaš:")
        if Config.OPENAI_API_KEY:
            print("   ✓ OpenAI")
        if Config.GEMINI_API_KEY:
            print("   ✓ Gemini")
        return

    print("⚠️  Benchmark će pokrenuti seriju testova na oba servisa.")
    print("   Ovo može potrajati nekoliko minuta.")
    print("\nDa li želiš da nastaviš? (da/ne): ", end="")

    if input().strip().lower() in ['da', 'd', 'yes', 'y']:
        benchmark = AIBenchmark()
        results_file = benchmark.run_full_benchmark()

        if results_file:
            print(f"\n📁 Detaljni rezultati sačuvani u: {results_file}")


def kontinuirani_razgovor():
    """Omogućava kontinuiranu konverzaciju sa Učiteljem Vasom."""
    print("\n💬 KONTINUIRANI RAZGOVOR SA UČITELJEM VASOM")
    print("=" * 50)
    print("Sada možeš da razgovaraš sa mnom kao sa pravim učiteljem!")
    print("Pamtiću kontekst našeg razgovora.")
    print("Kucaj 'izlaz' ili 'exit' kada želiš da završiš razgovor.\n")

    # Istorija razgovora
    conversation_history = []

    while True:
        # Korisnikov unos
        pitanje = input("👤 Ti: ").strip()

        # Proveri da li korisnik želi da izađe
        if pitanje.lower() in ['izlaz', 'exit', 'kraj', 'quit']:
            print("\n👋 Hvala na razgovoru! Vraćam te u glavni meni.\n")
            break

        if not pitanje:
            print("💭 Molim te, postavi pitanje ili napiši komentar.\n")
            continue

        # Dodaj korisnikovo pitanje u istoriju
        conversation_history.append({
            "role": "user",
            "content": pitanje
        })

        print("\n🤖 Učitelj Vasa: ", end="", flush=True)

        try:
            if ai_service:
                # Pripremi system prompt sa kontekstom
                system_prompt_with_context = VASA_LICNOST + "\n\nVodi računa o kontekstu prethodnog razgovora."

                # Koristi istoriju razgovora
                odgovor = ai_service.pozovi_sa_istorijom([
                    {"role": "system", "content": system_prompt_with_context},
                    *conversation_history
                ])

                # Dodaj Vasin odgovor u istoriju
                conversation_history.append({
                    "role": "assistant",
                    "content": odgovor
                })

                # Ograniči istoriju na poslednjih 10 razmena (20 poruka)
                if len(conversation_history) > 20:
                    conversation_history = conversation_history[-20:]

            else:
                # Fallback na simulaciju
                odgovor = simuliraj_ai_odgovor(pitanje)

            print(odgovor)

        except Exception as e:
            print(f"\n❌ Greška: {e}")
            print("Pokušaj ponovo sa drugim pitanjem.")

        print()  # Prazan red za preglednost


def prikazi_ai_status():
    """Prikazuje trenutni status AI servisa."""
    print("\n🔍 STATUS AI SERVISA")
    print("=" * 50)

    # Trenutni provider
    print(f"📡 Trenutni provider: {Config.AI_PROVIDER.upper()}")

    # Status servisa
    if ai_service:
        print("✅ AI servis je aktivan")

        # Trenutne postavke
        settings = ai_service.get_current_settings()
        print(f"🤖 Model: {settings.get('model', 'nepoznat')}")
        print(f"🌡️ Temperature: {settings.get('temperature', 'N/A')}")
        print(f"📏 Max tokena: {settings.get('max_tokens', 'N/A')}")

        # Test konekcije
        print("\n🔌 Testiram konekciju...")
        if ai_service.test_konekcija():
            print("✅ Konekcija sa AI servisom je stabilna!")
        else:
            print("❌ Problem sa konekcijom. Proveri API ključ i internet vezu.")
    else:
        print("❌ AI servis nije aktivan")
        print("📚 Koristim simulaciju umesto pravog AI-ja")

    # Dostupni provideri
    print("\n📋 Dostupni provideri:")
    if Config.OPENAI_API_KEY:
        print("   ✓ OpenAI")
    else:
        print("   ✗ OpenAI (nedostaje API ključ)")

    if Config.GEMINI_API_KEY:
        print("   ✓ Gemini")
    else:
        print("   ✗ Gemini (nedostaje API ključ)")

    print()  # Prazan red


def promeni_ai_servis():
    """Omogućava promenu AI servisa tokom rada."""
    global ai_service

    print("\n🔄 PROMENA AI SERVISA")
    print("=" * 50)

    # Prikaži trenutni servis
    print(f"Trenutno koristiš: {Config.AI_PROVIDER.upper()}")

    # Proveri dostupne opcije
    dostupni = []
    if Config.OPENAI_API_KEY:
        dostupni.append("openai")
    if Config.GEMINI_API_KEY:
        dostupni.append("gemini")

    if len(dostupni) < 2:
        print("\n⚠️ Nemaš konfigurisan drugi AI servis!")
        print("Potreban ti je API ključ za oba servisa da bi mogao da menjaš između njih.")
        return

    # Ponudi opcije
    print("\nDostupni servisi:")
    for i, servis in enumerate(dostupni, 1):
        print(f"{i}. {servis.upper()}")

    # Zatraži izbor
    try:
        izbor = input("\nIzaberi servis (broj): ").strip()
        idx = int(izbor) - 1

        if 0 <= idx < len(dostupni):
            novi_servis = dostupni[idx]

            if novi_servis == Config.AI_PROVIDER:
                print("ℹ️ Već koristiš taj servis!")
                return

            # Promeni servis
            Config.AI_PROVIDER = novi_servis

            # Resetuj factory (forsiraj novo kreiranje)
            AIServiceFactory.reset()

            # Kreiraj novi servis
            print(f"\n🔄 Prebacujem na {novi_servis.upper()}...")
            try:
                ai_service = AIServiceFactory.get_service()
                print(f"✅ Uspešno prebačeno na {novi_servis.upper()}!")

                # Test konekcije
                if ai_service.test_konekcija():
                    print("✅ Novi servis radi perfektno!")
                else:
                    print("⚠️ Servis je kreiran ali konekcija nije stabilna.")

            except Exception as e:
                print(f"❌ Greška pri prebacivanju: {e}")
                print("Vraćam se na prethodni servis...")
                # Vrati na stari servis ako ne uspe
                Config.AI_PROVIDER = "openai" if novi_servis == "gemini" else "gemini"
                AIServiceFactory.reset()
                ai_service = AIServiceFactory.get_service()
        else:
            print("❌ Nevaljan izbor!")

    except ValueError:
        print("❌ Molim te unesi broj!")
    except Exception as e:
        print(f"❌ Greška: {e}")


def glavni_meni_profilisanje():
    """Vraća prošireni glavni meni."""
    meni = """
Šta želiš da uradiš?
1. Pozdravi me
2. Predstavi se
3. Postavi pitanje Učitelju Vasi
4. Razgovaraj sa Vasom (kontinuirani mod)
5. Proveri AI status
6. Promeni AI servis
7. 📊 Prikaži performanse
8. 🎯 Upravljaj profilima
9. 🏁 Pokreni benchmark
10. Izađi

Tvoj izbor: """
    return meni


def pokreni_vasu():
    """Pokreće glavnu petlju programa Učitelj Vasa."""
    # Inicijalizuj AI servis
    ai_dostupan = inicijalizuj_ai_servis()

    print("\n" + "🎓" * 25)
    print(pozdrav())
    if ai_dostupan:
        provider_info = {
            'openai': "✨ Povezan sa OpenAI GPT - najpoznatiji AI model!",
            'gemini': "✨ Povezan sa Google Gemini - moćan i besplatan!"
        }
        print(provider_info.get(Config.AI_PROVIDER.lower(), "✨ AI je spreman!"))
        print("🎯 Automatska optimizacija je UKLJUČENA")
    else:
        print("📚 Radim u offline modu sa simulacijom.")
    print("🎓" * 25 + "\n")

    # Glavna petlja programa
    while True:
        print(glavni_meni_profilisanje())
        izbor = input().strip()

        if izbor == "1":
            print("\n" + pozdrav() + "\n")

        elif izbor == "2":
            print("\n" + predstavi_se() + "\n")

        elif izbor == "3":
            print("\n💭 Postavi mi bilo koje pitanje o programiranju:")
            pitanje = input("👤 Ti: ").strip()
            if pitanje:
                print("\n🤖 Učitelj Vasa: ", end="", flush=True)
                odgovor = postavi_pitanje_vasi(pitanje)
                print(odgovor)

                # Prikaži metrike ako postoje
                if current_profile and ai_service:
                    settings = ai_service.get_current_settings()
                    print(f"\n📊 [Parametri: temp={settings['temperature']}, "
                         f"max_tokens={settings['max_tokens']}]")
            else:
                print("\n❌ Nisi uneo pitanje.")

        elif izbor == "4":
            kontinuirani_razgovor()

        elif izbor == "5":
            prikazi_ai_status()

        elif izbor == "6":
            promeni_ai_servis()

        elif izbor == "7":
            prikazi_performanse()

        elif izbor == "8":
            upravljanje_profilima()

        elif izbor == "9":
            pokreni_benchmark()

        elif izbor == "10":
            print("\nHvala što si koristio Učitelja Vasu! ")
            print("Nastavi sa učenjem i ne zaboravi - svaki ekspert je nekad bio početnik! 🌟")

            # Prikaži finalne statistike ako postoje
            if ai_service and len(tracker.all_metrics) > 0:
                print("\n📊 FINALNE STATISTIKE SESIJE:")
                print(tracker.compare_providers())

            break

        else:
            print("\n❌ Nepoznata opcija. Pokušaj ponovo.\n")

    print("\nProgram završen. Srećno sa programiranjem! 👋")


if __name__ == "__main__":
    pokreni_vasu()
