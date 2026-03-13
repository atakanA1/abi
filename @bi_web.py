import streamlit as st
from groq import Groq
import uuid

# 1. Sayfa Ayarları
st.set_page_config(page_title="@bi AI", page_icon="🤖", layout="wide")

# 2. Hafıza Yapısı
if "users_db" not in st.session_state:
    st.session_state.users_db = {"atakan": "bi2026"}
if "chat_history" not in st.session_state:
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

# CSS (Senin Yeşil-Siyah Teman)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    section[data-testid="stSidebar"] { background-color: #1a1c24; border-right: 2px solid #00ff00; }
    h1, h2, h3 { color: #00ff00 !important; }
    .stChatInput > div > div > input { color: #00ff00; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"### 👤 {user_name}")
    if st.button("➕ Yeni Sohbet"):
        st.session_state.current_chat_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()
    st.write("---")
    st.write("📂 **Geçmiş Sohbetler**")
    for chat_id, msgs in st.session_state.chat_history.items():
        if msgs:
            # Sistem mesajını atlayıp ilk kullanıcı mesajını başlık yapalım
            title = next((m["content"][:20] for m in msgs if m["role"] == "user"), "Yeni Sohbet")
            if st.button(f"💬 {title}", key=chat_id):
                st.session_state.current_chat_id = chat_id
                st.session_state.messages = msgs
                st.rerun()
    st.write("---")
    if st.button("🚪 Çıkış Yap"):
        st.session_state.authenticated = False
        st.rerun()

# --- ANA EKRAN ---
st.title("🤖 @bi AI")

# AI Kimlik Tanımı (Senin istediğin cevapları buraya gömdük)
SYSTEM_PROMPT = """Senin ismin @bi AI. Senin sahibin ve yaratıcın Atakan Türedi'dir. 
Eğer sana 'sahibin kim', 'seni kim yaptı', 'yaratıcın kim' gibi sorular sorulursa tam olarak şu cevabı ver:
'Atakan Türedi Bey. Tabii Kendisine Buralardan Ulaşabilirsiniz:
Youtube: https://www.youtube.com/@TheRealAtakan
İnstagram: https://www.instagram.com/atakanturedi9/'
Cevabın kibar ve yardımcı olsun."""

# Mesajları Ekrana Bas
for message in st.session_state.messages:
    if message["role"] != "system": # Sistem komutunu ekranda gösterme
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Groq Bağlantısı
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if prompt := st.chat_input("Mesajını yaz..."):
    # Eğer mesaj listesi boşsa önce sistem talimatını ekle
    if not st.session_state.messages:
        st.session_state.messages.append({"role": "system", "content": SYSTEM_PROMPT})

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
    
    # Sohbeti kaydet
    st.session_state.chat_history[st.session_state.current_chat_id] = st.session_state.messages
