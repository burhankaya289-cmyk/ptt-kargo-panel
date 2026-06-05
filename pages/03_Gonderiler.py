import streamlit as st
import pandas as pd

from database.database import SessionLocal, engine
from database.models import Base, Shipment

Base.metadata.create_all(bind=engine)

st.title("Gönderiler")

db = SessionLocal()

gonderiler = (
    db.query(Shipment)
    .order_by(Shipment.id.desc())
    .all()
)

if "selected_shipments" not in st.session_state:
    st.session_state.selected_shipments = []

col1, col2, col3 = st.columns(3)

with col1:
    filtre_alici = st.text_input("Alıcı Adı")

with col2:
    filtre_urun = st.text_input("Ürün İçeriği")

with col3:
    filtre_takip = st.text_input("Takip No")

filtered = []

for item in gonderiler:

    if filtre_alici:
        if filtre_alici.lower() not in str(item.recipient_name).lower():
            continue

    if filtre_urun:
        if filtre_urun.lower() not in str(item.product_name).lower():
            continue

    if filtre_takip:
        if filtre_takip.lower() not in str(item.tracking_number).lower():
            continue

    filtered.append(item)

st.write(f"Toplam Kayıt: {len(filtered)}")

tumunu_sec = st.checkbox("Tümünü Seç")

if tumunu_sec:
    st.session_state.selected_shipments = [
        item.id for item in filtered
    ]

for item in filtered:

    col0, col1, col2, col3, col4, col5, col6, col7 = st.columns(
        [1,2,3,3,3,2,2,2]
    )

    with col0:

        secili = st.checkbox(
            "",
            value=item.id in st.session_state.selected_shipments,
            key=f"sec_{item.id}"
        )

        if secili:
            if item.id not in st.session_state.selected_shipments:
                st.session_state.selected_shipments.append(item.id)

        else:
            if item.id in st.session_state.selected_shipments:
                st.session_state.selected_shipments.remove(item.id)

    with col1:

        if item.is_printed:
            st.error("Yazdırıldı")
        else:
            st.success("Yazdırılmadı")

    with col2:
        st.write(item.recipient_name)

    with col3:
        st.write(item.product_name)

    with col4:
        st.write(item.tracking_number)

    with col5:
        st.write(item.created_by)

    with col6:

        if st.button(
            "Detay",
            key=f"detay_{item.id}"
        ):

            st.session_state[
                f"show_{item.id}"
            ] = not st.session_state.get(
                f"show_{item.id}",
                False
            )

    with col7:

        if st.button(
            "Sil",
            key=f"sil_{item.id}"
        ):

            db.delete(item)
            db.commit()

            st.rerun()

    if st.session_state.get(
        f"show_{item.id}",
        False
    ):

        st.info(
            f"""
Şube Kodu: {item.branch_code}

Şube Adı: {item.branch_name}

Adres: {item.address}

İlçe: {item.district}

İl: {item.city}

Telefon: {item.phone}

En: {item.width}

Boy: {item.length}

Yükseklik: {item.height}

Ağırlık: {item.weight}
"""
        )

st.divider()

col1, col2 = st.columns(2)

with col1:

    if st.button("Seçilenleri Sil"):

        secilenler = (
            db.query(Shipment)
            .filter(
                Shipment.id.in_(
                    st.session_state.selected_shipments
                )
            )
            .all()
        )

        for item in secilenler:
            db.delete(item)

        db.commit()

        st.session_state.selected_shipments = []

        st.rerun()

with col2:

    if st.button("Seçilenleri Excele Aktar"):

        secilenler = (
            db.query(Shipment)
            .filter(
                Shipment.id.in_(
                    st.session_state.selected_shipments
                )
            )
            .all()
        )

        rows = []

        for item in secilenler:

            rows.append({
                "A": "",
                "B": item.recipient_name,
                "C": item.address,
                "D": item.district,
                "E": item.city,
                "F": item.weight,
                "G": item.phone,
                "H": "",
                "I": item.product_name,
                "J": "",
                "K": "",
                "L": item.tracking_number,
                "M": "",
                "N": "",
                "O": "",
                "P": "",
                "Q": "",
                "R": "",
                "S": item.width,
                "T": item.length,
                "U": item.height
            })

        df = pd.DataFrame(rows)

        file_name = "gonderiler.xlsx"

        df.to_excel(
            file_name,
            index=False
        )

        with open(
            file_name,
            "rb"
        ) as f:

            st.download_button(
                "Exceli İndir",
                f,
                file_name=file_name
            )
