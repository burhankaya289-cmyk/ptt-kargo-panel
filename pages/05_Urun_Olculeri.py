import streamlit as st
import pandas as pd

from database.database import SessionLocal, engine
from database.models import Base, ProductDimension

Base.metadata.create_all(bind=engine)

st.title("Ürün Ölçüleri")

db = SessionLocal()

# Excel yükleme

uploaded_file = st.file_uploader(
    "Excel Yükle",
    type=["xlsx"]
)

if uploaded_file is not None:

    try:

        df = pd.read_excel(uploaded_file)

        st.subheader("Excel Önizleme")
        st.dataframe(df, use_container_width=True)

        if st.button("Exceli İçe Aktar"):

            for _, row in df.iterrows():

                product_name = str(
                    row.get("Ürün Adı", "")
                ).strip()

                width = float(
                    row.get("En", 0)
                )

                length = float(
                    row.get("Boy", 0)
                )

                height = float(
                    row.get("Yükseklik", 0)
                )

                weight = float(
                    row.get("Ağırlık", 0)
                )

                existing = (
                    db.query(ProductDimension)
                    .filter(
                        ProductDimension.product_name
                        == product_name
                    )
                    .first()
                )

                if existing:

                    existing.width = width
                    existing.length = length
                    existing.height = height
                    existing.weight = weight

                else:

                    db.add(
                        ProductDimension(
                            product_name=product_name,
                            width=width,
                            length=length,
                            height=height,
                            weight=weight
                        )
                    )

            db.commit()

            st.success("Ürünler içe aktarıldı")
            st.rerun()

    except Exception as e:

        st.error(str(e))

st.divider()

# Manuel ürün ekleme

st.subheader("Manuel Ürün Ekle")

with st.form("urun_form"):

    product_name = st.text_input("Ürün Adı")

    width = st.number_input(
        "En",
        min_value=0.0,
        value=0.0
    )

    length = st.number_input(
        "Boy",
        min_value=0.0,
        value=0.0
    )

    height = st.number_input(
        "Yükseklik",
        min_value=0.0,
        value=0.0
    )

    weight = st.number_input(
        "Ağırlık (Gram)",
        min_value=0.0,
        value=0.0
    )

    submit = st.form_submit_button(
        "Kaydet"
    )

    if submit:

        existing = (
            db.query(ProductDimension)
            .filter(
                ProductDimension.product_name
                == product_name
            )
            .first()
        )

        if existing:

            existing.width = width
            existing.length = length
            existing.height = height
            existing.weight = weight

        else:

            db.add(
                ProductDimension(
                    product_name=product_name,
                    width=width,
                    length=length,
                    height=height,
                    weight=weight
                )
            )

        db.commit()

        st.success("Ürün kaydedildi")
        st.rerun()

st.divider()

# Liste

st.subheader("Kayıtlı Ürünler")

urunler = db.query(
    ProductDimension
).all()

if not urunler:

    st.info("Kayıt bulunamadı")

else:

    data = []

    for urun in urunler:

        data.append(
            {
                "Ürün Adı": urun.product_name,
                "En": urun.width,
                "Boy": urun.length,
                "Yükseklik": urun.height,
                "Ağırlık": urun.weight
            }
        )

    st.dataframe(
        pd.DataFrame(data),
        use_container_width=True
    )
