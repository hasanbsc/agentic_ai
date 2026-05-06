# 🏢 Agentic AI — SAP Personel Aktivite Analiz Sistemi

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Status](https://img.shields.io/badge/Status-Faz%200%20%E2%80%93%20Haz%C4%B1rl%C4%B1k-yellow)
![License](https://img.shields.io/badge/License-MIT-green)

## 🎯 Proje Hakkında

SAP'deki personel aktivite (izin/çalışma) verilerini analiz eden, tamamen localhost'ta çalışan, **çok ajanlı bir yapay zeka sistemi**.

Sistem, çizgi film tarzı bir **ofis simülasyonu** arayüzüyle çalışır. Her ajan bir ofis çalışanı gibi görünür, konuşma balonlarıyla ne yaptığını gösterir ve analiz sürecini eğlenceli bir deneyime dönüştürür.

## 🤖 Ajanlar

| Ajan | Karakter | Görev |
|------|----------|-------|
| 🗄️ **Arşiv Memuru** | Gözlüklü dosya memuru | SAP'den veri çekme |
| 🔧 **Veri Teknisyeni** | Tamirci | Veri temizleme ve dönüştürme |
| 🔍 **Müfettiş** | Dedektif | İstatistiksel analiz |
| 🎨 **Grafik Sihirbazı** | Ressam | Grafik ve rapor üretimi |
| 📋 **Koordinatör** | Müdür | İş akışı yönetimi |

## 📊 Analizler

- Personel bazında toplam izin süresi
- Aylara göre izin dağılımı
- Lokasyon (EV/Ofis) dağılımı
- Proje tipi dağılımı

## 🛠️ Teknoloji

- **Backend:** Python 3.10+
- **SAP Bağlantı:** requests + OData
- **Analiz:** pandas, matplotlib
- **Arayüz:** Streamlit (MVP) → HTML5 Canvas (v2)

## 🚀 Kurulum

```bash
# Repo'yu klonla
git clone https://github.com/hasanbsc/agentic_ai.git
cd agentic_ai

# Sanal ortam oluştur
python -m venv venv
venv\Scripts\activate  # Windows

# Bağımlılıkları yükle
pip install -r requirements.txt

# SAP yapılandırmasını ayarla
copy config\config.example.yaml config\config.yaml
# config.yaml dosyasını kendi SAP bilgilerinle düzenle

# Uygulamayı çalıştır
python main.py
```

## 📁 Proje Yapısı

```
agentic_ai/
├── agents/              # Ajan tanımları ve mantığı
│   ├── base_agent.py    # Tüm ajanların temel sınıfı
│   ├── archive_clerk.py # Arşiv Memuru (veri çekme)
│   ├── data_tech.py     # Veri Teknisyeni (temizleme)
│   ├── inspector.py     # Müfettiş (analiz)
│   ├── graphic_wizard.py# Grafik Sihirbazı (raporlama)
│   └── coordinator.py   # Koordinatör (orkestrasyon)
├── data/                # Veri dosyaları
│   ├── sample/          # Örnek test verileri
│   └── raw/             # SAP'den çekilen ham veriler
├── analysis/            # Analiz motorları
├── ui/                  # Görsel ofis simülasyonu
├── reports/             # Üretilen raporlar
├── config/              # Yapılandırma dosyaları
├── scripts/             # Yardımcı komut dosyaları
├── tests/               # Test dosyaları
├── main.py              # Ana giriş noktası
├── requirements.txt     # Python bağımlılıkları
└── STATUS.md            # Proje durum takibi
```

## 📋 Durum

Güncel proje durumu için [STATUS.md](STATUS.md) dosyasına bakınız.

## 📜 Lisans

MIT License
