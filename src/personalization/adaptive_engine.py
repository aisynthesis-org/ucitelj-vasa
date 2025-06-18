"""
Adaptive Learning Engine za Učitelja Vasu
Automatski prilagođava ponašanje tokom razgovora
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json

from .user_profile import UserProfile, SkillLevel
from .profile_analyzer import ProfileAnalyzer


class AdaptiveEngine:
    """Engine koji dinamički prilagođava AI ponašanje."""

    def __init__(self):
        self.analyzer = ProfileAnalyzer()
        self.session_data = {
            "confusion_indicators": 0,
            "understanding_indicators": 0,
            "questions_asked": 0,
            "topics_covered": set(),
            "adaptations_made": []
        }

    def analyze_user_response(self, response: str) -> Dict[str, any]:
        """
        Analizira korisnikov odgovor na AI objašnjenje.

        Args:
            response: Korisnička poruka

        Returns:
            Analiza sa indikatorima razumevanja
        """
        response_lower = response.lower()

        # Indikatori konfuzije
        confusion_words = [
            "ne razumem", "nije jasno", "zbunjuje", "komplikovano",
            "možeš li ponovo", "ne kapiram", "šta", "kako to",
            "zašto baš tako", "previše informacija"
        ]

        # Indikatori razumevanja
        understanding_words = [
            "razumem", "jasno", "ima smisla", "okej", "važi",
            "super", "hvala", "shvatam", "logično", "aha"
        ]

        # Follow-up pitanja
        is_followup = "?" in response and len(response) < 100

        # Brojanje indikatora
        confusion_count = sum(1 for word in confusion_words if word in response_lower)
        understanding_count = sum(1 for word in understanding_words if word in response_lower)

        # Ažuriraj session data
        self.session_data["confusion_indicators"] += confusion_count
        self.session_data["understanding_indicators"] += understanding_count

        return {
            "shows_confusion": confusion_count > 0,
            "shows_understanding": understanding_count > 0,
            "is_followup_question": is_followup,
            "confidence_score": self._calculate_confidence_score()
        }

    def _calculate_confidence_score(self) -> float:
        """Računa skor poverenja korisnika (0-1)."""
        total = (self.session_data["confusion_indicators"] +
                self.session_data["understanding_indicators"])

        if total == 0:
            return 0.5  # Neutralno

        return self.session_data["understanding_indicators"] / total

    def suggest_adaptation(
        self,
        profile: UserProfile,
        last_response_analysis: Dict[str, any]
    ) -> Optional[Dict[str, any]]:
        """
        Predlaže prilagođavanje na osnovu analize.

        Args:
            profile: Korisnički profil
            last_response_analysis: Analiza poslednjeg odgovora

        Returns:
            Predlog prilagođavanja ili None
        """
        if last_response_analysis["shows_confusion"]:
            # Korisnik je zbunjen
            if profile.skill_level == SkillLevel.BEGINNER:
                return {
                    "action": "simplify",
                    "suggestion": "Koristi još jednostavnije objašnjenje sa analogijom",
                    "prompt_addon": "Objasni ponovo, ali još jednostavnije. "
                                  "Koristi analogiju iz svakodnevnog života."
                }
            else:
                return {
                    "action": "clarify",
                    "suggestion": "Razloži na korake",
                    "prompt_addon": "Razloži objašnjenje na numerisane korake."
                }

        elif last_response_analysis["is_followup_question"]:
            # Dublje objašnjenje
            return {
                "action": "elaborate",
                "suggestion": "Daj detaljnije objašnjenje",
                "prompt_addon": "Daj detaljnije objašnjenje sa fokusom na pitanje korisnika."
            }

        elif last_response_analysis["confidence_score"] > 0.8:
            # Korisnik dobro razume
            if self.session_data["questions_asked"] > 5:
                return {
                    "action": "advance",
                    "suggestion": "Pređi na naprednije koncepte",
                    "prompt_addon": "Korisnik dobro razume. Možeš preći na naprednije aspekte."
                }

        return None

    def apply_adaptation(
        self,
        adaptation: Dict[str, any],
        original_prompt: str
    ) -> str:
        """
        Primenjuje prilagođavanje na prompt.

        Args:
            adaptation: Predlog prilagođavanja
            original_prompt: Originalni prompt

        Returns:
            Prilagođen prompt
        """
        # Zapamti prilagođavanje
        self.session_data["adaptations_made"].append({
            "time": datetime.now().isoformat(),
            "action": adaptation["action"]
        })

        # Primeni na prompt
        return f"{original_prompt}\n\n[PRILAGOĐAVANJE: {adaptation['prompt_addon']}]"

    def generate_session_summary(self) -> Dict[str, any]:
        """Generiše rezime sesije za čuvanje u profilu."""
        confidence = self._calculate_confidence_score()

        return {
            "duration_questions": self.session_data["questions_asked"],
            "final_confidence": confidence,
            "topics_covered": list(self.session_data["topics_covered"]),
            "adaptations_count": len(self.session_data["adaptations_made"]),
            "recommendation": self._generate_recommendation(confidence)
        }

    def _generate_recommendation(self, confidence: float) -> str:
        """Generiše preporuku za dalji rad."""
        if confidence < 0.3:
            return "Preporučujem dodatno vežbanje osnova pre novih tema."
        elif confidence < 0.7:
            return "Solidno napredovanje, nastavi trenutnim tempom."
        else:
            return "Odlično razumevanje! Spreman si za naprednije teme."

    def reset_session(self):
        """Resetuje session podatke za novi razgovor."""
        self.session_data = {
            "confusion_indicators": 0,
            "understanding_indicators": 0,
            "questions_asked": 0,
            "topics_covered": set(),
            "adaptations_made": []
        }
