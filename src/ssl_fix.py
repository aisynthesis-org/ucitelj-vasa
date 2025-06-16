"""
SSL Fix za Windows i druge sisteme
Rešava česte probleme sa SSL certifikatima i environment varijablama

Ovaj modul automatski čisti problematične environment varijable
koje mogu da interferiraju sa HTTPS konekcijama.
"""

import os
import sys
import platform


def clean_ssl_environment():
    """
    Čisti problematične SSL environment varijable.

    Mnogi programi (Anaconda, Git, razni Python alati) postavljaju
    SSL environment varijable koje mogu da kvare rad drugih biblioteka.
    Ova funkcija ih uklanja da bi omogućila normalnu komunikaciju.
    """
    # Lista svih SSL varijabli koje mogu praviti probleme
    problematic_vars = [
        'SSL_CERT_FILE',
        'SSL_CERT_DIR',
        'REQUESTS_CA_BUNDLE',
        'CURL_CA_BUNDLE',
        'HTTPLIB2_CA_CERTS',
        'GRPC_DEFAULT_SSL_ROOTS_FILE_PATH'
    ]

    cleaned_vars = []

    for var in problematic_vars:
        if var in os.environ:
            # Sačuvaj vrednost za debug
            old_value = os.environ[var]
            del os.environ[var]
            cleaned_vars.append((var, old_value))

    # Prikaži šta je očišćeno (samo ako je bilo problema)
    if cleaned_vars:
        print("🧹 SSL Fix: Očišćene problematične environment varijable:")
        for var, value in cleaned_vars:
            print(f"   - {var} = {value[:50]}..." if len(value) > 50 else f"   - {var} = {value}")
        print("✅ SSL environment je sada čist!")

    return cleaned_vars


def setup_ssl_certificates():
    """
    Postavlja ispravnu putanju do SSL certifikata koristeći certifi.

    Certifi je Python paket koji sadrži pouzdan skup SSL certifikata.
    Ova funkcija osigurava da Python može da pronađe te certifikate.
    """
    try:
        import certifi

        # Postavi ispravnu putanju
        cert_path = certifi.where()
        os.environ['SSL_CERT_FILE'] = cert_path
        os.environ['REQUESTS_CA_BUNDLE'] = cert_path

        if os.path.exists(cert_path):
            print(f"✅ SSL certifikati postavljeni na: {cert_path}")
            return True
        else:
            print(f"⚠️ Certifi putanja postoji ali fajl nije pronađen: {cert_path}")
            return False

    except ImportError:
        print("⚠️ Certifi paket nije instaliran. Instaliraj sa: pip install certifi")
        return False


def diagnose_ssl_issues():
    """
    Dijagnostikuje potencijalne SSL probleme na sistemu.
    Korisno za debugging kada stvari ne rade.
    """
    print("\n🔍 SSL DIJAGNOZA")
    print("=" * 60)

    # Informacije o sistemu
    print(f"OS: {platform.system()} {platform.version()}")
    print(f"Python: {sys.version}")

    # Proveri SSL modul
    try:
        import ssl
        print(f"SSL verzija: {ssl.OPENSSL_VERSION}")
    except Exception as e:
        print(f"❌ SSL modul problem: {e}")

    # Proveri certifi
    try:
        import certifi
        print(f"Certifi lokacija: {certifi.where()}")
        print(f"Certifi verzija: {certifi.__version__}")
    except Exception as e:
        print(f"❌ Certifi problem: {e}")

    # Prikaži trenutne SSL environment varijable
    print("\nTrenutne SSL environment varijable:")
    ssl_vars = ['SSL_CERT_FILE', 'SSL_CERT_DIR', 'REQUESTS_CA_BUNDLE', 'CURL_CA_BUNDLE']
    for var in ssl_vars:
        value = os.environ.get(var)
        if value:
            print(f"  {var} = {value}")
        else:
            print(f"  {var} = Nije postavljena")

    print("=" * 60)


# Automatski počisti environment kada se modul učita
_cleaned = clean_ssl_environment()

# Test funkcionalnost
if __name__ == "__main__":
    print("🧪 Test SSL Fix modula")
    print("=" * 50)

    # Pokreni dijagnozu
    diagnose_ssl_issues()

    # Pokušaj da postaviš certifikate
    print("\n🔧 Postavljanje SSL certifikata...")
    if setup_ssl_certificates():
        print("✅ SSL certifikati uspešno postavljeni!")
    else:
        print("❌ Problem sa postavljanjem SSL certifikata")

    # Test sa OpenAI
    print("\n🧪 Test OpenAI konekcije...")
    try:
        from openai import OpenAI

        client = OpenAI(api_key="test-key")
        print("✅ OpenAI klijent kreiran bez SSL grešaka!")
    except Exception as e:
        print(f"❌ OpenAI greška: {type(e).__name__}: {e}")
