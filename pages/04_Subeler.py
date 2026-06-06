import streamlit as st
import pandas as pd
from utils.auth import require_login

require_login()
from database.database import SessionLocal, engine
from database.models import Base, Branch

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
html, body, [class*="css"] {
    font-size: 14px !important;
}
section[data-testid="stSidebar"] {
    min-width: 230px !important;
    max-width: 230px !important;
}
button[kind="header"] {
    display: none !important;
}
.stButton button {
    font-size: 13px !important;
    padding: 0.35rem 0.6rem !important;
}
.stDownloadButton button {
    font-size: 13px !important;
    padding: 0.35rem 0.6rem !important;
}
.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stSelectbox div {
    font-size: 13px !important;
}
div[data-testid="stMarkdownContainer"] p {
    font-size: 13px !important;
}
h1 {
    font-size: 26px !important;
}
h2, h3 {
    font-size: 18px !important;
}
.small-table {
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)



st.title("Şubeler")

db = SessionLocal()


def temizle(value):
    return str(value or "").strip()


def kod_sirala(branch):
    kod = str(branch.branch_code or "").strip()

    try:
        return int(kod)
    except Exception:
        return kod


uploaded_file = st.file_uploader(
    "Excel Yükle",
    type=["xlsx"]
)

if uploaded_file is not None:

    try:
        df = pd.read_excel(uploaded_file)

        st.subheader("Excel Önizleme")
        st.dataframe(df, use_container_width=True)

        if st.button("Exceli İçe Aktar", use_container_width=True):

            eklenen = 0
            guncellenen = 0
            atlanan = 0

            for _, row in df.iterrows():

                branch_code = temizle(row.get("Şube Kodu", ""))
                branch_name = temizle(row.get("Şube Adı", ""))
                address = temizle(row.get("Adres", ""))
                district = temizle(row.get("İlçe", ""))
                city = temizle(row.get("İl", ""))

                if not branch_code or not branch_name:
                    atlanan += 1
                    continue

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
                    guncellenen += 1

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
                    eklenen += 1

            db.commit()

            st.success(
                f"Excel aktarıldı. Eklenen: {eklenen} | Güncellenen: {guncellenen} | Atlanan: {atlanan}"
            )

            st.rerun()

    except Exception as e:
        st.error(f"Hata: {e}")

st.divider()

st.subheader("Manuel Şube Ekle / Güncelle")

with st.form("sube_form"):

    branch_code = st.text_input("Şube Kodu")
    branch_name = st.text_input("Şube Adı")
    address = st.text_input("Adres")
    district = st.text_input("İlçe")
    city = st.text_input("İl")

    submit = st.form_submit_button("Kaydet")

    if submit:

        branch_code = temizle(branch_code)
        branch_name = temizle(branch_name)
        address = temizle(address)
        district = temizle(district)
        city = temizle(city)

        if not branch_code or not branch_name:
            st.error("Şube kodu ve şube adı zorunludur.")

        else:
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

                db.commit()
                st.success("Şube güncellendi.")

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
                st.success("Şube kaydedildi.")

            st.rerun()

st.divider()

st.subheader("Kayıtlı Şubeler")

filtre1, filtre2, filtre3 = st.columns(3)

with filtre1:
    filtre_kod = st.text_input("Şube Kodu Ara")

with filtre2:
    filtre_ad = st.text_input("Şube Adı Ara")

with filtre3:
    filtre_il = st.text_input("İl Ara")

subeler = db.query(Branch).all()

filtered = []

for sube in subeler:
    if filtre_kod and filtre_kod.lower() not in str(sube.branch_code or "").lower():
        continue

    if filtre_ad and filtre_ad.lower() not in str(sube.branch_name or "").lower():
        continue

    if filtre_il and filtre_il.lower() not in str(sube.city or "").lower():
        continue

    filtered.append(sube)

filtered = sorted(filtered, key=kod_sirala)

st.write(f"Toplam Şube: {len(filtered)}")

if not filtered:

    st.info("Kayıtlı şube bulunamadı.")

else:

    header = st.columns([1.2, 3, 4, 2, 2, 1.2, 1.2])

    header[0].markdown("**Şube Kodu**")
    header[1].markdown("**Şube Adı**")
    header[2].markdown("**Adres**")
    header[3].markdown("**İlçe**")
    header[4].markdown("**İl**")
    header[5].markdown("**Düzenle**")
    header[6].markdown("**Sil**")

    st.divider()

    for sube in filtered:

        col1, col2, col3, col4, col5, col6, col7 = st.columns(
            [1.2, 3, 4, 2, 2, 1.2, 1.2]
        )

        with col1:
            st.write(sube.branch_code)

        with col2:
            st.write(sube.branch_name)

        with col3:
            st.write(sube.address)

        with col4:
            st.write(sube.district)

        with col5:
            st.write(sube.city)

        with col6:
            if st.button("Düzenle", key=f"edit_{sube.id}"):
                st.session_state[f"edit_sube_{sube.id}"] = not st.session_state.get(
                    f"edit_sube_{sube.id}",
                    False
                )
                st.rerun()

        with col7:
            if st.button("Sil", key=f"sil_{sube.id}"):

                db.delete(sube)
                db.commit()

                st.success("Şube silindi.")
                st.rerun()

        if st.session_state.get(f"edit_sube_{sube.id}", False):

            with st.expander("Şube Düzenle", expanded=True):

                with st.form(f"edit_form_{sube.id}"):

                    edit_code = st.text_input(
                        "Şube Kodu",
                        value=sube.branch_code or ""
                    )

                    edit_name = st.text_input(
                        "Şube Adı",
                        value=sube.branch_name or ""
                    )

                    edit_address = st.text_input(
                        "Adres",
                        value=sube.address or ""
                    )

                    edit_district = st.text_input(
                        "İlçe",
                        value=sube.district or ""
                    )

                    edit_city = st.text_input(
                        "İl",
                        value=sube.city or ""
                    )

                    save_edit = st.form_submit_button("Güncelle")

                    if save_edit:

                        sube.branch_code = temizle(edit_code)
                        sube.branch_name = temizle(edit_name)
                        sube.address = temizle(edit_address)
                        sube.district = temizle(edit_district)
                        sube.city = temizle(edit_city)

                        db.commit()

                        st.session_state[f"edit_sube_{sube.id}"] = False

                        st.success("Şube güncellendi.")
                        st.rerun()
