"""
Google Gemini servis za Učitelja Vasu
Implementira BaseAIService interfejs

NAPOMENA: Gemini obično ne zahteva SSL fix kao OpenAI,
ali importujemo ga za svaki slučaj.
"""

import time
from typing import Optional, List, Dict
import sys
import os

# Dodaj parent folder u path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# SSL fix (iako Gemini obično ne zahteva)
try:
    import ssl_fix
except ImportError:
    pass  # Gemini obično radi bez SSL fix-a

import google.generativeai as genai
from utils.config import Config
from .base_service import BaseAIService
# Dodaj na početak importa
from utils.performance_tracker import tracker

class GeminiService(BaseAIService):
    """Servis za komunikaciju sa Google Gemini API-jem."""

    def __init__(self):
        """Inicijalizuje Gemini klijenta sa API ključem iz Config-a."""
        if not Config.GEMINI_API_KEY:
            raise ValueError("Gemini API ključ nije postavljen!")

        # Konfiguriši Gemini
        genai.configure(api_key=Config.GEMINI_API_KEY)

        # Kreiraj model
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
        self.max_tokens = Config.GEMINI_MAX_TOKENS
        self.temperature = Config.GEMINI_TEMPERATURE

        # Gemini koristi drugačije nazive za parametre
        self.generation_config = genai.GenerationConfig(
            max_output_tokens=self.max_tokens,
            temperature=self.temperature
        )

        print(f"✅ Gemini servis inicijalizovan (model: {Config.GEMINI_MODEL})")

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
        tracking_id = tracker.start_tracking("gemini", Config.GEMINI_MODEL, "generate_content")

        try:
            # Gemini kombinuje system prompt i korisničku poruku
            full_prompt = poruka
            if system_prompt:
                full_prompt = f"{system_prompt}\n\nKorisnik: {poruka}\nAsistent:"

            # Generiši odgovor
            response = self.model.generate_content(
                full_prompt,
                generation_config=self.generation_config
            )

            result = response.text.strip()

            # Završi praćenje - uspešno
            tracker.end_tracking(
                tracking_id,
                success=True,
                response_length=len(result),
                additional_data={
                    "prompt_length": len(full_prompt),
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
            error_msg = f"Greška pri komunikaciji sa Gemini: {str(e)}"
            print(f"❌ {error_msg}")

            if "api_key" in str(e).lower():
                return "Izgleda da Gemini API ključ nije valjan. Proveri podešavanja."
            elif "rate_limit" in str(e).lower() or "429" in str(e):
                return "Previše zahteva ka Gemini. Sačekaj malo pa pokušaj ponovo."
            elif "safety" in str(e).lower():
                return "Gemini je blokirao odgovor iz sigurnosnih razloga. Pokušaj sa drugim pitanjem."
            elif "connection" in str(e).lower():
                return "Problem sa internet konekcijom. Proveri da li si povezan."
            else:
                return "Ups! Nešto je pošlo po zlu sa Gemini. Pokušaj ponovo za koji trenutak."

        try:
            # Gemini kombinuje system prompt i korisničku poruku
            full_prompt = poruka
            if system_prompt:
                full_prompt = f"{system_prompt}\n\nKorisnik: {poruka}\nAsistent:"

            # Generiši odgovor
            response = self.model.generate_content(
                full_prompt,
                generation_config=self.generation_config
            )

            # Vrati odgovor
            return response.text.strip()

        except Exception as e:
            # Rukovanje greškama
            error_msg = f"Greška pri komunikaciji sa Gemini: {str(e)}"
            print(f"❌ {error_msg}")

            # Vraćamo user-friendly poruku
            if "api_key" in str(e).lower():
                return "Izgleda da Gemini API ključ nije valjan. Proveri podešavanja."
            elif "rate_limit" in str(e).lower() or "429" in str(e):
                return "Previše zahteva ka Gemini. Sačekaj malo pa pokušaj ponovo."
            elif "safety" in str(e).lower():
                return "Gemini je blokirao odgovor iz sigurnosnih razloga. Pokušaj sa drugim pitanjem."
            elif "connection" in str(e).lower():
                return "Problem sa internet konekcijom. Proveri da li si povezan."
            else:
                return "Ups! Nešto je pošlo po zlu sa Gemini. Pokušaj ponovo za koji trenutak."

    def pozovi_sa_istorijom(self, messages: List[Dict[str, str]]) -> str:
        """
        Šalje celu istoriju razgovora AI-ju.

        Args:
            messages: Lista poruka sa 'role' i 'content' ključevima

        Returns:
            AI odgovor kao string
        """
        try:
            # Konvertuj poruke u Gemini format
            chat = self.model.start_chat(history=[])

            # Rekonstruiši razgovor
            full_conversation = ""
            system_prompt = ""

            for msg in messages:
                if msg['role'] == 'system':
                    system_prompt = msg['content']
                elif msg['role'] == 'user':
                    if full_conversation:
                        full_conversation += "\n\n"
                    full_conversation += f"Korisnik: {msg['content']}"
                elif msg['role'] == 'assistant':
                    full_conversation += f"\nAsistent: {msg['content']}"

            # Dodaj system prompt na početak ako postoji
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{full_conversation}\nAsistent:"
            else:
                full_prompt = f"{full_conversation}\nAsistent:"

            # Generiši odgovor
            response = self.model.generate_content(
                full_prompt,
                generation_config=self.generation_config
            )

            return response.text.strip()

        except Exception as e:
            print(f"❌ Gemini greška: {str(e)}")
            return "Izvini, trenutno ne mogu da odgovorim preko Gemini. Pokušaj ponovo."


# Test funkcionalnosti
if __name__ == "__main__":
    print("🧪 Test Gemini servisa")
    print("=" * 50)

    # Proveri da li je Gemini konfigurisan
    if Config.AI_PROVIDER != 'gemini':
        print(f"⚠️  AI_PROVIDER je postavljen na '{Config.AI_PROVIDER}'")
        print("   Promeni na 'gemini' u .env fajlu za ovaj test")
    elif not Config.GEMINI_API_KEY:
        print("❌ Gemini API ključ nije postavljen!")
    else:
        try:
            # Kreiraj servis
            service = GeminiService()

            # Test jednostavnog poziva
            print("\n📤 Test pitanje: 'Šta je Python?'")
            odgovor = service.pozovi_ai("Šta je Python u jednoj rečenici?")
            print(f"📥 Odgovor: {odgovor}")

            # Test konekcije
            print("\n🔌 Test konekcije...")
            if service.test_konekcija():
                print("✅ Konekcija sa Gemini API-jem uspešna!")

            # Malo pauze zbog rate limit-a
            time.sleep(1)

        except Exception as e:
            print(f"❌ Test neuspešan: {e}")
