import streamlit as st
from groq import Groq
import uuid
import time

# 1. Sayfa Ayarları
st.set_page_config(page_title="@bi AI - Müzik Premium", page_icon="🎵", layout="wide")

# 2. Veritabanı Yapısı (Session State)
if "users_db" not in st.session_state:
    st.session_state.users_db = {
        "Atakan": {"pass": "bi2026", "role": "admin"}
    }

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# 3. Giriş / Kayıt Ekranı
if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align: center; color: #00ff00;'>🤖 @bi AI</h1>", unsafe_allow_html=True)
    
    tab_l, tab_r = st.tabs(["Giriş Yap", "Kayıt Ol"])
    
    with tab_l:
        u = st.text_input("Kullanıcı Adı", key="login_username")
        p = st.text_input("Şifre", type="password", key="login_password")
        if st.button("Giriş Yap"):
            # HATAYI ÇÖZEN KRİTİK KONTROL BURADA:
            if u in st.session_state.users_db: # Önce kullanıcı var mı?
                if st.session_state.users_db[u]["pass"] == p: # Varsa şifre doğru mu?
                    st.session_state.authenticated = True
                    st.session_state.user_name = u
                    st.session_state.user_role = st.session_state.users_db[u]["role"]
                    st.session_state.messages = []
                    st.success("Giriş başarılı! Yönlendiriliyorsunuz...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Hatalı şifre!")
            else:
                st.error("Böyle bir kullanıcı bulunamadı. Lütfen kayıt olun.")
                
    with tab_r:
        nu = st.text_input("Yeni Kullanıcı Adı", key="reg_username")
        np = st.text_input("Yeni Şifre", type="password", key="reg_password")
        if st.button("Kayıt Ol"):
            if nu and np:
                if nu in st.session_state.users_db:
                    st.warning("Bu kullanıcı adı zaten alınmış.")
                else:
                    st.session_state.users_db[nu] = {"pass": np, "role": "free"}
                    st.success("Kayıt Başarılı! Şimdi Giriş Yap sekmesinden girebilirsin.")
            else:
                st.error("Lütfen tüm alanları doldur.")
    st.stop()

# --- GİRİŞ BAŞARILIYSA ---
# (Buradan aşağısı zaten senin çalışan chat ve metronom kısmın)
user_name = st.session_state.user_name
user_role = st.session_state.user_role

st.title(f"Hoş geldin {user_name}! 🚀")

if user_role == "free":
    st.info("Sohbet edebilmek için Premium almanız gerekmektedir (Şu an 0 TL!)")
    if st.button("Ücretsiz Premium Al"):
        st.session_state.users_db[user_name]["role"] = "premium"
        st.session_state.user_role = "premium"
        st.balloons()
        st.rerun()
else:
    # Chat ve Groq kodların buraya gelecek...
    st.write("Premium özellikler aktif!")
    # Groq API ve Chat Input kısımlarını buraya ekleyebilirsin.
