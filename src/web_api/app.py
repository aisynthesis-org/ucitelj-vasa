"""
FastAPI aplikacija za Učitelja Vasu
Transformiše konzolnu aplikaciju u web servis
"""

from fastapi import FastAPI, HTTPException
from typing import Dict
import sys
import os

# Dodaj src folder u Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Vasa modula
from vasa_core import pozdrav, predstavi_se, VASA_LICNOST
from ai_services.ai_factory import AIServiceFactory
from utils.config import Config

# Kreiraj FastAPI instancu
app = FastAPI(
    title="Učitelj Vasa API",
    description="AI asistent za učenje programiranja",
    version="1.0.0"
)

from fastapi.middleware.cors import CORSMiddleware

# Nakon kreiranja app instance, dodaj:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # U produkciji, navedi specifične domene
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Globalna varijabla za AI servis
ai_service = None

# Dodaj ovu globalnu varijablu nakon ai_service
startup_time = None


# Ažuriraj startup_event da zapamti vreme pokretanja
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


# Dodaj import za datetime na početak fajla
from datetime import datetime

# Dodaj import na početak
from utils.performance_tracker import tracker


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
        provider = metric.get('provider', 'unknown')  # Promenjeno sa metric.provider

        if provider not in stats:
            stats[provider] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "total_tokens": 0
            }

        stats[provider]["total_requests"] += 1

        # Koristi get() metod za bezbedno čitanje
        if metric.get('success', False):  # Promenjeno sa metric.success
            stats[provider]["successful_requests"] += 1
            stats[provider]["total_tokens"] += metric.get('tokens_used', 0)  # Promenjeno
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
        "collection_started": tracker.all_metrics[0].get('timestamp') if tracker.all_metrics else None  # Promenjeno
    }
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


@app.post("/pitaj")
async def pitaj_vasu(pitanje_data: Dict[str, str]):
    """
    Postavlja pitanje Učitelju Vasi.

    Očekuje JSON sa poljem:
    - pitanje: string (obavezno)
    """
    # Proveri da li postoji pitanje
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

    # Proveri AI servis
    if not ai_service:
        return {
            "greska": "AI servis trenutno nije dostupan",
            "savet": "Pokušaj ponovo za nekoliko sekundi"
        }

    try:
        # Jednostavno pozovi AI kao u konzoli
        odgovor = ai_service.pozovi_ai(pitanje, VASA_LICNOST)

        return {
            "pitanje": pitanje,
            "odgovor": odgovor
        }

    except Exception as e:
        # Loguj grešku ali vrati user-friendly poruku
        print(f"❌ Greška pri obradi pitanja: {e}")

        return {
            "greska": "Dogodila se greška pri obradi pitanja",
            "savet": "Pokušaj ponovo ili promeni formulaciju pitanja"
        }


# Dodaj nove endpoint-e nakon postojećih

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
