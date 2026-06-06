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

query_user = st.query_params.get("user", "")
query_role = st.query_params.get("role", "")

if query_user and query_role and not st.session_state.logged_in:
    st.session_state.logged_in = True
    st.session_state.username = query_user
    st.session_state.role = query_role


def login_page():
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    html, body, div, span, p, label, input, textarea, button {
        font-size: 12px !important;
    }
    .block-container {
        padding-top: 1rem !important;
        max-width: 520px !important;
    }
    h1 {
        font-size: 22px !important;
        text-align: center;
    }
    .stButton button {
        font-size: 12px !important;
        min-height: 30px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("PTT Kargo Panel Giriş")

    username = st.text_input("Kullanıcı Adı")
    password = st.text_input("Şifre", type="password")

    if st.button("Giriş Yap", use_container_width=True):
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


if not st.session_state.logged_in:
    login_page()
    st.stop()

st.sidebar.success(
    f"{st.session_state.username} | {st.session_state.role}"
)

if st.sidebar.button("Çıkış Yap"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

    st.query_params.clear()

    login_page()
    st.stop()

pages = [
    st.Page("pages/08_Dashboard.py", title="Dashboard", icon="📊"),
    st.Page("pages/02_Gonderi_Olustur.py", title="Gönderi Oluştur", icon="📦"),
    st.Page("pages/03_Gonderiler.py", title="Gönderiler", icon="📋"),
    st.Page("pages/04_Subeler.py", title="Şubeler", icon="🏢"),
    st.Page("pages/06_Barkodlar.py", title="Barkodlar", icon="🏷️"),
    st.Page("pages/05_Urun_Olculeri.py", title="Ürün Ölçüleri", icon="📐"),
    st.Page("pages/12_Yedekleme.py", title="Yedekleme", icon="💾"),
]

if str(st.session_state.role).strip().lower() == "admin":
    pages.append(
        st.Page("pages/07_Kullanicilar.py", title="Kullanıcılar", icon="👤")
    )

pg = st.navigation(pages)
pg.run()
