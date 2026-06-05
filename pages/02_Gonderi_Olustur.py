import streamlit as st

from database.database import SessionLocal, engine
from database.models import (
    Base,
    Branch,
    ProductDimension,
    Barcode,
    Shipment
)

Base.metadata.create_all(bind=engine)

st.title("Gönderi Oluştur")

db = SessionLocal()

if "sepet" not in st.session_state:
    st.session_state.sepet = []

# Şubeler

subeler = db.query(Branch).order_by(
    Branch.branch_name
).all()

sube_dict = {
    s.branch_name: s
    for s in subeler
}

if len(sube_dict) == 0:

    st.warning(
        "Önce Şubeler ekranından şube ekleyin."
    )
    st.stop()

sube_adi = st.selectbox(
    "Şube",
    list(sube_dict.keys())
)

secilen_sube = sube_dict[sube_adi]

# Alıcı Bilgileri

col1, col2 = st.columns(2)

with col1:

    recipient_name = st.text_input(
        "Alıcı Adı"
    )

    phone = st.text_input(
        "Telefon"
    )

with col2:

    district = st.text_input(
        "İlçe"
    )

    city = st.text_input(
        "İl"
    )

address = st.text_area(
    "Adres"
)

st.divider()

# Ürün

urun_adi = st.text_input(
    "Ürün İçeriği"
)

adet = st.number_input(
    "Adet",
    min_value=1,
    value=1,
    step=1
)

olcu = (
    db.query(ProductDimension)
    .filter(
        ProductDimension.product_name
        == urun_adi
    )
    .first()
)

if olcu:

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.info(f"En: {olcu.width}")

    with col2:
        st.info(f"Boy: {olcu.length}")

    with col3:
        st.info(f"Yükseklik: {olcu.height}")

    with col4:
        st.info(f"Ağırlık: {olcu.weight}")

if st.button("Sepete Ekle"):

    barkodlar = (
        db.query(Barcode)
        .filter(
            Barcode.is_used == False
        )
        .limit(adet)
        .all()
    )

    if len(barkodlar) < adet:

        st.error(
            "Yeterli boş barkod yok."
        )

    else:

        for barkod in barkodlar:

            st.session_state.sepet.append(
                {
                    "barcode": barkod.barcode,
                    "branch_code": secilen_sube.branch_code,
                    "branch_name": secilen_sube.branch_name,
                    "recipient_name": recipient_name,
                    "address": address,
                    "district": district,
                    "city": city,
                    "phone": phone,
                    "product_name": urun_adi,
                    "width": olcu.width if olcu else 0,
                    "length": olcu.length if olcu else 0,
                    "height": olcu.height if olcu else 0,
                    "weight": olcu.weight if olcu else 0
                }
            )

        st.success(
            f"{adet} kayıt sepete eklendi"
        )

st.divider()

st.subheader(
    f"Sepet ({len(st.session_state.sepet)})"
)

for i, item in enumerate(
    st.session_state.sepet
):

    col1, col2 = st.columns([12, 1])

    with col1:

        st.write(
            f"{item['barcode']} | "
            f"{item['branch_name']} | "
            f"{item['recipient_name']} | "
            f"{item['product_name']} | "
            f"{item['weight']} gr"
        )

    with col2:

        if st.button(
            "❌",
            key=f"sil_{i}"
        ):

            st.session_state.sepet.pop(i)

            st.rerun()

st.divider()

col1, col2 = st.columns(2)

with col1:

    if st.button(
        "Sepeti Temizle"
    ):

        st.session_state.sepet = []

        st.rerun()

with col2:

    if st.button(
        "Gönderileri Kaydet"
    ):

        for item in st.session_state.sepet:

            shipment = Shipment(
                barcode=item["barcode"],
                tracking_number=item["barcode"],
                branch_code=item["branch_code"],
                branch_name=item["branch_name"],
                recipient_name=item["recipient_name"],
                address=item["address"],
                district=item["district"],
                city=item["city"],
                phone=item["phone"],
                product_name=item["product_name"],
                width=item["width"],
                length=item["length"],
                height=item["height"],
                weight=item["weight"],
                created_by="admin",
                is_printed=False
            )

            db.add(shipment)

            barkod = (
                db.query(Barcode)
                .filter(
                    Barcode.barcode
                    == item["barcode"]
                )
                .first()
            )

            if barkod:
                barkod.is_used = True

        db.commit()

        st.session_state.sepet = []

        st.success(
            "Gönderiler kaydedildi."
        )

        st.rerun()
