"""
Glavni program za Učitelja Vasu
Sa podrškom za profilisanje, optimizaciju i personalizaciju
"""

# Dodaj src folder u Python path
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import re
from vasa_core import pozdrav, predstavi_se, VASA_LICNOST
from ai_simulator import simuliraj_ai_odgovor
from utils.config import Config
from utils.performance_tracker import tracker
from utils.optimization_profiles import profile_manager as optimization_manager, ProfileType
from utils.ai_benchmark import AIBenchmark
from ai_services.ai_factory import AIServiceFactory
from ai_services.base_service import BaseAIService
from typing import Optional

# Resilience importi
from utils.circuit_breaker import get_all_circuits_status, CircuitOpenError
from utils.fallback_manager import fallback_manager
from utils.retry_handler import smart_retry

# Personalizacija importi - sa preimenovanjem da izbegnemo konflikte
from personalization.user_profile import profile_manager as user_profile_manager, SkillLevel, LearningStyle
from personalization.profile_analyzer import ProfileAnalyzer
from personalization.adaptive_engine import AdaptiveEngine

# Globalne varijable
ai_service: Optional[BaseAIService] = None
optimization_profile: Optional[ProfileType] = None  # Za optimizacione profile
current_user_profile = None  # Za korisničke profile
conversation_history = []
analyzer = ProfileAnalyzer()
adaptive_engine = AdaptiveEngine()


def dobrodoslica_i_profil():
    """Pozdravlja korisnika i učitava/kreira profil."""
    global current_user_profile

    print("\n" + "🎓" * 25)
    print("Dobrodošao u Učitelja Vasu - tvog personalnog AI asistenta!")
    print("🎓" * 25 + "\n")

    # Prikaži postojeće profile
    existing_profiles = user_profile_manager.list_all_profiles()

    if existing_profiles:
        print("📚 Postojeći profili:")
        for i, username in enumerate(existing_profiles, 1):
            print(f"   {i}. {username}")
        print(f"   {len(existing_profiles) + 1}. Kreiraj novi profil")

        while True:
            izbor = input("\nIzaberi opciju (broj): ").strip()
            try:
                idx = int(izbor) - 1
                if 0 <= idx < len(existing_profiles):
                    username = existing_profiles[idx]
                    current_user_profile = user_profile_manager.get_or_create_profile(username)
                    break
                elif idx == len(existing_profiles):
                    # Novi profil
                    username = input("\nUnesi svoje ime: ").strip()
                    if username:
                        current_user_profile = user_profile_manager.get_or_create_profile(username)
                        postavi_pocetne_preference()
                        break
            except ValueError:
                print("❌ Molim te unesi broj.")
    else:
        print("🆕 Izgleda da si nov ovde!")
        username = input("Kako se zoveš? ").strip()
        if username:
            current_user_profile = user_profile_manager.get_or_create_profile(username)
            postavi_pocetne_preference()

    # Prikaži personalizovan pozdrav
    if current_user_profile:
        print(f"\n✨ Zdravo {current_user_profile.username}!")
        print(user_profile_manager.get_profile_summary(current_user_profile.username))


def postavi_pocetne_preference():
    """Postavlja početne preference za novog korisnika."""
    global current_user_profile

    print("\n🎯 Hajde da podesimo tvoje preference!")
    print("=" * 50)

    # Nivo znanja
    print("\n📚 Koji je tvoj nivo programiranja?")
    print("1. Početnik - tek počinjem")
    print("2. Srednji - znam osnove")
    print("3. Napredni - imam iskustva")

    while True:
        nivo = input("\nTvoj izbor (1-3): ").strip()
        if nivo == "1":
            current_user_profile.skill_level = SkillLevel.BEGINNER
            break
        elif nivo == "2":
            current_user_profile.skill_level = SkillLevel.INTERMEDIATE
            break
        elif nivo == "3":
            current_user_profile.skill_level = SkillLevel.ADVANCED
            break

    # Stil učenja
    print("\n🎨 Kako najlakše učiš?")
    print("1. Kroz praktične primere koda")
    print("2. Kroz detaljne tekstualne opise")
    print("3. Kroz dijagrame i vizuelne prikaze")
    print("4. Kroz teorijske koncepte")

    while True:
        stil = input("\nTvoj izbor (1-4): ").strip()
        if stil == "1":
            current_user_profile.learning_style = LearningStyle.PRACTICAL
            break
        elif stil == "2":
            current_user_profile.learning_style = LearningStyle.TEXTUAL
            break
        elif stil == "3":
            current_user_profile.learning_style = LearningStyle.VISUAL
            break
        elif stil == "4":
            current_user_profile.learning_style = LearningStyle.THEORETICAL
            break

    # Dužina odgovora
    print("\n📏 Kakve odgovore preferiraš?")
    print("1. Kratke i koncizne")
    print("2. Umerene dužine")
    print("3. Detaljne i opširne")

    while True:
        duzina = input("\nTvoj izbor (1-3): ").strip()
        if duzina == "1":
            current_user_profile.preferences.response_length = "short"
            break
        elif duzina == "2":
            current_user_profile.preferences.response_length = "medium"
            break
        elif duzina == "3":
            current_user_profile.preferences.response_length = "long"
            break

    # Sačuvaj profil
    user_profile_manager.save_profile(current_user_profile)
    print("\n✅ Tvoje preference su sačuvane!")


