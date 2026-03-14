import streamlit as st
from groq import Groq
import time
import json
import os

# --- 1. VERİ YÖNETİMİ (JSON DATABASE) ---
DB_FILE = "bi_ai_ultimate_db.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}
    return {"Atakan": {"pass": "bi2026", "role": "admin", "chats": {}}}

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

if "db" not in st.session_state:
    st.session_state.db = load_db()

# --- 2. TASARIM VE CSS ---
st.set_page_config(page_title="@bi AI - Kayıtlı & Hafızalı", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    section[data-testid="stSidebar"] { background-color: #1a1c24; border-right: 2px solid #00ff00; }
    h1, h2, h3 { color: #00ff00 !important; }
    .stButton>button { border-radius: 10px; border: 1px solid #00ff00; background: transparent; color: #00ff00; width: 100%; }
    .stButton>button:hover { background: #00ff00; color: #0e1117; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. GİRİŞ VE KAYIT SİSTEMİ (BURASI GELDİ!) ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>🤖 @bi AI Dünyası</h1>", unsafe_allow_html=True)
    tab_login, tab_reg = st.tabs(["Giriş Yap", "Kayıt Ol"])
    
    with tab_login:
        u = st.text_input("Kullanıcı Adı", key="login_u")
        p = st.text_input("Şifre", type="password", key="login_p")
        if st.button("Giriş", key="btn_login"):
            if u in st.session_state.db and st.session_state.db[u]["pass"] == p:
                st.session_state.auth = True
                st.session_state.user = u
                st.rerun()
            else: st.error("Kullanıcı bulunamadı veya şifre yanlış!")
            
    with tab_reg:
        nu = st.text_input("Yeni Kullanıcı Adı", key="reg_u")
        np = st.text_input("Yeni Şifre", type="password", key="reg_p")
        if st.button("Kayıt Ol ve Başla", key="btn_reg"):
            if nu and np:
                if nu in st.session_state.db:
                    st.warning("Bu kullanıcı zaten mevcut!")
                else:
                    st.session_state.db[nu] = {"pass": np, "role": "free", "chats": {}}
                    save_db(st.session_state.db)
                    st.success("Kaydın yapıldı Atakan'ın asistanına hoş geldin! Şimdi giriş yap.")
            else: st.error("Lütfen alanları doldur!")
    st.stop()

# --- 4. SOL MENÜ (GEÇMİŞ SOHBETLER) ---
user = st.session_state.user
user_data = st.session_state.db[user]

with st.sidebar:
    st.title(f"👤 {user}")
    st.write(f"Paket: **{user_data['role'].upper()}**")
    
    if st.button("➕ Yeni Sohbet", key="new_chat"):
        chat_id = str(int(time.time()))
        st.session_state.db[user]["chats"][chat_id] = {"title": "Yeni Sohbet", "messages": []}
        st.session_state.active_chat = chat_id
        save_db(st.session_state.db)
        st.rerun()
    
    st.write("---")
    st.subheader("📜 Sohbet Geçmişin")
    
    chats = st.session_state.db[user]["chats"]
    for cid in sorted(chats.keys(), reverse=True):
        title = chats[cid]["title"]
        if st.button(f"💬 {title[:20]}", key=f"btn_{cid}"):
            st.session_state.active_chat = cid
            st.rerun()
            
    st.write("---")
    if st.button("🚪 Çıkış Yap"):
        st.session_state.auth = False
        st.rerun()

# --- 5. ANA EKRAN (SOHBET ALANI) ---
if "active_chat" not in st.session_state:
    st.info("Sohbet etmek için sol taraftan bir geçmiş seç veya 'Yeni Sohbet' başlat!")
else:
    cid = st.session_state.active_chat
    active_chat_data = st.session_state.db[user]["chats"][cid]
    
    st.title(f"💬 {active_chat_data['title']}")
    
    # Eski Mesajları Listele
    for m in active_chat_data["messages"]:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # Yeni Mesaj Girişi
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    if prompt := st.chat_input("Mesajını buraya bırak..."):
        # 1. Kullanıcı mesajını kaydet
        st.session_state.db[user]["chats"][cid]["messages"].append({"role": "user", "content": prompt})
        
        # 2. Eğer ilk mesajsa başlığı güncelle
        if active_chat_data["title"] == "Yeni Sohbet":
            st.session_state.db[user]["chats"][cid]["title"] = prompt[:20] + "..."
            
        with st.chat_message("user"):
            st.markdown(prompt)

        # 3. AI Yanıtı (Akıllı Karakterli)
        sys_msg = f"""Sen @bi AI'sın. Yapımcın Atakan Türedi. 
        Sana kim sorarsa sorsun 'Beni Atakan Türedi oluşturdu' de. 
        Karakterin kullanıcının mesajına göre değişir: Kankaysa mizahkar, flört ediyorsa sevgili gibi davran.
        Mevcut kullanıcı: {user}."""
        
        history = [{"role": "system", "content": sys_msg}] + st.session_state.db[user]["chats"][cid]["messages"]
        
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=history)
        ans = res.choices[0].message.content
        
        # 4. Yanıtı Kaydet ve Göster
        st.session_state.db[user]["chats"][cid]["messages"].append({"role": "assistant", "content": ans})
        save_db(st.session_state.db)
        
        with st.chat_message("assistant"):
            st.markdown(ans)
