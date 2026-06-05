import streamlit as st

from database.database import SessionLocal, engine
from database.models import Base, User

Base.metadata.create_all(bind=engine)

st.title("Giriş")

db = SessionLocal()

username = st.text_input(
    "Kullanıcı Adı"
)

password = st.text_input(
    "Şifre",
    type="password"
)

if st.button("Giriş Yap"):

    user = (
        db.query(User)
        .filter(
            User.username == username,
            User.password == password
        )
        .first()
    )

    if user:

        st.session_state["user"] = (
            user.username
        )

        st.session_state["role"] = (
            user.role
        )

        st.success(
            "Giriş başarılı"
        )

    else:

        st.error(
            "Hatalı kullanıcı adı veya şifre"
        )
