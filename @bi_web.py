import streamlit as st
from groq import Groq
import time
import json
import os

# --- 1. VERİ YÖNETİMİ (JSON DATABASE) ---
DB_FILE = "bi_ai_final_db.json"

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
st.set_page_config(page_title="@bi AI - Premium & Hafızalı", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    section[data-testid="stSidebar"] { background-color: #1a1c24; border-right: 2px solid #00ff00; }
    .premium-box { background: #1a1c24; border: 1px solid #00ff00; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 10px; }
    .price { font-size: 24px; color: #FFD700; font-weight: bold; }
    h1, h2, h3 { color: #00ff00 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. GİRİŞ VE KAYIT SİSTEMİ ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>🤖 @bi AI Dünyası</h1>", unsafe_allow_html=True)
    t_login, t_reg = st.tabs(["Giriş Yap", "Kayıt Ol"])
    
    with t_login:
        u = st.text_input("Kullanıcı Adı", key="l_u")
        p = st.text_input("Şifre", type="password", key="l_p")
        if st.button("Giriş", key="b_l"):
            if u in st.session_state.db and st.session_state.db[u]["pass"] == p:
                st.session_state.auth = True
                st.session_state.user = u
                st.rerun()
            else: st.error("Hatalı giriş!")
            
    with t_reg:
        nu = st.text_input("Yeni Kullanıcı", key="r_u")
        np = st.text_input("Yeni Şifre", type="password", key="r_p")
        if st.button("Kayıt Ol", key="b_r"):
            if nu and np:
                if nu not in st.session_state.db:
                    st.session_state.db[nu] = {"pass": np, "role": "free", "chats": {}}
                    save_db(st.session_state.db); st.success("Kayıt tamam! Giriş yap.")
                else: st.warning("Bu kullanıcı zaten var.")
    st.stop()

# --- 4. SOL MENÜ (GEÇMİŞ SOHBETLER) ---
user = st.session_state.user
user_role = st.session_state.db[user].get("role", "free")

with st.sidebar:
    st.title(f"👤 {user}")
    st.write(f"Paket: **{user_role.upper()}**")
    
    # Navigasyon
    page = st.radio("Menü", ["💬 Sohbet", "💎 Market"])
    st.write("---")
    
    if page == "💬 Sohbet":
        if st.button("➕ Yeni Sohbet Başlat", use_container_width=True):
            chat_id = str(int(time.time()))
            st.session_state.db[user]["chats"][chat_id] = {"title": "Yeni Sohbet", "messages": []}
            st.session_state.active_chat = chat_id
            save_db(st.session_state.db); st.rerun()
        
        st.subheader("📜 Geçmiş Sohbetler")
        chats = st.session_state.db[user]["chats"]
        for cid in sorted(chats.keys(), reverse=True):
            if st.button(f"💬 {chats[cid]['title'][:18]}", key=f"btn_{cid}", use_container_width=True):
                st.session_state.active_chat = cid; st.rerun()

    st.write("---")
    if st.button("🚪 Çıkış"):
        st.session_state.auth = False; st.rerun()

# --- 5. MARKET VE ÖDEME SAYFASI ---
if page == "💎 Market":
    st.title("💎 Abonelik Paketleri (3 Ay Ücretsiz)")
    col1, col2, col3 = st.columns(3)
    packs = {"Müzisyen": "0 TL", "Yazılımcı": "0 TL", "Full Paket": "0 TL"}
    
    for i, (name, price) in enumerate(packs.items()):
        with [col1, col2, col3][i]:
            st.markdown(f'<div class="premium-box"><h3>{name}</h3><p class="price">{price}</p></div>', unsafe_allow_html=True)
            if st.button(f"{name} Aktif Et", key=f"p_{name}"):
                st.session_state.temp_pkg = name; st.session_state.checkout = True

    if st.session_state.get("checkout"):
        st.write("---")
        with st.form("bank_card"):
            st.subheader(f"💳 {st.session_state.temp_pkg} İçin Kart Bilgileri")
            st.text_input("Kart No")
            c_a, c_b = st.columns(2)
            c_a.text_input("SKT")
            c_b.text_input("CVV", type="password")
            if st.form_submit_button("ÖDEMEYİ ONAYLA"):
                st.session_state.db[user]["role"] = st.session_state.temp_pkg.lower()
                save_db(st.session_state.db)
                st.balloons(); st.success("Paket Aktif Edildi!"); time.sleep(1); 
                st.session_state.checkout = False; st.rerun()

# --- 6. ANA CHAT EKRANI ---
else:
    if "active_chat" not in st.session_state:
        st.info("Sol taraftan bir sohbet seç veya 'Yeni Sohbet' başlat!")
    else:
        cid = st.session_state.active_chat
        active_chat = st.session_state.db[user]["chats"][cid]
        st.title(f"🤖 {active_chat['title']}")

        for m in active_chat["messages"]:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        if prompt := st.chat_input("Yaz bakalım..."):
            st.session_state.db[user]["chats"][cid]["messages"].append({"role": "user", "content": prompt})
            if active_chat["title"] == "Yeni Sohbet":
                st.session_state.db[user]["chats"][cid]["title"] = prompt[:20]
            
            with st.chat_message("user"): st.markdown(prompt)

            # Akıllı Karakter Talimatı
            sys = f"Sen @bi AI'sın. Yapımcın Atakan Türedi. Karakterin kullanıcının tavrına göre (kanka, flört vb.) değişir. Paket: {user_role.upper()}"
            history = [{"role": "system", "content": sys}] + st.session_state.db[user]["chats"][cid]["messages"]
            
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=history)
            ans = res.choices[0].message.content
            
            st.session_state.db[user]["chats"][cid]["messages"].append({"role": "assistant", "content": ans})
            save_db(st.session_state.db)
            with st.chat_message("assistant"): st.markdown(ans)