def postavi_pitanje_vasi(pitanje: str, auto_optimize: bool = True) -> str:
    """
    Postavlja pitanje Vasi sa personalizacijom i optimizacijom.

    Args:
        pitanje: Korisnikovo pitanje
        auto_optimize: Da li automatski optimizovati postavke

    Returns:
        AI odgovor
    """
    global optimization_profile, current_user_profile, conversation_history

    if not ai_service:
        # Fallback na simulaciju
        print("🎭 [Koristim simulaciju...]")
        return simuliraj_ai_odgovor(pitanje)

    # Ažuriraj korisničku aktivnost ako postoji profil
    topic = None
    if current_user_profile:
        conversation_history.append(pitanje)
        message_analysis = analyzer.analyze_message(pitanje)
        topic = message_analysis["topics"][0] if message_analysis["topics"] else None
        current_user_profile.update_activity(topic)

        # Proveri da li treba prilagoditi tokom razgovora
        if len(conversation_history) > 1:
            # Analiziraj poslednji odgovor korisnika
            response_analysis = adaptive_engine.analyze_user_response(pitanje)
            adaptation = adaptive_engine.suggest_adaptation(current_user_profile, response_analysis)

            if adaptation:
                print(f"\n💡 [Prilagođavam: {adaptation['suggestion']}]")

    # Počni sa osnovnim system promptom
    system_prompt = VASA_LICNOST

    # Dodaj personalizaciju ako postoji korisnički profil
    if current_user_profile:
        addon = analyzer.generate_personalized_prompt_addon(
            current_user_profile,
            topic
        )
        system_prompt += "\n\n" + addon

    # Dodaj optimizacioni profil ako je omogućen
    if auto_optimize:
        suggested_profile = optimization_manager.analyze_question(pitanje)
        profile_info = optimization_manager.get_profile(suggested_profile)
        print(f"📋 [Koristim optimizacioni profil: {profile_info.name}]")

        settings = optimization_manager.apply_profile(
            suggested_profile,
            ai_service.get_current_settings()
        )
        ai_service.apply_settings(settings)
        optimization_profile = suggested_profile

        system_prompt += profile_info.system_prompt_addon

    # Pozovi AI
    print(f"🤖 [Koristim {Config.AI_PROVIDER.upper()} AI model...]")

    try:
        # Koristi personalizovan poziv ako je dostupan
        if current_user_profile and hasattr(ai_service, 'pozovi_ai_personalizovano'):
            return ai_service.pozovi_ai_personalizovano(
                pitanje,
                current_user_profile,
                system_prompt
            )
        else:
            return ai_service.pozovi_ai(pitanje, system_prompt=system_prompt)
    except Exception as e:
        print(f"\n⚠️ Greška pri pozivu AI servisa: {e}")
        return simuliraj_ai_odgovor(pitanje)


