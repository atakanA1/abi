import streamlit as st
from groq import Groq
from streamlit_google_auth import Authenticate
import json

# 1. Sayfa Ayarları
st.set_page_config(page_title="@bi AI", page_icon="🤖", layout="wide")

# 2. CSS Stil (Yeşil-Siyah Tema)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    section[data-testid="stSidebar"] { background-color: #1a1c24; border-right: 2px solid #00ff00; }
    .sidebar-header { font-size: 24px; color: #00ff00; text-align: center; margin-bottom: 20px; }
    h1, h2, h3, h4 { color: #00ff00 !important; }
    .stChatInput > div > div > input { color: #00ff00; }
    </style>
    """, unsafe_allow_html=True)

# 3. Google Giriş Sistemi (Kasadaki veriyi kullanır)
# --- 3. Google Giriş Sistemi (Yeni Kütüphane Versiyonuna Uygun) ---
try:
    if "GOOGLE_JSON_DOSYASI" not in st.secrets:
        st.error("Kasa hatası: GOOGLE_JSON_DOSYASI bulunamadı!")
        st.stop()
        
    google_secrets_dict = json.loads(st.secrets["GOOGLE_JSON_DOSYASI"])
    
    # 'secret_path' hatasını çözmek için parametre ismini kaldırıp direkt veriyi veriyoruz
    authenticator = Authenticate(
        google_secrets_dict, # Direkt veriyi gönderiyoruz, isim yazmıyoruz
        cookie_name='bi_session',
        cookie_key='atakan_ozel_anahtar_99',
        redirect_uri="https://yapay-abi.streamlit.app",
    )
    authenticator.check_authenticator()
except Exception as e:
    # Eğer yukarıdaki de yemezse (bazı versiyonlarda config_data ister)
    try:
        authenticator = Authenticate(
            config_data=google_secrets_dict, 
            cookie_name='bi_session',
            cookie_key='atakan_ozel_anahtar_99',
            redirect_uri="https://yapay-abi.streamlit.app",
        )
        authenticator.check_authenticator()
    except Exception as e2:
        st.error(f"Sistem başlatılamadı (Kütüphane Hatası): {e2}")
        st.stop()

# Giriş Yapılmamışsa
if not st.session_state.get('connected'):
    st.title("🤖 @bi AI")
    st.warning("Lütfen devam etmek için Google hesabınızla giriş yapın.")
    authenticator.login()
    st.stop()

# Giriş Yapıldıysa
user_info = st.session_state.get('user_info', {})
user_name = user_info.get('name', 'Atakan')

# --- BOT KONTROLÜ ---
if "is_human" not in st.session_state:
    st.session_state.is_human = False

if not st.session_state.is_human:
    st.title(f"Selam {user_name}! 👋")
    if st.checkbox("Ben bir bot değilim."):
        st.session_state.is_human = True
        st.rerun()
    st.stop()

# --- ANA SOHBET EKRANI ---
with st.sidebar:
    st.markdown(f'<div class="sidebar-header">{user_name}</div>', unsafe_allow_html=True)
    if st.button("Çıkış Yap"):
        authenticator.logout()
        st.rerun()

st.title("🤖 @bi AI")
st.subheader(f"Hoş geldin {user_name}, bugün ne yapıyoruz?")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Eski mesajları bas
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

