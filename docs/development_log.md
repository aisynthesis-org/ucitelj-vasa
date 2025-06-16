# Razvojni Dnevnik - Učitelj Vasa

## Dan 4: Prvi AI poziv - univerzalna podrška! (16.06.2025)

### Šta je urađeno:
- ✅ Instalirane obe AI biblioteke (openai i google-generativeai)
- ✅ Kreiran ssl_fix.py modul za rešavanje SSL problema
- ✅ Kreiran BaseAIService interfejs
- ✅ Implementiran OpenAIService sa automatskim SSL fix-om
- ✅ Implementiran GeminiService sa istim interfejsom
- ✅ Kreiran AIServiceFactory sa Singleton pattern-om
- ✅ main.py koristi factory za automatski izbor servisa
- ✅ Dodata opcija promene servisa tokom rada
- ✅ Kontinuirani razgovor radi sa oba servisa

### Naučene lekcije:
- Environment varijable mogu da interferiraju sa bibliotekama
- SSL problemi su česti na Windows sistemima
- Factory pattern omogućava elegantno upravljanje više servisa
- Isti interfejs (BaseAIService) čini servise zamenljivim
- Singleton pattern štedi resurse
- Error handling mora biti specifičan za svaki servis
- Defensive programming predviđa i rešava probleme pre nego što se jave

### Problemi i rešenja:
- **Problem**: [Errno 2] No such file or directory sa OpenAI
- **Rešenje**: Kreiran ssl_fix.py koji čisti problematične environment varijable
- **Lekcija**: Environment pollution je realan problem u produkciji

### Testiranje:
- OpenAI: Brži odgovori, kraći, precizniji
- Gemini: Detaljniji odgovori, ponekad previše opširni
- SSL fix: Rešava probleme na većini Windows sistema

### Za sutra (Dan 5):
- Proširivanje Vasine ličnosti
- Fine-tuning parametara za oba servisa
- Dodavanje "modova" ponašanja


## Dan 3: Dobijanje i čuvanje API ključa - Multi-provider podrška (15.06.2025)

### Šta je urađeno:
- ✅ Dodata podrška za OpenAI i Gemini API servise
- ✅ Kreiran univerzalni Config modul koji radi sa oba
- ✅ API ključ bezbedno sačuvan u .env
- ✅ Implementirano elegantno prebacivanje između servisa
- ✅ test_api_key.py prikazuje info za oba servisa
- ✅ main.py ažuriran sa provider-aware porukama

### Naučene lekcije:
- OpenAI više ne daje besplatne kredite (januar 2025)
- Gemini je odlična besplatna alternativa
- Univerzalni Config dizajn omogućava laku ekstenziju
- Type hints (`Literal`) poboljšavaju sigurnost koda

### Problemi i rešenja:
- **Problem**: Kako elegantno podržati dva različita API servisa?
- **Rešenje**: AI_PROVIDER varijabla + get_api_key() / get_model() metode

### Izbor servisa:
- **OpenAI**: $5 investicija, industrijski standard, najbolja dokumentacija
- **Gemini**: Potpuno besplatno, moderni model, velikodušni limiti

### Za sutra (Dan 4):
- Instalacija biblioteka (openai ili google-generativeai)
- Kreiranje wrapper funkcije za univerzalne pozive
- Prvi pravi AI poziv - Vasa konačno postaje inteligentan!


## Dan 2: Razumevanje AI API-ja (15.06.2025)

### Šta je urađeno:
- ✅ Kreiran ai_simulator.py za demonstraciju API koncepta
- ✅ Implementirana simulacija AI odgovora sa kašnjenjem
- ✅ Dodata demonstracija API strukture (JSON format)
- ✅ Kreiran api_key_info.py sa sigurnosnim uputstvima
- ✅ Ažuriran main.py sa novim opcijama

### Naučene lekcije:
- API omogućava programima da komuniciraju preko interneta
- JSON je univerzalni format za razmenu podataka
- AI servisi koriste role-based sistem za kontrolu ponašanja
- API ključevi su kao lozinke i moraju se čuvati sigurno

### Problemi i rešenja:
- **Problem**: Kako objasniti API bez stvarnog poziva?
- **Rešenje**: Kreirana simulacija koja pokazuje strukturu i kašnjenje

### Za sutra (Dan 3):
- Registracija na OpenAI platform.openai.com
- Dobijanje pravog API ključa
- Čuvanje ključa u .env fajl


## Dan 1: Prvi Python Moduli (15.06.2025)

### Šta je urađeno:
- ✅ Kreiran vasa_core.py sa osnovnim funkcionalnostima
- ✅ Implementirane funkcije: pozdrav(), predstavi_se(), glavni_meni()
- ✅ Kreiran main.py sa glavnom programskom petljom
- ✅ Dodate type hints za bolje razumevanje koda
- ✅ Učitelj Vasa može da komunicira kroz konzolu!

### Naučene lekcije:
- Python moduli su jednostavno .py fajlovi
- Funkcije grupišu kod koji obavlja specifičan zadatak
- f-stringovi omogućavaju lako formatiranje teksta
- if __name__ == "__main__" omogućava dvostruku upotrebu fajla

### Problemi i rešenja:
- **Problem**: Import error pri pokretanju
- **Rešenje**: Označen src folder kao Sources Root

### Za sutra (Dan 2):
- Razumevanje kako AI API-ji funkcionišu
- Priprema za integraciju sa OpenAI

## Dan 0: Struktura Projekta 14.06.2025.

### Šta je urađeno:
- ✅ Kreirana profesionalna folder struktura
- ✅ Dodati __init__.py fajlovi za Python pakete  
- ✅ Kreiran .gitignore sa standardnim pravilima
- ✅ Postavljen requirements.txt sa python-dotenv
- ✅ Kreiran .env za čuvanje API ključeva
- ✅ README.md ažuriran sa novom strukturom

### Naučene lekcije:
- Python paketi zahtevaju __init__.py fajlove
- .env fajlovi čuvaju tajne podatke van koda
- Dobra struktura je temelj svakog projekta

### Za sutra (Dan 1):
- Kreirati vasa_core.py sa prvim funkcijama
- Naučiti rad sa Python modulima i importima