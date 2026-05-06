"""
📊 STATUS.md Otomatik Güncelleme Scripti
=========================================

Bu script proje durumunu analiz ederek STATUS.md dosyasını
otomatik olarak günceller.

Kullanım:
    python scripts/status_update.py

Ne yapar:
    - Proje klasörlerini tarar, dosya sayılarını hesaplar
    - Python dosyalarındaki toplam satır sayısını bulur
    - Ajan, analiz ve test dosyalarını sayar
    - Git commit sayısını alır
    - STATUS.md dosyasını güncel bilgilerle yazar
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path


# Proje kök dizini (scripts/ klasöründen bir üst dizin)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATUS_FILE = PROJECT_ROOT / "STATUS.md"


def count_files(directory, extension="*.py"):
    """Belirli uzantıdaki dosyaları say."""
    path = PROJECT_ROOT / directory
    if not path.exists():
        return 0
    return len(list(path.rglob(extension)))


def count_lines(directory, extension=".py"):
    """Python dosyalarındaki toplam satır sayısını hesapla."""
    path = PROJECT_ROOT / directory
    total = 0
    if not path.exists():
        return 0
    
    ignore_dirs = {"venv", ".venv", "__pycache__", ".git", "node_modules"}
    
    for file in path.rglob(f"*{extension}"):
        # Ignore files inside ignore_dirs
        if any(ignored in file.parts for ignored in ignore_dirs):
            continue
            
        try:
            with open(file, "r", encoding="utf-8") as f:
                lines = [l for l in f.readlines() if l.strip() and not l.strip().startswith("#")]
                total += len(lines)
        except Exception:
            pass
    return total


def count_agents():
    """Tanımlı ajan dosyalarını say (base_agent hariç)."""
    agents_dir = PROJECT_ROOT / "agents"
    if not agents_dir.exists():
        return 0
    agent_files = [f for f in agents_dir.glob("*.py") 
                   if f.name not in ("__init__.py", "base_agent.py")]
    return len(agent_files)


def count_analyses():
    """Analiz modüllerini say."""
    analysis_dir = PROJECT_ROOT / "analysis"
    if not analysis_dir.exists():
        return 0
    analysis_files = [f for f in analysis_dir.glob("*.py") 
                      if f.name != "__init__.py"]
    return len(analysis_files)


def count_tests():
    """Test dosyalarını say."""
    return count_files("tests", "test_*.py")


def get_git_commit_count():
    """Git commit sayısını al."""
    try:
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            capture_output=True, text=True, cwd=PROJECT_ROOT
        )
        if result.returncode == 0:
            return int(result.stdout.strip())
    except Exception:
        pass
    return 0


def get_total_files():
    """Projedeki toplam dosya sayısını hesapla."""
    total = 0
    ignore_dirs = {"venv", ".venv", "__pycache__", ".git", "node_modules"}
    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        total += len(files)
    return total


def detect_current_phase():
    """Mevcut fazı tespit et."""
    # Basit kural tabanlı tespit
    agents_dir = PROJECT_ROOT / "agents"
    ui_dir = PROJECT_ROOT / "ui"
    analysis_dir = PROJECT_ROOT / "analysis"
    
    agent_files = [f for f in agents_dir.glob("*.py") 
                   if f.name not in ("__init__.py",)] if agents_dir.exists() else []
    analysis_files = [f for f in analysis_dir.glob("*.py") 
                      if f.name != "__init__.py"] if analysis_dir.exists() else []
    ui_files = [f for f in ui_dir.glob("*.py") 
                if f.name != "__init__.py"] if ui_dir.exists() else []
    
    if len(ui_files) > 0:
        return "Faz 4 — Görsel Ofis Simülasyonu", 4
    elif len(analysis_files) > 0:
        return "Faz 3 — Analiz Motoru", 3
    elif len(agent_files) > 1:  # base_agent + en az 1 ajan
        return "Faz 2 — Ajan Mimarisi", 2
    elif (PROJECT_ROOT / "agents" / "base_agent.py").exists():
        return "Faz 1 — SAP Veri Entegrasyonu", 1
    else:
        return "Faz 0 — Hazırlık ve Altyapı", 0


def calculate_progress(phase_num):
    """Genel ilerleme yüzdesini hesapla."""
    # Her fazın ağırlığı
    phase_weights = {0: 10, 1: 25, 2: 50, 3: 70, 4: 90, 5: 100}
    return phase_weights.get(phase_num, 0)


def generate_progress_bar(percentage, length=10):
    """Metin tabanlı ilerleme çubuğu oluştur."""
    filled = int(length * percentage / 100)
    empty = length - filled
    return "█" * filled + "░" * empty


def update_status():
    """STATUS.md dosyasını güncelle."""
    now = datetime.now()
    
    # Metrikleri topla
    total_files = get_total_files()
    total_lines = (count_lines("agents") + count_lines("analysis") + 
                   count_lines("ui") + count_lines("scripts") + count_lines("."))
    agent_count = count_agents()
    analysis_count = count_analyses()
    test_count = count_tests()
    commit_count = get_git_commit_count()
    phase_name, phase_num = detect_current_phase()
    progress = calculate_progress(phase_num)
    progress_bar = generate_progress_bar(progress)
    
    # Faz durumları
    phase_statuses = []
    phases = [
        ("Faz 0 — Hazırlık ve Altyapı", 0),
        ("Faz 1 — SAP Veri Entegrasyonu", 1),
        ("Faz 2 — Ajan Mimarisi", 2),
        ("Faz 3 — Analiz Motoru", 3),
        ("Faz 4 — Görsel Ofis Simülasyonu", 4),
        ("Faz 5 — İleri Seviye", 5),
    ]
    
    for name, num in phases:
        if num < phase_num:
            phase_statuses.append(f"### {name} ✅ Tamamlandı")
        elif num == phase_num:
            phase_statuses.append(f"### {name} 🔄 Devam Ediyor")
        else:
            phase_statuses.append(f"### {name} ⏳ Bekliyor")
    
    phases_text = "\n".join(phase_statuses)
    
    # STATUS.md içeriğini oluştur
    content = f"""# 📊 Proje Durum Takibi — SAP Agentic AI

