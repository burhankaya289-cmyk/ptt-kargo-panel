import streamlit as st

from database.database import SessionLocal, engine
from database.models import Base, User

st.set_page_config(
    page_title="PTT Kargo Panel",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

Base.metadata.create_all(bind=engine)

db = SessionLocal()

admin = db.query(User).filter(User.username == "admin").first()

if not admin:
    db.add(User(username="admin", password="admin123", role="Admin"))
    db.commit()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "role" not in st.session_state:
    st.session_state.role = ""

if not st.session_state.logged_in:
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("PTT Kargo Panel Giriş")

    username = st.text_input("Kullanıcı Adı")
    password = st.text_input("Şifre", type="password")

    if st.button("Giriş Yap"):
        user = (
            db.query(User)
            .filter(User.username == username, User.password == password)
            .first()
        )

        if user:
            st.session_state.logged_in = True
            st.session_state.username = user.username
            st.session_state.role = user.role
            st.rerun()
        else:
            st.error("Hatalı kullanıcı adı veya şifre.")

    st.stop()

st.sidebar.success(f"{st.session_state.username} | {st.session_state.role}")

if st.sidebar.button("Çıkış Yap"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.rerun()

st.title("PTT Kargo Panel")
st.info("Sol menüden işlem seçiniz.")
