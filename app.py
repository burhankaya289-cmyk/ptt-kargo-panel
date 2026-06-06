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

token_user = st.query_params.get("user", "")
token_role = st.query_params.get("role", "")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = bool(token_user)

if "username" not in st.session_state:
    st.session_state.username = token_user

if "role" not in st.session_state:
    st.session_state.role = token_role

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

            st.query_params["user"] = user.username
            st.query_params["role"] = user.role

            st.rerun()
        else:
            st.error("Hatalı kullanıcı adı veya şifre.")

    st.stop()

st.sidebar.success(f"{st.session_state.username} | {st.session_state.role}")

if st.sidebar.button("Çıkış Yap"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

    st.query_params.clear()

    st.rerun()

pages = [
    st.Page("pages/08_Dashboard.py", title="Dashboard", icon="📊"),
    st.Page("pages/02_Gonderi_Olustur.py", title="Gönderi Oluştur", icon="📦"),
    st.Page("pages/03_Gonderiler.py", title="Gönderiler", icon="📋"),
    st.Page("pages/04_Subeler.py", title="Şubeler", icon="🏢"),
    st.Page("pages/06_Barkodlar.py", title="Barkodlar", icon="🏷️"),
    st.Page("pages/05_Urun_Olculeri.py", title="Ürün Ölçüleri", icon="📐"),
    st.Page("pages/12_Yedekleme.py", title="Yedekleme", icon="💾"),
]

if st.session_state.role == "Admin":
    pages.append(
        st.Page("pages/07_Kullanicilar.py", title="Kullanıcılar", icon="👤")
    )

pg = st.navigation(pages)
pg.run()
