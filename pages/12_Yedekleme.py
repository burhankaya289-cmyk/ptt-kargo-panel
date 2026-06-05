import os
import shutil
import streamlit as st

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

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
.stSelectbox div,
.stFileUploader label {
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

st.title("Yedekleme")

DB_FILE = "ptt_kargo.db"

st.subheader("Veritabanı Yedeği İndir")

if os.path.exists(DB_FILE):

    with open(DB_FILE, "rb") as f:

        st.download_button(
            "Veritabanını İndir",
            f,
            file_name="ptt_kargo_yedek.db",
            mime="application/octet-stream",
            use_container_width=True
        )

else:
    st.error("Veritabanı dosyası bulunamadı.")

st.divider()

st.subheader("Veritabanı Yedeği Yükle")

uploaded_file = st.file_uploader(
    "Yedek DB Dosyası Yükle",
    type=["db"]
)

if uploaded_file is not None:

    if st.button("Yedeği Geri Yükle", use_container_width=True):

        with open(DB_FILE, "wb") as f:
            f.write(uploaded_file.read())

        st.success("Yedek geri yüklendi. Sayfayı yenileyin.")

st.divider()

st.subheader("Manuel Kopya Oluştur")

if st.button("Sunucuda Yedek Kopya Oluştur", use_container_width=True):

    if os.path.exists(DB_FILE):

        backup_file = "ptt_kargo_backup.db"

        shutil.copy(DB_FILE, backup_file)

        st.success("Sunucuda yedek oluşturuldu.")

    else:
        st.error("Veritabanı dosyası bulunamadı.")
