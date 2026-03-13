import streamlit as st
from groq import Groq
from streamlit_google_auth import Authenticate
import json

# 1. Sayfa Ayarları
st.set_page_config(page_title="@bi AI", page_icon="🤖", layout="wide")

# 2. Google Giriş Sistemi (Yeni Versiyon Uyumluluk Modu)
if "GOOGLE_JSON_DOSYASI" not in st.secrets:
    st.error("Secrets: GOOGLE_JSON_DOSYASI bulunamadı!")
    st.stop()

google_secrets = json.loads(st.secrets["GOOGLE_JSON_DOSYASI"])

# Kütüphanenin en güncel hali genellikle login() çağrıldığında kontrol yapar
authenticator = Authenticate(
    secret_path=google_secrets, 
    cookie_name='bi_session',
    cookie_key='atakan_bi_key',
    redirect_uri="https://yapay-abi.streamlit.app",
)

# Eski check_authenticator yerine doğrudan login durumunu kontrol ediyoruz
if not st.session_state.get('connected'):
    st.title("🤖 @bi AI")
    # Login butonu kullanıcıyı Google'a yönlendirir
    authenticator.login()
    st.stop()

# --- GİRİŞ BAŞARILIYSA BURADAN DEVAM EDER ---
user_info = st.session_state.get('user_info', {})
user_name = user_info.get('name', 'Atakan')

# CSS (Yeşil-Siyah Tema)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    section[data-testid="stSidebar"] { background-color: #1a1c24; border-right: 2px solid #00ff00; }
    h1, h2, h3 { color: #00ff00 !important; }
    .stChatInput > div > div > input { color: #00ff00; }
    </style>
    """, unsafe_allow_html=True)

# Bot Kontrolü
if "is_human" not in st.session_state:
    st.session_state.is_human = False

if not st.session_state.is_human:
    st.title(f"Selam {user_name}! 👋")
    if st.checkbox("Ben bir bot değilim."):
        st.session_state.is_human = True
        st.rerun()
    st.stop()

# Sidebar ve Çıkış
with st.sidebar:
    st.header(f"👤 {user_name}")
    if st.button("Çıkış Yap"):
        st.session_state.connected = False
        st.rerun()

# Ana Sohbet Ekranı
st.title("🤖 @bi AI")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if prompt := st.chat_input("Mesajını yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
        )
        msg = response.choices[0].message.content
        st.markdown(msg)
        st.session_state.messages.append({"role": "assistant", "content": msg})
