import streamlit as st
from groq import Groq
import uuid # Her sohbet için benzersiz ID oluşturmak için

# 1. Sayfa Ayarları
st.set_page_config(page_title="@bi AI", page_icon="🤖", layout="wide")

# 2. Kalıcı Veritabanı Yapısı (Session State üzerinde)
if "users_db" not in st.session_state:
    st.session_state.users_db = {"atakan": "bi2026"}

if "chat_history" not in st.session_state:
    # Tüm sohbetleri burada saklayacağız: { 'sohbet_id': [mesajlar] }
    st.session_state.chat_history = {}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# 3. Giriş / Kayıt Ekranı
if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align: center; color: #00ff00;'>🤖 @bi AI</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])
    
    with tab1:
        login_user = st.text_input("Kullanıcı Adı", key="l_user")
        login_pass = st.text_input("Şifre", type="password", key="l_pass")
        if st.button("Giriş"):
            if login_user in st.session_state.users_db and st.session_state.users_db[login_user] == login_pass:
                st.session_state.authenticated = True
                st.session_state.user_name = login_user
                # GİRİŞ ANINDA: Mevcut mesajları sıfırla (Sıfır sayfa aç)
                st.session_state.current_chat_id = str(uuid.uuid4())
                st.session_state.messages = []
                st.rerun()
            else:
                st.error("Hatalı kullanıcı adı veya şifre.")
    with tab2:
        new_user = st.text_input("Yeni Kullanıcı Adı", key="r_user")
        new_pass = st.text_input("Yeni Şifre", type="password", key="r_pass")
        if st.button("Kayıt Ol"):
            if new_user and new_pass:
                st.session_state.users_db[new_user] = new_pass
                st.success("Kayıt başarılı! Giriş yapabilirsin.")
    st.stop()

# --- GİRİŞ BAŞARILIYSA ---
user_name = st.session_state.user_name

# CSS Stil (Yeşil-Siyah Tema)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    section[data-testid="stSidebar"] { background-color: #1a1c24; border-right: 2px solid #00ff00; padding-top: 20px; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #262730; color: #00ff00; border: 1px solid #333; }
    .stChatInput > div > div > input { color: #00ff00; }
    h1, h2, h3 { color: #00ff00 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- SOL SIDEBAR: Geçmiş Sohbetler ---
with st.sidebar:
    st.markdown(f"### 👤 {user_name}")
    if st.button("➕ Yeni Sohbet Başlat"):
        st.session_state.current_chat_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()
    
    st.write("---")
    st.write("📂 **Geçmiş Sohbetler**")
    
    # Kayıtlı sohbetleri listele
    for chat_id, msgs in st.session_state.chat_history.items():
        if msgs: # Eğer sohbet boş değilse
            first_msg = msgs[0]["content"][:20] + "..."
            if st.button(first_msg, key=chat_id):
                st.session_state.current_chat_id = chat_id
                st.session_state.messages = msgs
                st.rerun()
    
    st.write("---")
    if st.button("🚪 Çıkış Yap"):
        st.session_state.authenticated = False
        st.rerun()

# --- ANA EKRAN ---
st.title("🤖 @bi AI")

# Mesajları ekrana bas
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Groq Bağlantısı
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if prompt := st.chat_input("Mesajını yaz..."):
    # Mesajı mevcut listeye ekle
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
    
    # Sohbeti "Kalıcı Geçmişe" kaydet
    st.session_state.chat_history[st.session_state.current_chat_id] = st.session_state.messages
