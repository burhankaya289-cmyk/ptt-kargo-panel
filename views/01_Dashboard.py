import streamlit as st
from datetime import datetime

from database.database import SessionLocal, engine
from database.models import Base, Shipment, Barcode

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
html, body, [class*="css"] {
    font-size: 14px !important;
}
section[data-testid="stSidebar"] {
    min-width: 230px !important;
    max-width: 230px !important;
}
button[kind="header"] {
    display: none !important;
}
div[data-testid="stMarkdownContainer"] p {
    font-size: 13px !important;
}
h1 {
    font-size: 26px !important;
}
h2, h3 {
    font-size: 18px !important;
}
[data-testid="stMetricValue"] {
    font-size: 28px !important;
}
[data-testid="stMetricLabel"] {
    font-size: 13px !important;
}
</style>
""", unsafe_allow_html=True)

Base.metadata.create_all(bind=engine)

st.title("Dashboard")

db = SessionLocal()

toplam_gonderi = db.query(Shipment).count()

kalan_barkod = (
    db.query(Barcode)
    .filter(Barcode.is_used == False)
    .count()
)

tum_gonderiler = db.query(Shipment).all()

bugun = datetime.now()
aylik_gonderi = 0

for item in tum_gonderiler:
    aylik_gonderi += 1

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Toplam Gönderi", toplam_gonderi)

with col2:
    st.metric("Aylık Gönderi", aylik_gonderi)

with col3:
    st.metric("Kalan Barkod", kalan_barkod)
