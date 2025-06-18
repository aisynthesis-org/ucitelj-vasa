"""
Profile Analyzer za Učitelja Vasu
Analizira korisničko ponašanje i predlaže prilagođavanja
"""

import re
from typing import Dict, List, Tuple, Optional
from collections import Counter
from datetime import datetime, timedelta

from .user_profile import UserProfile, SkillLevel, LearningStyle


class ProfileAnalyzer:
    """Analizira korisničke profile i ponašanje."""

    # Ključne reči za detekciju tema
    TOPIC_KEYWORDS = {
        "python_osnove": ["python", "promenljiv", "variable", "tip", "string", "broj", "lista"],
        "funkcije": ["funkcij", "def", "return", "parametar", "argument"],
        "klase": ["klasa", "class", "objekat", "metod", "nasledjivanje"],
        "greske": ["greška", "error", "exception", "try", "except", "debug"],
        "api": ["api", "request", "response", "endpoint", "json"],
        "git": ["git", "commit", "branch", "merge", "repository"],
        "web": ["web", "html", "css", "javascript", "frontend", "backend"],
        "baze": ["baza", "sql", "database", "query", "tabela"],
        "ai": ["ai", "veštačk", "inteligencij", "machine learning", "neural"]
    }

    # Indikatori nivoa znanja
    SKILL_INDICATORS = {
        "beginner": [
            "šta je", "kako da", "ne razumem", "objasni", "pokaži primer",
            "prvi put", "početnik", "osnov", "jednostavn"
        ],
        "intermediate": [
            "zašto", "razlika između", "kada koristiti", "najbolja praksa",
            "efikasnij", "alternativ", "kako funkcioniše"
        ],
        "advanced": [
            "optimizacij", "performans", "složenost", "algoritam",
            "arhitektur", "pattern", "skalabilnost", "concurrency"
        ]
    }

    def analyze_message(self, message: str) -> Dict[str, any]:
        """
        Analizira pojedinačnu poruku korisnika.

        Args:
            message: Poruka za analizu

        Returns:
            Dict sa rezultatima analize
        """
        message_lower = message.lower()

        # Detektuj temu
        detected_topics = []
        for topic, keywords in self.TOPIC_KEYWORDS.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_topics.append(topic)

        # Detektuj nivo
        skill_scores = {
            "beginner": 0,
            "intermediate": 0,
            "advanced": 0
        }

        for level, indicators in self.SKILL_INDICATORS.items():
            for indicator in indicators:
                if indicator in message_lower:
                    skill_scores[level] += 1

        # Analiziraj karakteristike pitanja
        characteristics = {
            "length": len(message),
            "has_code": bool(re.search(r'`.*?`|def\s+\w+|class\s+\w+', message)),
            "is_question": message.strip().endswith("?"),
            "complexity": self._calculate_complexity(message),
            "requests_example": any(word in message_lower for word in
                                  ["primer", "pokaži", "demonstr", "kako izgleda"])
        }

        return {
            "topics": detected_topics,
            "skill_indicators": skill_scores,
            "characteristics": characteristics,
            "suggested_level": max(skill_scores, key=skill_scores.get)
        }

    def _calculate_complexity(self, message: str) -> float:
        """
        Računa složenost pitanja (0-10 skala).

        Args:
            message: Poruka za analizu

        Returns:
            Skor složenosti
        """
        score = 0.0

        # Dužina doprinosi složenosti
        if len(message) > 200:
            score += 2
        elif len(message) > 100:
            score += 1

        # Tehničke reči
        tech_words = ["algoritam", "struktur", "implement", "optimiz",
                     "performans", "async", "thread", "memory"]
        tech_count = sum(1 for word in tech_words if word in message.lower())
        score += min(3, tech_count)

        # Više rečenica = veća složenost
        sentences = len(re.split(r'[.!?]+', message))
        if sentences > 3:
            score += 2
        elif sentences > 1:
            score += 1

        # Kod blokovi
        if re.search(r'```.*?```', message, re.DOTALL):
            score += 2

        return min(10, score)

    def analyze_conversation_history(
        self,
        messages: List[str],
        profile: UserProfile
    ) -> Dict[str, any]:
        """
        Analizira celu istoriju razgovora.

        Args:
            messages: Lista poruka korisnika
            profile: Korisnički profil

        Returns:
            Agregirana analiza
        """
        if not messages:
            return {}

        # Analiziraj svaku poruku
        analyses = [self.analyze_message(msg) for msg in messages]

        # Agregiraj teme
        all_topics = []
        for analysis in analyses:
            all_topics.extend(analysis["topics"])
        topic_counts = Counter(all_topics)

        # Prosečna složenost
        avg_complexity = sum(a["characteristics"]["complexity"]
                           for a in analyses) / len(analyses)

        # Učestalost traženja primera
        example_rate = sum(1 for a in analyses
                         if a["characteristics"]["requests_example"]) / len(analyses)

        # Preporučeni nivo na osnovu svih poruka
        skill_totals = {"beginner": 0, "intermediate": 0, "advanced": 0}
        for analysis in analyses:
            for level, score in analysis["skill_indicators"].items():
                skill_totals[level] += score

        recommended_level = max(skill_totals, key=skill_totals.get)

        return {
            "total_messages": len(messages),
            "top_topics": topic_counts.most_common(3),
            "average_complexity": avg_complexity,
            "example_request_rate": example_rate,
            "recommended_skill_level": recommended_level,
            "skill_confidence": skill_totals[recommended_level] / sum(skill_totals.values())
                               if sum(skill_totals.values()) > 0 else 0
        }

    def suggest_profile_updates(
        self,
        profile: UserProfile,
        recent_messages: List[str]
    ) -> List[Tuple[str, any]]:
        """
        Predlaže ažuriranja profila na osnovu skorašnje aktivnosti.

        Args:
            profile: Trenutni profil
            recent_messages: Poslednjih N poruka

        Returns:
            Lista (atribut, nova_vrednost) tuplova
        """
        suggestions = []

        if len(recent_messages) < 5:
            return suggestions  # Premalo podataka

        # Analiziraj skorašnje poruke
        analysis = self.analyze_conversation_history(recent_messages, profile)

        # Predlog za skill level
        if analysis["skill_confidence"] > 0.7:
            recommended = analysis["recommended_skill_level"]
            current = profile.skill_level.value

            if recommended != current:
                if recommended == "intermediate" and current == "beginner":
                    suggestions.append(("skill_level", SkillLevel.INTERMEDIATE))
                elif recommended == "advanced" and current == "intermediate":
                    suggestions.append(("skill_level", SkillLevel.ADVANCED))

        # Predlog za learning style
        if analysis["example_request_rate"] > 0.6:
            if profile.learning_style != LearningStyle.PRACTICAL:
                suggestions.append(("learning_style", LearningStyle.PRACTICAL))
        elif analysis["average_complexity"] > 7:
            if profile.learning_style != LearningStyle.THEORETICAL:
                suggestions.append(("learning_style", LearningStyle.THEORETICAL))

        # Predlog za response length
        avg_msg_length = sum(len(msg) for msg in recent_messages) / len(recent_messages)
        if avg_msg_length < 50 and profile.preferences.response_length != "short":
            suggestions.append(("preferences.response_length", "short"))
        elif avg_msg_length > 150 and profile.preferences.response_length != "long":
            suggestions.append(("preferences.response_length", "long"))

        return suggestions

    def generate_personalized_prompt_addon(
        self,
        profile: UserProfile,
        current_topic: Optional[str] = None
    ) -> str:
        """
        Generiše personalizovan dodatak za system prompt.

        Args:
            profile: Korisnički profil
            current_topic: Trenutna tema razgovora

        Returns:
            Dodatak za system prompt
        """
        parts = []

        # Osnovno prilagođavanje nivou
        if profile.skill_level == SkillLevel.BEGINNER:
            parts.append(
                "Korisnik je početnik. Koristi jednostavne termine, "
                "daj detaljne korake i izbegavaj napredne koncepte."
            )
        elif profile.skill_level == SkillLevel.INTERMEDIATE:
            parts.append(
                "Korisnik ima osnovno znanje. Možeš koristiti tehničke termine "
                "ali ih objasni kada su novi. Fokusiraj se na praktičnu primenu."
            )
        else:  # ADVANCED
            parts.append(
                "Korisnik je napredan. Možeš koristiti složene koncepte, "
                "govoriti o optimizaciji i arhitekturi bez detaljnih objašnjenja osnova."
            )

        # Prilagođavanje stilu učenja
        if profile.learning_style == LearningStyle.VISUAL:
            parts.append("Koristi ASCII dijagrame i vizuelne reprezentacije kad god je moguće.")
        elif profile.learning_style == LearningStyle.PRACTICAL:
            parts.append("Fokusiraj se na praktične primere koda koje korisnik može odmah isprobati.")
        elif profile.learning_style == LearningStyle.THEORETICAL:
            parts.append("Objasni teorijske osnove i razloge zašto nešto funkcioniše kako funkcioniše.")

        # Dodaj preference
        parts.append(profile.preferences.to_system_prompt_addon())

        # Kontekstualne informacije
        if current_topic and current_topic in profile.topics_count:
            times = profile.topics_count[current_topic]
            if times > 5:
                parts.append(f"Korisnik je već postavljao pitanja o ovoj temi {times} puta, "
                           "tako da možeš graditi na prethodnom znanju.")

        # Personalizovani pozdrav
        if profile.total_questions < 5:
            parts.append("Korisnik je nov, budi posebno ljubazan i ohrabrujući.")
        elif profile.total_questions > 50:
            parts.append(f"Pozdravi korisnika kao 'dragi {profile.username}' - već se dobro poznajete.")

        return " ".join(parts)
