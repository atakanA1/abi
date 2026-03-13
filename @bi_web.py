import streamlit as st
from streamlit_google_auth import Authenticate
from groq import Groq
import os

# --- AYARLAR ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="@bi AI", page_icon="🟢", layout="wide")

# --- TASARIM (Dumanlı Yeşil Tema) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    h1 { color: #128c7e !important; text-align: center; font-size: 60px !important; font-family: 'Segoe UI'; }
    .stChatMessage { border-radius: 15px; border: 1px solid #128c7e33; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- GOOGLE AUTH SİSTEMİ ---
# Not: client_secrets.json dosyanın içinde 'web' tipi istemci olmalı.
authenticator = Authenticate(
    secret_path='client_secrets.json',
    cookie_name='abi_session',
    cookie_key='abi_guclu_anahtar',
    cookie_expiry_days=1,
    redirect_uri="http://localhost:8501",
)

# Giriş Kontrolü
authenticator.check_authenticator()

if not st.session_state.get('connected'):
    st.title("@bi")
    st.write("<p style='text-align:center;'>Devam etmek için Google hesabınla kimliğini doğrula.</p>", unsafe_allow_html=True)
    authenticator.login()
else:
    # Giriş Başarılı - Verileri Çek
    user_info = st.session_state.get('user_info')
    user_name = user_info.get('given_name', 'Atakan')
    
    with st.sidebar:
        st.image(user_info.get('picture', ''), width=100)
        st.write(f"**Hoş geldin, {user_name}!**")
        if st.button("Çıkış Yap"):
            authenticator.logout()
            st.rerun()

    st.title("@bi")

    # Sohbet Geçmişi Başlat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mesajları Ekrana Bas
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Kullanıcı Girişi
    if prompt := st.chat_input("Mesajını buraya yaz..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # ÖZEL CEVAPLAR (ATAKAN FİLTRESİ)
        p_lower = prompt.lower()
        if any(t in p_lower for t in ["seni kim yarattı", "kim kurdu", "yapımcın kim"]):
            full_response = "Beni Atakan Türedi Bey yarattı ve kurdu.\n\n📸 Instagram: https://www.instagram.com/atakanturedi9/\n🎥 YouTube: https://www.youtube.com/@TheRealAtakan"
        elif any(t in p_lower for t in ["en sevdiğin öğretmen", "en sevdiği öğretmen"]):
            full_response = f"{user_name}, senin en sevdiğin öğretmen tabii ki Fuat Lafçı!"
        else:
            # GROQ AI CEVABI
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": f"Sen ABi'sin. Kullanıcın {user_name}. Yapımcın Atakan Türedi."},
                        {"role": "user", "content": prompt}
                    ]
                )
                full_response = response.choices[0].message.content
            except:
                full_response = "Bağlantıda bir sorun var Atakan Bey."

        with st.chat_message("assistant"):
            st.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})