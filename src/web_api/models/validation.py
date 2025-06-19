"""
Pydantic modeli za validaciju podataka u Učitelju Vasi
Osigurava type safety i automatsku validaciju
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Dict, Any, List, Literal, Union
from datetime import datetime
from enum import Enum

from web_api.models.request_types import RequestType


# Osnovni modeli za request/response

class BaseRequest(BaseModel):
    """Bazni model za sve zahteve."""

    class Config:
        # Dozvoli enum values umesto samo enum objekata
        use_enum_values = True
        # Prikaži primer u dokumentaciji
        json_schema_extra = {
            "example": {
                "pitanje": "Kako da sortiram listu u Python-u?"
            }
        }


class SimpleQuestionRequest(BaseRequest):
    """Jednostavan zahtev sa samo pitanjem."""

    pitanje: str = Field(
        ...,  # ... znači obavezno polje
        min_length=1,
        max_length=2000,
        description="Pitanje za AI asistenta"
    )

    @field_validator('pitanje')
    @classmethod
    def pitanje_not_empty(cls, v):
        """Proveri da pitanje nije samo whitespace."""
        if not v.strip():
            raise ValueError('Pitanje ne može biti prazno')
        return v.strip()


class ProgrammingLanguage(str, Enum):
    """Podržani programski jezici."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    CPP = "cpp"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"
    OTHER = "other"


