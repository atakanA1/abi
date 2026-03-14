import streamlit as st
from groq import Groq
import time
import json
import os
from datetime import datetime

# --- 1. VERİ YÖNETİMİ ---
DB_FILE = "bi_database_v2.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}
    return {}

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

if "db" not in st.session_state:
    st.session_state.db = load_db()

# --- 2. TASARIM ---
st.set_page_config(page_title="@bi AI - Geçmiş Hafızalı", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    section[data-testid="stSidebar"] { background-color: #1a1c24; border-right: 2px solid #00ff00; width: 300px !important; }
    .chat-history-item { 
        padding: 10px; border-radius: 5px; margin-bottom: 5px; 
        background: #262730; cursor: pointer; border: 1px solid #333;
    }
    .chat-history-item:hover { border-color: #00ff00; }
    h1, h2, h3 { color: #00ff00 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. GİRİŞ KONTROLÜ ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🤖 @bi AI")
    u = st.text_input("Kullanıcı")
    p = st.text_input("Şifre", type="password")
    if st.button("Giriş"):
        if u == "Atakan" and p == "bi2026": # Basit tuttum, db'den çekebilirsin
            st.session_state.auth = True
            st.session_state.user = u
            st.rerun()
    st.stop()

# --- 4. SOL MENÜ (SIDEBAR) - GEÇMİŞ BURADA ---
user = st.session_state.user
if user not in st.session_state.db:
    st.session_state.db[user] = {"chats": {}}

with st.sidebar:
    st.title(f"👤 {user}")
    
    if st.button("➕ Yeni Sohbet Başlat", use_container_width=True):
        chat_id = str(int(time.time()))
        st.session_state.db[user]["chats"][chat_id] = {"title": "Yeni Sohbet", "messages": []}
        st.session_state.active_chat = chat_id
        save_db(st.session_state.db)
        st.rerun()
    
    st.write("---")
    st.subheader("📜 Geçmiş Sohbetler")
    
    # Geçmiş Sohbetleri Listele
    user_chats = st.session_state.db[user]["chats"]
    for cid in sorted(user_chats.keys(), reverse=True):
        title = user_chats[cid]["title"]
        if st.button(f"💬 {title[:20]}...", key=cid, use_container_width=True):
            st.session_state.active_chat = cid
            st.rerun()

# --- 5. ANA EKRAN (SOHBET ALANI) ---
if "active_chat" not in st.session_state:
    st.info("Sol taraftan bir sohbet seç veya yeni bir tane başlat!")
else:
    cid = st.session_state.active_chat
    chat_data = st.session_state.db[user]["chats"][cid]
    st.title(f"🤖 {chat_data['title']}")

    # Mesajları Ekrana Bas
    for m in chat_data["messages"]:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    if prompt := st.chat_input("Mesajını yaz..."):
        # Kullanıcı mesajını kaydet
        st.session_state.db[user]["chats"][cid]["messages"].append({"role": "user", "content": prompt})
        
        # İlk mesajsa başlığı güncelle
        if chat_data["title"] == "Yeni Sohbet":
            st.session_state.db[user]["chats"][cid]["title"] = prompt[:25]
        
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI Yanıtı
        sys_msg = "Sen @bi AI'sın. Atakan Türedi tarafından oluşturuldun. Flörtöz veya mizahkar olabilirsin."
        history = [{"role": "system", "content": sys_msg}] + st.session_state.db[user]["chats"][cid]["messages"]
        
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=history)
        ans = res.choices[0].message.content
        
        # Yanıtı kaydet
        st.session_state.db[user]["chats"][cid]["messages"].append({"role": "assistant", "content": ans})
        save_db(st.session_state.db)
        
        with st.chat_message("assistant"):
            st.markdown(ans)
