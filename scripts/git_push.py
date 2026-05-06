"""
GitHub Push Scripti
====================
.env dosyasindaki GITHUB_TOKEN bilgisini kullanarak
GitHub'a otomatik push yapar.

Kullanim:
    python scripts/git_push.py
    python scripts/git_push.py "commit mesaji"
"""

import os
import sys
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


def load_env():
    """".env dosyasini oku ve degiskenleri dondur."""
    env_vars = {}
    if not ENV_FILE.exists():
        print("[HATA] .env dosyasi bulunamadi!")
        print("       Lutfen .env.example dosyasini .env olarak kopyalayin:")
        print("       copy .env.example .env")
        print("       Sonra kendi bilgilerinizle doldurun.")
        sys.exit(1)

    with open(ENV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip()
    return env_vars


def git_push(commit_message=None):
    """.env'deki token ile GitHub'a push yap."""
    env = load_env()

    token = env.get("GITHUB_TOKEN", "")
    repo = env.get("GITHUB_REPO", "hasanbsc/agentic_ai")

    if not token or token == "ghp_BURAYA_TOKEN_YAZIN":
        print("[HATA] GITHUB_TOKEN ayarlanmamis!")
        print("       .env dosyasina gecerli bir GitHub token yazin.")
        print("       GitHub -> Settings -> Developer settings -> Personal access tokens")
        sys.exit(1)

    # Remote URL'i token ile guncelle
    remote_url = f"https://{token}@github.com/{repo}.git"
    subprocess.run(
        ["git", "remote", "set-url", "origin", remote_url],
        cwd=PROJECT_ROOT, check=True
    )

    # Commit mesaji
    if not commit_message:
        commit_message = "Guncelleme"

    # Degisiklik var mi kontrol et
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=PROJECT_ROOT, capture_output=True, text=True
    )

    if status.stdout.strip():
        # Degisiklikler var, commit yap
        subprocess.run(["git", "add", "-A"], cwd=PROJECT_ROOT, check=True)
        subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=PROJECT_ROOT, check=True
        )
        print(f"[OK] Commit olusturuldu: {commit_message}")
    else:
        print("[i] Yeni degisiklik yok, mevcut commitler push ediliyor...")

    # Push
    result = subprocess.run(
        ["git", "push", "-u", "origin", "main"],
        cwd=PROJECT_ROOT, capture_output=True, text=True
    )

    if result.returncode == 0:
        print(f"[OK] GitHub'a basariyla push edildi!")
        print(f"     https://github.com/{repo}")
    else:
        print(f"[HATA] Push basarisiz:")
        print(f"       {result.stderr}")

    # Guvenlik: remote URL'den tokeni kaldir
    safe_url = f"https://github.com/{repo}.git"
    subprocess.run(
        ["git", "remote", "set-url", "origin", safe_url],
        cwd=PROJECT_ROOT
    )


if __name__ == "__main__":
    msg = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    git_push(msg)
