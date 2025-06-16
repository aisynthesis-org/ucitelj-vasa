# Učitelj Vasa - AI Asistent za Učenje Programiranja

## 📚 O Projektu

Učitelj Vasa je AI-powered asistent kreiran kroz 28-dnevni praktični kurs AI SYNTHESIS akademije. 
Cilj je pomoći početnicima da savladaju osnove programiranja kroz interakciju sa AI asistentom.

## 🚀 Trenutni Status

- ✅ Dan -3: Python 3.13+ instaliran
- ✅ Dan -2: PyCharm unified edition podešen
- ✅ Dan -1: GitHub repository kreiran
- ✅ Dan 0: Profesionalna struktura projekta
- ✅ Dan 1: Prvi Python moduli - Vasa može da pozdravi!
- ✅ Dan 2: Razumevanje AI API-ja - simulacija komunikacije
- ✅ Dan 3: Multi-provider podrška - OpenAI i Gemini
- ✅ Dan 4: Prvi AI poziv - Vasa govori preko OpenAI ili Gemini! 🤖
- ⏳ Dan 5: Dodavanje ličnosti i prilagođavanje odgovora (sutra)

## 🎯 Trenutne mogućnosti

Učitelj Vasa sada može:
- ✨ Odgovarati na pitanja koristeći OpenAI GPT ili Google Gemini
- 🔄 Prebacivati između AI servisa tokom rada
- 💬 Voditi kontinuirane razgovore sa kontekstom
- 🎓 Objašnjavati programske koncepte na srpskom jeziku
- 🔄 Raditi u offline modu sa simulacijom ako AI nije dostupan
- 🛡️ Automatski rešavati SSL probleme na Windows sistemima

## 🤖 Arhitektura

    main.py
    ├── AIServiceFactory
    ├── OpenAIService (sa SSL fix-om)
    ├── GeminiService

## ⚠️ Poznati problemi i rešenja

### SSL problemi na Windows-u
Ako dobiješ `[Errno 2] No such file or directory` grešku sa OpenAI:
1. ssl_fix.py automatski rešava većinu problema
2. Restartuj PyCharm/terminal ako problemi potraju
3. Koristi Gemini kao alternativu

## 🤖 Podržani AI servisi

Učitelj Vasa podržava:
- **OpenAI GPT-4.1** - Industrijski standard (potreban $5 kredit)
- **Google Gemini 2.0 Flash** - Besplatna alternativa

Prebacivanje između servisa je jednostavno - samo promeni `AI_PROVIDER` u `.env` fajlu!


## 🛠️ Tehnologije

- **Python** 3.13+
- **PyCharm** unified edition
- **python-dotenv** za environment varijable
- Uskoro: OpenAI API, FastAPI, SQLite

## 📁 Struktura Projekta

    ucitelj-vasa/
    ├── src/                    # Izvorni kod
    │   ├── __init__.py
    │   ├── ai_services/       # AI integracije
    │   ├── web_api/          # Web API (od nedelje 2)
    │   └── utils/            # Pomoćne funkcije
    ├── tests/                 # Testovi
    ├── docs/                  # Dokumentacija
    ├── .env                   # Environment varijable (ne commit-uj!)
    ├── .gitignore            # Git ignore pravila
    ├── requirements.txt      # Python dependencies
    └── README.md            # Ovaj fajl

## 🔧 Instalacija

1. Kloniraj repository:

    git clone https://github.com/aisynthesis-org/ucitelj-vasa.git
    cd ucitelj-vasa

2. Kreiraj virtuelno okruženje (preporučeno):

    python -m venv venv
    source venv/bin/activate  # Na Windows: venv\Scripts\activate

3. Instaliraj dependencies:

    pip install -r requirements.txt

## 👤 Autor

Radoje Đorda - AI SYNTHESIS akademija

## 📄 Licenca

MIT License - slobodno koristi za učenje!
