import streamlit as st
from groq import Groq
import time
import json
import os

# --- VERİ YÖNETİMİ (KALICILIK) ---
DB_FILE = "users_data.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {"Atakan": {"pass": "bi2026", "role": "admin", "messages": []}}

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

# Verileri dosyadan çek
if "users_db" not in st.session_state:
    st.session_state.users_db = load_data()

# 1. Sayfa Ayarları
st.set_page_config(page_title="@bi AI - Kalıcı Hafıza", page_icon="💾", layout="wide")

# 2. Oturum Yönetimi
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_name" not in st.session_state:
    st.session_state.user_name = None

# --- TASARIM CSS (Aynen Kalıyor) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    section[data-testid="stSidebar"] { background-color: #1a1c24; border-right: 2px solid #00ff00; }
    .premium-box { background: #1a1c24; border: 1px solid #00ff00; padding: 20px; border-radius: 15px; text-align: center; }
    h1, h2, h3 { color: #00ff00 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. Giriş Sistemi
if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align: center;'>🤖 @bi AI</h1>", unsafe_allow_html=True)
    tab_l, tab_r = st.tabs(["Giriş Yap", "Kayıt Ol"])
    
    with tab_l:
        u = st.text_input("Kullanıcı Adı", key="l_u")
        p = st.text_input("Şifre", type="password", key="l_p")
        if st.button("Sisteme Gir"):
            user_data = st.session_state.users_db.get(u)
            if user_data and user_data["pass"] == p:
                st.session_state.authenticated = True
                st.session_state.user_name = u
                # Mesajları kullanıcının kendi geçmişinden yükle
                st.session_state.messages = user_data.get("messages", [])
                st.rerun()
            else: st.error("Hatalı giriş!")
            
    with tab_r:
        nu = st.text_input("Yeni Kullanıcı", key="reg_u")
        np = st.text_input("Yeni Şifre", type="password", key="reg_p")
        if st.button("Hesap Oluştur"):
            if nu and np:
                if nu in st.session_state.users_db:
                    st.warning("Bu kullanıcı zaten var!")
                else:
                    st.session_state.users_db[nu] = {"pass": np, "role": "free", "messages": []}
                    save_data(st.session_state.users_db) # DOSYAYA KAYDET
                    st.success("Kayıt başarılı! Şimdi giriş yapabilirsin.")
    st.stop()

# --- GİRİŞ BAŞARILI ---
user_name = st.session_state.user_name
user_role = st.session_state.users_db[user_name]["role"]

# 4. SIDEBAR
with st.sidebar:
    st.title(f"👤 {user_name}")
    st.write(f"Paket: **{user_role.upper()}**")
    if st.button("💬 @bi AI Sohbet"): st.session_state.page = "Chat"; st.rerun()
    if st.button("💎 Paket Market"): st.session_state.page = "Premium"; st.rerun()
    if st.button("➕ Sohbeti Sıfırla"):
        st.session_state.users_db[user_name]["messages"] = []
        st.session_state.messages = []
        save_data(st.session_state.users_db)
        st.rerun()
    if st.button("🚪 Çıkış"): st.session_state.authenticated = False; st.rerun()

# 5. SAYFA YÖNETİMİ (MARKET VE ÖDEME)
if st.session_state.get("page") == "Premium":
    st.title("💎 Abonelik Market")
    col1, col2 = st.columns(2)
    # Örnek Paket Değişimi
    with col1:
        if st.button("Müzisyen Paketi Al (0 TL)"):
            st.session_state.users_db[user_name]["role"] = "müzisyen"
            save_data(st.session_state.users_db)
            st.rerun()

# --- CHAT SİSTEMİ (KALICI HAFIZALI) ---
else:
    st.title(f"🤖 @bi AI")
    
    # Geçmiş mesajları göster
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    if pr := st.chat_input("Yaz bakalım..."):
        # Kullanıcının mesajını ekle
        st.session_state.messages.append({"role": "user", "content": pr})
        with st.chat_message("user"): st.markdown(pr)
        
        sys_prompt = f"Sen @bi AI'sın. Yapımcın Atakan Türedi. Kullanıcı: {user_name}. Paket: {user_role}."
        full_m = [{"role": "system", "content": sys_prompt}] + st.session_state.messages
        
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=full_m)
        ans = res.choices[0].message.content
        
        # Yanıtı ekle ve VERİTABANINA (JSON) KAYDET
        st.session_state.messages.append({"role": "assistant", "content": ans})
        st.session_state.users_db[user_name]["messages"] = st.session_state.messages
        save_data(st.session_state.users_db)
        
        with st.chat_message("assistant"): st.markdown(ans)
