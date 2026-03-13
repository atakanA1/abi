import streamlit as st
from groq import Groq
import uuid
import time

# 1. Sayfa Ayarları
st.set_page_config(page_title="@bi AI - Müzik Premium", page_icon="🎵", layout="wide")

# 2. Veritabanı Yapısı (Session State)
if "users_db" not in st.session_state:
    # Varsayılan Admin ve birkaç test kullanıcısı
    st.session_state.users_db = {
        "Atakan": {"pass": "bi2026", "role": "admin"}
    }

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# 3. Giriş / Kayıt Ekranı
if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align: center; color: #00ff00;'>🤖 @bi AI</h1>", unsafe_allow_html=True)
    
    tab_l, tab_r = st.tabs(["Giriş Yap", "Kayıt Ol"])
    
    with tab_l:
        u = st.text_input("Kullanıcı Adı", key="login_u")
        p = st.text_input("Şifre", type="password", key="login_p")
        if st.button("Giriş Yap", key="login_btn"):
            # Hata veren kısım düzeltildi: Önce kullanıcı var mı diye bak, sonra şifreyi kontrol et
            if u in st.session_state.users_db:
                if st.session_state.users_db[u]["pass"] == p:
                    st.session_state.authenticated = True
                    st.session_state.user_name = u
                    st.session_state.user_role = st.session_state.users_db[u]["role"]
                    st.session_state.messages = []
                    st.success("Giriş başarılı!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Hatalı şifre!")
            else:
                st.error("Kullanıcı bulunamadı!")
                
    with tab_r:
        nu = st.text_input("Yeni Kullanıcı Adı", key="reg_u")
        np = st.text_input("Yeni Şifre", type="password", key="reg_p")
        if st.button("Kayıt Ol", key="reg_btn"):
            if nu and np:
                if nu in st.session_state.users_db:
                    st.warning("Bu kullanıcı zaten mevcut.")
                else:
                    st.session_state.users_db[nu] = {"pass": np, "role": "free"}
                    st.success("Kayıt Başarılı! Şimdi giriş yapabilirsin.")
            else:
                st.error("Lütfen alanları doldurun.")
    st.stop()

# --- GİRİŞ BAŞARILI (Buradan sonrası aynı mantık) ---
user_role = st.session_state.user_role
user_name = st.session_state.user_name

# Tasarım CSS
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
    st.title(f"👤 {user_name}")
    st.write(f"Üyelik: **{user_role.upper()}**")
    if st.button("🚪 Çıkış Yap"):
        st.session_state.authenticated = False
        st.rerun()

# --- PREMIUM KONTROL VE CHAT ---
if user_role == "free":
    st.title("🚀 Premium'a Yükselt")
    st.markdown("""
    <div class="premium-card">
        <h2>🎵 Türk Müziği Premium</h2>
        <p>Llama-3.3-70B • Usul Metronomu • Makam Analizi</p>
        <div class="price-tag">0 TL</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("ŞİMDİ ÜCRETSİZ AL"):
        with st.spinner("İşleniyor..."):
            time.sleep(1)
            st.session_state.users_db[user_name]["role"] = "premium"
            st.session_state.user_role = "premium"
            st.balloons()
            st.rerun()
else:
    # CHAT VE METRONOM KISMI
    st.title("🤖 @bi AI")
    
    # Metronom
    with st.expander("🥁 Türk Müziği Metronomu"):
        u_sec = st.selectbox("Usul", ["Düyek", "Aksak", "Semai"])
        if st.button("Vur"):
            st.write(f"{u_sec} usulü vuruşları simüle ediliyor...")

    # Mesajlaşma
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    if pr := st.chat_input("Mesajını yaz..."):
        st.session_state.messages.append({"role": "user", "content": pr})
        with st.chat_message("user"): st.markdown(pr)
        
        # Sistem promptu (Atakan Bey'e selamlar)
        sys = "Sahibin Atakan Türedi. Türk müziği ve genel konularda uzmansın."
        msgs = [{"role": "system", "content": sys}] + st.session_state.messages
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=msgs)
        ans = res.choices[0].message.content
        with st.chat_message("assistant"): st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
