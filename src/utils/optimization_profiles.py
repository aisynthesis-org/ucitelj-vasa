"""
Optimizacioni profili za AI servise
Predefinisane postavke za različite scenarije korišćenja
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ProfileType(Enum):
    """Tipovi optimizacionih profila."""
    QUICK_ANSWER = "quick_answer"
    DETAILED_EXPLANATION = "detailed_explanation"
    CODE_GENERATION = "code_generation"
    CREATIVE_WRITING = "creative_writing"
    DEBUGGING_HELP = "debugging_help"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"


@dataclass
class OptimizationProfile:
    """Definiše optimizacioni profil za AI pozive."""
    name: str
    description: str
    temperature: float
    max_tokens: int
    system_prompt_addon: str
    provider_preference: Optional[str] = None  # None znači koristi trenutni

    def to_dict(self) -> Dict[str, Any]:
        """Konvertuje profil u dictionary."""
        return {
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "system_prompt_addon": self.system_prompt_addon,
            "provider_preference": self.provider_preference
        }


# Predefinisani profili
PROFILES = {
    ProfileType.QUICK_ANSWER: OptimizationProfile(
        name="Brzi odgovor",
        description="Kratki, direktni odgovori za jednostavna pitanja",
        temperature=0.3,
        max_tokens=100,
        system_prompt_addon="\nDaj kratak i direktan odgovor u 1-2 rečenice.",
        provider_preference="gemini"  # Gemini je obično brži za kratke odgovore
    ),

    ProfileType.DETAILED_EXPLANATION: OptimizationProfile(
        name="Detaljno objašnjenje",
        description="Opširna objašnjenja sa primerima",
        temperature=0.7,
        max_tokens=500,
        system_prompt_addon="\nDaj detaljno objašnjenje sa primerima. Objasni korak po korak.",
        provider_preference="openai"  # OpenAI bolje strukturira duge odgovore
    ),

    ProfileType.CODE_GENERATION: OptimizationProfile(
        name="Generisanje koda",
        description="Precizno generisanje koda sa komentarima",
        temperature=0.2,
        max_tokens=400,
        system_prompt_addon="\nGeneriši samo kod sa komentarima na srpskom. Kod mora biti funkcionalan i dobro struktuiran.",
        provider_preference=None  # Oba su dobra za kod
    ),

    ProfileType.CREATIVE_WRITING: OptimizationProfile(
        name="Kreativno pisanje",
        description="Kreativni sadržaj sa više mašte",
        temperature=1.2,
        max_tokens=600,
        system_prompt_addon="\nBudi kreativan i maštovit u svom odgovoru. Koristi žive opise i interesantne ideje.",
        provider_preference="openai"  # OpenAI tradicionalno bolji za kreativnost
    ),

    ProfileType.DEBUGGING_HELP: OptimizationProfile(
        name="Pomoć pri debug-ovanju",
        description="Analiza grešaka i predlozi rešenja",
        temperature=0.3,
        max_tokens=300,
        system_prompt_addon="\nAnaliziraj problem sistematski. Identifikuj mogući uzrok i predloži konkretna rešenja.",
        provider_preference=None
    ),

    ProfileType.TRANSLATION: OptimizationProfile(
        name="Prevođenje",
        description="Tačno prevođenje sa očuvanjem konteksta",
        temperature=0.1,
        max_tokens=200,
        system_prompt_addon="\nPrevedi tačno, očuvavajući originalni smisao i ton.",
        provider_preference="gemini"  # Gemini odličan za prevode
    ),

    ProfileType.SUMMARIZATION: OptimizationProfile(
        name="Rezimiranje",
        description="Sažeto predstavljanje ključnih informacija",
        temperature=0.4,
        max_tokens=200,
        system_prompt_addon="\nRezimiraj ključne informacije jasno i koncizno.",
        provider_preference=None
    )
}


class ProfileManager:
    """Upravlja optimizacionim profilima."""

    def __init__(self):
        self.profiles = PROFILES
        self.active_profile: Optional[ProfileType] = None

    def get_profile(self, profile_type: ProfileType) -> OptimizationProfile:
        """
        Vraća profil za dati tip.

        Args:
            profile_type: Tip profila

        Returns:
            OptimizationProfile objekat
        """
        return self.profiles[profile_type]

    def list_profiles(self) -> str:
        """
        Vraća formatiranu listu svih dostupnih profila.

        Returns:
            String sa listom profila
        """
        result = "📋 DOSTUPNI OPTIMIZACIONI PROFILI\n"
        result += "=" * 50 + "\n\n"

        for i, (ptype, profile) in enumerate(self.profiles.items(), 1):
            result += f"{i}. {profile.name}\n"
            result += f"   📝 {profile.description}\n"
            result += f"   🌡️ Temperature: {profile.temperature}\n"
            result += f"   📏 Max tokena: {profile.max_tokens}\n"
            if profile.provider_preference:
                result += f"   🤖 Preporučen: {profile.provider_preference.upper()}\n"
            result += "\n"

        return result

    def analyze_question(self, question: str) -> ProfileType:
        """
        Analizira pitanje i predlaže najbolji profil.

        Args:
            question: Korisnikovo pitanje

        Returns:
            Preporučeni ProfileType
        """
        question_lower = question.lower()

        # Ključne reči za različite profile
        code_keywords = ["kod", "funkcija", "class", "python", "napiši", "implementiraj",
                        "sintaksa", "primer koda", "programa"]
        debug_keywords = ["greška", "error", "ne radi", "problem", "bug", "zašto",
                         "debug", "exception", "traceback"]
        creative_keywords = ["priča", "pesma", "kreativno", "zamisli", "osmisli",
                           "maštovito", "originalno"]
        translation_keywords = ["prevedi", "prevod", "na engleski", "na srpski",
                              "translate"]
        summary_keywords = ["rezimiraj", "ukratko", "sažmi", "glavni", "ključn"]
        detail_keywords = ["objasni", "detaljno", "kako", "zašto", "razumem",
                         "nauči me", "korak po korak"]

        # Proveri ključne reči
        if any(kw in question_lower for kw in code_keywords):
            return ProfileType.CODE_GENERATION
        elif any(kw in question_lower for kw in debug_keywords):
            return ProfileType.DEBUGGING_HELP
        elif any(kw in question_lower for kw in creative_keywords):
            return ProfileType.CREATIVE_WRITING
        elif any(kw in question_lower for kw in translation_keywords):
            return ProfileType.TRANSLATION
        elif any(kw in question_lower for kw in summary_keywords):
            return ProfileType.SUMMARIZATION
        elif any(kw in question_lower for kw in detail_keywords):
            return ProfileType.DETAILED_EXPLANATION
        elif len(question.split()) < 10:  # Kratko pitanje
            return ProfileType.QUICK_ANSWER
        else:
            return ProfileType.DETAILED_EXPLANATION

    def apply_profile(self, profile_type: ProfileType,
                     current_settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Primenjuje profil na trenutne postavke.

        Args:
            profile_type: Tip profila koji se primenjuje
            current_settings: Trenutne postavke

        Returns:
            Ažurirane postavke
        """
        profile = self.get_profile(profile_type)
        self.active_profile = profile_type

        # Kopiraj trenutne postavke
        new_settings = current_settings.copy()

        # Primeni postavke profila
        new_settings["temperature"] = profile.temperature
        new_settings["max_tokens"] = profile.max_tokens

        # Dodaj addon na system prompt ako postoji
        if "system_prompt" in new_settings and profile.system_prompt_addon:
            new_settings["system_prompt"] += profile.system_prompt_addon

        # Postavi provider prefereneciju ako je specificirana
        if profile.provider_preference:
            new_settings["provider_hint"] = profile.provider_preference

        return new_settings


# Globalna instanca
profile_manager = ProfileManager()


# Test funkcionalnost
if __name__ == "__main__":
    print("🧪 Test Optimization Profiles")
    print("=" * 50)

    # Prikaži sve profile
    print(profile_manager.list_profiles())

    # Test analize pitanja
    test_questions = [
        "Šta je Python?",
        "Napiši funkciju za sortiranje liste",
        "Zašto mi kod baca IndexError?",
        "Prevedi 'Hello World' na srpski",
        "Objasni mi detaljno kako rade dekoratori u Python-u"
    ]

    print("🔍 ANALIZA PITANJA:")
    print("-" * 50)

    for q in test_questions:
        suggested = profile_manager.analyze_question(q)
        profile = profile_manager.get_profile(suggested)
        print(f"\nPitanje: '{q}'")
        print(f"Predlog: {profile.name}")
        print(f"Razlog: {profile.description}")
