import streamlit as st

from database.database import SessionLocal, engine
from database.models import Base, User

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
html, body, div, span, p, label, input, textarea, button {
    font-size: 12px !important;
}
.block-container {
    padding-top: 1rem !important;
    padding-left: 1.2rem !important;
    padding-right: 1.2rem !important;
    max-width: 100% !important;
}
h1 {
    font-size: 22px !important;
    margin-bottom: 8px !important;
}
h2, h3 {
    font-size: 15px !important;
}
section[data-testid="stSidebar"] {
    min-width: 220px !important;
    max-width: 220px !important;
}
section[data-testid="stSidebar"] * {
    font-size: 12px !important;
}
button[kind="header"] {
    display: none !important;
}
.stButton button,
.stDownloadButton button,
button {
    font-size: 12px !important;
    padding: 0.22rem 0.45rem !important;
    min-height: 28px !important;
}
.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stSelectbox div {
    font-size: 12px !important;
}
div[data-testid="stMarkdownContainer"] p {
    font-size: 12px !important;
    margin-bottom: 0.2rem !important;
}
hr {
    margin-top: 0.5rem !important;
    margin-bottom: 0.5rem !important;
}
</style>
""", unsafe_allow_html=True)

Base.metadata.create_all(bind=engine)

st.title("Kullanıcılar")

db = SessionLocal()

default_admin = (
    db.query(User)
    .filter(User.username == "admin")
    .first()
)

if not default_admin:
    db.add(
        User(
            username="admin",
            password="admin123",
            role="Admin"
        )
    )
    db.commit()

st.subheader("Yeni Kullanıcı Ekle")

with st.form("kullanici_form"):

    username = st.text_input("Kullanıcı Adı")
    password = st.text_input("Şifre", type="password")

    role = st.selectbox(
        "Rol",
        [
            "Admin",
            "Operatör"
        ]
    )

    submit = st.form_submit_button("Kaydet")

    if submit:

        username = str(username or "").strip()
        password = str(password or "").strip()

        if not username or not password:
            st.error("Kullanıcı adı ve şifre zorunludur.")

        else:
            mevcut = (
                db.query(User)
                .filter(User.username == username)
                .first()
            )

            if mevcut:
                st.error("Bu kullanıcı zaten mevcut.")

            else:
                db.add(
                    User(
                        username=username,
                        password=password,
                        role=role
                    )
                )

                db.commit()

                st.success("Kullanıcı eklendi.")
                st.rerun()

st.divider()

st.subheader("Kullanıcı Listesi")

filtre = st.text_input("Kullanıcı Ara")

kullanicilar = (
    db.query(User)
    .order_by(User.username.asc())
    .all()
)

filtered = []

for user in kullanicilar:
    if filtre and filtre.lower() not in str(user.username or "").lower():
        continue

    filtered.append(user)

st.write(f"Toplam Kullanıcı: {len(filtered)}")

if not filtered:
    st.info("Kayıt yok.")

else:

    header = st.columns([3, 2, 2, 2, 1])

    header[0].markdown("**Kullanıcı Adı**")
    header[1].markdown("**Rol**")
    header[2].markdown("**Şifre Değiştir**")
    header[3].markdown("**Rol Değiştir**")
    header[4].markdown("**Sil**")

    st.divider()

    for user in filtered:

        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])

        with col1:
            st.write(user.username)

        with col2:
            st.write(user.role)

        with col3:
            if st.button("Şifre", key=f"sifre_{user.id}"):
                st.session_state[f"sifre_form_{user.id}"] = not st.session_state.get(
                    f"sifre_form_{user.id}",
                    False
                )
                st.rerun()

        with col4:
            if st.button("Rol", key=f"rol_{user.id}"):
                st.session_state[f"rol_form_{user.id}"] = not st.session_state.get(
                    f"rol_form_{user.id}",
                    False
                )
                st.rerun()

        with col5:
            if user.username == "admin":
                st.write("-")
            else:
                if st.button("Sil", key=f"sil_{user.id}"):
                    db.delete(user)
                    db.commit()
                    st.rerun()

        if st.session_state.get(f"sifre_form_{user.id}", False):

            with st.form(f"sifre_degistir_{user.id}"):

                yeni_sifre = st.text_input(
                    "Yeni Şifre",
                    type="password",
                    key=f"new_pass_{user.id}"
                )

                kaydet = st.form_submit_button("Şifreyi Güncelle")

                if kaydet:

                    if not yeni_sifre.strip():
                        st.error("Şifre boş olamaz.")

                    else:
                        user.password = yeni_sifre.strip()
                        db.commit()

                        st.session_state[f"sifre_form_{user.id}"] = False

                        st.success("Şifre güncellendi.")
                        st.rerun()

        if st.session_state.get(f"rol_form_{user.id}", False):

            with st.form(f"rol_degistir_{user.id}"):

                yeni_rol = st.selectbox(
                    "Yeni Rol",
                    [
                        "Admin",
                        "Operatör"
                    ],
                    index=0 if user.role == "Admin" else 1,
                    key=f"new_role_{user.id}"
                )

                kaydet = st.form_submit_button("Rolü Güncelle")

                if kaydet:

                    user.role = yeni_rol
                    db.commit()

                    st.session_state[f"rol_form_{user.id}"] = False

                    st.success("Rol güncellendi.")
                    st.rerun()
