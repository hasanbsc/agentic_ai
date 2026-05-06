"""
Grafik Sihirbazi Ajani
======================
Mufettis ajanindan gelen analiz sonuclarini kullanarak
gorsel grafikler ve raporlar olusturur.

Kullanim:
    from agents.graphic_wizard import GraphicWizard
    wizard = GraphicWizard(analysis_results)
    charts = wizard.run()
"""

import sys
import io
import os
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

class GraphicWizard:
    """
    Grafik Sihirbazi Ajani
    
    Analiz sonuclarindan gorsel grafikler uretir.
    """
    
    NAME = "Grafik Sihirbazi"
    ICON = "[FIRCA]"
    
    def __init__(self, analysis_results=None):
        self.results = analysis_results or {}
        self.status = "bekliyor"
        self.messages = []
        self.charts = []
        self.output_dir = PROJECT_ROOT / "reports" / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {self.ICON} {self.NAME}: {message}"
        self.messages.append(entry)
        print(entry)
        
    def set_results(self, results):
        self.results = results
        
    def create_personnel_leave_chart(self):
        self.log("Personel izin dagilimi grafigi ciziliyor...")
        data = self.results.get("personel_izin", [])
        if not data:
            return None
            
        personel = [item["personel"] for item in data]
        saatler = [item["toplam_izin_saat"] for item in data]
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(personel, saatler, color='#4c72b0')
        plt.title('Personel Bazinda Toplam Izin Sureleri (Saat)', fontsize=14)
        plt.xlabel('Personel', fontsize=12)
        plt.ylabel('Toplam Izin Saati', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        
        # Degerleri barlarin uzerine yaz
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval + 0.5, f'{yval}s', ha='center', va='bottom')
            
        plt.tight_layout()
        filepath = self.output_dir / "personel_izin.png"
        plt.savefig(filepath, dpi=300)
        plt.close()
        
        self.charts.append(str(filepath))
        return filepath
        
    def create_location_pie_chart(self):
        self.log("Lokasyon dagilimi pasta grafigi ciziliyor...")
        data = self.results.get("lokasyon_dagilimi", [])
        if not data:
            return None
            
        lokasyonlar = [item["lokasyon"] for item in data]
        oranlar = [item["oran_yuzde"] for item in data]
        
        plt.figure(figsize=(8, 8))
        colors = ['#55a868', '#c44e52', '#8172b2', '#ccb974', '#64b5cd']
        plt.pie(oranlar, labels=lokasyonlar, autopct='%1.1f%%', startangle=90, colors=colors[:len(lokasyonlar)])
        plt.title('Calisma Lokasyonu Dagilimi', fontsize=14)
        
        plt.tight_layout()
        filepath = self.output_dir / "lokasyon_dagilim.png"
        plt.savefig(filepath, dpi=300)
        plt.close()
        
        self.charts.append(str(filepath))
        return filepath
        
    def create_project_type_chart(self):
        self.log("Proje tipi dagilimi grafigi ciziliyor...")
        data = self.results.get("proje_tipi_dagilimi", [])
        if not data:
            return None
            
        projeler = [item["proje"] for item in data]
        saatler = [item["toplam_saat"] for item in data]
        
        plt.figure(figsize=(10, 6))
        bars = plt.barh(projeler, saatler, color='#8172b2')
        plt.title('Aktivite / Proje Tipi Dagilimi (Toplam Saat)', fontsize=14)
        plt.xlabel('Toplam Saat', fontsize=12)
        plt.ylabel('Aktivite Tipi', fontsize=12)
        
        plt.tight_layout()
        filepath = self.output_dir / "proje_tipi.png"
        plt.savefig(filepath, dpi=300)
        plt.close()
        
        self.charts.append(str(filepath))
        return filepath

    def run(self):
        self.status = "calisiyor"
        self.log("Gorev basliyor...")
        
        if not self.results:
            self.status = "hata"
            self.log("Analiz sonuclari bulunamadi!")
            return []
            
        self.charts = []
        
        self.create_personnel_leave_chart()
        self.create_location_pie_chart()
        self.create_project_type_chart()
        
        self.log(f"{len(self.charts)} adet grafik basariyla olusturuldu.")
        
        self.status = "tamamlandi"
        self.log("Gorev tamamlandi!")
        
        return self.charts
        
    def get_summary(self):
        return {
            "ajan": self.NAME,
            "durum": self.status,
            "grafik_sayisi": len(self.charts),
            "mesaj_sayisi": len(self.messages),
            "son_mesaj": self.messages[-1] if self.messages else None,
        }

if __name__ == "__main__":
    from agents.archive_clerk import ArchiveClerk
    from agents.data_tech import DataTech
    from agents.inspector import Inspector
    
    print("=" * 60)
    print("  Grafik Sihirbazi - Test Calistirmasi")
    print("=" * 60)
    print()
    
    clerk = ArchiveClerk()
    clerk.sample_mode = True
    raw_data = clerk.fetch_from_sample()
    
    tech = DataTech(raw_data)
    clean_data = tech.run()
    
    inspector = Inspector(clean_data)
    results = inspector.run()
    
    print()
    print("-" * 60)
    print()
    
    wizard = GraphicWizard(results)
    charts = wizard.run()
    
    print()
    print("Olusturulan Grafikler:")
    for chart in charts:
        print(f"  - {chart}")
