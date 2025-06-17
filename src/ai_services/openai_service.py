"""
OpenAI servis za Učitelja Vasu
Implementira BaseAIService interfejs

NAPOMENA: Ovaj modul automatski rešava česte SSL probleme
koji se javljaju na Windows sistemima sa OpenAI bibliotekom.
"""

# KRITIČNO: Učitaj SSL fix PRE bilo čega drugog!
# Ovo mora biti prva linija da bi počistilo environment varijable
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importuj i primeni SSL fix
try:
    import ssl_fix
except ImportError:
    print("⚠️ SSL fix modul nije pronađen, nastavljam bez njega...")

# Sada možemo bezbedno da importujemo ostale module
from typing import Optional, List, Dict
from openai import OpenAI
from utils.config import Config
from .base_service import BaseAIService
# Dodaj na početak importa
from utils.performance_tracker import tracker

class OpenAIService(BaseAIService):
    """Servis za komunikaciju sa OpenAI API-jem."""

    def __init__(self):
        """Inicijalizuje OpenAI klijenta sa API ključem iz Config-a."""
        if not Config.OPENAI_API_KEY:
            raise ValueError("OpenAI API ključ nije postavljen!")

        try:
            # Kreiraj klijent
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
            self.model = Config.OPENAI_MODEL or "gpt-3.5-turbo"
            self.max_tokens = Config.OPENAI_MAX_TOKENS
            self.temperature = Config.OPENAI_TEMPERATURE

            print(f"✅ OpenAI servis inicijalizovan (model: {self.model})")

        except Exception as e:
            # Dodatna dijagnoza ako i dalje ima problema
            if "SSL" in str(e) or "certificate" in str(e).lower() or "[Errno 2]" in str(e):
                print("❌ SSL problem detektovan!")
                print("   Pokušaj ove korake:")
                print("   1. Restartuj PyCharm/terminal")
                print("   2. Proveri sistemske environment varijable")
                print("   3. Koristi Gemini kao alternativu")
            raise

    def pozovi_ai(self, poruka: str, system_prompt: Optional[str] = None) -> str:
        """
        Šalje poruku AI-ju i vraća odgovor.

        Args:
            poruka: Korisnikova poruka/pitanje
            system_prompt: Opcioni system prompt za definisanje ponašanja

        Returns:
            AI odgovor kao string
        """

        # Počni praćenje
        tracking_id = tracker.start_tracking("openai", self.model, "chat_completion")

        try:
            # Pripremi poruke
            messages = []

            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })

            messages.append({
                "role": "user",
                "content": poruka
            })

            # Pozovi API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            result = response.choices[0].message.content.strip()

            # Završi praćenje - uspešno
            tracker.end_tracking(
                tracking_id,
                success=True,
                response_length=len(result),
                additional_data={
                    "prompt_length": len(poruka),
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens
                }
            )

            return result

        except Exception as e:
            # Završi praćenje - neuspešno
            tracker.end_tracking(
                tracking_id,
                success=False,
                error=str(e)
            )

            # Postojeći error handling...
            error_msg = f"Greška pri komunikaciji sa OpenAI: {str(e)}"
            print(f"❌ {error_msg}")

            if "api_key" in str(e).lower():
                return "Izgleda da OpenAI API ključ nije valjan. Proveri podešavanja."
            elif "rate_limit" in str(e).lower():
                return "Previše zahteva ka OpenAI. Sačekaj malo pa pokušaj ponovo."
            elif "insufficient_quota" in str(e).lower():
                return "Nemaš dovoljno OpenAI kredita. Proveri svoj balans ili prebaci se na Gemini (AI_PROVIDER=gemini)."
            elif "connection" in str(e).lower():
                return "Problem sa internet konekcijom. Proveri da li si povezan."
            elif "SSL" in str(e) or "certificate" in str(e).lower():
                return "SSL problem - restartuj program ili koristi Gemini servis."
            else:
                return "Ups! Nešto je pošlo po zlu sa OpenAI. Pokušaj ponovo za koji trenutak."

        try:
            # Pripremi poruke
            messages = []

            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })

            messages.append({
                "role": "user",
                "content": poruka
            })

            # Pozovi API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            # Detaljno rukovanje greškama
            error_msg = f"Greška pri komunikaciji sa OpenAI: {str(e)}"
            print(f"❌ {error_msg}")

            # Specifične poruke za različite greške
            if "api_key" in str(e).lower():
                return "Izgleda da OpenAI API ključ nije valjan. Proveri podešavanja."
            elif "rate_limit" in str(e).lower():
                return "Previše zahteva ka OpenAI. Sačekaj malo pa pokušaj ponovo."
            elif "insufficient_quota" in str(e).lower():
                return "Nemaš dovoljno OpenAI kredita. Proveri svoj balans ili prebaci se na Gemini (AI_PROVIDER=gemini)."
            elif "connection" in str(e).lower():
                return "Problem sa internet konekcijom. Proveri da li si povezan."
            elif "SSL" in str(e) or "certificate" in str(e).lower():
                return "SSL problem - restartuj program ili koristi Gemini servis."
            else:
                return "Ups! Nešto je pošlo po zlu sa OpenAI. Pokušaj ponovo za koji trenutak."

    def pozovi_sa_istorijom(self, messages: List[Dict[str, str]]) -> str:
        """
        Šalje celu istoriju razgovora AI-ju.

        Args:
            messages: Lista poruka sa 'role' i 'content' ključevima

        Returns:
            AI odgovor kao string
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"❌ OpenAI greška: {str(e)}")
            return "Izvini, trenutno ne mogu da odgovorim preko OpenAI. Pokušaj ponovo."


# Test funkcionalnosti
if __name__ == "__main__":
    print("🧪 Test OpenAI servisa")
    print("=" * 50)

    # Prvo pokreni SSL dijagnozu
    print("\n🔍 SSL dijagnoza:")
    import ssl_fix

    ssl_fix.diagnose_ssl_issues()

    # Proveri da li je OpenAI konfigurisan
    if Config.AI_PROVIDER != 'openai':
        print(f"\n⚠️  AI_PROVIDER je postavljen na '{Config.AI_PROVIDER}'")
        print("   Promeni na 'openai' u .env fajlu za ovaj test")
    elif not Config.OPENAI_API_KEY:
        print("\n❌ OpenAI API ključ nije postavljen!")
    else:
        try:
            # Kreiraj servis
            print("\n🏗️ Kreiram OpenAI servis...")
            service = OpenAIService()

            # Test jednostavnog poziva
            print("\n📤 Test pitanje: 'Šta je Python?'")
            odgovor = service.pozovi_ai("Šta je Python u jednoj rečenici?")
            print(f"📥 Odgovor: {odgovor}")

            # Test konekcije
            print("\n🔌 Test konekcije...")
            if service.test_konekcija():
                print("✅ Konekcija sa OpenAI API-jem uspešna!")

        except Exception as e:
            print(f"\n❌ Test neuspešan: {type(e).__name__}: {e}")

            if "[Errno 2]" in str(e):
                print("\n💡 REŠENJE:")
                print("1. SSL environment varijable su problematične")
                print("2. Restartuj PyCharm/terminal")
                print("3. Ili koristi Gemini umesto OpenAI")
