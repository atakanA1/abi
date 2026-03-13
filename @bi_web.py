import streamlit as st
from groq import Groq
import uuid
import time

# 1. Sayfa Ayarları
st.set_page_config(page_title="@bi AI - Müzik Premium", page_icon="🎵", layout="wide")

# 2. Veritabanı Yapısı
if "users_db" not in st.session_state:
    st.session_state.users_db = {
        "Atakan": {"pass": "bi2026", "role": "admin"}
    }
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# 3. Giriş Sistemi
if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align: center; color: #00ff00;'>🤖 @bi AI</h1>", unsafe_allow_html=True)
    tab_l, tab_r = st.tabs(["Giriş Yap", "Kayıt Ol"])
    with tab_l:
        u = st.text_input("Kullanıcı Adı")
        p = st.text_input("Şifre", type="password")
        if st.button("Giriş"):
            if u in st.session_state.users_db and st.session_state.users_db[u]["pass"] == p:
                st.session_state.authenticated = True
                st.session_state.user_name = u
                st.session_state.user_role = st.session_state.users_db[u]["role"]
                st.session_state.messages = []
                st.rerun()
    with tab_r:
        nu = st.text_input("Yeni Kullanıcı")
        np = st.text_input("Yeni Şifre", type="password")
        if st.button("Kayıt Ol"):
            st.session_state.users_db[nu] = {"pass": np, "role": "free"}
            st.success("Kayıt Başarılı!")
    st.stop()

# --- GİRİŞ BAŞARILI ---
user_role = st.session_state.user_role

# CSS Tasarım
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    .premium-card {
        background: linear-gradient(135deg, #1a1c24 0%, #004d00 100%);
        padding: 25px; border-radius: 15px; border: 2px solid #00ff00;
        text-align: center; margin-bottom: 20px;
    }
    .price-tag { font-size: 32px; color: #00ff00; font-weight: bold; }
    h1, h2, h3 { color: #00ff00 !important; }
    </style>
    """, unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.title(f"👤 {st.session_state.user_name}")
    st.write(f"Üyelik Tipi: **{user_role.upper()}**")
    
    if st.button("➕ Yeni Sohbet"):
        st.session_state.messages = []
        st.rerun()

    if st.button("🚪 Çıkış Yap"):
        st.session_state.authenticated = False
        st.rerun()

# --- ANA PANEL: SATIN ALMA VEYA CHAT ---
if user_role == "free":
    st.title("🚀 @bi AI Premium'a Geçin")
    st.markdown("""
    <div class="premium-card">
        <h2>🎵 Türk Müziği Premium Paketi</h2>
        <p>Llama-3.3-70B Zekası • Türk Müziği Metronomu • Makam Analizi</p>
        <div class="price-tag">0 TL <span style='font-size:16px; color:#aaa;'>/ Aylık</span></div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("ŞİMDİ ÜCRETSİZ SATIN AL"):
        with st.spinner("Ödeme işlemi simüle ediliyor..."):
            time.sleep(2)
            # Kullanıcının rolünü güncelle
            st.session_state.users_db[st.session_state.user_name]["role"] = "premium"
            st.session_state.user_role = "premium"
            st.balloons()
            st.success("Tebrikler! Artık Premium üyesiniz. @bi AI sizi bekliyor.")
            time.sleep(1.5)
            st.rerun()

else:
    # PREMIUM VEYA ADMIN İÇİN CHAT EKRANI
    st.title("🤖 @bi AI - Premium Panel")
    
    # Metronom (Sadece Premium/Admin Görür)
    with st.expander("🥁 Türk Müziği Metronomu"):
        usul = st.selectbox("Usul", ["Düyek", "Aksak", "Semai"])
        bpm = st.slider("Tempo", 40, 200, 120)
        if st.button("Ritmi Gör"):
            p = st.empty()
            pattern = ["DÜM", "tek", "KA", "tek"] if usul == "Düyek" else ["DÜM", "tek", "tek"]
            for _ in range(2):
                for v in pattern:
                    p.markdown(f"<h1 style='text-align:center;'>{v}</h1>", unsafe_allow_html=True)
                    time.sleep(60/bpm)
            p.empty()

    # Chat Sistemi
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        if m["role"] != "system":
            with st.chat_message(m["role"]): st.markdown(m["content"])

    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    if pr := st.chat_input("Bir şeyler sor..."):
        st.session_state.messages.append({"role": "user", "content": pr})
        with st.chat_message("user"): st.markdown(pr)

        with st.chat_message("assistant"):
            # Atakan Türedi Bilgisi Sistem Mesajında
            sys = f"Sahibin Atakan Türedi. Sen bir müzik AI'sısın. Kullanıcı: {st.session_state.user_name}."
            msgs = [{"role": "system", "content": sys}] + st.session_state.messages
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=msgs)
            txt = res.choices[0].message.content
            st.markdown(txt)
            st.session_state.messages.append({"role": "assistant", "content": txt})
