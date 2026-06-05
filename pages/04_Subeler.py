import streamlit as st
import pandas as pd

from database.database import SessionLocal
from database.models import Branch

st.title("Şubeler")

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

                branch_code = str(row.get("Şube Kodu", "")).strip()
                branch_name = str(row.get("Şube Adı", "")).strip()
                address = str(row.get("Adres", "")).strip()
                district = str(row.get("İlçe", "")).strip()
                city = str(row.get("İl", "")).strip()

                existing = (
                    db.query(Branch)
                    .filter(Branch.branch_code == branch_code)
                    .first()
                )

                if existing:

                    existing.branch_name = branch_name
                    existing.address = address
                    existing.district = district
                    existing.city = city

                else:

                    branch = Branch(
                        branch_code=branch_code,
                        branch_name=branch_name,
                        address=address,
                        district=district,
                        city=city
                    )

                    db.add(branch)

            db.commit()

            st.success("Excel içe aktarıldı")

    except Exception as e:
        st.error(str(e))

st.divider()

# Manuel Şube Ekleme

st.subheader("Manuel Şube Ekle")

with st.form("sube_form"):

    branch_code = st.text_input("Şube Kodu")
    branch_name = st.text_input("Şube Adı")
    address = st.text_input("Adres")
    district = st.text_input("İlçe")
    city = st.text_input("İl")

    submit = st.form_submit_button("Kaydet")

    if submit:

        branch = Branch(
            branch_code=branch_code,
            branch_name=branch_name,
            address=address,
            district=district,
            city=city
        )

        db.add(branch)
        db.commit()

        st.success("Şube kaydedildi")

st.divider()

# Şubeler Listesi

st.subheader("Kayıtlı Şubeler")

subeler = db.query(Branch).all()

if len(subeler) == 0:

    st.info("Kayıtlı şube bulunamadı.")

else:

    data = []

    for sube in subeler:

        data.append(
            {
                "Şube Kodu": sube.branch_code,
                "Şube Adı": sube.branch_name,
                "Adres": sube.address,
                "İlçe": sube.district,
                "İl": sube.city,
            }
        )

    st.dataframe(
        pd.DataFrame(data),
        use_container_width=True
    )
