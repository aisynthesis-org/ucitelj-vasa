"""
Informacije o API ključevima
Edukativni modul koji objašnjava važnost sigurnog čuvanja API ključeva.
"""


def objasni_api_kljuc():
    """Objašnjava šta je API ključ i zašto je važan."""
    objasnjenje = """
    🔑 ŠTA JE API KLJUČ?
    ==================

    API ključ je kao lozinka za korišćenje AI servisa. 
    Kada sutra dobijemo OpenAI API ključ, on će izgledati ovako:

    sk-proj-abcd1234wxyz5678...

    ⚠️  VAŽNA PRAVILA:

    1. NIKAD ne stavljaj API ključ direktno u kod:
       ❌ LOŠE:  api_key = "sk-proj-tvoj-pravi-kljuc"
       ✅ DOBRO: api_key = os.getenv("OPENAI_API_KEY")

    2. NIKAD ne commit-uj API ključ na GitHub:
       - Koristi .env fajl (već je u .gitignore)
       - Čuvaj ključ lokalno

    3. API ključ = NOVAC:
       - Svaki API poziv košta
       - Neko ko ima tvoj ključ može da troši tvoj novac
       - OpenAI naplaćuje po broju tokena (reči)

    4. Ako ključ procuri:
       - Odmah ga deaktiviraj na OpenAI dashboard-u
       - Generiši novi ključ
       - Ažuriraj .env fajl

    💡 CENE (okvirno):
    - GPT-3.5: ~$0.001 za 1000 tokena (≈750 reči)
    - GPT-4: ~$0.03 za 1000 tokena (30x skuplje!)
    - Prosečan razgovor: 500-2000 tokena

    📊 PRIMER TROŠKA:
    Ako Učitelj Vasa odgovori na 100 pitanja dnevno:
    - Sa GPT-3.5: ~$0.10-0.20 dnevno
    - Sa GPT-4: ~$3-6 dnevno

    Zato ćemo početi sa GPT-3.5! 😊
    """
    return objasnjenje


def pripremi_env_fajl():
    """Prikazuje kako će izgledati .env fajl sutra."""
    env_sadrzaj = """
    # Ovako će izgledati tvoj .env fajl od sutra:

    # OpenAI API ključ (dobićeš ga na https://platform.openai.com)
    OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxx

    # Opciono: Koji model da koristi Vasa
    OPENAI_MODEL=gpt-3.5-turbo

    # Opciono: Maksimalan broj tokena po odgovoru
    MAX_TOKENS=150

    # NAPOMENA: Zameni xxxx sa pravim ključem!
    """
    return env_sadrzaj


if __name__ == "__main__":
    print(objasni_api_kljuc())
    print("\n" + "=" * 60)
    print(pripremi_env_fajl())
