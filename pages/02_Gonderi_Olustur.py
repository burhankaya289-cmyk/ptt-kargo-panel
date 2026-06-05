import streamlit as st

st.title("Yeni Gönderi Oluştur")

# Sepet oluştur
if "sepet" not in st.session_state:
    st.session_state.sepet = []

# Form alanları
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

# Sepete ekle
if st.button("Sepete Ekle"):

    if urun.strip() == "":
        st.error("Ürün içeriği boş olamaz")
    else:

        for _ in range(adet):

            st.session_state.sepet.append(
                {
                    "Şube Kodu": sube_kodu,
                    "Şube Adı": sube_adi,
                    "Ürün": urun
                }
            )

        st.success(f"{adet} kayıt sepete eklendi")

st.divider()

# Sepet
st.subheader("Sepet")

if not st.session_state.sepet:

    st.info("Sepet boş")

else:

    for i, kayit in enumerate(st.session_state.sepet):

        col1, col2 = st.columns([10, 1])

        with col1:
            st.write(
                f"{i+1} | "
                f"{kayit['Şube Adı']} | "
                f"{kayit['Ürün']}"
            )

        with col2:
            if st.button(
                "❌",
                key=f"sil_{i}"
            ):
                st.session_state.sepet.pop(i)
                st.rerun()

    st.divider()

    st.write(
        f"Toplam Kayıt: {len(st.session_state.sepet)}"
    )

    if st.button("Sepeti Temizle"):

        st.session_state.sepet = []

        st.rerun()
