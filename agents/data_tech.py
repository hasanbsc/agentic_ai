"""
Veri Teknisyeni Ajani
=======================
Ham verileri alir, format donusumlerini yapar,
eksik veya hatali verileri temizler.

Kullanim:
    from agents.data_tech import DataTech
    tech = DataTech(raw_data)
    clean_data = tech.run()
"""

import sys
import io
import re
from datetime import datetime
from pathlib import Path

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def parse_odata_date(date_str):
    if not date_str:
        return None
    match = re.search(r'/Date\((\d+)\)/', str(date_str))
    if match:
        epoch_ms = int(match.group(1))
        return datetime.fromtimestamp(epoch_ms / 1000)
    return None

def parse_odata_duration(duration_str):
    if not duration_str:
        return None
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', str(duration_str))
    if match:
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        total_hours = hours + minutes / 60 + seconds / 3600
        return {
            "saat": hours,
            "dakika": minutes,
            "saniye": seconds,
            "toplam_saat": round(total_hours, 2)
        }
    return None

def transform_record(record):
    tarih = parse_odata_date(record.get("Tarih"))
    baslama = parse_odata_duration(record.get("BaslamaSaat"))
    bitis = parse_odata_duration(record.get("BitisSaat"))
    
    return {
        "personel_adi": record.get("PersonelAdi", "").strip(),
        "proje": record.get("ProjeTxt", "").strip() or record.get("Proje", "").strip(),
        "tarih": tarih.strftime("%Y-%m-%d") if tarih else None,
        "tarih_obj": tarih,
        "yil": tarih.year if tarih else None,
        "ay": tarih.month if tarih else None,
        "ay_adi": tarih.strftime("%B") if tarih else None,
        "gun_adi": tarih.strftime("%A") if tarih else None,
        "baslama_saat": f"{baslama['saat']:02d}:{baslama['dakika']:02d}" if baslama else None,
        "bitis_saat": f"{bitis['saat']:02d}:{bitis['dakika']:02d}" if bitis else None,
        "lokasyon": record.get("LokasyonTxt", "").strip(),
        "sure_saat": float(record.get("Sure", 0)),
        "aciklama": record.get("Aciklama", "").strip(),
    }


class DataTech:
    """
    Veri Teknisyeni Ajani
    
    Ham verileri isler, temizler ve analize hazir hale getirir.
    """
    
    NAME = "Veri Teknisyeni"
    ICON = "[ANAHTAR]"
    
    def __init__(self, raw_data=None):
        self.raw_data = raw_data or []
        self.clean_data = []
        self.status = "bekliyor"
        self.messages = []
    
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {self.ICON} {self.NAME}: {message}"
        self.messages.append(entry)
        print(entry)
        
    def set_data(self, data):
        self.raw_data = data
        
    def run(self):
        self.status = "calisiyor"
        self.log("Gorev basliyor...")
        
        if not self.raw_data:
            self.status = "hata"
            self.log("Ham veri bulunamadi!")
            return []
            
        self.log(f"{len(self.raw_data)} ham kayit inceleniyor...")
        
        # Donusum ve temizleme
        self.clean_data = []
        hatali_kayitlar = 0
        
        for record in self.raw_data:
            try:
                clean_rec = transform_record(record)
                # Basit dogrulama: personel adi veya sure eksikse hatali kabul et
                if not clean_rec["personel_adi"] or clean_rec["sure_saat"] < 0:
                    hatali_kayitlar += 1
                    continue
                self.clean_data.append(clean_rec)
            except Exception as e:
                hatali_kayitlar += 1
        
        self.log(f"{len(self.clean_data)} kayit basariyla temizlendi ve donusturuldu.")
        if hatali_kayitlar > 0:
            self.log(f"DIKKAT: {hatali_kayitlar} hatali kayit tespit edildi ve atlandi.")
            
        self.status = "tamamlandi"
        self.log("Gorev tamamlandi!")
        
        return self.clean_data
        
    def get_summary(self):
        return {
            "ajan": self.NAME,
            "durum": self.status,
            "ham_kayit_sayisi": len(self.raw_data),
            "temiz_kayit_sayisi": len(self.clean_data),
            "mesaj_sayisi": len(self.messages),
            "son_mesaj": self.messages[-1] if self.messages else None,
        }

if __name__ == "__main__":
    from agents.archive_clerk import ArchiveClerk
    
    print("=" * 60)
    print("  Veri Teknisyeni - Test Calistirmasi")
    print("=" * 60)
    print()
    
    # Ham veriyi almak icin ArchiveClerk'i kullaniyoruz,
    # ancak ArchiveClerk'in orjinalinde temizleme islemi de vardi.
    # Bu yuzden buradaki test amaciyla ArchiveClerk ciktisini girdi olarak verebiliriz.
    clerk = ArchiveClerk()
    # Aslinda clerk.raw_data almaliyiz
    clerk.sample_mode = True
    raw_data = clerk.fetch_from_sample()
    
    print()
    print("-" * 60)
    print()
    
    tech = DataTech(raw_data)
    clean_data = tech.run()
    
    print()
    if clean_data:
        print("Ilk kayit ornegi:")
        print(clean_data[0])
