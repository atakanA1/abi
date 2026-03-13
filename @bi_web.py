import streamlit as st
from groq import Groq

# Sayfa Ayarları (Havalı bir görünüm için)
st.set_page_config(page_title="@bi AI", page_icon="🤖", layout="centered")

# CSS ile @bi'ye özel stil (Yeşil dumanlı hava)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTextInput > div > div > input { color: #00ff00; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 @bi AI")
st.subheader("Hoş geldin Atakan, bugün ne yapıyoruz?")

# Secrets'tan API Key'i çekiyoruz
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    st.error("Kasa (Secrets) bulunamadı! Lütfen secrets.toml dosyasını kontrol et.")
    st.stop()

# Sohbet geçmişini başlat (Uygulama yenilense de mesajlar gitmesin)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Eski mesajları ekrana bas
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kullanıcıdan girdi al
if prompt := st.chat_input("Mesajını yaz..."):
    # Kullanıcı mesajını ekrana bas ve hafızaya ekle
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Groq API ile yanıt üret
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Groq'tan cevap alıyoruz
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            stream=True,
        )
        
        for chunk in completion:
            full_response += (chunk.choices[0].delta.content or "")
            message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
