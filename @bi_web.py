import streamlit as st
from groq import Groq
from streamlit_google_auth import Authenticate
import json

# 1. Sayfa Ayarları
st.set_page_config(page_title="@bi AI", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

# 2. Google Giriş Sistemi (Kasadaki veriyi kullanır)
try:
    # Secrets'tan JSON metnini alıp sözlüğe çeviriyoruz
    google_secrets_dict = json.loads(st.secrets["GOOGLE_JSON_DOSYASI"])
    
    authenticator = Authenticate(
        secret_path=google_secrets_dict, 
        cookie_name='bi_session',
        cookie_key='atakan_bi_key_123', # Buraya rastgele bir metin yazabilirsin
        redirect_uri="https://senin-uygulaman.streamlit.app", # Burayı kendi url'nle güncelle!
    )
except Exception as e:
    st.error("Google yapılandırması Secrets içinde bulunamadı!")
    st.stop()

# Giriş Kontrolü
authenticator.check_authenticator()

# 3. CSS ile Stillendirme (Senin yeşil-siyah teman)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    section[data-testid="stSidebar"] { background-color: #1a1c24; border-right: 2px solid #00ff00; }
    .sidebar-header { font-size: 24px; color: #00ff00; text-align: center; margin-bottom: 20px; }
    h1, h2, h3, h4 { color: #00ff00 !important; }
    .stSubheader { color: #ffffff !important; }
    .stChatInput > div > div > input { color: #00ff00; }
    </style>
    """, unsafe_allow_html=True)

# --- GİRİŞ YAPILMAMIŞSA EKRANI ---
if not st.session_state.get('connected'):
    st.title("🤖 @bi AI")
    st.warning("Devam etmek için lütfen Google ile giriş yapın.")
    authenticator.login()
    st.stop()

# --- GİRİŞ YAPILDIYSA BİLGİLERİ AL ---
user_info = st.session_state.get('user_info', {})
user_name = user_info.get('name', 'Atakan')

# --- BOT KONTROLÜ ---
if "is_human" not in st.session_state:
    st.session_state.is_human = False

if not st.session_state.is_human:
    st.title(f"Selam {user_name}! 👋")
    st.subheader("Uygulamaya girmeden önce minik bir onay:")
    if st.checkbox("Ben bir bot değilim, Atakan'ın arkadaşıyım/kullanıcıyım."):
        st.session_state.is_human = True
        st.rerun()
    st.stop()

# --- ANA UYGULAMA (Sohbet Ekranı) ---

# Sol Sidebar: Sohbet Geçmişi
with st.sidebar:
    st.markdown(f'<div class="sidebar-header">{user_name}</div>', unsafe_allow_html=True)
    st.write("---")
    
    if "messages" in st.session_state:
        message_previews = [msg["content"][:20] + "..." for msg in st.session_state.messages if msg["role"] == "user"]
        for preview in list(dict.fromkeys(message_previews)):
            st.button(preview, use_container_width=True)
    
    st.write("---")
    if st.button("Çıkış Yap"):
        authenticator.logout()
        st.rerun()

# Ana Ekran
st.title("🤖 @bi AI")
st.subheader(f"Hoş geldin {user_name}, bugün ne üzerine kafa yoralım?")

# Groq Bağlantısı
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

# Eski mesajları bas
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Sohbet Girişi
if prompt := st.chat_input("Buraya yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            stream=True,
        )
        
        for chunk in completion:
            full_response += (chunk.choices[0].delta.content or "")
            message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
