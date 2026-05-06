"""
Ortam Degiskenleri Yardimci Modulu
===================================
.env dosyasindan yapIlandirma bilgilerini okur.
Tum modUller bu dosya uzerinden erisim bilgilerine ulasir.

Kullanim:
    from config.env_loader import get_env, get_sap_config, get_github_token
"""

import os
from pathlib import Path


# .env dosyasinin yolu
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
_env_cache = None


def _load_env():
    """".env dosyasini yukle ve cache'le."""
    global _env_cache
    if _env_cache is not None:
        return _env_cache

    _env_cache = {}
    if not _ENV_PATH.exists():
        return _env_cache

    with open(_ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                _env_cache[key.strip()] = value.strip()

    return _env_cache


def get_env(key, default=None):
    """Ortam degiskenini oku. Once .env, sonra sistem ortam degiskeni."""
    env = _load_env()
    return env.get(key, os.environ.get(key, default))


def get_sap_config():
    """SAP baglanti bilgilerini sozluk olarak dondur."""
    return {
        "base_url": get_env("SAP_BASE_URL", ""),
        "service": get_env("SAP_SERVICE", "YMONO_AKT_PLN_SRV"),
        "username": get_env("SAP_USERNAME", ""),
        "password": get_env("SAP_PASSWORD", ""),
        "verify_ssl": get_env("SAP_VERIFY_SSL", "true").lower() == "true",
        "client": get_env("SAP_CLIENT", "100"),
    }


def get_github_token():
    """GitHub token'ini dondur."""
    return get_env("GITHUB_TOKEN", "")


def is_sample_mode():
    """Ornek veri modu aktif mi?"""
    return get_env("USE_SAMPLE_DATA", "true").lower() == "true"


def get_log_level():
    """Log seviyesini dondur."""
    return get_env("LOG_LEVEL", "INFO")


def validate_env():
    """Gerekli degiskenlerin dolu olup olmadigini kontrol et."""
    issues = []
    env = _load_env()

    if not env:
        issues.append(".env dosyasi bulunamadi veya bos")
        return issues

    # GitHub token kontrolu
    token = get_github_token()
    if not token or token == "ghp_BURAYA_TOKEN_YAZIN":
        issues.append("GITHUB_TOKEN ayarlanmamis")

    # SAP bilgileri (sample mod kapaliysa kontrol et)
    if not is_sample_mode():
        sap = get_sap_config()
        if not sap["base_url"] or "your-sap-server" in sap["base_url"]:
            issues.append("SAP_BASE_URL ayarlanmamis")
        if not sap["username"] or sap["username"] == "SAP_KULLANICI_ADI":
            issues.append("SAP_USERNAME ayarlanmamis")
        if not sap["password"] or sap["password"] == "SAP_SIFRE":
            issues.append("SAP_PASSWORD ayarlanmamis")

    return issues


if __name__ == "__main__":
    # Dogrudan calistirilirsa kontrol yap
    print("=== .env Dogrulama ===")
    issues = validate_env()
    if issues:
        print("Eksikler:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("Tum yapilandirmalar tamam!")

    print("\nSAP Ayarlari:")
    sap = get_sap_config()
    for k, v in sap.items():
        if k == "password" and v:
            print(f"  {k}: {'*' * len(v)}")
        else:
            print(f"  {k}: {v}")

    print(f"\nOrnek Veri Modu: {is_sample_mode()}")
    print(f"Log Seviyesi: {get_log_level()}")
