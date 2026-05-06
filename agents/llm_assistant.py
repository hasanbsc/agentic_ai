"""
LLM Asistani (Bilge Ajan)
=========================
SAP'den cekilen verileri inceleyip dogal dilde sorulan 
sorulara Gemini modeli kullanarak yanit verir.

Kullanim:
    from agents.llm_assistant import LLMAssistant
    asistan = LLMAssistant(clean_data)
    cevap = asistan.ask("Haziran ayinda en cok kim calismis?")
"""

import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.env_loader import get_gemini_api_key

class LLMAssistant:
    """
    LLM Asistani (Bilge Ajan)
    
    Verileri analiz ederek kullanicinin sorularini 
    dogal dille cevaplar.
    """
    
    NAME = "Bilge Asistan"
    ICON = "🧠"
    
    def __init__(self, clean_data=None):
        self.data = clean_data or []
        self.api_key = get_gemini_api_key()
        self.status = "bekliyor"
        self.messages = []
        
        # Eger key varsa clienti baslat
        if self.api_key and self.api_key != "buraya_api_key_yazilacak":
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except ImportError:
                self.client = None
                self.log("Uyari: google-genai kutuphanesi yuklu degil!")
        else:
            self.client = None
            
    def log(self, message):
        """Ajan mesaji kaydet."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {self.ICON} {self.NAME}: {message}"
        self.messages.append(entry)
        print(entry)
        
    def set_data(self, data):
        self.data = data
        
    def ask(self, question):
        """Soruya cevap uretir"""
        if not self.client:
            return "Sistem: Gemini API Anahtari bulunamadi veya google-genai yuklu degil. Lutfen .env dosyasina GEMINI_API_KEY ekleyin."
            
        if not self.data:
            return "Sistem: Analiz edilecek hic veri bulunamadi. Once verileri cekmelisiniz."
            
        self.status = "calisiyor"
        self.log(f"Soru analiz ediliyor: '{question}'")
        
        # Veriyi kucult (Prompt'a sigmasi icin cok fazla alan varsa sadece onemlileri tutalim)
        # Ama 100 kayit genelde kucuktur, hepsini string'e cevirebiliriz.
        mini_data = []
        for d in self.data:
            mini_data.append({
                "Personel": d.get("personel_adi"),
                "Tarih": d.get("tarih"),
                "Sure": d.get("sure_saat"),
                "Proje": d.get("proje"),
                "Lokasyon": d.get("lokasyon")
            })
            
        json_data = json.dumps(mini_data, ensure_ascii=False)
        
        prompt = f"""
Sen bir IK ve Proje Yonetimi asistanisin (Bilge Ajan). 
Asagida sana sirketimizin SAP sisteminden cekilmis personel aktivite (zaman cizelgesi) verilerini JSON formatinda veriyorum.
Bu verilere dayanarak kullanicinin sorusunu samimi, profesyonel ve dogru bir sekilde, tamamen Turkce cevapla.
Eger sorunun cevabi verilerde yoksa, uydurma, "Bu bilgiye sahip degilim" de.

[VERILER]:
{json_data}

[KULLANICI SORUSU]:
{question}
"""
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            self.status = "tamamlandi"
            self.log("Cevap uretildi.")
            return response.text
        except Exception as e:
            self.status = "hata"
            self.log(f"API Hatasi: {str(e)}")
            return f"Maalesef bir hata olustu: {str(e)}"

if __name__ == "__main__":
    asistan = LLMAssistant([{"personel_adi": "Bora Uckun", "tarih": "2023-06-26", "sure_saat": 8.0, "proje": "Yillik Izin"}])
    print(asistan.ask("Bora Uckun ne zaman izin almis?"))