> Bu dosya proje ilerlemesini otomatik olarak takip eder.  
> Son güncelleme: **{now.strftime('%Y-%m-%d %H:%M')}**

---

## 🚦 Genel Durum

| Bilgi | Değer |
|-------|-------|
| **Aktif Faz** | {phase_name} |
| **Genel İlerleme** | {progress_bar} **{progress}%** |
| **Başlangıç Tarihi** | 2026-05-06 |
| **Tahmini MVP** | 2026-06-17 |
| **Son Güncelleme** | {now.strftime('%Y-%m-%d %H:%M')} |

---

## 📍 Neredeyiz?

{phases_text}

---

## 📈 İstatistikler

| Metrik | Değer |
|--------|-------|
| Toplam dosya | {total_files} |
| Toplam satır kod | {total_lines} |
| Ajan sayısı | {agent_count}/5 |
| Analiz sayısı | {analysis_count}/4 |
| Test sayısı | {test_count} |
| Commit sayısı | {commit_count} |

---

> 💡 Bu dosyayı güncellemek için: `python scripts/status_update.py`
"""
    
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"[OK] STATUS.md guncellendi - {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Aktif Faz: {phase_name}")
    print(f"   Ilerleme:  {progress}%")
    print(f"   Dosyalar:  {total_files} dosya, {total_lines} satir kod")
    print(f"   Ajanlar:   {agent_count}/5 | Analizler: {analysis_count}/4 | Testler: {test_count}")
    print(f"   Commitler: {commit_count}")


if __name__ == "__main__":
    update_status()
