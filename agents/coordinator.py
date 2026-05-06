"""
Koordinator Ajani
=================
Tüm ajanlari yonetir, is akisini sirayla calistirir.

Kullanim:
    from agents.coordinator import Coordinator
    coordinator = Coordinator()
    results = coordinator.run_pipeline()
"""

import sys
import io
import time
from datetime import datetime
from pathlib import Path

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.archive_clerk import ArchiveClerk
from agents.data_tech import DataTech
from agents.inspector import Inspector
from agents.graphic_wizard import GraphicWizard

class Coordinator:
    """
    Koordinator Ajani
    
    Arsiv Memuru -> Veri Teknisyeni -> Mufettis -> Grafik Sihirbazi
    is akisini yonetir.
    """
    
    NAME = "Koordinator"
    ICON = "[LISTE]"
    
    def __init__(self):
        self.status = "bekliyor"
        self.messages = []
        self.pipeline_results = {}
        
        # Ajanlari baslat
        self.clerk = ArchiveClerk()
        self.tech = DataTech()
        self.inspector = Inspector()
        self.wizard = GraphicWizard()
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {self.ICON} {self.NAME}: {message}"
        self.messages.append(entry)
        print(entry)
        
    def run_pipeline(self):
        self.status = "calisiyor"
        self.log("=== SAP Agentic AI Sureci Basliyor ===")
        start_time = time.time()
        
        # 1. Arsiv Memuru (Veri Cekme)
        self.log("Adim 1: Arsiv Memuru goreve cagiriliyor...")
        raw_data = self.clerk.run()
        if self.clerk.status == "hata":
            self.log("HATA: Arsiv Memuru gorevi tamamlayamadi. Surec durduruldu.")
            self.status = "hata"
            return None
            
        # 2. Veri Teknisyeni (Temizleme/Donusum)
        self.log("Adim 2: Veri Teknisyeni goreve cagiriliyor...")
        self.tech.set_data(raw_data)
        clean_data = self.tech.run()
        if self.tech.status == "hata":
            self.log("HATA: Veri Teknisyeni gorevi tamamlayamadi. Surec durduruldu.")
            self.status = "hata"
            return None
            
        # 3. Mufettis (Analiz)
        self.log("Adim 3: Mufettis goreve cagiriliyor...")
        self.inspector.set_data(clean_data)
        analysis_results = self.inspector.run()
        if self.inspector.status == "hata":
            self.log("HATA: Mufettis gorevi tamamlayamadi. Surec durduruldu.")
            self.status = "hata"
            return None
            
        # 4. Grafik Sihirbazi (Gorsellestirme)
        self.log("Adim 4: Grafik Sihirbazi goreve cagiriliyor...")
        self.wizard.set_results(analysis_results)
        charts = self.wizard.run()
        if self.wizard.status == "hata":
            self.log("HATA: Grafik Sihirbazi gorevi tamamlayamadi. Surec durduruldu.")
            self.status = "hata"
            return None
            
        # Tamamlanma
        duration = time.time() - start_time
        self.log(f"=== Surec Basariyla Tamamlandi! ({duration:.2f} saniye) ===")
        self.status = "tamamlandi"
        
        self.pipeline_results = {
            "raw_data_count": len(raw_data),
            "clean_data_count": len(clean_data),
            "analysis_results": analysis_results,
            "charts": charts,
            "duration": duration
        }
        
        return self.pipeline_results

if __name__ == "__main__":
    print("=" * 60)
    print("  Koordinator - Tam Surec Testi")
    print("=" * 60)
    print()
    
    coordinator = Coordinator()
    results = coordinator.run_pipeline()
    
    print()
    if results:
        print("Uretilen Dosyalar:")
        for chart in results["charts"]:
            print(f"  - {chart}")
