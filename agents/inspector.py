"""
Mufettis Ajani — Istatistiksel Analiz
=======================================
Temizlenmis personel aktivite verilerini analiz eder.

Analizler:
  1. Personel bazinda toplam izin suresi
  2. Aylara gore izin dagilimi
  3. Lokasyon (EV/Ofis) dagilimi
  4. Proje tipi dagilimi

Kullanim:
    from agents.inspector import Inspector
    inspector = Inspector(clean_data)
    results = inspector.run()
"""

import sys
import io
from datetime import datetime
from collections import defaultdict
from pathlib import Path

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class Inspector:
    """
    Mufettis Ajani
    
    Personel aktivite verilerini analiz ederek istatistiksel
    sonuclar ve raporlar uretir.
    """
    
    NAME = "Mufettis"
    ICON = "[BUYUTEC]"
    
    def __init__(self, data=None):
        self.data = data or []
        self.status = "bekliyor"
        self.messages = []
        self.results = {}
    
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {self.ICON} {self.NAME}: {message}"
        self.messages.append(entry)
        print(entry)
    
    def set_data(self, data):
        """Analiz edilecek veriyi ayarla."""
        self.data = data
    
    # ---- Analiz 1: Personel bazinda toplam izin suresi ----
    def analiz_personel_izin(self):
        """Her personelin toplam izin suresini hesapla."""
        self.log("Analiz 1: Personel bazinda izin suresi hesaplaniyor...")
        
        izin_tipleri = {"Yillik Izin", "Yıllık İzin", "Hastalık İzni", "Hastalik Izni"}
        personel = defaultdict(lambda: {"toplam_izin_saat": 0, "izin_gun": 0, "kayitlar": []})
        
        for r in self.data:
            if r["proje"] in izin_tipleri:
                p = personel[r["personel_adi"]]
                p["toplam_izin_saat"] += r["sure_saat"]
                p["izin_gun"] += 1
                p["kayitlar"].append(r)
        
        result = []
        for ad, bilgi in sorted(personel.items()):
            result.append({
                "personel": ad,
                "toplam_izin_saat": bilgi["toplam_izin_saat"],
                "izin_gun_sayisi": bilgi["izin_gun"],
                "ortalama_saat_gun": round(bilgi["toplam_izin_saat"] / max(bilgi["izin_gun"], 1), 1)
            })
        
        self.log(f"  -> {len(result)} personel icin izin analizi tamamlandi")
        return result
    
    # ---- Analiz 2: Aylara gore dagilim ----
    def analiz_aylik_dagilim(self):
        """Aylara gore aktivite dagilimini hesapla."""
        self.log("Analiz 2: Aylik dagilim hesaplaniyor...")
        
        ay_isimleri = {
            1: "Ocak", 2: "Subat", 3: "Mart", 4: "Nisan",
            5: "Mayis", 6: "Haziran", 7: "Temmuz", 8: "Agustos",
            9: "Eylul", 10: "Ekim", 11: "Kasim", 12: "Aralik"
        }
        
        aylar = defaultdict(lambda: {"toplam_saat": 0, "kayit_sayisi": 0, "izin_saat": 0, "calisma_saat": 0})
        izin_tipleri = {"Yillik Izin", "Yıllık İzin", "Hastalık İzni", "Hastalik Izni"}
        
        for r in self.data:
            if r["ay"]:
                ay = aylar[r["ay"]]
                ay["toplam_saat"] += r["sure_saat"]
                ay["kayit_sayisi"] += 1
                if r["proje"] in izin_tipleri:
                    ay["izin_saat"] += r["sure_saat"]
                else:
                    ay["calisma_saat"] += r["sure_saat"]
        
        result = []
        for ay_no in sorted(aylar.keys()):
            bilgi = aylar[ay_no]
            result.append({
                "ay": ay_no,
                "ay_adi": ay_isimleri.get(ay_no, f"Ay {ay_no}"),
                "toplam_saat": bilgi["toplam_saat"],
                "izin_saat": bilgi["izin_saat"],
                "calisma_saat": bilgi["calisma_saat"],
                "kayit_sayisi": bilgi["kayit_sayisi"]
            })
        
        self.log(f"  -> {len(result)} ay icin dagilim hesaplandi")
        return result
    
    # ---- Analiz 3: Lokasyon dagilimi ----
    def analiz_lokasyon(self):
        """EV vs Ofis dagilimini hesapla."""
        self.log("Analiz 3: Lokasyon dagilimi hesaplaniyor...")
        
        lokasyonlar = defaultdict(lambda: {"toplam_saat": 0, "kayit_sayisi": 0, "personeller": set()})
        
        for r in self.data:
            lok = r["lokasyon"] or "Bilinmiyor"
            l = lokasyonlar[lok]
            l["toplam_saat"] += r["sure_saat"]
            l["kayit_sayisi"] += 1
            l["personeller"].add(r["personel_adi"])
        
        toplam_kayit = sum(l["kayit_sayisi"] for l in lokasyonlar.values())
        
        result = []
        for lok_adi, bilgi in sorted(lokasyonlar.items()):
            oran = (bilgi["kayit_sayisi"] / max(toplam_kayit, 1)) * 100
            result.append({
                "lokasyon": lok_adi,
                "toplam_saat": bilgi["toplam_saat"],
                "kayit_sayisi": bilgi["kayit_sayisi"],
                "oran_yuzde": round(oran, 1),
                "personel_sayisi": len(bilgi["personeller"])
            })
        
        self.log(f"  -> {len(result)} lokasyon icin dagilim hesaplandi")
        return result
    
    # ---- Analiz 4: Proje tipi dagilimi ----
    def analiz_proje_tipi(self):
        """Proje/aktivite tipi dagilimini hesapla."""
        self.log("Analiz 4: Proje tipi dagilimi hesaplaniyor...")
        
        projeler = defaultdict(lambda: {"toplam_saat": 0, "kayit_sayisi": 0, "personeller": set()})
        
        for r in self.data:
            proje = r["proje"] or "Bilinmiyor"
            p = projeler[proje]
            p["toplam_saat"] += r["sure_saat"]
            p["kayit_sayisi"] += 1
            p["personeller"].add(r["personel_adi"])
        
        toplam_saat = sum(p["toplam_saat"] for p in projeler.values())
        
        result = []
        for proje_adi, bilgi in sorted(projeler.items(), key=lambda x: -x[1]["toplam_saat"]):
            oran = (bilgi["toplam_saat"] / max(toplam_saat, 1)) * 100
            result.append({
                "proje": proje_adi,
                "toplam_saat": bilgi["toplam_saat"],
                "kayit_sayisi": bilgi["kayit_sayisi"],
                "oran_yuzde": round(oran, 1),
                "personel_sayisi": len(bilgi["personeller"])
            })
        
        self.log(f"  -> {len(result)} proje tipi icin dagilim hesaplandi")
        return result
    
    # ---- Genel ozet ----
    def analiz_genel_ozet(self):
        """Veri setinin genel ozetini cikar."""
        self.log("Genel ozet hazirlaniyor...")
        
        personeller = set()
        tarihler = []
        
        for r in self.data:
            personeller.add(r["personel_adi"])
            if r["tarih"]:
                tarihler.append(r["tarih"])
        
        tarihler.sort()
        toplam_saat = sum(r["sure_saat"] for r in self.data)
        
        ozet = {
            "toplam_kayit": len(self.data),
            "toplam_personel": len(personeller),
            "personel_listesi": sorted(personeller),
            "toplam_saat": toplam_saat,
            "ilk_tarih": tarihler[0] if tarihler else None,
            "son_tarih": tarihler[-1] if tarihler else None,
            "ortalama_saat_kayit": round(toplam_saat / max(len(self.data), 1), 1)
        }
        
        self.log(f"  -> {ozet['toplam_kayit']} kayit, {ozet['toplam_personel']} personel, {ozet['toplam_saat']} saat")
        return ozet
    
    def run(self):
        """Tum analizleri calistir."""
        self.status = "calisiyor"
        self.log("Gorev basliyor...")
        self.log(f"Analiz edilecek kayit sayisi: {len(self.data)}")
        
        if not self.data:
            self.status = "hata"
            self.log("Veri yok! Analiz yapilamiyor.")
            return {}
        
        self.results = {
            "genel_ozet": self.analiz_genel_ozet(),
            "personel_izin": self.analiz_personel_izin(),
            "aylik_dagilim": self.analiz_aylik_dagilim(),
            "lokasyon_dagilimi": self.analiz_lokasyon(),
            "proje_tipi_dagilimi": self.analiz_proje_tipi(),
        }
        
        self.status = "tamamlandi"
        self.log("Tum analizler tamamlandi!")
        
        return self.results
    
    def get_summary(self):
        return {
            "ajan": self.NAME,
            "durum": self.status,
            "analiz_sayisi": len(self.results),
            "mesaj_sayisi": len(self.messages),
            "son_mesaj": self.messages[-1] if self.messages else None,
        }


