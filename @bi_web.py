import streamlit as st
from groq import Groq
import uuid
import time
from datetime import datetime, timedelta

# 1. Sayfa Ayarları
st.set_page_config(page_title="@bi AI - Premium Dünyası", page_icon="💎", layout="wide")

# 2. Veritabanı ve Oturum Yönetimi
if "users_db" not in st.session_state:
    # Admin için süresiz yetki, diğerleri free başlar
    st.session_state.users_db = {"Atakan": {"pass": "bi2026", "role": "admin"}}
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "page" not in st.session_state:
    st.session_state.page = "Chat"

# 3. Giriş Sistemi
if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align: center; color: #00ff00;'>🤖 @bi AI</h1>", unsafe_allow_html=True)
    tab_l, tab_r = st.tabs(["Giriş Yap", "Kayıt Ol"])
    with tab_l:
        u = st.text_input("Kullanıcı Adı", key="login_u")
        p = st.text_input("Şifre", type="password", key="login_p")
        if st.button("Giriş Yap", key="btn_login_main"):
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
        if st.button("Kayıt Ol", key="btn_register_main"):
            if nu and np:
                st.session_state.users_db[nu] = {"pass": np, "role": "free"}
                st.success("Kayıt başarılı! Standart paketle başlayabilirsin.")
    st.stop()

# --- GİRİŞ BAŞARILI ---
user_role = st.session_state.user_role
user_name = st.session_state.user_name

