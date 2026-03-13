import streamlit as st
from groq import Groq
import time

# 1. Sayfa Ayarları
st.set_page_config(page_title="@bi AI - Özgür Paketler", page_icon="🤖", layout="wide")

# 2. Oturum Yönetimi
if "users_db" not in st.session_state:
    st.session_state.users_db = {"Atakan": {"pass": "bi2026", "role": "admin"}}
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "page" not in st.session_state:
    st.session_state.page = "Chat"
if "temp_package" not in st.session_state:
    st.session_state.temp_package = None

# 3. Giriş Sistemi
if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align: center; color: #00ff00;'>🤖 @bi AI</h1>", unsafe_allow_html=True)
    tab_l, tab_r = st.tabs(["Giriş Yap", "Kayıt Ol"])
    with tab_l:
        u = st.text_input("Kullanıcı Adı", key="l_u")
        p = st.text_input("Şifre", type="password", key="l_p")
        if st.button("Giriş Yap", key="btn_login"):
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
        if st.button("Kayıt Ol", key="btn_reg"):
            if nu and np:
                # Yeni kayıt olanlar direkt FREE paketle başlar
                st.session_state.users_db[nu] = {"pass": np, "role": "free"}
                st.success("Kayıt başarılı! Free paketle giriş yapabilirsin.")
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
        border-radius: 15px; text-align: center; margin-bottom: 15px; min-height: 250px;
    }
    .free-box {
        background: #1a1c24; border: 1px solid #888888; padding: 20px;
        border-radius: 15px; text-align: center; margin-bottom: 15px; min-height: 250px;
    }
    .premium-title { color: #00ff00; font-size: 20px; font-weight: bold; }
    .price { font-size: 28px; color: #FFD700; font-weight: bold; }
    h1, h2, h3 { color: #00ff00 !important; }
    </style>
    """, unsafe_allow_html=True)

# 5. SIDEBAR
with st.sidebar:
    st.title(f"👤 {user_name}")
    st.write(f"Mevcut Paket: **{user_role.upper()}**")
    st.write("---")
    if st.button("💬 @bi AI Sohbet", key="nav_c"): st.session_state.page = "Chat"; st.rerun()
    if st.button("💎 Paket Değiştir", key="nav_p"): st.session_state.page = "Premium"; st.rerun()
    st.write("---")
    if st.button("➕ Sohbeti Sıfırla"): st.session_state.messages = []; st.rerun()
    if st.button("🚪 Çıkış"): st.session_state.authenticated = False; st.rerun()

# 6. SAYFA YÖNETİMİ

# --- PREMIUM MARKET ---
if st.session_state.page == "Premium":
    st.title("💎 Abonelik Market")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="free-box"><div style="color:#888; font-weight:bold; font-size:20px;">Standart (Free)</div><p>Temel Özellikler<br>Süresiz Kullanım</p><div class="price">0 TL</div></div>', unsafe_allow_html=True)
        if st.button("Free'ye Geç", key="buy_free"):
            st.session_state.users_db[user_name]["role"] = "free"
            st.session_state.user_role = "free"
            st.rerun()

    with col2:
        st.markdown('<div class="premium-box"><div class="premium-title">🎵 Müzisyen</div><p>Metronom + Makam Analizi</p><div class="price">0 TL</div></div>', unsafe_allow_html=True)
        if st.button("Müzisyen Aktif Et", key="buy_muz"):
            st.session_state.temp_package = "Müzisyen"; st.session_state.page = "Checkout"; st.rerun()

    with col3:
        st.markdown('<div class="premium-box"><div class="premium-title">💻 Yazılımcı</div><p>Hata Ayıklama + Kod Desteği</p><div class="price">0 TL</div></div>', unsafe_allow_html=True)
        if st.button("Yazılımcı Aktif Et", key="buy_yaz"):
            st.session_state.temp_package = "Yazılımcı"; st.session_state.page = "Checkout"; st.rerun()

    with col4:
        st.markdown('<div class="premium-box"><div class="premium-title">👑 Full Paket</div><p>Tüm Premium Yetenekler</p><div class="price">0 TL</div></div>', unsafe_allow_html=True)
        if st.button("Full Paket Aktif Et", key="buy_full"):
            st.session_state.temp_package = "Full Paket"; st.session_state.page = "Checkout"; st.rerun()

# --- ÖDEME EKRANI ---
elif st.session_state.page == "Checkout":
    st.title("💳 Banka Kartı Onayı")
    pkg = st.session_state.temp_package
    with st.form("pay"):
        st.write(f"### {pkg} Paketi (3 Ay)")
        st.text_input("Kart Numarası", placeholder="0000 0000 0000 0000")
        c1, c2 = st.columns(2)
        c1.text_input("SKT (AA/YY)")
        c2.text_input("CVV", type="password")
        if st.form_submit_button("ONAYLA VE AKTİF ET"):
            with st.spinner("Onaylanıyor..."):
                time.sleep(1.5)
                st.session_state.users_db[user_name]["role"] = pkg.lower()
                st.session_state.user_role = pkg.lower()
                st.balloons(); st.session_state.page = "Chat"; st.rerun()

# --- CHAT SİSTEMİ ---
elif st.session_state.page == "Chat":
    st.title(f"🤖 @bi AI - {user_role.upper()}")
    
    # Metronom (Sadece Premiumlarda)
    if user_role in ["müzisyen", "full", "admin"]:
        with st.expander("🥁 Türk Müziği Metronomu"):
            u = st.selectbox("Usul", ["Düyek", "Aksak", "Semai"], key="u_sel")
            b = st.number_input("BPM", 40, 220, 120, key="b_num")
            if st.button("▶️ Başlat"):
                ms = (60/b)*1000
                p_js = '["D","T","K","T"]' if u=="Düyek" else ('["D","T","T","D","T"]' if u=="Aksak" else '["D","T","T"]')
                js = f"<script>if(window.ctx)window.ctx.close(); window.ctx=new AudioContext(); var p={p_js},i=0; window.m=setInterval(function(){{var c=p[i]; var o=window.ctx.createOscillator(); var g=window.ctx.createGain(); o.connect(g); g.connect(window.ctx.destination); o.frequency.value=(c=='D'?130:(c=='T'?440:290)); g.gain.setValueAtTime(0.5,window.ctx.currentTime); g.gain.exponentialRampToValueAtTime(0.001,window.ctx.currentTime+0.2); o.start(); o.stop(window.ctx.currentTime+0.2); i=(i+1)%p.length;}},{ms});</script>"
                st.components.v1.html(js + f'<p style="color:#00ff00;text-align:center;">🥁 {u} çalıyor...</p>', height=50)
            if st.button("⏹️ Durdur"):
                st.components.v1.html("<script>clearInterval(window.m); window.ctx.close();</script>", height=0); st.rerun()

    # Mood Slider
    st.write("---")
    mood = st.select_slider("🤖 @bi AI Karakteri:", options=["Resmi", "Mizahkar", "Flörtöz/Sevgili"], value="Mizahkar")

    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    if pr := st.chat_input("Yaz bakalım..."):
        st.session_state.messages.append({"role": "user", "content": pr})
        with st.chat_message("user"): st.markdown(pr)
        
        id_msg = "Sen @bi AI'sın. Yapımcın Atakan Türedi. Sadece sorulursa ondan bahset."
        mood_msg = "Sevgili gibi flörtöz ol." if mood == "Flörtöz/Sevgili" else ("Esprili ve samimi ol." if mood == "Mizahkar" else "Resmi ol.")
        sys = f"{id_msg} {mood_msg} Yetkin: {user_role.upper()}."

        full_m = [{"role": "system", "content": sys}] + st.session_state.messages
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=full_m)
        ans = res.choices[0].message.content
        with st.chat_message("assistant"): st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
