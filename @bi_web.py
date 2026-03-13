import streamlit as st
from groq import Groq
import uuid
import time

# 1. Sayfa Ayarları
st.set_page_config(page_title="@bi AI - Premium Dünyası", page_icon="💎", layout="wide")

# 2. Veritabanı ve Oturum Yönetimi
if "users_db" not in st.session_state:
    st.session_state.users_db = {"Atakan": {"pass": "bi2026", "role": "admin"}}
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "page" not in st.session_state:
    st.session_state.page = "Chat" # Varsayılan sayfa

# 3. Giriş Sistemi
if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align: center; color: #00ff00;'>🤖 @bi AI</h1>", unsafe_allow_html=True)
    tab_l, tab_r = st.tabs(["Giriş Yap", "Kayıt Ol"])
    with tab_l:
        u = st.text_input("Kullanıcı Adı", key="login_u")
        p = st.text_input("Şifre", type="password", key="login_p")
        if st.button("Giriş Yap"):
            user_data = st.session_state.users_db.get(u)
            if user_data and user_data["pass"] == p:
                st.session_state.authenticated = True
                st.session_state.user_name = u
                st.session_state.user_role = user_data["role"]
                st.rerun()
            else: st.error("Hatalı giriş!")
    with tab_r:
        nu = st.text_input("Yeni Kullanıcı", key="reg_u")
        np = st.text_input("Yeni Şifre", type="password", key="reg_p")
        if st.button("Kayıt Ol"):
            if nu and np:
                st.session_state.users_db[nu] = {"pass": np, "role": "free"}
                st.success("Kayıt başarılı!")
    st.stop()

# --- GİRİŞ BAŞARILI ---
user_role = st.session_state.user_role

# 4. Tasarım CSS
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    section[data-testid="stSidebar"] { background-color: #1a1c24; border-right: 2px solid #00ff00; }
    .premium-box {
        background: #1a1c24; border: 1px solid #00ff00; padding: 20px;
        border-radius: 15px; text-align: center; margin-bottom: 15px;
    }
    .premium-title { color: #00ff00; font-size: 22px; font-weight: bold; }
    .price { font-size: 28px; color: #FFD700; }
    h1, h2, h3 { color: #00ff00 !important; }
    </style>
    """, unsafe_allow_html=True)

# 5. SIDEBAR (Sayfa Navigasyonu)
with st.sidebar:
    st.title(f"👤 {st.session_state.user_name}")
    st.write(f"Rütbe: **{user_role.upper()}**")
    st.write("---")
    
    # Menü Seçenekleri
    if st.button("💬 @bi AI Sohbet"):
        st.session_state.page = "Chat"
        st.rerun()
    
    if st.button("💎 Premium Paketler"):
        st.session_state.page = "Premium"
        st.rerun()
        
    st.write("---")
    if st.button("➕ Sohbeti Temizle"):
        st.session_state.messages = []
        st.rerun()
    if st.button("🚪 Çıkış"):
        st.session_state.authenticated = False
        st.rerun()

# 6. SAYFA YÖNETİMİ

# --- PREMİUM SAYFASI ---
if st.session_state.page == "Premium":
    st.title("💎 Premium Paketler")
    st.subheader("İhtiyacına en uygun @bi AI gücünü seç.")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""<div class="premium-box">
            <div class="premium-title">🎵 Müzisyen Paketi</div>
            <p>Sesli Metronom • Makam Analizi • Llama 70B</p>
            <div class="price">0 TL</div></div>""", unsafe_allow_html=True)
        if st.button("Müzik Premium Al", key="p1"):
            st.session_state.users_db[st.session_state.user_name]["role"] = "premium"
            st.session_state.user_role = "premium"
            st.balloons(); st.rerun()

    with col2:
        st.markdown("""<div class="premium-box">
            <div class="premium-title">💻 Yazılımcı Paketi</div>
            <p>Gelişmiş Kod Analizi • Python Uzmanı • Limitsiz Mesaj</p>
            <div class="price">Yakında</div></div>""", unsafe_allow_html=True)
        st.button("Beklemede...", key="p2", disabled=True)

    with col3:
        st.markdown("""<div class="premium-box">
            <div class="premium-title">👑 Full Paket</div>
            <p>Tüm Özellikler • Özel Destek • Atakan Türedi Onayı</p>
            <div class="price">Yakında</div></div>""", unsafe_allow_html=True)
        st.button("Beklemede...", key="p3", disabled=True)

# --- CHAT SAYFASI ---
elif st.session_state.page == "Chat":
    if user_role == "free":
        st.warning("⚠️ Sohbet etmek için lütfen 'Premium Paketler' sayfasından bir paket seçin!")
    else:
        st.title("🤖 @bi AI")
        
        # Sesli Metronom (Müzik Premium özelliği)
        with st.expander("🥁 Türk Müziği Sesli Metronom"):
            bpm = st.number_input("BPM", 40, 220, 120)
            if st.button("▶️ Başlat"):
                ms = (60/bpm)*1000
                js = f"<script>if(window.m)clearInterval(window.m); var d=new Audio('https://www.soundjay.com/buttons/sounds/button-2.mp3'); var t=new Audio('https://www.soundjay.com/buttons/sounds/button-3.mp3'); var p=['D','T','K','T']; var i=0; window.m=setInterval(function(){{if(p[i]=='D')d.play();else t.play(); i=(i+1)%p.length;}},{ms});</script>"
                st.components.v1.html(js, height=0)
            if st.button("⏹️ Durdur"):
                st.components.v1.html("<script>clearInterval(window.m);</script>", height=0)

        # Chat
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        if pr := st.chat_input("Atakan Türedi'nin AI asistanına yaz..."):
            st.session_state.messages.append({"role": "user", "content": pr})
            with st.chat_message("user"): st.markdown(pr)
            
            sys = "Sahibin Atakan Türedi. Sen bir müzik ve teknoloji AI'sısın."
            full_m = [{"role": "system", "content": sys}] + st.session_state.messages
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=full_m)
            ans = res.choices[0].message.content
            with st.chat_message("assistant"): st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
