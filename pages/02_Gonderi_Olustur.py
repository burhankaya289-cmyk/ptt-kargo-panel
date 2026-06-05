import streamlit as st

st.title("Yeni Gönderi Oluştur")

if "sepet" not in st.session_state:
    st.session_state.sepet = []

col1, col2 = st.columns(2)

with col1:
    sube_kodu = st.text_input("Şube Kodu")
    sube_adi = st.text_input("Şube Adı")

with col2:
    urun = st.text_input("Ürün İçeriği")
    adet = st.number_input(
        "Adet",
        min_value=1,
        value=1,
        step=1
    )

if st.button("Sepete Ekle"):

    for i in range(adet):

        st.session_state.sepet.append({
            "Şube Kodu": sube_kodu,
            "Şube Adı": sube_adi,
            "Ürün": urun
        })

    st.success(f"{adet} kayıt sepete eklendi")

st.divider()

st.subheader("Sepet")

for i, kayit in enumerate(st.session_state.sepet, start=1):

    st.write(
        f"{i} - "
        f"{kayit['Şube Adı']} | "
        f"{kayit['Ürün']}"
    )

st.write(f"Toplam Kayıt: {len(st.session_state.sepet)}")
