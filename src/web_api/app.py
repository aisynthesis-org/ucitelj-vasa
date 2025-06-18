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


@app.on_event("startup")
async def startup_event():
    """Inicijalizuje AI servis pri pokretanju."""
    global ai_service

    print("🚀 Pokrećem Učitelja Vasu Web API...")

    try:
        # Jednostavno kreiraj AI servis kao što smo radili u konzoli
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
