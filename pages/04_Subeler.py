import streamlit as st

from database.database import SessionLocal
from database.models import Branch

st.title("Şubeler")

db = SessionLocal()

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

subeler = db.query(Branch).all()

for sube in subeler:

    st.write(
        f"{sube.branch_code} | "
        f"{sube.branch_name} | "
        f"{sube.city}"
    )