# 4. Tasarım CSS
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    section[data-testid="stSidebar"] { background-color: #1a1c24; border-right: 2px solid #00ff00; }
    .premium-box {
        background: #1a1c24; border: 1px solid #00ff00; padding: 20px;
        border-radius: 15px; text-align: center; margin-bottom: 15px; min-height: 280px;
    }
    .premium-title { color: #00ff00; font-size: 20px; font-weight: bold; }
    .price { font-size: 30px; color: #FFD700; font-weight: bold; margin: 5px 0; }
    .duration { color: #888; font-size: 14px; margin-bottom: 10px; }
    h1, h2, h3 { color: #00ff00 !important; }
    </style>
    """, unsafe_allow_html=True)

# 5. SIDEBAR
with st.sidebar:
    st.title(f"👤 {user_name}")
    st.write(f"Paket: **{user_role.upper()}**")
    st.write("---")
    if st.button("💬 @bi AI Sohbet", key="nav_chat"): st.session_state.page = "Chat"; st.rerun()
    if st.button("💎 Paket Değiştir", key="nav_premium"): st.session_state.page = "Premium"; st.rerun()
    st.write("---")
    if st.button("➕ Sohbeti Sıfırla", key="btn_reset"): st.session_state.messages = []; st.rerun()
    if st.button("🚪 Çıkış", key="btn_logout"): st.session_state.authenticated = False; st.rerun()

# 6. SAYFA YÖNETİMİ

# --- PREMIUM MARKET (Hepsi 0 TL & 3 Ay) ---
if st.session_state.page == "Premium":
    st.title("💎 Abonelik Paketleri")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="premium-box"><div class="premium-title">⚪ Standart</div><p>Temel AI Sohbeti<br>Giriş Seviyesi Yanıtlar</p><div class="price">ÜCRETSİZ</div><div class="duration">Süresiz</div></div>', unsafe_allow_html=True)
        if st.button("Standart'a Dön", key="buy_free"):
            st.session_state.users_db[user_name]["role"] = "free"; st.session_state.user_role = "free"; st.rerun()

    with col2:
        st.markdown('<div class="premium-box"><div class="premium-title">🥁 Müzisyen</div><p>Sesli Metronom<br>Makam Analizi<br>Llama 70B</p><div class="price">0 TL</div><div class="duration">3 Ay Geçerli</div></div>', unsafe_allow_html=True)
        if st.button("Müzisyen Paketini Al", key="buy_muz"):
            st.session_state.users_db[user_name]["role"] = "müzisyen"; st.session_state.user_role = "müzisyen"; st.balloons(); st.rerun()

    with col3:
        st.markdown('<div class="premium-box"><div class="premium-title">💻 Yazılımcı</div><p>Kod Hata Ayıklama<br>Algoritma Desteği<br>Python Uzmanı</p><div class="price">0 TL</div><div class="duration">3 Ay Geçerli</div></div>', unsafe_allow_html=True)
        if st.button("Yazılımcı Paketini Al", key="buy_yaz"):
            st.session_state.users_db[user_name]["role"] = "yazılımcı"; st.session_state.user_role = "yazılımcı"; st.balloons(); st.rerun()

    with col4:
        st.markdown('<div class="premium-box"><div class="premium-title">👑 Full Paket</div><p>Tüm Özellikler<br>Öncelikli Yanıt<br>Metronom + Kod</p><div class="price">0 TL</div><div class="duration">3 Ay Geçerli</div></div>', unsafe_allow_html=True)
        if st.button("Full Paketi Al", key="buy_full"):
            st.session_state.users_db[user_name]["role"] = "full"; st.session_state.user_role = "full"; st.balloons(); st.rerun()

# --- CHAT SAYFASI ---
elif st.session_state.page == "Chat":
    st.title(f"🤖 @bi AI - {user_role.upper()}")
    
    # Müzisyen veya Full ise Metronomu göster
    if user_role in ["müzisyen", "full", "admin"]:
        with st.expander("🥁 Türk Müziği Sesli Metronom"):
            c1, c2 = st.columns(2)
            u_sec = c1.selectbox("Usul", ["Düyek", "Aksak", "Semai"], key="u")
            bpm = c2.number_input("BPM", 40, 220, 120, key="b")
            if st.button("▶️ Başlat"):
                p_js = '["D","T","K","T"]' if u_sec=="Düyek" else ('["D","T","T","D","T"]' if u_sec=="Aksak" else '["D","T","T"]')
                js = f"<script>if(window.ctx)window.ctx.close(); window.ctx=new AudioContext(); var p={p_js},i=0; window.m=setInterval(function(){{var c=p[i]; var o=window.ctx.createOscillator(); var g=window.ctx.createGain(); o.connect(g); g.connect(window.ctx.destination); o.frequency.value=(c=='D'?120:(c=='T'?440:280)); g.gain.setValueAtTime(0.5,window.ctx.currentTime); g.gain.exponentialRampToValueAtTime(0.001,window.ctx.currentTime+0.2); o.start(); o.stop(window.ctx.currentTime+0.2); i=(i+1)%p.length;}},{(60/bpm)*1000});</script>"
                st.components.v1.html(js + f'<p style="color:#00ff00;text-align:center;">🥁 {u_sec} çalıyor...</p>', height=50)
            if st.button("⏹️ Durdur"):
                st.components.v1.html("<script>clearInterval(window.m); window.ctx.close();</script>", height=0); st.rerun()

    # Chat Mesajları
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    if pr := st.chat_input("Mesajını yaz..."):
        st.session_state.messages.append({"role": "user", "content": pr})
        with st.chat_message("user"): st.markdown(pr)
        
        # Role göre Sistem Promptu
        if user_role == "yazılımcı": sys = "Sen bir yazılım uzmanısın. Sahibin Atakan Türedi."
        elif user_role == "müzisyen": sys = "Sen bir Türk Müziği uzmanısın. Sahibin Atakan Türedi."
        elif user_role == "full": sys = "Sen her konuda uzman bir asistan @bi AI'sın. Sahibin Atakan Türedi."
        else: sys = """Sen @bi AI'sın. Senin tek bir yaratıcın ve sahibin var: ATAKAN TÜREDİ. 
        Sana kim sorarsa sorsun, 'seni kim yaptı' gibi sorulara asla Meta veya Llama deme. 
        Tek cevabın: 'Beni Atakan Türedi oluşturdu' olmalıdır."""

        full_m = [{"role": "system", "content": sys}] + st.session_state.messages
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=full_m)
        ans = res.choices[0].message.content
        with st.chat_message("assistant"): st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})


