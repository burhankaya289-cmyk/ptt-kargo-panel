import streamlit as st
import pandas as pd

from database.database import SessionLocal, engine
from database.models import Base, User

Base.metadata.create_all(bind=engine)

st.title("Kullanıcılar")

db = SessionLocal()

st.subheader("Yeni Kullanıcı")

with st.form("kullanici_form"):

    username = st.text_input("Kullanıcı Adı")
    password = st.text_input(
        "Şifre",
        type="password"
    )

    role = st.selectbox(
        "Rol",
        [
            "Admin",
            "Operatör"
        ]
    )

    submit = st.form_submit_button(
        "Kaydet"
    )

    if submit:

        mevcut = (
            db.query(User)
            .filter(
                User.username == username
            )
            .first()
        )

        if mevcut:

            st.error(
                "Bu kullanıcı mevcut."
            )

        else:

            db.add(
                User(
                    username=username,
                    password=password,
                    role=role
                )
            )

            db.commit()

            st.success(
                "Kullanıcı eklendi."
            )

            st.rerun()

st.divider()

kullanicilar = (
    db.query(User)
    .order_by(User.id.desc())
    .all()
)

if not kullanicilar:

    st.info("Kayıt yok.")

else:

    for user in kullanicilar:

        col1, col2, col3, col4 = st.columns(
            [3,3,2,1]
        )

        with col1:
            st.write(user.username)

        with col2:
            st.write(user.role)

        with col3:

            if st.button(
                "Şifre Sıfırla",
                key=f"sifre_{user.id}"
            ):

                user.password = "123456"

                db.commit()

                st.success(
                    "Şifre 123456 yapıldı."
                )

                st.rerun()

        with col4:

            if st.button(
                "Sil",
                key=f"sil_{user.id}"
            ):

                db.delete(user)

                db.commit()

                st.rerun()
