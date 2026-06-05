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
    margin-bottom: 8px !important;
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
.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stSelectbox div {
    font-size: 12px !important;
}
div[data-testid="stMarkdownContainer"] p {
    font-size: 12px !important;
    margin-bottom: 0.2rem !important;
}
hr {
    margin-top: 0.5rem !important;
    margin-bottom: 0.5rem !important;
}
</style>
""", unsafe_allow_html=True)

Base.metadata.create_all(bind=engine)

db = SessionLocal()

admin = (
    db.query(User)
    .filter(User.username == "admin")
    .first()
)

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

if not st.session_state.logged_in:

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

                st.success("Giriş başarılı.")
                st.rerun()

            else:
                st.error("Hatalı kullanıcı adı veya şifre.")

else:

    st.sidebar.success(
        f"{st.session_state.username} | {st.session_state.role}"
    )

    if st.sidebar.button("Çıkış Yap"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.rerun()

    st.title("PTT Kargo Panel")

    st.info("Sol menüden işlem seçiniz.")
