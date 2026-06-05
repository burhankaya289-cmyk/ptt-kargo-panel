import streamlit as st

from database.database import engine
from database.models import Base

Base.metadata.create_all(bind=engine)

st.set_page_config(
    page_title="PTT Kargo Panel",
    layout="wide"
)

st.title("PTT Kargo Panel")

st.success("Veritabanı hazır")