class UserLevel(str, Enum):
    """Nivoi znanja korisnika."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class RequestContext(BaseModel):
    """Kontekst zahteva sa dodatnim informacijama."""

    programming_language: Optional[ProgrammingLanguage] = Field(
        None,
        description="Programski jezik za koji se traži pomoć"
    )

    error_message: Optional[str] = Field(
        None,
        max_length=1000,
        description="Poruka o grešci ako postoji"
    )

    code_snippet: Optional[str] = Field(
        None,
        max_length=5000,
        description="Deo koda relevantan za pitanje"
    )

    user_level: UserLevel = Field(
        UserLevel.INTERMEDIATE,
        description="Nivo znanja korisnika"
    )

    previous_attempts: List[str] = Field(
        default_factory=list,
        max_items=5,
        description="Prethodni pokušaji rešavanja"
    )

    @field_validator('code_snippet')
    @classmethod
    def clean_code_snippet(cls, v):
        """Očisti code snippet od ekstra whitespace."""
        if v:
            return v.strip()
        return v


class AIPreferences(BaseModel):
    """Preference za AI odgovor."""

    temperature: float = Field(
        0.7,
        ge=0.0,  # greater or equal
        le=2.0,  # less or equal
        description="Kreativnost odgovora (0=deterministički, 2=vrlo kreativan)"
    )

    max_tokens: int = Field(
        150,
        ge=50,
        le=2000,
        description="Maksimalan broj tokena u odgovoru"
    )

    response_style: Literal["concise", "detailed", "tutorial"] = Field(
        "concise",
        description="Stil odgovora"
    )

    include_examples: bool = Field(
        True,
        description="Da li uključiti primere koda"
    )

    language: Literal["sr", "en"] = Field(
        "sr",
        description="Jezik odgovora"
    )


class StructuredQuestionRequest(BaseRequest):
    """Strukturiran zahtev sa svim opcijama."""

    pitanje: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Glavno pitanje"
    )

    tip: Optional[RequestType] = Field(
        None,
        description="Eksplicitni tip zahteva"
    )

    context: Optional[RequestContext] = Field(
        None,
        description="Dodatni kontekst"
    )

    preferences: Optional[AIPreferences] = Field(
        None,
        description="AI preference"
    )

    force_provider: Optional[Literal["openai", "gemini"]] = Field(
        None,
        description="Forsiraj specifičan provider"
    )

    session_id: Optional[str] = Field(
        None,
        pattern="^[a-zA-Z0-9_-]+$",  # Promenjen regex u pattern
        max_length=50,
        description="ID sesije za praćenje konverzacije"
    )

    @field_validator('pitanje')
    @classmethod
    def clean_question(cls, v):
        """Očisti pitanje."""
        return v.strip()

    @model_validator(mode='after')
    def validate_context_with_type(self):
        """Proveri da li kontekst odgovara tipu."""
        if self.tip == RequestType.CODE_DEBUG and self.context:
            if not self.context.code_snippet and not self.context.error_message:
                raise ValueError(
                    'Debug tip zahteva kod ili error poruku u kontekstu'
                )
        return self

    class Config:
        json_schema_extra = {  # Promenjeno iz schema_extra
            "example": {
                "pitanje": "Zašto mi ova funkcija vraća None?",
                "tip": "debug",
                "context": {
                    "programming_language": "python",
                    "code_snippet": "def suma(a, b):\n    print(a + b)",
                    "user_level": "beginner"
                },
                "preferences": {
                    "temperature": 0.3,
                    "response_style": "detailed",
                    "include_examples": True
                }
            }
        }


# Response modeli

class ProviderInfo(BaseModel):
    """Informacije o korišćenom provideru."""

    selected: str = Field(..., description="Izabrani provider")
    reason: str = Field(..., description="Razlog izbora")
    strategy: str = Field(..., description="Korišćena strategija")
    available_providers: List[str] = Field(
        ...,
        description="Svi dostupni provideri"
    )


class OptimizationInfo(BaseModel):
    """Informacije o optimizaciji."""

    temperature: float = Field(..., description="Korišćena temperatura")
    max_tokens: int = Field(..., description="Max tokena")
    adjusted_for_type: bool = Field(
        ...,
        description="Da li su parametri prilagođeni tipu"
    )


class QuestionResponse(BaseModel):
    """Standardni odgovor na pitanje."""

    pitanje: str = Field(..., description="Originalno pitanje")
    odgovor: str = Field(..., description="AI odgovor")
    tip_zahteva: str = Field(..., description="Prepoznat tip zahteva")
    provider: ProviderInfo = Field(..., description="Provider info")
    optimization: Optional[OptimizationInfo] = Field(
        None,
        description="Optimizacija info"
    )
    context_used: bool = Field(
        False,
        description="Da li je korišćen kontekst"
    )
    session_id: Optional[str] = Field(
        None,
        description="ID sesije"
    )
    response_time_ms: Optional[int] = Field(
        None,
        description="Vreme odgovora u milisekundama"
    )

    class Config:
        json_schema_extra = {  # Promenjeno iz schema_extra
            "example": {
                "pitanje": "Kako da sortiram listu?",
                "odgovor": "U Python-u možeš sortirati listu na nekoliko načina...",
                "tip_zahteva": "explain",
                "provider": {
                    "selected": "gemini",
                    "reason": "Best for explain requests",
                    "strategy": "static",
                    "available_providers": ["openai", "gemini"]
                },
                "optimization": {
                    "temperature": 0.6,
                    "max_tokens": 400,
                    "adjusted_for_type": True
                },
                "context_used": False,
                "response_time_ms": 1250
            }
        }


class ErrorResponse(BaseModel):
    """Standardni error response."""

    error: str = Field(..., description="Tip greške")
    detail: str = Field(..., description="Detaljan opis")
    suggestion: Optional[str] = Field(
        None,
        description="Predlog za rešavanje"
    )
    error_code: Optional[str] = Field(
        None,
        description="Interni kod greške"
    )

    class Config:
        json_schema_extra = {  # Promenjeno iz schema_extra
            "example": {
                "error": "validation_error",
                "detail": "Pitanje je predugačko (max 2000 karaktera)",
                "suggestion": "Skrati pitanje ili ga podeli na više manjih",
                "error_code": "VAL001"
            }
        }


# Provider-specifični modeli

class OpenAISpecificRequest(BaseModel):
    """OpenAI specifične opcije."""

    model: Literal["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"] = Field(
        "gpt-3.5-turbo",
        description="OpenAI model"
    )

    system_prompt: Optional[str] = Field(
        None,
        max_length=1000,
        description="Custom system prompt"
    )

    presence_penalty: float = Field(
        0.0,
        ge=-2.0,
        le=2.0,
        description="Penalizuje ponavljanje tema"
    )

    frequency_penalty: float = Field(
        0.0,
        ge=-2.0,
        le=2.0,
        description="Penalizuje ponavljanje reči"
    )

    top_p: float = Field(
        1.0,
        ge=0.0,
        le=1.0,
        description="Nucleus sampling"
    )

    stop_sequences: List[str] = Field(
        default_factory=list,
        max_items=4,
        description="Sekvence za prekid generisanja"
    )


class GeminiSpecificRequest(BaseModel):
    """Gemini specifične opcije."""

    model: Literal["gemini-pro", "gemini-pro-vision"] = Field(
        "gemini-pro",
        description="Gemini model"
    )

    safety_settings: Dict[str, str] = Field(
        default_factory=dict,
        description="Safety filter settings"
    )

    candidate_count: int = Field(
        1,
        ge=1,
        le=8,
        description="Broj kandidat odgovora"
    )

    stop_sequences: List[str] = Field(
        default_factory=list,
        max_items=5,
        description="Stop sekvence"
    )


class ProviderSpecificRequest(BaseModel):
    """Wrapper za provider-specifične opcije."""

    provider: Literal["openai", "gemini"] = Field(
        ...,
        description="Target provider"
    )

    options: Union[OpenAISpecificRequest, GeminiSpecificRequest] = Field(
        ...,
        description="Provider-specific options"
    )

    @model_validator(mode='after')
    def validate_options_match_provider(self):
        """Proveri da opcije odgovaraju provideru."""
        if self.provider == 'openai' and not isinstance(self.options, OpenAISpecificRequest):
            raise ValueError('OpenAI provider zahteva OpenAISpecificRequest opcije')

        if self.provider == 'gemini' and not isinstance(self.options, GeminiSpecificRequest):
            raise ValueError('Gemini provider zahteva GeminiSpecificRequest opcije')

        return self


# Validation utility funkcije

def validate_api_key(api_key: str, provider: str) -> bool:
    """
    Validira format API ključa za provider.

    Args:
        api_key: API ključ za validaciju
        provider: Ime providera

    Returns:
        True ako je valjan format
    """
    if provider == "openai":
        # OpenAI ključevi počinju sa 'sk-'
        return api_key.startswith("sk-") and len(api_key) > 20

    elif provider == "gemini":
        # Gemini ključevi su obično 39 karaktera
        return len(api_key) == 39

    return False


def sanitize_code_snippet(code: str) -> str:
    """
    Sanitizuje kod snippet za sigurno procesiranje.

    Args:
        code: Sirovi kod

    Returns:
        Očišćen kod
    """
    # Ukloni potencijalno opasne stringove
    dangerous_patterns = [
        "__import__",
        "eval(",
        "exec(",
        "compile(",
        "globals(",
        "locals("
    ]

    sanitized = code
    for pattern in dangerous_patterns:
        sanitized = sanitized.replace(pattern, f"[REMOVED: {pattern}]")

    return sanitized.strip()


# Test funkcionalnost
if __name__ == "__main__":
    print("🧪 Test Pydantic modela")
    print("=" * 50)

    # Test jednostavnog zahteva
    print("\n1. Test jednostavnog zahteva:")
    try:
        simple = SimpleQuestionRequest(pitanje="  Kako da sortiram listu?  ")
        print(f"✅ Validno: {simple.pitanje}")
    except Exception as e:
        print(f"❌ Greška: {e}")

    # Test praznog pitanja
    print("\n2. Test praznog pitanja:")
    try:
        empty = SimpleQuestionRequest(pitanje="   ")
        print(f"✅ Validno: {empty.pitanje}")
    except Exception as e:
        print(f"❌ Greška: {e}")

    # Test strukturiranog zahteva
    print("\n3. Test strukturiranog zahteva:")
    structured_data = {
        "pitanje": "Debug ovaj kod",
        "tip": "debug",
        "context": {
            "programming_language": "python",
            "code_snippet": "def test():\n    pass",
            "user_level": "beginner"
        },
        "preferences": {
            "temperature": 0.3,
            "response_style": "detailed"
        }
    }

    try:
        structured = StructuredQuestionRequest(**structured_data)
        print(f"✅ Validno:")
        print(f"   Tip: {structured.tip}")
        print(f"   Jezik: {structured.context.programming_language}")
        print(f"   Stil: {structured.preferences.response_style}")
    except Exception as e:
        print(f"❌ Greška: {e}")

    # Test JSON Schema generisanja
    print("\n4. JSON Schema:")
    print(f"Schema ima {len(StructuredQuestionRequest.model_json_schema()['properties'])} polja")

    # Test provider-specific
    print("\n5. Test provider-specific modela:")
    openai_req = ProviderSpecificRequest(
        provider="openai",
        options=OpenAISpecificRequest(
            model="gpt-4",
            temperature=0.5,
            top_p=0.9
        )
    )
    print(f"✅ OpenAI request: model={openai_req.options.model}")
