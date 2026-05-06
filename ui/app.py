"""
Gorsel Ofis Simulasyonu (Streamlit)
===================================
Ajanlarin calisma surecini ve sonuclari
gorsellestiren arayuz.

Kullanim:
    streamlit run ui/app.py
"""

import sys
import time
import os
from pathlib import Path
import streamlit as st

# Proje kok dizinini Python path'ine ekle
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.coordinator import Coordinator
from config.env_loader import is_sample_mode

# Sayfa ayarlari
st.set_page_config(
    page_title="SAP Agentic AI - Ofis",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ozel CSS ile tasarimi guzellestirme
st.markdown("""
<style>
    /* Ana arka plan rengi ve fontlar */
    .stApp {
        background-color: #0e1117;
        font-family: 'Inter', sans-serif;
    }
    
    /* Ajan Kartlari */
    .agent-card {
        background-color: #1e212b;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 5px solid #4c72b0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease;
    }
    .agent-card:hover {
        transform: translateY(-5px);
    }
    
    /* Konusma Balonu */
    .speech-bubble {
        background-color: #2b303b;
        border-radius: 15px;
        padding: 15px;
        position: relative;
        margin-top: 10px;
        font-family: monospace;
        color: #e0e0e0;
        border: 1px solid #3b4252;
    }
    .speech-bubble::before {
        content: "";
        position: absolute;
        top: -10px;
        left: 20px;
        border-width: 0 10px 10px 10px;
        border-style: solid;
        border-color: transparent transparent #2b303b transparent;
    }
    
    /* Basliklar */
    h1, h2, h3 {
        color: #f8f9fa !important;
    }
    
    /* Durum gostergeleri */
    .status-badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 0.8em;
        font-weight: bold;
        margin-left: 10px;
    }
    .status-bekliyor { background-color: #4b5563; color: white; }
    .status-calisiyor { background-color: #d97706; color: white; }
    .status-tamamlandi { background-color: #059669; color: white; }
    .status-hata { background-color: #dc2626; color: white; }
</style>
""", unsafe_allow_html=True)


def draw_header():
    """Uygulama ust kismini ciz."""
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown("<h1 style='text-align: center; font-size: 4em;'>🏢</h1>", unsafe_allow_html=True)
    with col2:
        st.title("SAP Agentic AI")
        st.subheader("Personel Aktivite Analiz Sistemi")
        mode_text = "Ornek Veri Modu" if is_sample_mode() else "Canli SAP Baglantisi"
        st.caption(f"Veri Kaynagi: **{mode_text}**")
    st.divider()


def draw_agent(name, icon, status, messages, description):
    """Tek bir ajan kartini ekrana ciz."""
    status_class = f"status-{status.lower()}"
    status_text = status.upper()
    
    html = f"""
    <div class="agent-card">
        <h3 style="margin-top: 0;">{icon} {name} 
            <span class="status-badge {status_class}">{status_text}</span>
        </h3>
        <p style="color: #a0aec0; font-size: 0.9em; margin-bottom: 5px;">{description}</p>
    """
    
    st.markdown(html, unsafe_allow_html=True)
    
    # Eger ajan calisiyor veya bitirdiyse mesaj balonunu goster
    if messages and status != "bekliyor":
        # Son 3 mesaji goster
        recent_msgs = messages[-3:] if len(messages) > 3 else messages
        msgs_html = "<br>".join([m.split(":", 3)[-1].strip() for m in recent_msgs])
        
        st.markdown(f"""
        <div class="speech-bubble">
            {msgs_html}
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)


def main():
    draw_header()
    
    # Session state baslatma
    if 'coordinator' not in st.session_state:
        st.session_state.coordinator = Coordinator()
        st.session_state.is_running = False
        st.session_state.is_done = False
        st.session_state.results = None
        
    c = st.session_state.coordinator
    
    # --- Sol Panel: Kontroller ---
    with st.sidebar:
        st.header("📋 Kontrol Paneli")
        st.write("Tum ajan is akisini buradan baslatabilirsiniz.")
        
        start_btn = st.button("🚀 Sureci Baslat", use_container_width=True, type="primary", disabled=st.session_state.is_running)
        reset_btn = st.button("🔄 Sifirla", use_container_width=True, disabled=st.session_state.is_running)
        
        if reset_btn:
            st.session_state.coordinator = Coordinator()
            st.session_state.is_running = False
            st.session_state.is_done = False
            st.session_state.results = None
            st.rerun()
            
        st.divider()
        st.subheader("Ajan Takimi")
        st.markdown("""
        - 🗄️ **Arsiv Memuru:** SAP baglantisi
        - 🔧 **Veri Teknisyeni:** Temizleme
        - 🔍 **Mufettis:** Istatistik
        - 🎨 **Grafik Sihirbazi:** Raporlama
        """)
        
    # --- Ana Ekran: Ofis Simulasyonu ---
    st.header("Ofis Simulasyonu")
    
    col1, col2 = st.columns(2)
    
    # Ofisi cizme fonksiyonu (Ajanlarin durumlarina gore)
    def render_office():
        with col1:
            draw_agent("Arsiv Memuru", "🗄️", c.clerk.status, c.clerk.messages, "SAP'den personel verilerini ceker.")
            draw_agent("Mufettis", "🔍", c.inspector.status, c.inspector.messages, "Temiz verilerden istatistikler uretir.")
            
        with col2:
            draw_agent("Veri Teknisyeni", "🔧", c.tech.status, c.tech.messages, "Ham verileri temizler ve donusturur.")
            draw_agent("Grafik Sihirbazi", "🎨", c.wizard.status, c.wizard.messages, "Istatistikleri gorsellestirir.")

    # Eger butona basildiysa sureci animasyonlu olarak yurut
    if start_btn:
        st.session_state.is_running = True
        st.session_state.is_done = False
        
        # Streamlit'te gercek zamanli animasyon hissi vermek icin
        # ajanlari adim adim calistirip aralarda st.rerun kullanmak yerine
        # ekrani guncelleyebilen placeholder'lar kullaniyoruz.
        
        office_container = st.empty()
        with office_container.container():
            render_office()
            
        # 1. Arsiv Memuru
        time.sleep(1)
        c.clerk.status = "calisiyor"
        c.clerk.log("SAP OData servisine baglaniliyor...")
        with office_container.container(): render_office()
        time.sleep(1)
        
        raw_data = c.clerk.run()
        with office_container.container(): render_office()
        
        if c.clerk.status != "hata":
            # 2. Veri Teknisyeni
            time.sleep(1)
            c.tech.status = "calisiyor"
            c.tech.log(f"{len(raw_data)} kayit teslim alindi...")
            with office_container.container(): render_office()
            time.sleep(1)
            
            c.tech.set_data(raw_data)
            clean_data = c.tech.run()
            with office_container.container(): render_office()
            
            # 3. Mufettis
            time.sleep(1)
            c.inspector.status = "calisiyor"
            c.inspector.log("Temiz veriler istatistik motoruna yukleniyor...")
            with office_container.container(): render_office()
            time.sleep(1.5)
            
            c.inspector.set_data(clean_data)
            analysis_results = c.inspector.run()
            with office_container.container(): render_office()
            
            # 4. Grafik Sihirbazi
            time.sleep(1)
            c.wizard.status = "calisiyor"
            c.wizard.log("Tablolar gorsel grafiklere cevriliyor...")
            with office_container.container(): render_office()
            time.sleep(2)
            
            c.wizard.set_results(analysis_results)
            charts = c.wizard.run()
            with office_container.container(): render_office()
            
            st.session_state.results = {
                "charts": charts,
                "analysis": analysis_results
            }
            
        st.session_state.is_running = False
        st.session_state.is_done = True
        st.rerun()
        
    else:
        # Normal cizim (calismiyorken)
        render_office()

    # --- Rapor Paneli ---
    if st.session_state.is_done and st.session_state.results:
        st.divider()
        st.header("📊 Rapor Paneli")
        
        # Metin Ozetleri
        ozet = st.session_state.results["analysis"]["genel_ozet"]
        st.success(f"Analiz tamamlandi! Toplam **{ozet['toplam_kayit']}** kayit, **{ozet['toplam_personel']}** personel icin incelendi.")
        
        # Grafikleri goster
        charts = st.session_state.results["charts"]
        
        tab1, tab2, tab3 = st.tabs(["Personel Izinleri", "Lokasyon Dagilimi", "Proje Tipleri"])
        
        with tab1:
            if len(charts) > 0 and os.path.exists(charts[0]):
                st.image(charts[0], use_column_width=True)
        with tab2:
            if len(charts) > 1 and os.path.exists(charts[1]):
                st.image(charts[1], use_column_width=True)
        with tab3:
            if len(charts) > 2 and os.path.exists(charts[2]):
                st.image(charts[2], use_column_width=True)


if __name__ == "__main__":
    main()
