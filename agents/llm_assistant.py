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
import requests
from pathlib import Path

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
        self.status = "bekliyor"
        self.messages = []
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "llama3" # Kullanacaginiz yerel model (llama3, mistral, phi3 vb.)
            
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
        if not self.data:
            return "Sistem: Analiz edilecek hic veri bulunamadi. Once verileri cekmelisiniz."
            
        self.status = "calisiyor"
        self.log(f"Soru analiz ediliyor: '{question}'")
        
        # Veriyi kucult (Prompt'a sigmasi icin cok fazla alan varsa sadece onemlileri tutalim)
        # Ama 100 kayit genelde kucuktur, hepsini string'e cevirebiliriz.
        # Local LLM'in baglamina (context) sigmasi icin sadece son 50 kaydi gonderiyoruz
        # Eger 16.000 kayit gonderirsek local LLM'in hafizasi sisebilir!
        mini_data = []
        for d in self.data[:50]:
            mini_data.append({
                "Personel": d.get("personel_adi"),
                "Sure": d.get("sure_saat"),
                "Proje": d.get("proje")
            })
            
        json_data = json.dumps(mini_data, ensure_ascii=False)
        
        prompt = f"""Sen bir IK asistanisin. Asagidaki JSON verilerine bakarak kullanicinin sorusunu kisa ve oz sekilde, Turkce cevapla.
Veriler: {json_data}
Soru: {question}"""
        
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }
            response = requests.post(self.ollama_url, json=payload, timeout=120)
            response.raise_for_status()
            
            result_text = response.json().get("response", "")
            
            self.status = "tamamlandi"
            self.log("Yerel LLM'den cevap alindi.")
            return result_text
            
        except requests.exceptions.ConnectionError:
            self.status = "hata"
            self.log("HATA: Ollama calismiyor olabilir.")
            return "Sistem: Ollama'ya baglanilamadi. Lutfen bilgisayarinizda Ollama'nin calistigindan emin olun (http://localhost:11434)."
        except Exception as e:
            self.status = "hata"
            self.log(f"HATA: {str(e)}")
            return f"Maalesef yerel modelde bir hata olustu: {str(e)}"

if __name__ == "__main__":
    asistan = LLMAssistant([{"personel_adi": "Bora Uckun", "tarih": "2023-06-26", "sure_saat": 8.0, "proje": "Yillik Izin"}])
    print(asistan.ask("Bora Uckun ne zaman izin almis?"))
