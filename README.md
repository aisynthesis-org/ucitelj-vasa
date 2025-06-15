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
- ✅ Dan 3: API ključ dobijen (OpenAI ili Gemini) i bezbedno sačuvan
- ⏳ Dan 4: Prvi pravi AI poziv (sutra)

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
