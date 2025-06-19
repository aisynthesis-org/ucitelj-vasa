"""
Definicije tipova zahteva za Učitelja Vasu
Omogućava strukturirano rukovanje različitim vrstama pitanja
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime


class RequestType(Enum):
    """Tipovi zahteva koje Vasa može da obrađuje."""
    CHAT = "chat"                # Obična konverzacija
    CODE_GENERATION = "code"     # Generisanje koda
    CODE_DEBUG = "debug"         # Debugging pomoć
    CONCEPT_EXPLAIN = "explain"  # Objašnjenje koncepata
    CODE_REVIEW = "review"       # Pregled i analiza koda
    TRANSLATION = "translate"    # Prevod koda između jezika
    OPTIMIZATION = "optimize"    # Optimizacija koda

    def get_description(self) -> str:
        """Vraća opis tipa zahteva."""
        descriptions = {
            "chat": "Opšta konverzacija i jednostavna pitanja",
            "code": "Generisanje novog koda prema specifikaciji",
            "debug": "Pomoć pri pronalaženju i rešavanju grešaka",
            "explain": "Detaljno objašnjenje programskih koncepata",
            "review": "Analiza kvaliteta postojećeg koda",
            "translate": "Prevođenje koda između programskih jezika",
            "optimize": "Poboljšanje performansi postojećeg koda"
        }
        return descriptions.get(self.value, "Nepoznat tip")

    def get_preferred_provider(self) -> str:
        """Vraća preferiranog providera za ovaj tip."""
        # Ovo može biti konfigurisano ili naučeno kroz vreme
        preferences = {
            "chat": "gemini",      # Gemini brži za jednostavne odgovore
            "code": "openai",      # OpenAI bolji za kod
            "debug": "openai",     # OpenAI bolji za analizu
            "explain": "gemini",   # Gemini daje jasnije objašnjenje
            "review": "openai",    # OpenAI detaljniji review
            "translate": "openai", # OpenAI precizniji prevod
            "optimize": "openai"  # OpenAI bolje optimizuje
        }
        return preferences.get(self.value, "any")


class RequestContext:
    """Kontekst zahteva sa dodatnim informacijama."""

    def __init__(
        self,
        programming_language: Optional[str] = None,
        error_message: Optional[str] = None,
        code_snippet: Optional[str] = None,
        user_level: Optional[str] = None,
        previous_attempts: Optional[List[str]] = None
    ):
        self.programming_language = programming_language
        self.error_message = error_message
        self.code_snippet = code_snippet
        self.user_level = user_level or "intermediate"
        self.previous_attempts = previous_attempts or []

    def to_dict(self) -> Dict[str, Any]:
        """Konvertuje kontekst u dictionary."""
        return {
            "programming_language": self.programming_language,
            "error_message": self.error_message,
            "code_snippet": self.code_snippet,
            "user_level": self.user_level,
            "previous_attempts": self.previous_attempts
        }

    def has_code_context(self) -> bool:
        """Proverava da li postoji kod kontekst."""
        return bool(self.code_snippet or self.error_message)


class StructuredRequest:
    """Strukturiran zahtev sa svim potrebnim informacijama."""

    def __init__(
        self,
        content: str,
        request_type: RequestType,
        context: Optional[RequestContext] = None,
        preferences: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.content = content
        self.request_type = request_type
        self.context = context or RequestContext()
        self.preferences = preferences or {}
        self.metadata = metadata or {}

        # Automatski dodaj timestamp
        self.metadata["timestamp"] = datetime.now().isoformat()

    def get_optimized_params(self) -> Dict[str, Any]:
        """Vraća optimizovane parametre za ovaj tip zahteva."""
        # Bazni parametri
        params = {
            "temperature": 0.7,
            "max_tokens": 150
        }

        # Prilagodi prema tipu
        if self.request_type == RequestType.CODE_GENERATION:
            params["temperature"] = 0.3  # Manja kreativnost za kod
            params["max_tokens"] = 300   # Više tokena za kod
        elif self.request_type == RequestType.CHAT:
            params["temperature"] = 0.8  # Veća kreativnost za chat
            params["max_tokens"] = 100   # Kraći odgovori
        elif self.request_type == RequestType.CODE_DEBUG:
            params["temperature"] = 0.2  # Vrlo precizno za debug
            params["max_tokens"] = 250
        elif self.request_type == RequestType.CONCEPT_EXPLAIN:
            params["temperature"] = 0.6
            params["max_tokens"] = 400   # Duže objašnjenje

        # Primeni korisničke preference
        params.update(self.preferences)

        return params

    def get_enhanced_prompt(self) -> str:
        """Generiše poboljšani prompt sa kontekstom."""
        enhanced = self.content

        # Dodaj kontekst ako postoji
        if self.context.programming_language:
            enhanced = f"[Jezik: {self.context.programming_language}] {enhanced}"

        if self.context.error_message:
            enhanced += f"\n\nGreška: {self.context.error_message}"

        if self.context.code_snippet:
            enhanced += f"\n\nKod:\n```\n{self.context.code_snippet}\n```"

        if self.context.user_level == "beginner":
            enhanced += "\n\n(Napomena: Korisnik je početnik, koristi jednostavne termine)"

        return enhanced

    def to_dict(self) -> Dict[str, Any]:
        """Konvertuje zahtev u dictionary za serijalizaciju."""
        return {
            "content": self.content,
            "request_type": self.request_type.value,
            "context": self.context.to_dict(),
            "preferences": self.preferences,
            "metadata": self.metadata
        }


class RequestAnalyzer:
    """Analizira sirovi zahtev i određuje tip."""

    # Ključne reči za prepoznavanje tipova
    TYPE_KEYWORDS = {
        RequestType.CODE_GENERATION: [
            "napiši", "generiši", "kreiraj", "kod za", "funkcij",
            "implementiraj", "primer koda", "write", "create", "generate"
        ],
        RequestType.CODE_DEBUG: [
            "greška", "error", "ne radi", "problem", "bug", "debug",
            "zašto", "exception", "pomaži", "popravi", "fix"
        ],
        RequestType.CONCEPT_EXPLAIN: [
            "objasni", "šta je", "kako funkcioniše", "razumem",
            "koncept", "teorija", "explain", "what is", "how does"
        ],
        RequestType.CODE_REVIEW: [
            "pregled", "review", "da li je dobro", "proveri",
            "analiza", "kvalitet", "najbolja praksa", "check"
        ],
        RequestType.TRANSLATION: [
            "prevedi", "konvertuj", "iz python u", "translate",
            "convert", "prebaci"
        ],
        RequestType.OPTIMIZATION: [
            "optimizuj", "brže", "performanse", "optimize",
            "faster", "performance", "poboljšaj", "improve"
        ]
    }

    @classmethod
    def analyze(cls, raw_content: str) -> RequestType:
        """
        Analizira sirovi sadržaj i određuje tip zahteva.

        Args:
            raw_content: Originalni tekst korisnika

        Returns:
            Prepoznat RequestType
        """
        content_lower = raw_content.lower()

        # Brojač poena za svaki tip
        scores = {req_type: 0 for req_type in RequestType}

        # Analiziraj ključne reči
        for req_type, keywords in cls.TYPE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in content_lower:
                    scores[req_type] += 1

        # Dodatni poeni za specifične obrasce
        if "```" in raw_content or "def " in raw_content or "class " in raw_content:
            scores[RequestType.CODE_DEBUG] += 2
            scores[RequestType.CODE_REVIEW] += 1

        if "?" in raw_content and any(word in content_lower for word in ["šta", "kako", "zašto"]):
            scores[RequestType.CONCEPT_EXPLAIN] += 1

        # Pronađi tip sa najviše poena
        max_score = max(scores.values())
        if max_score > 0:
            for req_type, score in scores.items():
                if score == max_score:
                    return req_type

        # Default na CHAT
        return RequestType.CHAT

    @classmethod
    def extract_context(cls, raw_content: str) -> RequestContext:
        """
        Ekstraktuje kontekst iz sirovog sadržaja.

        Args:
            raw_content: Originalni tekst

        Returns:
            RequestContext sa izvučenim informacijama
        """
        context = RequestContext()

        # Prepoznaj programski jezik
        languages = ["python", "javascript", "java", "c++", "c#", "go", "rust"]
        content_lower = raw_content.lower()

        for lang in languages:
            if lang in content_lower:
                context.programming_language = lang
                break

        # Izvuci kod između ``` markera
        import re
        code_blocks = re.findall(r'```[\w]*\n(.*?)```', raw_content, re.DOTALL)
        if code_blocks:
            context.code_snippet = code_blocks[0].strip()

        # Prepoznaj error poruke
        error_patterns = [
            r'(Error:.*)',
            r'(Exception:.*)',
            r'(Traceback.*)',
            r'(\w+Error:.*)'
        ]

        for pattern in error_patterns:
            match = re.search(pattern, raw_content, re.IGNORECASE)
            if match:
                context.error_message = match.group(1)
                break

        return context

    @classmethod
    def create_structured_request(
        cls,
        raw_content: str,
        force_type: Optional[RequestType] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> StructuredRequest:
        """
        Kreira strukturiran zahtev iz sirovog sadržaja.

        Args:
            raw_content: Originalni tekst
            force_type: Opciono forsiraj tip
            additional_context: Dodatni kontekst

        Returns:
            StructuredRequest objekat
        """
        # Odredi tip
        request_type = force_type or cls.analyze(raw_content)

        # Izvuci kontekst
        context = cls.extract_context(raw_content)

        # Primeni dodatni kontekst ako postoji
        if additional_context:
            if "user_level" in additional_context:
                context.user_level = additional_context["user_level"]
            if "programming_language" in additional_context:
                context.programming_language = additional_context["programming_language"]

        # Kreiraj strukturiran zahtev
        return StructuredRequest(
            content=raw_content,
            request_type=request_type,
            context=context
        )


# Test funkcionalnost - izvršava se samo ako se fajl pokrene direktno
if __name__ == "__main__":
    print("🧪 Test Request Types modula")
    print("=" * 50)

    # Kreiraj instancu analyzer-a za testiranje
    analyzer = RequestAnalyzer()

    # Test primeri
    test_cases = [
        "Kako da sortiram listu u Python-u?",
        "Napiši funkciju koja računa fibonacci",
        "Zašto mi ovaj kod baca IndexError?",
        "Objasni mi šta su closure u JavaScript-u",
        "Pregledaj ovaj kod i reci da li je dobar",
        "Kako da optimizujem ovu petlju?",
        "Zdravo, kako si?"
    ]

    for test in test_cases:
        print(f"\nTest: '{test[:50]}...'")
        req_type = analyzer.analyze(test)
        context = analyzer.extract_context(test)

        print(f"  Tip: {req_type.value} - {req_type.get_description()}")
        print(f"  Preferirani provider: {req_type.get_preferred_provider()}")
        if context.programming_language:
            print(f"  Jezik: {context.programming_language}")

    # Test strukturiranog zahteva
    print("\n" + "=" * 50)
    print("Test strukturiranog zahteva:")

    complex_request = """
    Imam problem sa ovim Python kodom:
    ```python
    def calculate_average(numbers):
        return sum(numbers) / len(numbers)
    ```
    
    Error: ZeroDivisionError: division by zero
    
    Kako da popravim ovu grešku?
    """

    # Ovde koristi već definisan analyzer
    structured = analyzer.create_structured_request(complex_request)
    print(f"\nTip: {structured.request_type.value}")
    print(f"Kontekst: {structured.context.to_dict()}")
    print(f"Optimizovani parametri: {structured.get_optimized_params()}")
