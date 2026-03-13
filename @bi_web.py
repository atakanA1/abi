import streamlit as st
from groq import Groq

# 1. Sayfa Ayarları
st.set_page_config(page_title="@bi AI", page_icon="🤖", layout="wide")

# 2. CSS Stil (Yeşil-Siyah Tema)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    section[data-testid="stSidebar"] { background-color: #1a1c24; border-right: 2px solid #00ff00; }
    h1, h2, h3 { color: #00ff00 !important; }
    .stChatInput > div > div > input { color: #00ff00; }
    </style>
    """, unsafe_allow_html=True)

# 3. Basit ve Güvenli Giriş Sistemi (Kütüphanesiz)
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🤖 @bi AI Giriş")
    # Atakan, buraya kendine özel bir şifre koyabilirsin
    password = st.text_input("Giriş Şifresi", type="password")
    if st.button("Giriş Yap"):
        if password == "bi2026": # Şifreni buradan değiştir
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Hatalı şifre!")
    st.stop()

# --- GİRİŞ BAŞARILIYSA ---
user_name = "Atakan" # Şimdilik sabit, sonra Google'dan çekeriz

# Bot Kontrolü
if "is_human" not in st.session_state:
    st.session_state.is_human = False

if not st.session_state.is_human:
    st.title(f"Selam {user_name}! 👋")
    if st.checkbox("Ben bir bot değilim."):
        st.session_state.is_human = True
        st.rerun()
    st.stop()

# Ana Sohbet Ekranı
st.title("🤖 @bi AI")
with st.sidebar:
    st.header(f"👤 {user_name}")
    if st.button("Çıkış Yap"):
        st.session_state.authenticated = False
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Groq Bağlantısı
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
