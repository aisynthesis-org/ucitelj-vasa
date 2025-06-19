"""
Provider servisi sa Pydantic validacijom
Omogućava type-safe rad sa AI servisima
"""

from typing import Dict, Any, Optional, List

from fastapi import HTTPException
from pydantic import BaseModel, ValidationError
import logging

from ai_services.base_service import BaseAIService
from ai_services.openai_service import OpenAIService
from ai_services.gemini_service import GeminiService
from web_api.models.validation import (
    OpenAISpecificRequest,
    GeminiSpecificRequest,
    ProviderSpecificRequest
)

logger = logging.getLogger(__name__)


class ValidatedOpenAIService(OpenAIService):
    """OpenAI servis sa Pydantic validacijom."""

    def __init__(self):
        super().__init__()
        self._custom_settings: Optional[OpenAISpecificRequest] = None

    def apply_validated_settings(self, settings: OpenAISpecificRequest):
        """
        Primenjuje validirane postavke.

        Args:
            settings: OpenAI specifične postavke
        """
        self._custom_settings = settings

        # Konvertuj u standardne postavke
        standard_settings = {
            "model": settings.model,
            "temperature": settings.temperature if hasattr(settings, 'temperature') else 0.7,
            "max_tokens": settings.max_tokens if hasattr(settings, 'max_tokens') else 150,
            "top_p": settings.top_p,
            "frequency_penalty": settings.frequency_penalty,
            "presence_penalty": settings.presence_penalty
        }

        # Primeni kroz baznu metodu
        self.apply_settings(standard_settings)

        logger.info(f"Primenjene OpenAI postavke: model={settings.model}, top_p={settings.top_p}")

    def pozovi_ai(
            self,
            poruka: str,
            system_prompt: Optional[str] = None,
            **kwargs
    ) -> str:
        """
        Poziva OpenAI sa validiranim postavkama.

        Args:
            poruka: Korisnička poruka
            system_prompt: System prompt
            **kwargs: Dodatne opcije

        Returns:
            AI odgovor
        """
        # Ako imamo custom settings, koristi ih
        if self._custom_settings:
            # Override system prompt ako je dat
            if self._custom_settings.system_prompt:
                system_prompt = self._custom_settings.system_prompt

            # Dodaj stop sekvence ako postoje
            if self._custom_settings.stop_sequences:
                kwargs['stop'] = self._custom_settings.stop_sequences

        # Pozovi parent metodu
        return super().pozovi_ai(poruka, system_prompt, **kwargs)

    def get_capabilities(self) -> Dict[str, Any]:
        """Vraća mogućnosti ovog servisa."""
        return {
            "provider": "openai",
            "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
            "features": {
                "streaming": True,
                "function_calling": True,
                "vision": False,  # Zavisi od modela
                "max_context": 4096,  # Zavisi od modela
                "fine_tuning": True
            },
            "parameters": {
                "temperature": {"min": 0, "max": 2, "default": 0.7},
                "max_tokens": {"min": 1, "max": 4096, "default": 150},
                "top_p": {"min": 0, "max": 1, "default": 1},
                "frequency_penalty": {"min": -2, "max": 2, "default": 0},
                "presence_penalty": {"min": -2, "max": 2, "default": 0}
            }
        }


class ValidatedGeminiService(GeminiService):
    """Gemini servis sa Pydantic validacijom."""

    def __init__(self):
        super().__init__()
        self._custom_settings: Optional[GeminiSpecificRequest] = None

    def apply_validated_settings(self, settings: GeminiSpecificRequest):
        """
        Primenjuje validirane Gemini postavke.

        Args:
            settings: Gemini specifične postavke
        """
        self._custom_settings = settings

        # Gemini koristi drugačije nazive
        standard_settings = {
            "model": settings.model,
            "temperature": 0.7,  # Default, Gemini možda ne podržava
            "max_tokens": 150,  # Default
            "candidate_count": settings.candidate_count
        }

        self.apply_settings(standard_settings)

        logger.info(f"Primenjene Gemini postavke: model={settings.model}, candidates={settings.candidate_count}")

    def pozovi_ai(
            self,
            poruka: str,
            system_prompt: Optional[str] = None,
            **kwargs
    ) -> str:
        """
        Poziva Gemini sa validiranim postavkama.

        Args:
            poruka: Korisnička poruka
            system_prompt: System prompt
            **kwargs: Dodatne opcije

        Returns:
            AI odgovor
        """
        # Pripremi generation config
        if self._custom_settings:
            generation_config = {
                "candidate_count": self._custom_settings.candidate_count,
                "stop_sequences": self._custom_settings.stop_sequences,
                "temperature": kwargs.get('temperature', 0.7),
                "max_output_tokens": kwargs.get('max_tokens', 150)
            }

            # Primeni safety settings
            if self._custom_settings.safety_settings:
                kwargs['safety_settings'] = self._custom_settings.safety_settings

            kwargs['generation_config'] = generation_config

        return super().pozovi_ai(poruka, system_prompt, **kwargs)

    def get_capabilities(self) -> Dict[str, Any]:
        """Vraća mogućnosti Gemini servisa."""
        return {
            "provider": "gemini",
            "models": ["gemini-pro", "gemini-pro-vision"],
            "features": {
                "streaming": True,
                "function_calling": False,  # Trenutno
                "vision": True,  # gemini-pro-vision
                "max_context": 32768,
                "fine_tuning": False
            },
            "parameters": {
                "temperature": {"min": 0, "max": 1, "default": 0.7},
                "max_tokens": {"min": 1, "max": 2048, "default": 150},
                "candidate_count": {"min": 1, "max": 8, "default": 1}
            },
            "safety_categories": [
                "HARM_CATEGORY_HARASSMENT",
                "HARM_CATEGORY_HATE_SPEECH",
                "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "HARM_CATEGORY_DANGEROUS_CONTENT"
            ]
        }


