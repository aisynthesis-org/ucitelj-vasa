"""
User Profile sistem za Učitelja Vasu
Omogućava personalizaciju iskustva za svakog korisnika
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum


class SkillLevel(Enum):
    """Nivoi znanja korisnika."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

    def to_serbian(self) -> str:
        """Vraća naziv na srpskom."""
        translations = {
            "beginner": "Početnik",
            "intermediate": "Srednji nivo",
            "advanced": "Napredni"
        }
        return translations.get(self.value, self.value)


class LearningStyle(Enum):
    """Stilovi učenja korisnika."""
    VISUAL = "visual"          # Voli dijagrame i ilustracije
    TEXTUAL = "textual"        # Preferira detaljne tekstualne opise
    PRACTICAL = "practical"    # Želi kod primere odmah
    THEORETICAL = "theoretical" # Voli da razume teoriju prvo

    def to_serbian(self) -> str:
        """Vraća naziv na srpskom."""
        translations = {
            "visual": "Vizuelni",
            "textual": "Tekstualni",
            "practical": "Praktični",
            "theoretical": "Teorijski"
        }
        return translations.get(self.value, self.value)


@dataclass
class UserPreferences:
    """Korisničke preference za AI odgovore."""
    response_length: str = "medium"  # short, medium, long
    code_examples: bool = True       # Da li želi primere koda
    use_analogies: bool = True       # Da li voli analogije
    language_mix: str = "mixed"      # serbian, english, mixed
    detail_level: int = 5           # 1-10 skala

    def to_system_prompt_addon(self) -> str:
        """Konvertuje preference u dodatak za system prompt."""
        prompt_parts = []

        # Dužina odgovora
        if self.response_length == "short":
            prompt_parts.append("Daj kratke, koncizne odgovore.")
        elif self.response_length == "long":
            prompt_parts.append("Daj detaljne, opširne odgovore.")

        # Primeri koda
        if not self.code_examples:
            prompt_parts.append("Izbegavaj primere koda osim ako nisu eksplicitno traženi.")
        else:
            prompt_parts.append("Uvek uključi relevantne primere koda.")

        # Analogije
        if not self.use_analogies:
            prompt_parts.append("Fokusiraj se na tehničke detalje bez analogija.")
        else:
            prompt_parts.append("Koristi analogije iz svakodnevnog života za objašnjenja.")

        # Jezik
        if self.language_mix == "serbian":
            prompt_parts.append("Koristi isključivo srpski jezik, čak i za tehničke termine.")
        elif self.language_mix == "english":
            prompt_parts.append("Koristi engleski za sve tehničke termine i objašnjenja.")

        # Nivo detalja
        if self.detail_level <= 3:
            prompt_parts.append("Drži se samo osnova bez ulaženja u detalje.")
        elif self.detail_level >= 8:
            prompt_parts.append("Daj vrlo detaljne tehničke informacije.")

        return " ".join(prompt_parts)


