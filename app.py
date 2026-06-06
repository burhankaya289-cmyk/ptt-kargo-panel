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
.stApp {
    background: #f6f9fc !important;
}

.block-container {
    padding-top: 2rem !important;
    padding-left: 2.2rem !important;
    padding-right: 2.2rem !important;
    max-width: 100% !important;
}

html, body, div, span, p, label, input, textarea, button {
    font-size: 13px !important;
    font-family: Inter, "Segoe UI", Arial, sans-serif !important;
}

h1 {
    font-size: 30px !important;
    font-weight: 800 !important;
    color: #020617 !important;
    margin-bottom: 0.25rem !important;
}

h2, h3 {
    font-size: 17px !important;
    font-weight: 700 !important;
    color: #0f172a !important;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #071426 0%, #081b33 100%) !important;
    min-width: 260px !important;
    max-width: 260px !important;
    border-right: 1px solid rgba(255,255,255,0.06);
}
section[data-testid="stSidebar"]::before {
    content: "🚚  PTT ENTEGRASYON\A     Barkod Yönetim Sistemi";
    white-space: pre-line;
    display: block;
    color: white;
    font-weight: 800;
    font-size: 16px;
    line-height: 1.25;
    padding: 18px 18px 14px 18px;
    border-bottom: 1px solid rgba(255,255,255,.08);
}
section[data-testid="stSidebar"] * {
    color: #cbd5e1 !important;
    font-size: 14px !important;
}

section[data-testid="stSidebar"] > div {
    padding-top: 0.8rem !important;
}

.sidebar-logo {
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    padding: 12px 10px 20px 10px !important;
    margin-bottom: 12px !important;
}

.sidebar-icon {
    width: 44px;
    height: 44px;
    border-radius: 14px;
    background: #1669f2;
    color: white !important;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px !important;
    font-weight: 800;
}

.sidebar-title {
    color: white !important;
    font-size: 16px !important;
    font-weight: 800 !important;
    line-height: 1.1;
}

.sidebar-sub {
    color: #94a3b8 !important;
    font-size: 12px !important;
    margin-top: 2px;
}

section[data-testid="stSidebar"] a {
    border-radius: 12px !important;
    padding: 9px 12px !important;
    margin: 4px 0 !important;
    color: #cbd5e1 !important;
    text-decoration: none !important;
}

section[data-testid="stSidebar"] a:hover {
    background: rgba(59,130,246,0.18) !important;
    color: white !important;
}

section[data-testid="stSidebar"] a[aria-current="page"] {
    background: #19365c !important;
    color: white !important;
    font-weight: 700 !important;
}

section[data-testid="stSidebar"] .stButton button {
    background: transparent !important;
    color: #cbd5e1 !important;
    border: 0 !important;
    text-align: left !important;
    padding: 8px 4px !important;
}

div[data-testid="stForm"],
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 18px !important;
}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stSelectbox div {
    background: #f8fafc !important;
    border: 1px solid #dbe3ef !important;
    border-radius: 12px !important;
    min-height: 42px !important;
    font-size: 13px !important;
}

.stButton button,
.stDownloadButton button {
    border-radius: 12px !important;
    min-height: 38px !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    border: 1px solid #dbe3ef !important;
}

.stButton button:hover,
.stDownloadButton button:hover {
    border-color: #1672f3 !important;
    color: #1672f3 !important;
}

[data-testid="stAlert"] {
    border-radius: 14px !important;
}

[data-testid="stSidebarCollapseButton"] {
    display: none !important;
}

[data-testid="stBaseButton-headerNoPadding"] {
    display: none !important;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

hr {
    margin-top: 0.7rem !important;
    margin-bottom: 0.7rem !important;
}

.login-card {
    background: white;
    border: 1px solid #dbe3ef;
    border-radius: 20px;
    padding: 26px;
    box-shadow: 0 12px 35px rgba(15,23,42,0.06);
}
</style>
""", unsafe_allow_html=True)

if "db_initialized" not in st.session_state:
    Base.metadata.create_all(bind=engine)
    st.session_state.db_initialized = True

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

    .block-container {
        max-width: 560px !important;
        padding-top: 5rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        """
        <div style="text-align:center; margin-bottom:22px;">
            <div style="
                width:54px;
                height:54px;
                background:#1669f2;
                border-radius:16px;
                color:white;
                display:inline-flex;
                align-items:center;
                justify-content:center;
                font-size:26px;
                font-weight:800;
                margin-bottom:12px;
            ">📦</div>
            <h1 style="font-size:28px !important;">PTT Kargo Panel Giriş</h1>
            <p style="color:#64748b;">Yönetim paneline erişmek için giriş yapın.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

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



pages = [
    st.Page("pages/08_Dashboard.py", title="Dashboard", icon="📊"),
    st.Page("pages/02_Gonderi_Olustur.py", title="Gönderi Oluştur", icon="📦"),
    st.Page("pages/03_Gonderiler.py", title="Oluşturulan Barkodlar", icon="📋"),
    st.Page("pages/04_Subeler.py", title="Şubeler", icon="🏢"),
    st.Page("pages/06_Barkodlar.py", title="Barkod Import", icon="🏷️"),
    st.Page("pages/05_Urun_Olculeri.py", title="Ürün Ölçüleri", icon="📐"),
    st.Page("pages/12_Yedekleme.py", title="Yedekleme", icon="💾"),
]

if str(st.session_state.role).strip().lower() == "admin":
    pages.append(
        st.Page("pages/07_Kullanicilar.py", title="Kullanıcılar", icon="👥")
    )

    pages.append(
        st.Page("pages/13_Ayarlar.py", title="Ayarlar", icon="⚙️")
    )

pg = st.navigation(pages)

st.sidebar.markdown("---")

st.sidebar.markdown(
    f"""
    <div style="position:fixed; bottom:72px; left:24px;">
        <div style="color:white; font-weight:800; font-size:13px;">{st.session_state.username}</div>
        <div style="color:#94a3b8; font-size:12px;">{st.session_state.role}</div>
    </div>
    """,
    unsafe_allow_html=True
)

if st.sidebar.button("↪ Çıkış"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

    st.query_params.clear()

    login_page()
    st.stop()

pg.run()
