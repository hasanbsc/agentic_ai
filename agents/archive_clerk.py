"""
SAP OData Baglanti Modulu
==========================
SAP sistemine OData protokolu uzerinden baglanarak
personel aktivite verilerini ceker.

Kullanim:
    from agents.archive_clerk import ArchiveClerk
    clerk = ArchiveClerk()
    data = clerk.run()
"""

import json
import re
import sys
import io
from datetime import datetime, timedelta
from pathlib import Path

# Windows terminal Unicode fix
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Proje kok dizini
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.env_loader import get_sap_config, is_sample_mode


# ============================================================
# Arsiv Memuru Ajani
# ============================================================

class ArchiveClerk:
    """
    Arsiv Memuru Ajani
    
    SAP OData servisinden personel aktivite verilerini ceker,
    OData formatlarini donusturur ve temiz veriyi dondurur.
    """
    
    NAME = "Arsiv Memuru"
    ICON = "[ARSIV]"
    
    def __init__(self):
        self.sap_config = get_sap_config()
        self.sample_mode = is_sample_mode()
        self.status = "bekliyor"
        self.messages = []
        self.raw_data = []
    
    def log(self, message):
        """Ajan mesaji kaydet."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {self.ICON} {self.NAME}: {message}"
        self.messages.append(entry)
        print(entry)
    
    def fetch_from_sap(self):
        """SAP OData servisinden veri cek."""
        import requests
        
        base_url = self.sap_config["base_url"]
        service = self.sap_config["service"]
        url = f"{base_url}{service}/AktivitePlanSet?$format=json"
        
        self.log(f"SAP'ye baglaniliyor: {base_url}")
        
        try:
            response = requests.get(
                url,
                auth=(self.sap_config["username"], self.sap_config["password"]),
                verify=self.sap_config["verify_ssl"],
                timeout=30,
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            
            data = response.json()
            # OData response yapisini coz
            results = data.get("d", {}).get("results", [])
            self.log(f"SAP'den {len(results)} kayit cekildi")
            return results
            
        except requests.exceptions.ConnectionError:
            self.log("HATA: SAP sunucusuna baglanilamiyor!")
            return []
        except requests.exceptions.Timeout:
            self.log("HATA: SAP baglantisi zaman asimina ugradi!")
            return []
        except requests.exceptions.HTTPError as e:
            self.log(f"HATA: SAP HTTP hatasi: {e}")
            return []
        except Exception as e:
            self.log(f"HATA: Beklenmeyen hata: {e}")
            return []
    
    def fetch_from_sample(self):
        """Yerel ornek veriden oku."""
        sample_path = PROJECT_ROOT / "data" / "sample" / "sample_activities.json"
        
        self.log(f"Ornek veri okunuyor: {sample_path.name}")
        
        if not sample_path.exists():
            self.log("HATA: Ornek veri dosyasi bulunamadi!")
            return []
        
        with open(sample_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self.log(f"Ornek dosyadan {len(data)} kayit okundu")
        return data
    
    def save_raw_data(self, data):
        """Ham veriyi yerel dosyaya kaydet."""
        raw_path = PROJECT_ROOT / "data" / "raw"
        raw_path.mkdir(parents=True, exist_ok=True)
        
        filename = f"aktiviteler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = raw_path / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        self.log(f"Ham veri kaydedildi: {filename}")
        return filepath
    
    def run(self):
        """
        Arsiv Memuru ana gorevi:
        1. Veri kaynagindan veri cek (SAP veya ornek)
        """
        self.status = "calisiyor"
        self.log("Gorev basliyor...")
        
        # 1. Veri cek
        if self.sample_mode:
            self.log("Mod: Ornek Veri (USE_SAMPLE_DATA=true)")
            self.raw_data = self.fetch_from_sample()
        else:
            self.log("Mod: Canli SAP Baglantisi")
            self.raw_data = self.fetch_from_sap()
        
        if not self.raw_data:
            self.status = "hata"
            self.log("Veri alinamadi! Gorev basarisiz.")
            return []
        
        # 2. Kaydet
        self.save_raw_data(self.raw_data)
        
        self.status = "tamamlandi"
        self.log("Gorev tamamlandi!")
        
        return self.raw_data
    
    def get_summary(self):
        """Ajan durum ozeti."""
        return {
            "ajan": self.NAME,
            "durum": self.status,
            "kayit_sayisi": len(self.raw_data),
            "mesaj_sayisi": len(self.messages),
            "son_mesaj": self.messages[-1] if self.messages else None,
        }


# ============================================================
# Dogrudan calistirma
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  Arsiv Memuru - Test Calistirmasi")
    print("=" * 60)
    print()
    
    clerk = ArchiveClerk()
    data = clerk.run()
    
    print()
    print(f"--- Sonuc: {len(data)} kayit ---")
    if data:
        print()
        print("Ilk 3 ham kayit:")
        for i, record in enumerate(data[:3]):
            print(f"  {i+1}. {record}")
    
    print()
    print("--- Ajan Ozeti ---")
    summary = clerk.get_summary()
    for k, v in summary.items():
        print(f"  {k}: {v}")
