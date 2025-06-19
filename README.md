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
- ✅ Dan 4: Prvi AI poziv - univerzalni sistem sa SSL fix-om
- ✅ Dan 5: Profilisanje i optimizacija - automatski izbor najboljih postavki
- ✅ Dan 6: Resilience sistem - retry, circuit breaker, fallback i graceful degradation
- ✅ Dan 7: Napredna personalizacija - profili, preference i adaptivno učenje
- ✅ Dan 8: Uvod u FastAPI - Učitelj Vasa je sada web servis!
- ✅ Dan 9: Multi-provider web endpoint-i - transparentnost i monitoring
- ✅ Dan 10: Strukturirani zahtevi i inteligentno rutiranje
- ✅ Dan 11: Pydantic validacija i type safety! 🛡️
- ⏳ Dan 12: Naprednije testiranje multi-provider API-ja (sutra)

## 🛡️ Validacija i Type Safety

### Pydantic modeli:
- `SimpleQuestionRequest` - Osnovno pitanje
- `StructuredQuestionRequest` - Pitanje sa kontekstom
- `QuestionResponse` - Standardizovan odgovor
- `ErrorResponse` - Standardizovane greške

### Provider-specifični modeli:
- `OpenAISpecificRequest` - OpenAI opcije
- `GeminiSpecificRequest` - Gemini opcije
- Validacija svih parametara

### Novi endpoint-i:
- `POST /validate-request` - Validira bez slanja
- Provider-specific pozivi sa custom opcijama

### Test UI:
- http://localhost:8000/static/validation_test.html

## 🎯 Request Routing

### Tipovi zahteva:
- `chat` - Obična konverzacija
- `code` - Generisanje koda
- `debug` - Pomoć sa greškama
- `explain` - Objašnjenje koncepata
- `review` - Pregled koda
- `translate` - Prevod između jezika
- `optimize` - Optimizacija koda

### Routing strategije:
- **Static** - Fiksna pravila po tipu
- **Performance** - Bazirana na metrikama
- **LoadBalance** - Round-robin distribucija
- **Hybrid** - Kombinacija strategija

### API Endpoints:
- `POST /pitaj` - Napredni endpoint sa rutiranjem
- `GET /request-types` - Lista podržanih tipova
- `GET /routing/stats` - Statistika rutiranja
- `POST /routing/strategy` - Promena strategije

## 📊 Provider Management API

### Informacioni endpoint-i:
- `GET /providers` - Lista dostupnih AI providera
- `GET /providers/current` - Detalji o aktivnom provideru
- `GET /providers/statistics` - Statistike korišćenja

### Status i Health:
- `GET /status` - Kompletan status sistema
- `GET /health` - Osnovni health check
- `GET /health/ai` - Health check AI servisa

### Monitoring:
- Python script za kontinuirano praćenje
- Jednostavna provera svih komponenti


## 🌐 Web API

Učitelj Vasa je sada dostupan kao REST API!

### Pokretanje servera:

### Pokretanje servera:
`cd src 
web_api/run_server.py`

### Dostupni endpoint-i:
* GET / – Osnovne informacije
* GET /zdravo – Vasin pozdrav
* GET /o-vasi – Detalji o Učitelju Vasi
* POST /pitaj – Postavi pitanje

### Dokumentacija:
* Swagger UI: http://localhost:8000/docs
* ReDoc: http://localhost:8000/redoc

## 👤 Personalizacija

Učitelj Vasa sada:
- **Pamti korisnike**: Čuva profile sa preferencama
- **Prepoznaje nivo znanja**: Početnik, srednji, napredni
- **Prilagođava stil**: Praktičan, vizuelni, teorijski
- **Prati napredak**: Omiljene teme, dostignuća, statistike
- **Adaptivno uči**: Prilagođava se tokom razgovora

## 🧠 Arhitektura personalizacije

[Korisnik] → [ProfileManager] → [UserProfile]
↓ ↓
[ProfileAnalyzer] → [PersonalizedPrompt]
↓ ↓
[AdaptiveEngine] → [AI Response]


## 🛡️ Resilience funkcionalnosti

Učitelj Vasa sada ima naprednu zaštitu:
- **Retry logika**: Automatski pokušava ponovo pri privremenim greškama
- **Circuit Breaker**: Štiti sistem od kaskadnih padova
- **Fallback strategije**: Primary → Secondary → Simulation → Static
- **Graceful Degradation**: Radi sa ograničenim mogućnostima umesto pada
- **Health Monitoring**: Praćenje zdravlja svih komponenti

## 🏥 Sistem stabilnosti

[AI Poziv] → [Retry Wrapper] → [Circuit Breaker] → [Fallback Chain]
                ↓                    ↓                    ↓
           (3 pokušaja)      (Zaštita od pada)    (Plan B, C, D)


## 🎯 Trenutne mogućnosti

Učitelj Vasa sada može:
- ✨ Odgovarati koristeći OpenAI ili Gemini
- 🔄 Prebacivati između servisa tokom rada
- 💬 Voditi kontinuirane razgovore
- 📊 **NOVO**: Meriti performanse svakog poziva
- 🎯 **NOVO**: Automatski optimizovati parametre prema tipu pitanja
- 🏁 **NOVO**: Pokretati benchmark testove
- 📈 **NOVO**: Generisati izveštaje o performansama
- 🎨 **NOVO**: Koristiti 7 različitih profila rada

## 📊 Optimizacioni profili

- **Brzi odgovor**: Kratki, direktni odgovori (temp: 0.3, max: 100)
- **Detaljno objašnjenje**: Opširna objašnjenja (temp: 0.7, max: 500)
- **Generisanje koda**: Precizno, bez greške (temp: 0.2, max: 400)
- **Kreativno pisanje**: Maštoviti sadržaj (temp: 1.2, max: 600)
- **Debug pomoć**: Sistematska analiza (temp: 0.3, max: 300)
- **Prevođenje**: Tačni prevodi (temp: 0.1, max: 200)
- **Rezimiranje**: Sažeti prikazi (temp: 0.4, max: 200)


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
