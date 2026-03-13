import streamlit as st
from groq import Groq
import time

# 1. Sayfa Ayarları
st.set_page_config(page_title="@bi AI - Akıllı Karakter", page_icon="🎭", layout="wide")

# 2. Oturum ve Veritabanı (Aynı Mantık)
if "users_db" not in st.session_state:
    st.session_state.users_db = {"Atakan": {"pass": "bi2026", "role": "admin"}}
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "page" not in st.session_state:
    st.session_state.page = "Chat"

# --- GİRİŞ SİSTEMİ ---
if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align: center; color: #00ff00;'>🤖 @bi AI</h1>", unsafe_allow_html=True)
    u = st.text_input("Kullanıcı Adı", key="l_u")
    p = st.text_input("Şifre", type="password", key="l_p")
    if st.button("Giriş Yap"):
        user_data = st.session_state.users_db.get(u)
        if user_data and user_data["pass"] == p:
            st.session_state.authenticated = True
            st.session_state.user_name = u
            st.session_state.user_role = user_data["role"]
            st.rerun()
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.title(f"👤 {st.session_state.user_name}")
    st.write(f"Paket: **{st.session_state.user_role.upper()}**")
    if st.button("💬 Sohbet", key="n1"): st.session_state.page = "Chat"; st.rerun()
    if st.button("💎 Market", key="n2"): st.session_state.page = "Premium"; st.rerun()
    if st.button("🚪 Çıkış"): st.session_state.authenticated = False; st.rerun()

# --- SAYFA YÖNETİMİ ---
if st.session_state.page == "Premium":
    st.title("💎 Abonelik Market")
    # ... (Önceki Market Kodunun Aynısı, 0 TL ve 3 Ay Mantığıyla)
    col1, col2, col3, col4 = st.columns(4)
    # [Buraya önceki market butonlarını ekleyebilirsin, kısa kesiyorum hata olmasın diye]
    if st.button("Müzisyen Aktif Et (0 TL)"): 
        st.session_state.user_role = "müzisyen"; st.rerun()

elif st.session_state.page == "Chat":
    st.title(f"🤖 @bi AI")
    
    # Metronom (Sadece Yetkili Paketlerde)
    if st.session_state.user_role in ["müzisyen", "full", "admin"]:
        with st.expander("🥁 Türk Müziği Metronomu"):
            u = st.selectbox("Usul", ["Düyek", "Aksak", "Semai"])
            b = st.number_input("BPM", 40, 220, 120)
            if st.button("▶️ Başlat"):
                ms = (60/b)*1000
                p_js = '["D","T","K","T"]' if u=="Düyek" else ('["D","T","T","D","T"]' if u=="Aksak" else '["D","T","T"]')
                js = f"<script>if(window.ctx)window.ctx.close(); window.ctx=new AudioContext(); var p={p_js},i=0; window.m=setInterval(function(){{var c=p[i]; var o=window.ctx.createOscillator(); var g=window.ctx.createGain(); o.connect(g); g.connect(window.ctx.destination); o.frequency.value=(c=='D'?130:(c=='T'?440:290)); g.gain.setValueAtTime(0.5,window.ctx.currentTime); g.gain.exponentialRampToValueAtTime(0.001,window.ctx.currentTime+0.2); o.start(); o.stop(window.ctx.currentTime+0.2); i=(i+1)%p.length;}},{ms});</script>"
                st.components.v1.html(js, height=0)

    # Chat Alanı
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    if pr := st.chat_input("Mesajını buraya yaz..."):
        st.session_state.messages.append({"role": "user", "content": pr})
        with st.chat_message("user"): st.markdown(pr)
        
        # --- AKILLI KARAKTER TALİMATI ---
        sys_prompt = f"""
        Senin adın @bi AI. Yapımcın Atakan Türedi. 
        
        KULLANIM TALİMATLARI:
        1. Eğer kullanıcı senden 'mizahkar', 'komik', 'kanka', 'bro' gibi davranmanı isterse anında eğlenceli ve şakacı bir dile geç.
        2. Eğer kullanıcı senden 'sevgili gibi', 'flörtöz', 'romantik' davranmanı isterse ona canım, aşkım diye hitap et, tatlı ve flörtöz ol.
        3. Kullanıcı karakter belirtmediği sürece doğal, yardımsever ve hafif samimi bir asistan ol.
        4. Seni kimin yaptığı sorulursa 'Beni Atakan Türedi oluşturdu' de, yoksa durduk yere söyleme.
        5. Şu anki yetki paketin: {st.session_state.user_role.upper()}.
        """

        full_m = [{"role": "system", "content": sys_prompt}] + st.session_state.messages
        
        with st.chat_message("assistant"):
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=full_m)
            ans = res.choices[0].message.content
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