# ============================================================
# Dogrudan calistirma
# ============================================================

if __name__ == "__main__":
    from agents.archive_clerk import ArchiveClerk
    
    print("=" * 60)
    print("  Mufettis - Test Calistirmasi")
    print("=" * 60)
    print()
    
    # Once Arsiv Memuru veri ceksin
    clerk = ArchiveClerk()
    data = clerk.run()
    
    print()
    print("-" * 60)
    print()
    
    # Sonra Mufettis analiz etsin
    inspector = Inspector(data)
    results = inspector.run()
    
    print()
    print("=" * 60)
    print("  ANALIZ SONUCLARI")
    print("=" * 60)
    
    # Genel Ozet
    ozet = results["genel_ozet"]
    print(f"\n--- Genel Ozet ---")
    print(f"  Toplam Kayit: {ozet['toplam_kayit']}")
    print(f"  Personel: {ozet['toplam_personel']} kisi")
    print(f"  Tarih Araligi: {ozet['ilk_tarih']} - {ozet['son_tarih']}")
    print(f"  Toplam Saat: {ozet['toplam_saat']}")
    
    # Personel Izin
    print(f"\n--- Personel Izin Sureleri ---")
    for p in results["personel_izin"]:
        print(f"  {p['personel']:20s} | {p['toplam_izin_saat']:5.1f} saat | {p['izin_gun_sayisi']} gun")
    
    # Lokasyon
    print(f"\n--- Lokasyon Dagilimi ---")
    for l in results["lokasyon_dagilimi"]:
        bar = "#" * int(l["oran_yuzde"] / 5)
        print(f"  {l['lokasyon']:10s} | {l['oran_yuzde']:5.1f}% | {bar}")
    
    # Proje Tipi
    print(f"\n--- Proje Tipi Dagilimi ---")
    for p in results["proje_tipi_dagilimi"]:
        bar = "#" * int(p["oran_yuzde"] / 5)
        print(f"  {p['proje']:20s} | {p['toplam_saat']:5.1f}s | {p['oran_yuzde']:5.1f}% | {bar}")
