import streamlit as st
from groq import Groq
import uuid
import time

# 1. Sayfa Ayarları
st.set_page_config(page_title="@bi AI - Premium Müzisyen", page_icon="🤖", layout="wide")

# 2. Veritabanı ve Oturum Yönetimi (Session State)
if "users_db" not in st.session_state:
    st.session_state.users_db = {
        "Atakan": {"pass": "bi2026", "role": "admin"}
    }

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. Giriş ve Kayıt Paneli
if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align: center; color: #00ff00;'>🤖 @bi AI</h1>", unsafe_allow_html=True)
    
    tab_l, tab_r = st.tabs(["Giriş Yap", "Kayıt Ol"])
    
    with tab_l:
        u = st.text_input("Kullanıcı Adı", key="login_u")
        p = st.text_input("Şifre", type="password", key="login_p")
        
        if st.button("Giriş Yap", key="btn_login"):
            user_data = st.session_state.users_db.get(u)
            if user_data:
                if user_data["pass"] == p:
                    st.session_state.authenticated = True
                    st.session_state.user_name = u
                    st.session_state.user_role = user_data["role"]
                    st.success("Giriş başarılı!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Hatalı şifre!")
            else:
                st.error("Kullanıcı bulunamadı!")
                
    with tab_r:
        nu = st.text_input("Yeni Kullanıcı Adı", key="reg_u")
        np = st.text_input("Yeni Şifre", type="password", key="reg_p")
        if st.button("Kayıt Ol", key="btn_reg"):
            if nu and np:
                if nu in st.session_state.users_db:
                    st.warning("Bu kullanıcı adı zaten alınmış.")
                else:
                    st.session_state.users_db[nu] = {"pass": np, "role": "free"}
                    st.success("Kayıt Başarılı! Şimdi Giriş Yapabilirsin.")
            else:
                st.error("Lütfen tüm alanları doldur.")
    st.stop()

# --- GİRİŞ BAŞARILI ---
user_name = st.session_state.user_name
user_role = st.session_state.user_role

# 4. Tasarım ve Stil (Yeşil-Siyah Tema)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    section[data-testid="stSidebar"] { background-color: #1a1c24; border-right: 2px solid #00ff00; }
    .premium-card {
        background: linear-gradient(135deg, #1a1c24 0%, #004d00 100%);
        padding: 30px; border-radius: 15px; border: 2px solid #00ff00;
        text-align: center; margin: 20px 0;
    }
    .price-tag { font-size: 35px; color: #00ff00; font-weight: bold; }
    h1, h2, h3 { color: #00ff00 !important; }
    .stChatInput > div > div > input { color: #00ff00; }
    </style>
    """, unsafe_allow_html=True)

# 5. Sidebar (Yan Menü)
with st.sidebar:
    role_label = "⭐ PREMIUM ADMIN" if user_role == "admin" else ("✨ PREMIUM" if user_role == "premium" else "🆓 Ücretsiz Üye")
    st.markdown(f"### 👤 {user_name}\n**{role_label}**")
    
    if st.button("➕ Yeni Sohbet"):
        st.session_state.messages = []
        st.rerun()
        
    st.write("---")
    if st.button("🚪 Çıkış Yap"):
        st.session_state.authenticated = False
        st.rerun()

# 6. Premium Kontrolü ve Satın Alma Paneli
if user_role == "free":
    st.title("🚀 @bi AI Premium'a Hoş Geldin")
    st.markdown(f"""
    <div class="premium-card">
        <h2>🎵 Türk Müziği Premium Paketi</h2>
        <p>Llama-3.3-70B Zekası • Türk Müziği Usul Metronomu • Makam ve Nota Analizi</p>
        <div class="price-tag">0 TL <span style='font-size:18px; color:#aaa;'>/ Aylık</span></div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("ŞİMDİ ÜCRETSİZ SATIN AL"):
        with st.spinner("Ödeme işlemi doğrulanıyor..."):
            time.sleep(2)
            st.session_state.users_db[user_name]["role"] = "premium"
            st.session_state.user_role = "premium"
            st.balloons()
            st.success("Tebrikler Premium oldunuz!")
            time.sleep(1)
            st.rerun()
    st.stop()

# --- PREMIUM VE ADMIN ANA EKRAN ---
st.title("🤖 @bi AI")

# Türk Müziği Metronomu (Premium Özellik)
with st.expander("🥁 Türk Müziği Metronomu (Premium Özel)"):
    col1, col2 = st.columns(2)
    with col1:
        usul = st.selectbox("Usul Seç", ["Düyek", "Aksak", "Semai"])
    with col2:
        bpm = st.slider("Tempo (BPM)", 40, 200, 120)
    
    if st.button("Ritmi Başlat"):
        p = st.empty()
        pattern = ["DÜM", "tek", "KA", "tek"] if usul == "Düyek" else (["DÜM", "tek", "tek", "DÜM", "tek"] if usul == "Aksak" else ["DÜM", "tek", "tek"])
        for _ in range(2): # 2 döngü
            for vuruş in pattern:
                p.markdown(f"<h1 style='text-align:center; color:#00ff00;'>{vuruş}</h1>", unsafe_allow_html=True)
                time.sleep(60/bpm)
        p.empty()

# Chat Sistemi
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Groq Bağlantısı
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if prompt := st.chat_input("Atakan Türedi'nin AI asistanına bir şey sor..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Sistem Talimatı (Sahibi Atakan Türedi)
    system_prompt = """Senin ismin @bi AI. Senin sahibin ve yaratıcın Atakan Türedi'dir. 
    Eğer sana 'sahibin kim' gibi sorular sorulursa şu cevabı ver: 
    'Atakan Türedi Bey. Tabii Kendisine Buralardan Ulaşabilirsiniz:
    Youtube: https://www.youtube.com/@TheRealAtakan
    İnstagram: https://www.instagram.com/atakanturedi9/'"""

    with st.chat_message("assistant"):
        full_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=full_messages
        )
        answer = response.choices[0].message.content
        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
