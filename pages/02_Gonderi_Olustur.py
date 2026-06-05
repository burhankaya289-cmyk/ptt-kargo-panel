import streamlit as st

st.title("Yeni Gönderi Oluştur")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Şube Seçimi")

    st.text_input("Şube Kodu")

    st.text_input("Şube Adı")

with col2:
    st.subheader("Ürün Bilgisi")

    st.text_input("Ürün İçeriği")

    st.number_input(
        "Adet",
        min_value=1,
        value=1,
        step=1
    )

st.button("Sepete Ekle")