@dataclass
class UserProfile:
    """Profil korisnika sa svim relevantnim informacijama."""
    username: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    skill_level: SkillLevel = SkillLevel.BEGINNER
    learning_style: LearningStyle = LearningStyle.PRACTICAL
    preferences: UserPreferences = field(default_factory=UserPreferences)

    # Statistike
    total_questions: int = 0
    topics_count: Dict[str, int] = field(default_factory=dict)
    last_active: str = field(default_factory=lambda: datetime.now().isoformat())
    session_count: int = 0

    # Napredak
    completed_topics: List[str] = field(default_factory=list)
    current_learning_path: Optional[str] = None
    achievements: List[str] = field(default_factory=list)

    def update_activity(self, topic: Optional[str] = None):
        """Ažurira aktivnost korisnika."""
        self.last_active = datetime.now().isoformat()
        self.total_questions += 1

        if topic:
            self.topics_count[topic] = self.topics_count.get(topic, 0) + 1

    def get_favorite_topics(self, limit: int = 3) -> List[str]:
        """Vraća omiljene teme korisnika."""
        sorted_topics = sorted(
            self.topics_count.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [topic for topic, _ in sorted_topics[:limit]]

    def calculate_engagement_score(self) -> float:
        """Računa skor angažovanosti korisnika (0-100)."""
        score = 0.0

        # Aktivnost u poslednjih 7 dana
        last_active_date = datetime.fromisoformat(self.last_active)
        days_inactive = (datetime.now() - last_active_date).days

        if days_inactive == 0:
            score += 30
        elif days_inactive <= 3:
            score += 20
        elif days_inactive <= 7:
            score += 10

        # Broj pitanja
        if self.total_questions >= 50:
            score += 20
        elif self.total_questions >= 20:
            score += 15
        elif self.total_questions >= 10:
            score += 10
        elif self.total_questions >= 5:
            score += 5

        # Raznovrsnost tema
        topic_diversity = len(self.topics_count)
        if topic_diversity >= 10:
            score += 20
        elif topic_diversity >= 5:
            score += 15
        elif topic_diversity >= 3:
            score += 10

        # Achievements
        score += min(30, len(self.achievements) * 5)

        return min(100, score)

    def should_level_up(self) -> bool:
        """Proverava da li korisnik treba da pređe na viši nivo."""
        if self.skill_level == SkillLevel.BEGINNER:
            return (self.total_questions >= 30 and
                   len(self.completed_topics) >= 5)
        elif self.skill_level == SkillLevel.INTERMEDIATE:
            return (self.total_questions >= 100 and
                   len(self.completed_topics) >= 15)
        return False

    def level_up(self):
        """Podiže korisnika na viši nivo."""
        if self.skill_level == SkillLevel.BEGINNER:
            self.skill_level = SkillLevel.INTERMEDIATE
            self.achievements.append("intermediate_level_reached")
        elif self.skill_level == SkillLevel.INTERMEDIATE:
            self.skill_level = SkillLevel.ADVANCED
            self.achievements.append("advanced_level_reached")

    def to_dict(self) -> Dict[str, Any]:
        """Konvertuje profil u dictionary za čuvanje."""
        data = asdict(self)
        data['skill_level'] = self.skill_level.value
        data['learning_style'] = self.learning_style.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        """Kreira profil iz dictionary podataka."""
        # Konvertuj enum vrednosti
        if 'skill_level' in data:
            data['skill_level'] = SkillLevel(data['skill_level'])
        if 'learning_style' in data:
            data['learning_style'] = LearningStyle(data['learning_style'])

        # Konvertuj preferences
        if 'preferences' in data and isinstance(data['preferences'], dict):
            data['preferences'] = UserPreferences(**data['preferences'])

        return cls(**data)


class ProfileManager:
    """Upravlja svim korisničkim profilima."""

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Inicijalizuje ProfileManager.

        Args:
            storage_path: Putanja do foldera za čuvanje profila
        """
        if storage_path is None:
            # Default putanja
            self.storage_path = Path(__file__).parent.parent.parent / "data" / "profiles"
        else:
            self.storage_path = storage_path

        # Kreiraj folder ako ne postoji
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Keširan trenutni profil
        self._current_profile: Optional[UserProfile] = None

    def _get_profile_path(self, username: str) -> Path:
        """Vraća putanju do fajla profila."""
        # Sanitizuj username za bezbedno ime fajla
        safe_username = "".join(c for c in username if c.isalnum() or c in "._-")
        return self.storage_path / f"{safe_username}_profile.json"

    def create_profile(self, username: str) -> UserProfile:
        """
        Kreira novi profil korisnika.

        Args:
            username: Korisničko ime

        Returns:
            Novi UserProfile objekat
        """
        profile = UserProfile(username=username)
        self.save_profile(profile)
        return profile

    def load_profile(self, username: str) -> Optional[UserProfile]:
        """
        Učitava postojeći profil.

        Args:
            username: Korisničko ime

        Returns:
            UserProfile ili None ako ne postoji
        """
        profile_path = self._get_profile_path(username)

        if not profile_path.exists():
            return None

        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return UserProfile.from_dict(data)
        except Exception as e:
            print(f"⚠️ Greška pri učitavanju profila: {e}")
            return None

    def save_profile(self, profile: UserProfile):
        """
        Čuva profil na disk.

        Args:
            profile: UserProfile objekat za čuvanje
        """
        profile_path = self._get_profile_path(profile.username)

        try:
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(profile.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Greška pri čuvanju profila: {e}")

    def get_or_create_profile(self, username: str) -> UserProfile:
        """
        Učitava postojeći ili kreira novi profil.

        Args:
            username: Korisničko ime

        Returns:
            UserProfile objekat
        """
        profile = self.load_profile(username)
        if profile is None:
            print(f"🆕 Kreiram novi profil za: {username}")
            profile = self.create_profile(username)
        else:
            print(f"✅ Učitan postojeći profil za: {username}")
            profile.session_count += 1
            self.save_profile(profile)

        self._current_profile = profile
        return profile

    def get_current_profile(self) -> Optional[UserProfile]:
        """Vraća trenutno aktivni profil."""
        return self._current_profile

    def list_all_profiles(self) -> List[str]:
        """
        Lista sva korisnička imena sa profilima.

        Returns:
            Lista korisničkih imena
        """
        profiles = []
        for profile_file in self.storage_path.glob("*_profile.json"):
            username = profile_file.stem.replace("_profile", "")
            profiles.append(username)
        return sorted(profiles)

    def delete_profile(self, username: str) -> bool:
        """
        Briše profil korisnika.

        Args:
            username: Korisničko ime

        Returns:
            True ako je uspešno obrisano
        """
        profile_path = self._get_profile_path(username)

        if profile_path.exists():
            try:
                profile_path.unlink()
                if self._current_profile and self._current_profile.username == username:
                    self._current_profile = None
                return True
            except Exception as e:
                print(f"❌ Greška pri brisanju profila: {e}")

        return False

    def get_profile_summary(self, username: str) -> str:
        """
        Vraća kratak pregled profila.

        Args:
            username: Korisničko ime

        Returns:
            Formatiran string sa pregledom
        """
        profile = self.load_profile(username)
        if not profile:
            return f"Profil '{username}' ne postoji."

        favorite_topics = profile.get_favorite_topics()
        engagement = profile.calculate_engagement_score()

        summary = f"""
📊 PROFIL: {profile.username}
{'=' * 40}
📚 Nivo: {profile.skill_level.to_serbian()}
🎯 Stil učenja: {profile.learning_style.to_serbian()}
❓ Ukupno pitanja: {profile.total_questions}
🏆 Dostignuća: {len(profile.achievements)}
💯 Angažovanost: {engagement:.0f}%
⭐ Omiljene teme: {', '.join(favorite_topics) if favorite_topics else 'Nema još'}
📅 Poslednja aktivnost: {profile.last_active[:10]}
        """

        return summary.strip()


# Globalna instanca
profile_manager = ProfileManager()