def prikazi_i_uredi_profil():
    """Prikazuje i omogućava uređivanje profila."""
    global current_user_profile

    if not current_user_profile:
        print("❌ Nema učitanog profila!")
        return

    while True:
        print("\n" + user_profile_manager.get_profile_summary(current_user_profile.username))

        print("\n📝 OPCIJE:")
        print("1. Promeni nivo znanja")
        print("2. Promeni stil učenja")
        print("3. Promeni dužinu odgovora")
        print("4. Vidi moje dostignuća")
        print("5. Analiza napretka")
        print("6. Nazad")

        izbor = input("\nTvoj izbor: ").strip()

        if izbor == "1":
            print("\nTrenutni nivo:", current_user_profile.skill_level.to_serbian())
            print("1. Početnik")
            print("2. Srednji")
            print("3. Napredni")

            novi_nivo = input("Novi nivo (1-3): ").strip()
            if novi_nivo == "1":
                current_user_profile.skill_level = SkillLevel.BEGINNER
            elif novi_nivo == "2":
                current_user_profile.skill_level = SkillLevel.INTERMEDIATE
            elif novi_nivo == "3":
                current_user_profile.skill_level = SkillLevel.ADVANCED

            try:
                user_profile_manager.save_profile(current_user_profile)
                print("✅ Nivo ažuriran!")
            except Exception as e:
                print(f"⚠️ Greška pri čuvanju: {e}")

        elif izbor == "2":
            print("\nTrenutni stil:", current_user_profile.learning_style.to_serbian())
            print("1. Praktični")
            print("2. Tekstualni")
            print("3. Vizuelni")
            print("4. Teorijski")

            novi_stil = input("Novi stil (1-4): ").strip()
            if novi_stil == "1":
                current_user_profile.learning_style = LearningStyle.PRACTICAL
            elif novi_stil == "2":
                current_user_profile.learning_style = LearningStyle.TEXTUAL
            elif novi_stil == "3":
                current_user_profile.learning_style = LearningStyle.VISUAL
            elif novi_stil == "4":
                current_user_profile.learning_style = LearningStyle.THEORETICAL

            try:
                user_profile_manager.save_profile(current_user_profile)
                print("✅ Stil učenja ažuriran!")
            except Exception as e:
                print(f"⚠️ Greška pri čuvanju: {e}")

        elif izbor == "3":
            print("\nTrenutna dužina:", current_user_profile.preferences.response_length)
            print("1. Kratki odgovori")
            print("2. Srednji odgovori")
            print("3. Dugi odgovori")

            nova_duzina = input("Nova dužina (1-3): ").strip()
            if nova_duzina == "1":
                current_user_profile.preferences.response_length = "short"
            elif nova_duzina == "2":
                current_user_profile.preferences.response_length = "medium"
            elif nova_duzina == "3":
                current_user_profile.preferences.response_length = "long"

            try:
                user_profile_manager.save_profile(current_user_profile)
                print("✅ Preferenca dužine ažurirana!")
            except Exception as e:
                print(f"⚠️ Greška pri čuvanju: {e}")

        elif izbor == "4":
            print("\n🏆 TVOJA DOSTIGNUĆA:")
            if current_user_profile.achievements:
                for achievement in current_user_profile.achievements:
                    print(f"   ⭐ {achievement}")
            else:
                print("   Nemaš još dostignuća - nastavi da učiš!")

        elif izbor == "5":
            # Analiza napretka
            if conversation_history:
                analysis = analyzer.analyze_conversation_history(
                    conversation_history[-10:],  # Poslednjih 10 poruka
                    current_user_profile
                )

                print("\n📈 ANALIZA NAPRETKA:")
                print(f"Prosečna složenost pitanja: {analysis['average_complexity']:.1f}/10")
                print(f"Najčešće teme: ", end="")
                for topic, count in analysis['top_topics']:
                    print(f"{topic} ({count}x), ", end="")
                print()

                # Proveri da li treba level up
                if current_user_profile.should_level_up():
                    print("\n🎉 ČESTITAM! Spreman si za viši nivo!")
                    current_user_profile.level_up()
                    try:
                        user_profile_manager.save_profile(current_user_profile)
                    except Exception as e:
                        print(f"⚠️ Greška pri čuvanju napretka: {e}")

        elif izbor == "6":
            break


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
        print("\n🎯 UPRAVLJANJE OPTIMIZACIONIM PROFILIMA")
        print("=" * 50)
        print(optimization_manager.list_profiles())

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
                    settings = optimization_manager.apply_profile(
                        profile_type,
                        ai_service.get_current_settings()
                    )
                    ai_service.apply_settings(settings)

                    profile_info = optimization_manager.get_profile(profile_type)
                    modified_prompt = VASA_LICNOST + profile_info.system_prompt_addon

                    odgovor = ai_service.pozovi_ai(test_pitanje, modified_prompt)

                    print(f"\n🤖 Odgovor sa profilom '{profile_info.name}':")
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
                    profile = optimization_manager.get_profile(profile_type)

                    # Primeni profil
                    settings = optimization_manager.apply_profile(
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

    # Lokalna istorija za kontinuirani razgovor
    local_conversation_history = []

    while True:
        # Korisnikov unos
        pitanje = input("👤 Ti: ").strip()

        # Proveri da li korisnik želi da izađe
        if pitanje.lower() in ['izlaz', 'exit', 'kraj', 'quit']:
            print("\n👋 Hvala na razgovoru! Vraćam te u glavni meni.\n")

            # Sačuvaj sesiju ako je bila korisna
            if len(local_conversation_history) > 2 and current_user_profile:
                summary = adaptive_engine.generate_session_summary()
                print(f"📊 Rezime sesije: {summary['recommendation']}")
                adaptive_engine.reset_session()
            break

        if not pitanje:
            print("💭 Molim te, postavi pitanje ili napiši komentar.\n")
            continue

        # Dodaj korisnikovo pitanje u lokalnu istoriju
        local_conversation_history.append({
            "role": "user",
            "content": pitanje
        })

        print("\n🤖 Učitelj Vasa: ", end="", flush=True)

        try:
            if ai_service:
                # Pripremi system prompt sa kontekstom
                system_prompt_with_context = VASA_LICNOST

                # Dodaj personalizaciju ako postoji
                if current_user_profile:
                    addon = analyzer.generate_personalized_prompt_addon(
                        current_user_profile,
                        None  # Tema će biti detektovana iz pitanja
                    )
                    system_prompt_with_context += "\n\n" + addon

                system_prompt_with_context += "\n\nVodi računa o kontekstu prethodnog razgovora."

                # Koristi istoriju razgovora
                odgovor = ai_service.pozovi_sa_istorijom([
                    {"role": "system", "content": system_prompt_with_context},
                    *local_conversation_history
                ])

                # Dodaj Vasin odgovor u lokalnu istoriju
                local_conversation_history.append({
                    "role": "assistant",
                    "content": odgovor
                })

                # Ograniči istoriju na poslednjih 10 razmena (20 poruka)
                if len(local_conversation_history) > 20:
                    local_conversation_history = local_conversation_history[-20:]

                # Ažuriraj globalnu istoriju za analizu
                if current_user_profile:
                    conversation_history.append(pitanje)

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
                ai_service = AIServiceFactory.create_resilient_service()
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


def glavni_meni():
    """Vraća glavni meni sa personalizacijom."""
    ime = current_user_profile.username if current_user_profile else "Korisniče"

    meni = f"""
Zdravo {ime}! Šta želiš da uradiš?
1. Pozdravi me
2. Predstavi se
3. Postavi pitanje Učitelju Vasi
4. Razgovaraj sa Vasom (kontinuirani mod)
5. Proveri AI status
6. Promeni AI servis
7. 📊 Prikaži performanse
8. 🎯 Upravljaj optimizacionim profilima
9. 🏁 Pokreni benchmark
10. 👤 Moj profil
11. 🏥 Zdravlje sistema
12. Izađi

Tvoj izbor: """
    return meni


def pokreni_vasu():
    """Pokreće glavnu petlju programa Učitelj Vasa."""
    # Inicijalizuj AI servis
    ai_dostupan = inicijalizuj_ai_servis()

    # Pozovi dobrodošlicu i učitaj profil
    dobrodoslica_i_profil()

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
        print(glavni_meni())
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
                if optimization_profile and ai_service:
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
            prikazi_i_uredi_profil()

        elif izbor == "11":
            prikazi_sistem_zdravlje()

        elif izbor == "12":
            print("\nHvala što si koristio Učitelja Vasu! ")
            print("Nastavi sa učenjem i ne zaboravi - svaki ekspert je nekad bio početnik! 🌟")

            # Sačuvaj profil pre izlaska
            if current_user_profile:
                try:
                    user_profile_manager.save_profile(current_user_profile)
                    print(f"\n✅ Profil '{current_user_profile.username}' je sačuvan.")
                except Exception as e:
                    print(f"\n⚠️ Greška pri čuvanju profila: {e}")

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
