"""
Bazna klasa za sve AI servise
Definiše interfejs koji svi servisi moraju implementirati
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
import re


class BaseAIService(ABC):
    """Apstraktna bazna klasa za AI servise."""

    def pozovi_ai_personalizovano(
            self,
            poruka: str,
            profile: 'UserProfile',  # Forward reference da izbegnemo ciklični import
            base_system_prompt: str
    ) -> str:
        """
        Poziva AI sa personalizovanim podešavanjima.
        """
        # Import ovde da izbegnemo potencijalne ciklične importe
        from personalization.user_profile import UserProfile
        from personalization.profile_analyzer import ProfileAnalyzer

        # Generiši personalizovan system prompt
        analyzer = ProfileAnalyzer()

        # Detektuj temu trenutnog pitanja
        message_analysis = analyzer.analyze_message(poruka)
        current_topic = message_analysis["topics"][0] if message_analysis["topics"] else None

        # Dodaj personalizaciju na base prompt
        personalized_addon = analyzer.generate_personalized_prompt_addon(profile, current_topic)
        full_system_prompt = f"{base_system_prompt}\n\n{personalized_addon}"

        # Prilagodi parametre prema profilu
        original_settings = self.get_current_settings()

        # Prilagodi temperature prema skill level
        if profile.skill_level.value == "beginner":
            self.apply_settings({"temperature": 0.5})  # Konzistentniji odgovori
        elif profile.skill_level.value == "advanced":
            self.apply_settings({"temperature": 0.8})  # Kreativniji odgovori

        # Prilagodi max_tokens prema preferencama
        if profile.preferences.response_length == "short":
            self.apply_settings({"max_tokens": 100})
        elif profile.preferences.response_length == "long":
            self.apply_settings({"max_tokens": 300})

        try:
            # Pozovi AI sa personalizovanim postavkama
            response = self.pozovi_ai(poruka, full_system_prompt)

            # Post-procesiranje prema preferencama
            if not profile.preferences.code_examples and "```" in response:
                # Ukloni code blokove ako korisnik ne želi primere
                response = re.sub(r'```[\s\S]*?```', '[kod primer uklonjen]', response)

            return response

        finally:
            # Vrati originalne postavke
            self.apply_settings(original_settings)


    @abstractmethod
    def pozovi_ai(self, poruka: str, system_prompt: Optional[str] = None) -> str:
        """
        Šalje poruku AI-ju i vraća odgovor.

        Args:
            poruka: Korisnikova poruka/pitanje
            system_prompt: Opcioni system prompt za definisanje ponašanja

        Returns:
            AI odgovor kao string
        """
        pass

    @abstractmethod
    def pozovi_sa_istorijom(self, messages: List[Dict[str, str]]) -> str:
        """
        Šalje celu istoriju razgovora AI-ju.

        Args:
            messages: Lista poruka sa 'role' i 'content' ključevima

        Returns:
            AI odgovor kao string
        """
        pass

    def test_konekcija(self) -> bool:
        """
        Testira da li servis može da se poveže sa API-jem.

        Returns:
            True ako je konekcija uspešna, False inače
        """
        try:
            response = self.pozovi_ai("Reci 'zdravo' na srpskom.")
            return len(response) > 0
        except Exception as e:
            print(f"❌ Test konekcije neuspešan: {e}")
            return False

    def apply_settings(self, settings: Dict[str, Any]):
        """
        Primenjuje custom postavke na servis.

        Args:
            settings: Dictionary sa postavkama
        """
        # Primeni temperature ako postoji
        if "temperature" in settings and hasattr(self, "temperature"):
            self.temperature = settings["temperature"]
            if hasattr(self, "generation_config"):
                # Za Gemini, ažuriraj generation_config
                from google.generativeai import GenerationConfig
                self.generation_config = GenerationConfig(
                    max_output_tokens=getattr(self, "max_tokens", 150),
                    temperature=settings["temperature"]
                )

        # Primeni max_tokens ako postoji
        if "max_tokens" in settings and hasattr(self, "max_tokens"):
            self.max_tokens = settings["max_tokens"]
            if hasattr(self, "generation_config"):
                # Za Gemini, ažuriraj generation_config
                from google.generativeai import GenerationConfig
                self.generation_config = GenerationConfig(
                    max_output_tokens=settings["max_tokens"],
                    temperature=getattr(self, "temperature", 0.7)
                )

    def get_current_settings(self) -> Dict[str, Any]:
        """
        Vraća trenutne postavke servisa.

        Returns:
            Dict sa trenutnim postavkama
        """
        return {
            "temperature": getattr(self, "temperature", 0.7),
            "max_tokens": getattr(self, "max_tokens", 150),
            "model": getattr(self, "model", "unknown")
        }
