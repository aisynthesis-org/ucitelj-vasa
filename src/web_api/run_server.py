"""
Skripta za pokretanje FastAPI servera
"""

import uvicorn
import sys
import os

# Dodaj src u path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    print("🎓 Učitelj Vasa Web API")
    print("=" * 50)
    print("🚀 Server se pokreće na: http://localhost:8000")
    print("📚 Dokumentacija: http://localhost:8000/docs")
    print("📊 Alternativna dokumentacija: http://localhost:8000/redoc")
    print("\n✋ Za zaustavljanje pritisni Ctrl+C")
    print("=" * 50 + "\n")

    uvicorn.run(
        "web_api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
