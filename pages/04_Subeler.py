import streamlit as st
import pandas as pd

from database.database import SessionLocal, engine
from database.models import Base, Branch

# Tabloları garanti oluştur
Base.metadata.create_all(bind=engine)

st.title("Şubeler")

db = SessionLocal()

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

                    db.add(
                        Branch(
                            branch_code=branch_code,
                            branch_name=branch_name,
                            address=address,
                            district=district,
                            city=city
                        )
                    )

            db.commit()

            st.success("Excel içe aktarıldı")
            st.rerun()

    except Exception as e:
        st.error(f"Hata: {e}")

st.divider()

st.subheader("Manuel Şube Ekle")

with st.form("sube_form"):

    branch_code = st.text_input("Şube Kodu")
    branch_name = st.text_input("Şube Adı")
    address = st.text_input("Adres")
    district = st.text_input("İlçe")
    city = st.text_input("İl")

    submit = st.form_submit_button("Kaydet")

    if submit:

        db.add(
            Branch(
                branch_code=branch_code,
                branch_name=branch_name,
                address=address,
                district=district,
                city=city
            )
        )

        db.commit()

        st.success("Şube kaydedildi")
        st.rerun()

st.divider()

st.subheader("Kayıtlı Şubeler")

try:

    subeler = db.query(Branch).all()

    if not subeler:

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
                    "İl": sube.city
                }
            )

        st.dataframe(
            pd.DataFrame(data),
            use_container_width=True
        )

except Exception as e:

    st.error(f"Veritabanı Hatası: {e}")
