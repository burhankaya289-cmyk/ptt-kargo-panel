import streamlit as st
from datetime import datetime

from database.database import SessionLocal, engine
from database.models import (
    Base,
    Shipment,
    Barcode
)

Base.metadata.create_all(bind=engine)

st.title("Dashboard")

db = SessionLocal()

toplam_gonderi = (
    db.query(Shipment)
    .count()
)

kalan_barkod = (
    db.query(Barcode)
    .filter(
        Barcode.is_used == False
    )
    .count()
)

tum_gonderiler = (
    db.query(Shipment)
    .all()
)

aylik_gonderi = len(tum_gonderiler)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Toplam Gönderi",
        toplam_gonderi
    )

with col2:
    st.metric(
        "Aylık Gönderi",
        aylik_gonderi
    )

with col3:
    st.metric(
        "Kalan Barkod",
        kalan_barkod
    )