class ValidatedAIServiceFactory:
    """Factory za kreiranje validiranih AI servisa."""

    @staticmethod
    def create_validated_service(
            provider: str,
            specific_request: Optional[ProviderSpecificRequest] = None
    ) -> BaseAIService:
        """
        Kreira validiran AI servis.

        Args:
            provider: Ime providera
            specific_request: Provider-specifične opcije

        Returns:
            Validiran AI servis

        Raises:
            ValueError: Ako provider nije podržan
        """
        if provider == "openai":
            service = ValidatedOpenAIService()

            if specific_request and isinstance(specific_request.options, OpenAISpecificRequest):
                service.apply_validated_settings(specific_request.options)

        elif provider == "gemini":
            service = ValidatedGeminiService()

            if specific_request and isinstance(specific_request.options, GeminiSpecificRequest):
                service.apply_validated_settings(specific_request.options)

        else:
            raise ValueError(f"Provider '{provider}' nije podržan")

        return service

    @staticmethod
    def get_provider_schema(provider: str) -> Dict[str, Any]:
        """
        Vraća JSON Schema za provider-specifične opcije.

        Args:
            provider: Ime providera

        Returns:
            JSON Schema
        """
        if provider == "openai":
            return OpenAISpecificRequest.schema()
        elif provider == "gemini":
            return GeminiSpecificRequest.schema()
        else:
            return {}


# Dodaj endpoint za provider-specific pozive
def add_provider_specific_endpoint(app):
    """Dodaje provider-specific endpoint u FastAPI app."""

    @app.post("/providers/{provider}/ask",
              summary="Provider-specifični AI poziv",
              description="Poziva specifičan provider sa custom opcijama",
              tags=["Providers"]
              )
    async def provider_specific_ask(
            provider: str,
            request: ProviderSpecificRequest
    ):
        """Poziva specifičan provider sa validiranim opcijama."""
        try:
            # Validuj da provider odgovara request-u
            if provider != request.provider:
                raise HTTPException(
                    status_code=400,
                    detail=f"Provider '{provider}' ne odgovara request provideru '{request.provider}'"
                )

            # Kreiraj servis sa opcijama
            service = ValidatedAIServiceFactory.create_validated_service(
                provider,
                request
            )

            # Osnovno pitanje mora postojati
            if not hasattr(request, 'question'):
                raise HTTPException(
                    status_code=400,
                    detail="Request mora imati 'question' polje"
                )

            # Pozovi AI
            response = service.pozovi_ai(request.question)

            return {
                "provider": provider,
                "question": request.question,
                "response": response,
                "options_applied": request.options.dict()
            }

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Provider-specific error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Greška pri pozivanju provider-specific servisa"
            )


# Test validiranih servisa
if __name__ == "__main__":
    print("🧪 Test Validated Services")
    print("=" * 50)

    # Test OpenAI sa validacijom
    print("\n1. Test ValidatedOpenAIService:")
    try:
        openai_settings = OpenAISpecificRequest(
            model="gpt-4",
            temperature=0.5,
            top_p=0.9,
            presence_penalty=0.1
        )

        service = ValidatedOpenAIService()
        service.apply_validated_settings(openai_settings)

        print(f"✅ OpenAI servis konfigurisan")
        print(f"   Model: {openai_settings.model}")
        print(f"   Capabilities: {service.get_capabilities()['features']}")

    except Exception as e:
        print(f"❌ Greška: {e}")

    # Test schema generisanja
    print("\n2. Test Schema generisanja:")
    schema = ValidatedAIServiceFactory.get_provider_schema("openai")
    print(f"✅ OpenAI schema ima {len(schema['properties'])} propertija")

    schema = ValidatedAIServiceFactory.get_provider_schema("gemini")
    print(f"✅ Gemini schema ima {len(schema['properties'])} propertija")
