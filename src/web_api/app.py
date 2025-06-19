"""
FastAPI aplikacija za Učitelja Vasu
Transformiše konzolnu aplikaciju u web servis
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional, Union
from datetime import datetime
import sys
import os

# Dodaj src folder u Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Vasa modula
from vasa_core import pozdrav, predstavi_se, VASA_LICNOST
from ai_services.ai_factory import AIServiceFactory
from utils.config import Config
from utils.performance_tracker import tracker

# Import za routing i request handling
from web_api.models.request_types import RequestAnalyzer, RequestType, StructuredRequest
from web_api.models.router import smart_router

# Kreiraj FastAPI instancu
app = FastAPI(
    title="Učitelj Vasa API",
    description="AI asistent za učenje programiranja",
    version="1.0.0"
)

# Konfiguriši CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # U produkciji, navedi specifične domene
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Globalne varijable
ai_service = None
startup_time = None


@app.on_event("startup")
async def startup_event():
    """Inicijalizuje AI servis pri pokretanju."""
    global ai_service, startup_time

    startup_time = datetime.now()
    print("🚀 Pokrećem Učitelja Vasu Web API...")

    try:
        ai_service = AIServiceFactory.create_resilient_service()
        print("✅ AI servis spreman!")
    except Exception as e:
        print(f"⚠️ Problem sa AI servisom: {e}")
        print("📌 API će raditi u ograničenom režimu")


@app.get("/")
async def root():
    """Osnovne informacije o API-ju."""
    return {
        "ime": "Učitelj Vasa API",
        "verzija": "1.0.0",
        "status": "aktivan",
        "opis": "AI asistent za učenje programiranja"
    }


@app.get("/health")
async def health_check():
    """Osnovni health check endpoint."""
    return {
        "status": "healthy",
        "service": "ucitelj-vasa-api",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health/ai")
async def ai_service_health():
    """Proverava health AI servisa."""
    health_info = {
        "service_exists": ai_service is not None,
        "provider": Config.AI_PROVIDER,
        "timestamp": datetime.now().isoformat()
    }

    if ai_service:
        try:
            # Pokušaj da dobiješ postavke kao brzu proveru
            settings = ai_service.get_current_settings()
            health_info["responsive"] = True
            health_info["model"] = settings.get("model", "unknown")
        except:
            health_info["responsive"] = False
    else:
        health_info["responsive"] = False

    # Određi overall status
    if health_info["service_exists"] and health_info["responsive"]:
        health_info["status"] = "healthy"
    elif health_info["service_exists"]:
        health_info["status"] = "degraded"
    else:
        health_info["status"] = "unavailable"

    return health_info


@app.get("/zdravo")
async def zdravo():
    """Vasa pozdravlja."""
    return {
        "poruka": pozdrav(),
        "tip": "pozdrav"
    }


@app.get("/o-vasi")
async def o_vasi():
    """Informacije o Učitelju Vasi."""
    return {
        "ime": "Učitelj Vasa",
        "opis": predstavi_se(),
        "mogucnosti": [
            "Odgovara na pitanja o programiranju",
            "Objašnjava koncepte",
            "Pomaže sa debug-ovanjem",
            "Daje primere koda"
        ]
    }


@app.post("/pitaj",
    summary="Postavi pitanje sa inteligentnim rutiranjem",
    description="""
    Napredni endpoint koji:
    - Analizira tip pitanja
    - Bira najbolji AI provider
    - Optimizuje parametre
    - Vraća detaljan odgovor sa metapodacima
    
    Primer strukturiranog zahteva:
    ```json
    {
        "pitanje": "Napiši funkciju koja sortira listu",
        "tip": "code",
        "context": {
            "programming_language": "python",
            "user_level": "beginner"
        }
    }
    ```
    """,
    response_description="Odgovor sa routing informacijama"
)
async def pitaj_vasu(
    pitanje_data: Union[Dict[str, str], Dict[str, Any]],
    force_provider: Optional[str] = None,
    analyze_request: bool = True
):
    """
    Postavlja pitanje Učitelju Vasi sa inteligentnim rutiranjem.

    Podržava:
    - Jednostavan format: {"pitanje": "..."}
    - Strukturiran format: {"pitanje": "...", "tip": "code", "context": {...}}

    Query parametri:
    - force_provider: Forsiraj specifičan provider (openai/gemini)
    - analyze_request: Da li da analizira i struktuira zahtev (default: true)
    """
    # Osnovna validacija
    if "pitanje" not in pitanje_data:
        raise HTTPException(
            status_code=400,
            detail="Nedostaje 'pitanje' polje u zahtevu"
        )

    pitanje = pitanje_data["pitanje"]

    if not pitanje.strip():
        raise HTTPException(
            status_code=400,
            detail="Pitanje ne može biti prazno"
        )

    # Kreiraj strukturiran zahtev
    if analyze_request:
        # Proveri da li je već strukturiran
        if "tip" in pitanje_data:
            # Korisnik je poslao strukturiran zahtev
            try:
                request_type = RequestType(pitanje_data["tip"])
            except ValueError:
                request_type = RequestType.CHAT

            structured_request = StructuredRequest(
                content=pitanje,
                request_type=request_type,
                context=pitanje_data.get("context", {}),
                preferences=pitanje_data.get("preferences", {})
            )
        else:
            # Analiziraj sirovo pitanje
            structured_request = RequestAnalyzer.create_structured_request(
                pitanje,
                additional_context=pitanje_data.get("context")
            )
    else:
        # Bez analize, tretiraj kao obican chat
        structured_request = StructuredRequest(
            content=pitanje,
            request_type=RequestType.CHAT
        )

    # Rutiraj zahtev
    selected_provider, routing_metadata = smart_router.route_request(
        structured_request,
        override_provider=force_provider
    )

    # Proveri da li imamo AI servis
    if not ai_service:
        return {
            "greska": "AI servis trenutno nije dostupan",
            "tip_zahteva": structured_request.request_type.value,
            "routing": routing_metadata
        }

    try:
        # Promeni provider ako je potrebno
        original_provider = Config.AI_PROVIDER

        if selected_provider != original_provider and selected_provider != "simulation":
            Config.AI_PROVIDER = selected_provider
            # Reset factory da učita novi provider
            from ai_services.ai_factory import AIServiceFactory
            AIServiceFactory.reset()
            current_service = AIServiceFactory.create_resilient_service()
        else:
            current_service = ai_service

        # Dobij optimizovane parametre
        optimized_params = structured_request.get_optimized_params()

        # Primeni parametre
        current_service.apply_settings(optimized_params)

        # Generiši poboljšan prompt
        enhanced_prompt = structured_request.get_enhanced_prompt()

        # Pozovi AI sa personalizacijom ako postoji
        if hasattr(current_service, 'pozovi_ai_personalizovano'):
            # Ovde bi trebalo proslediti user profile
            odgovor = current_service.pozovi_ai(enhanced_prompt)
        else:
            odgovor = current_service.pozovi_ai(enhanced_prompt)

        # Vrati originalni provider
        if selected_provider != original_provider:
            Config.AI_PROVIDER = original_provider
            AIServiceFactory.reset()

        # Pripremi response
        response = {
            "pitanje": pitanje,
            "odgovor": odgovor,
            "tip_zahteva": structured_request.request_type.value,
            "provider": {
                "selected": selected_provider,
                "reason": routing_metadata.get("selected_reason"),
                "strategy": routing_metadata.get("strategy")
            },
            "optimizacija": {
                "temperature": optimized_params.get("temperature"),
                "max_tokens": optimized_params.get("max_tokens")
            }
        }

        # Dodaj kontekst ako postoji
        if structured_request.context.has_code_context():
            response["context"] = {
                "language": structured_request.context.programming_language,
                "has_code": bool(structured_request.context.code_snippet),
                "has_error": bool(structured_request.context.error_message)
            }

        return response

    except Exception as e:
        # Loguj grešku ali vrati user-friendly poruku
        print(f"❌ Greška pri obradi pitanja: {e}")

        return {
            "greska": "Dogodila se greška pri obradi pitanja",
            "savet": "Pokušaj ponovo ili promeni formulaciju pitanja",
            "tip_zahteva": structured_request.request_type.value,
            "provider_pokušan": selected_provider
        }


@app.get("/providers")
async def get_providers():
    """Vraća informacije o dostupnim AI providerima."""
    providers = []

    # Proveri OpenAI
    if Config.OPENAI_API_KEY:
        providers.append({
            "name": "openai",
            "display_name": "OpenAI GPT",
            "available": True,
            "is_active": Config.AI_PROVIDER == "openai",
            "features": ["chat", "code_generation", "analysis"]
        })

    # Proveri Gemini
    if Config.GEMINI_API_KEY:
        providers.append({
            "name": "gemini",
            "display_name": "Google Gemini",
            "available": True,
            "is_active": Config.AI_PROVIDER == "gemini",
            "features": ["chat", "multimodal", "fast_responses"]
        })

    # Ako nijedan nije dostupan
    if not providers:
        providers.append({
            "name": "simulation",
            "display_name": "Lokalna simulacija",
            "available": True,
            "is_active": True,
            "features": ["basic_responses"]
        })

    return {
        "providers": providers,
        "active_provider": Config.AI_PROVIDER,
        "total_configured": len([p for p in providers if p["name"] != "simulation"])
    }


@app.get("/status")
async def get_status():
    """Vraća osnovni status sistema."""
    # Računaj uptime
    uptime_seconds = 0
    if startup_time:
        uptime_seconds = (datetime.now() - startup_time).total_seconds()

    # Osnovno stanje
    status = {
        "status": "operational" if ai_service else "limited",
        "uptime_seconds": int(uptime_seconds),
        "uptime_human": f"{int(uptime_seconds // 60)} minuta",
        "current_provider": Config.AI_PROVIDER,
        "api_version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

    # Broj dostupnih providera
    available_count = 0
    if Config.OPENAI_API_KEY:
        available_count += 1
    if Config.GEMINI_API_KEY:
        available_count += 1

    status["providers_available"] = available_count
    status["multi_provider_enabled"] = available_count > 1

    # Circuit breaker status ako postoji
    if ai_service and hasattr(ai_service, '_circuit_breaker_call'):
        try:
            cb = ai_service._circuit_breaker_call.circuit_breaker
            status["circuit_breaker"] = cb.state.value
        except:
            status["circuit_breaker"] = "unknown"

    return status


@app.get("/providers/current")
async def get_current_provider():
    """Vraća detalje o trenutno aktivnom provideru."""
    current = Config.AI_PROVIDER

    info = {
        "provider": current,
        "display_name": "OpenAI GPT" if current == "openai" else "Google Gemini",
        "active_since": startup_time.isoformat() if startup_time else None
    }

    # Dodaj informacije o servisu ako postoji
    if ai_service:
        try:
            settings = ai_service.get_current_settings()
            info["model"] = settings.get("model", "nepoznat")
            info["service_status"] = "operational"
        except:
            info["service_status"] = "degraded"
    else:
        info["service_status"] = "unavailable"

    return info


@app.get("/providers/statistics")
async def get_provider_statistics():
    """Vraća osnovne statistike o korišćenju providera."""
    if not hasattr(tracker, 'all_metrics') or not tracker.all_metrics:
        return {
            "message": "Nema dovoljno podataka",
            "total_requests": 0,
            "providers": {}
        }

    # Grupiši podatke po providerima
    stats = {}

    for metric in tracker.all_metrics:
        # Koristi dictionary pristup umesto atributa
        provider = metric.get('provider', 'unknown')

        if provider not in stats:
            stats[provider] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "total_tokens": 0
            }

        stats[provider]["total_requests"] += 1

        # Koristi get() metod za bezbedno čitanje
        if metric.get('success', False):
            stats[provider]["successful_requests"] += 1
            stats[provider]["total_tokens"] += metric.get('tokens_used', 0)
        else:
            stats[provider]["failed_requests"] += 1

    # Dodaj procente
    for provider, data in stats.items():
        if data["total_requests"] > 0:
            data["success_rate"] = round(
                (data["successful_requests"] / data["total_requests"]) * 100,
                2
            )
        else:
            data["success_rate"] = 0

    return {
        "total_requests": len(tracker.all_metrics),
        "providers": stats,
        "collection_started": tracker.all_metrics[0].get('timestamp') if tracker.all_metrics else None
    }


@app.get("/request-types")
async def get_request_types():
    """Vraća sve podržane tipove zahteva sa opisima."""
    types = []

    for req_type in RequestType:
        types.append({
            "type": req_type.value,
            "description": req_type.get_description(),
            "preferred_provider": req_type.get_preferred_provider()
        })

    return {
        "supported_types": types,
        "total": len(types)
    }


@app.get("/routing/stats")
async def get_routing_statistics():
    """Vraća statistiku routing odluka."""
    stats = smart_router.get_routing_statistics()

    # Dodaj trenutnu strategiju
    stats["current_strategy"] = type(smart_router.strategy).__name__

    # Dodaj dostupne providere
    stats["available_providers"] = smart_router.get_available_providers()

    return stats


@app.post("/routing/strategy")
async def change_routing_strategy(strategy_name: str):
    """
    Menja routing strategiju.

    Dostupne strategije:
    - static: Fiksna pravila po tipu
    - performance: Bazirana na performansama
    - loadbalance: Round-robin
    - hybrid: Kombinacija (default)
    """
    from web_api.models.router import (
        StaticRoutingStrategy,
        PerformanceRoutingStrategy,
        LoadBalancingStrategy,
        HybridRoutingStrategy
    )

    strategies = {
        "static": StaticRoutingStrategy,
        "performance": PerformanceRoutingStrategy,
        "loadbalance": LoadBalancingStrategy,
        "hybrid": HybridRoutingStrategy
    }

    if strategy_name not in strategies:
        raise HTTPException(
            status_code=400,
            detail=f"Nepoznata strategija. Dostupne: {list(strategies.keys())}"
        )

    # Promeni strategiju
    smart_router.strategy = strategies[strategy_name]()

    return {
        "message": f"Routing strategija promenjena na: {strategy_name}",
        "strategy": strategy_name,
        "description": smart_router._get_selection_reason(None, "")
    }


# Primer strukturiranog zahteva za dokumentaciju
structured_request_example = {
    "pitanje": "Napiši funkciju koja sortira listu",
    "tip": "code",
    "context": {
        "programming_language": "python",
        "user_level": "beginner"
    },
    "preferences": {
        "temperature": 0.5,
        "max_tokens": 200
    }
}


if __name__ == "__main__":
    # Za development - pokreni server direktno
    import uvicorn

    print("🚀 Pokrećem Učitelja Vasu API na http://localhost:8000")
    print("📚 Dokumentacija dostupna na http://localhost:8000/docs")

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Automatski restart pri promeni koda
    )
