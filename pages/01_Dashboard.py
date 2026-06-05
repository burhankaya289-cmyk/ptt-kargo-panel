import streamlit as st

st.title("Dashboard")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Toplam Gönderi", 0)

with col2:
    st.metric("Aylık Gönderi", 0)

with col3:
    st.metric("Kalan Barkod", 0)
