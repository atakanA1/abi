import streamlit as st
from groq import Groq
import time
import json
import os

# --- 1. VERİ YÖNETİMİ (DOSYA TABANLI VERİTABANI) ---
DB_FILE = "bi_database.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"Atakan": {"pass": "bi2026", "role": "admin", "messages": []}}
    return {"Atakan": {"pass": "bi2026", "role": "admin", "messages": []}}

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

# Uygulama başladığında veritabanını yükle
if "users_db" not in st.session_state:
    st.session_state.users_db = load_db()

# --- 2. SAYFA AYARLARI VE TASARIM ---
st.set_page_config(page_title="@bi AI - Hafızalı Sistem", page_icon="💾", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    section[data-testid="stSidebar"] { background-color: #1a1c24; border-right: 2px solid #00ff00; }
    h1, h2, h3 { color: #00ff00 !important; }
    .stChatMessage { border-radius: 10px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. GİRİŞ SİSTEMİ ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🤖 @bi AI Giriş")
    t1, t2 = st.tabs(["Giriş", "Kayıt"])
    
    with t1:
        u = st.text_input("Kullanıcı", key="l_u")
        p = st.text_input("Şifre", type="password", key="l_p")
        if st.button("Giriş Yap"):
            user_data = st.session_state.users_db.get(u)
            if user_data and user_data["pass"] == p:
                st.session_state.authenticated = True
                st.session_state.user_name = u
                st.session_state.user_role = user_data["role"]
                # KRİTİK NOKTA: Geçmiş mesajları JSON'dan çekip Session'a yükle
                st.session_state.messages = user_data.get("messages", [])
                st.rerun()
            else: st.error("Hatalı bilgi!")
            
    with t2:
        nu = st.text_input("Yeni Kullanıcı", key="r_u")
        np = st.text_input("Yeni Şifre", type="password", key="r_p")
        if st.button("Kayıt Ol"):
            if nu and np:
                if nu in st.session_state.users_db: st.warning("Bu isim alınmış!")
                else:
                    st.session_state.users_db[nu] = {"pass": np, "role": "free", "messages": []}
                    save_db(st.session_state.users_db)
                    st.success("Kaydedildi! Giriş yapabilirsin.")
    st.stop()

# --- 4. SIDEBAR VE NAVİGASYON ---
u_name = st.session_state.user_name
u_role = st.session_state.users_db[u_name]["role"]

with st.sidebar:
    st.title(f"👤 {u_name}")
    st.write(f"Paket: **{u_role.upper()}**")
    page = st.radio("Menü", ["Sohbet", "Market"])
    st.write("---")
    if st.button("➕ Sohbeti Sıfırla"):
        st.session_state.messages = []
        st.session_state.users_db[u_name]["messages"] = []
        save_db(st.session_state.users_db)
        st.rerun()
    if st.button("🚪 Çıkış"):
        st.session_state.authenticated = False
        st.rerun()

# --- 5. MARKET SAYFASI ---
if page == "Market":
    st.title("💎 Paket Market")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Müzisyen Paketini Al"):
            st.session_state.users_db[u_name]["role"] = "müzisyen"
            save_db(st.session_state.users_db)
            st.success("Müzisyen paketi tanımlandı!")
            time.sleep(1); st.rerun()

# --- 6. CHAT SAYFASI (ASIL HAFIZA BURADA) ---
else:
    st.title("🤖 @bi AI Sohbet")
    
    # EKRANA ESKİ MESAJLARI BAS
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    
    if prompt := st.chat_input("Mesajını yaz..."):
        # 1. Kullanıcı mesajını ekle ve göster
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 2. AI Yanıtını Oluştur
        sys_msg = f"Sen @bi AI'sın. Yapımcın Atakan Türedi. Kullanıcı: {u_name}. Karakterin kullanıcının tavrına göre (flörtöz, mizahkar vb.) değişir."
        full_history = [{"role": "system", "content": sys_msg}] + st.session_state.messages
        
        try:
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=full_history)
            ans = res.choices[0].message.content
            
            # 3. Yanıtı ekle ve göster
            st.session_state.messages.append({"role": "assistant", "content": ans})
            with st.chat_message("assistant"):
                st.markdown(ans)
            
            # 4. KRİTİK NOKTA: Güncel mesaj listesini JSON veritabanına yaz
            st.session_state.users_db[u_name]["messages"] = st.session_state.messages
            save_db(st.session_state.users_db)
            
        except Exception as e:
            st.error("Bir sorun oluştu Atakan'a haber ver!")
