import streamlit as st

from database.database import SessionLocal, engine
from database.models import Base, User

st.set_page_config(
    page_title="PTT Kargo Panel",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
html, body, div, span, p, label, input, textarea, button {
    font-size: 12px !important;
}
.block-container {
    padding-top: 1rem !important;
    padding-left: 1.2rem !important;
    padding-right: 1.2rem !important;
    max-width: 100% !important;
}
h1 {
    font-size: 22px !important;
}
h2, h3 {
    font-size: 15px !important;
}
section[data-testid="stSidebar"] {
    min-width: 220px !important;
    max-width: 220px !important;
}
section[data-testid="stSidebar"] * {
    font-size: 12px !important;
}
button[kind="header"] {
    display: none !important;
}
.stButton button,
.stDownloadButton button,
button {
    font-size: 12px !important;
    padding: 0.22rem 0.45rem !important;
    min-height: 28px !important;
}
.stTextInput input {
    font-size: 12px !important;
}
</style>
""", unsafe_allow_html=True)

Base.metadata.create_all(bind=engine)

db = SessionLocal()

admin = db.query(User).filter(User.username == "admin").first()

if not admin:
    db.add(
        User(
            username="admin",
            password="admin123",
            role="Admin"
        )
    )
    db.commit()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "role" not in st.session_state:
    st.session_state.role = ""


def login_page():
    st.title("PTT Kargo Panel Giriş")

    col1, col2, col3 = st.columns([1, 1.2, 1])

    with col2:
        username = st.text_input("Kullanıcı Adı")
        password = st.text_input("Şifre", type="password")

        if st.button("Giriş Yap", use_container_width=True):
            user = (
                db.query(User)
                .filter(
                    User.username == username,
                    User.password == password
                )
                .first()
            )

            if user:
                st.session_state.logged_in = True
                st.session_state.username = user.username
                st.session_state.role = user.role
                st.rerun()
            else:
                st.error("Hatalı kullanıcı adı veya şifre.")


if not st.session_state.logged_in:

    pg = st.navigation(
        [
            st.Page(
                login_page,
                title="Giriş",
                icon="🔐"
            )
        ]
    )

    pg.run()

else:

    st.sidebar.success(
        f"{st.session_state.username} | {st.session_state.role}"
    )

    if st.sidebar.button("Çıkış Yap"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
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
