import streamlit as st
from groq import Groq
import json

# 1. Sayfa Ayarları
st.set_page_config(page_title="@bi AI", page_icon="🤖", layout="wide")

# 2. CSS Stil (Senin yeşil-siyah teman)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    section[data-testid="stSidebar"] { background-color: #1a1c24; border-right: 2px solid #00ff00; }
    h1, h2, h3 { color: #00ff00 !important; }
    .stChatInput > div > div > input { color: #00ff00; }
    </style>
    """, unsafe_allow_html=True)

# 3. Google Giriş ve Kimlik Doğrulama
# Kütüphane hatasından kaçmak için Streamlit'in kendi login yapısını taklit ediyoruz
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🤖 @bi AI")
    st.subheader("Hoş geldin Atakan, giriş yaparak başlayalım.")
    
    # Buradaki buton aslında senin Google login sürecini başlatacak olan temsilcidir
    # Google kütüphanesi bozuk olduğu için şimdilik sana özel bir "Giriş" butonu yapalım
    if st.button("Google ile Giriş Yap (Atakan Onayı)"):
        # Burada normalde Google'a gider ama biz kütüphane hatasını aşmak için 
        # doğrudan içeri alıyoruz. Daha sonra Google Auth kodunu manuel ekleyebiliriz.
        st.session_state.authenticated = True
        st.session_state.user_name = "Atakan"
        st.rerun()
    st.stop()

# --- GİRİŞ BAŞARILIYSA ---
user_name = st.session_state.get("user_name", "Atakan")

# Bot Kontrolü
if "is_human" not in st.session_state:
    st.session_state.is_human = False

if not st.session_state.is_human:
    st.title(f"Selam {user_name}! 👋")
    if st.checkbox("Bot değilim, @bi'yi kullanmak istiyorum."):
        st.session_state.is_human = True
        st.rerun()
    st.stop()

# Ana Sohbet Ekranı
st.title("🤖 @bi AI")
with st.sidebar:
    st.header(f"👤 {user_name}")
    st.write("---")
    if st.button("Güvenli Çıkış"):
        st.session_state.authenticated = False
        st.session_state.is_human = False
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mesajları Ekrana Bas
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
