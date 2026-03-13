import streamlit as st
from groq import Groq

# 1. Sayfa Ayarları
st.set_page_config(page_title="@bi AI", page_icon="🤖", layout="wide")

# 2. Veritabanı Simülasyonu (Hafızada tutar, uygulama kapanınca sıfırlanır)
# Not: Gerçek kalıcı kayıt için ilerde burayı Google Sheets'e bağlayabiliriz.
if "users_db" not in st.session_state:
    st.session_state.users_db = {"atakan": "bi2026"} # Varsayılan admin

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
                st.success(f"Hoş geldin {login_user}!")
                st.rerun()
            else:
                st.error("Hatalı kullanıcı adı veya şifre.")

    with tab2:
        new_user = st.text_input("Yeni Kullanıcı Adı", key="r_user")
        new_pass = st.text_input("Yeni Şifre", type="password", key="r_pass")
        confirm_pass = st.text_input("Şifreyi Onayla", type="password", key="r_confirm")
        if st.button("Kayıt Ol"):
            if new_user in st.session_state.users_db:
                st.warning("Bu kullanıcı adı zaten alınmış.")
            elif new_pass != confirm_pass:
                st.error("Şifreler eşleşmiyor.")
            elif new_user and new_pass:
                st.session_state.users_db[new_user] = new_pass
                st.success("Kayıt başarılı! Şimdi Giriş Yap sekmesine gidebilirsin.")
            else:
                st.error("Lütfen tüm alanları doldur.")
    st.stop()

# --- GİRİŞ BAŞARILIYSA ---
user_name = st.session_state.user_name

# CSS Stil (Yeşil-Siyah Tema)
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
    if st.checkbox("İnsan olduğumu doğrula"):
        st.session_state.is_human = True
        st.rerun()
    st.stop()

# --- ANA SOHBET EKRANI ---
st.sidebar.header(f"👤 {user_name}")
if st.sidebar.button("Çıkış Yap"):
    st.session_state.authenticated = False
    st.session_state.is_human = False
    st.rerun()

st.title("🤖 @bi AI")
st.subheader(f"Hoş geldin {user_name}, seni dinliyorum.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mesaj Geçmişini Göster
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Groq Bağlantısı
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if prompt := st.chat_input("Mesajını buraya yaz..."):
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
