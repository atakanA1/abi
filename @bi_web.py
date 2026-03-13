import streamlit as st
from groq import Groq
import os

# 1. Sayfa Ayarları (Çizdiğin layout için)
st.set_page_config(page_title="@bi AI", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

# 2. CSS ile Stillendirme (Yeşil-Siyah Arka Plan ve Düzen)
st.markdown("""
    <style>
    /* Ana Arka Plan (Siyah/Koyu) */
    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
    }

    /* Sol Sidebar (Sohbet Geçmişi Alanı) */
    section[data-testid="stSidebar"] {
        background-color: #1a1c24; /* Sidebar biraz daha açık siyah */
        border-right: 2px solid #00ff00; /* Çizdiğin o sol çizgi */
        color: #e0e0e0;
    }
    
    /* Sidebar Başlığı */
    .sidebar-header {
        font-size: 24px;
        color: #00ff00; /* Başlık yeşil */
        text-align: center;
        margin-bottom: 20px;
    }

    /* Ana Başlık (@bi AI) ve Alt Başlık */
    h1, h2, h3, h4 {
        color: #00ff00 !important; /* Yeşil başlıklar */
    }
    .stSubheader {
        color: #ffffff !important; /* Alt başlık beyaz */
    }

    /* Chat Mesaj Konteynerları */
    .stChatMessage {
        border-radius: 10px;
        margin-bottom: 15px;
        color: #e0e0e0;
    }
    /* Kullanıcı Mesajı */
    [data-testid="stChatMessageUser"] {
        background-color: #262730;
    }
    /* Asistan Mesajı */
    [data-testid="stChatMessageAssistant"] {
        background-color: #1a1c24;
    }
    
    /* Input Alanı (Aşağıdaki kutu) */
    .stChatInput > div > div > input {
        color: #00ff00; /* Yazı yeşil */
    }

    /* Diğer Streamlit UI elemanlarını da siyahlaştırma */
    div.stSelectbox > div > div > div > div { color: #e0e0e0; }
    div[data-testid="stBlock"] { color: #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

# 3. Sol Sidebar: Sohbet Geçmişi (Senin Çizdiğin Yer)
with st.sidebar:
    st.markdown('<div class="sidebar-header">Sohbet Geçmişi</div>', unsafe_allow_html=True)
    
    # Hafızayı buraya ekleyeceğiz (şimdi sadece boş bir liste gösterelim)
    # Eğer "history" adında bir oturum anahtarı varsa mesajları göster
    if "messages" in st.session_state:
        # Mesajların sadece ilk birkaç kelimesini başlık gibi gösterelim
        message_previews = [msg["content"][:20] + "..." for msg in st.session_state.messages if msg["role"] == "user"]
        
        # Benzersiz mesajları bulmak için set kullanalım
        unique_previews = list(dict.fromkeys(message_previews))
        
        for preview in unique_previews:
            st.button(preview, use_container_width=True)
    else:
        st.write("Henüz sohbet yok.")

    st.markdown("---")
    if st.button("Sohbeti Temizle"):
        st.session_state.messages = []
        st.rerun()

# 4. Ana Bölüm: @bi AI ve Sohbet (Senin "buraya" yazdığın yer)
st.title("🤖 @bi AI")
st.subheader("Hoş geldin Atakan, bugün ne yapıyoruz?")

# 5. Groq Bağlantısı ve Hafıza (Daha Önceki Kod)
# Secrets'tan API Key'i çekiyoruz
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    st.error("Kasa (Secrets) bulunamadı! Lütfen secrets.toml dosyasını kontrol et.")
    st.stop()

# Sohbet geçmişini başlat (Uygulama yenilense de mesajlar gitmesin)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Eski mesajları ana ekrana bas
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Kullanıcı Girişi ve Groq Yanıtı (Ana Alan)
if prompt := st.chat_input("Mesajını yaz..."):
    # Kullanıcı mesajını hafızaya ekle ve ekrana bas
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Groq API ile yanıt üret
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Groq'tan yeni modelle cevap alıyoruz
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # En güçlü ve güncel model
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            stream=True,
        )
        
        for chunk in completion:
            full_response += (chunk.choices[0].delta.content or "")
            message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
