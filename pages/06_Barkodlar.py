import streamlit as st
import pandas as pd
from io import BytesIO

from database.database import SessionLocal, engine
from database.models import Base, Barcode

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
.stSelectbox div,
.stFileUploader label {
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

st.title("Barkodlar")

db = SessionLocal()


def temizle(value):
    return str(value or "").strip()


def export_excel(barcodes):
    rows = []

    for item in barcodes:
        rows.append(
            {
                "Barkod": item.barcode
            }
        )

    output = BytesIO()
    pd.DataFrame(rows).to_excel(output, index=False)
    output.seek(0)

    return output


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
            atlanan = 0

            for _, row in df.iterrows():

                barkod = temizle(row.iloc[0])

                if not barkod:
                    atlanan += 1
                    continue

                existing = (
                    db.query(Barcode)
                    .filter(Barcode.barcode == barkod)
                    .first()
                )

                if existing:
                    atlanan += 1

                else:
                    db.add(
                        Barcode(
                            barcode=barkod,
                            is_used=False
                        )
                    )
                    eklenen += 1

            db.commit()

            st.success(
                f"Barkodlar aktarıldı. Eklenen: {eklenen} | Atlanan: {atlanan}"
            )

            st.rerun()

    except Exception as e:
        st.error(f"Hata: {e}")

st.divider()

st.subheader("Manuel Barkod Ekle")

with st.form("barkod_form"):

    barkod = st.text_input("Barkod")

    submit = st.form_submit_button("Kaydet")

    if submit:

        barkod = temizle(barkod)

        if not barkod:
            st.error("Barkod boş olamaz.")

        else:
            existing = (
                db.query(Barcode)
                .filter(Barcode.barcode == barkod)
                .first()
            )

            if existing:
                st.warning("Bu barkod zaten mevcut.")

            else:
                db.add(
                    Barcode(
                        barcode=barkod,
                        is_used=False
                    )
                )
                db.commit()

                st.success("Barkod eklendi.")
                st.rerun()

st.divider()

st.subheader("Kayıtlı Barkodlar")

col1, col2 = st.columns(2)

with col1:
    filtre_barkod = st.text_input("Barkod Ara")

with col2:
    filtre_durum = st.selectbox(
        "Durum",
        [
            "Tümü",
            "Kullanılanlar",
            "Kullanılmayanlar"
        ]
    )

all_barcodes = db.query(Barcode).order_by(Barcode.barcode.asc()).all()

filtered = []

for item in all_barcodes:

    if filtre_barkod and filtre_barkod not in str(item.barcode):
        continue

    if filtre_durum == "Kullanılanlar" and not item.is_used:
        continue

    if filtre_durum == "Kullanılmayanlar" and item.is_used:
        continue

    filtered.append(item)

st.write(f"Toplam Barkod: {len(filtered)}")

selected_key = "selected_barcodes"

if selected_key not in st.session_state:
    st.session_state[selected_key] = []

tumunu_sec = st.checkbox("Tümünü Seç")

if tumunu_sec:
    st.session_state[selected_key] = [
        item.id for item in filtered
    ]

selected_items = (
    db.query(Barcode)
    .filter(Barcode.id.in_(st.session_state[selected_key]))
    .all()
)

top1, top2, top3 = st.columns(3)

with top1:
    if selected_items:
        excel_file = export_excel(selected_items)
        st.download_button(
            "Seçilenleri Excele Aktar",
            excel_file,
            file_name="barkodlar.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    else:
        st.button(
            "Seçilenleri Excele Aktar",
            disabled=True,
            use_container_width=True
        )

with top2:
    if st.button("Seçilenleri Sil", use_container_width=True):
        for item in selected_items:
            db.delete(item)

        db.commit()

        st.session_state[selected_key] = []

        st.rerun()

with top3:
    if st.button("Kullanılanları Sil", use_container_width=True):
        (
            db.query(Barcode)
            .filter(Barcode.is_used == True)
            .delete()
        )

        db.commit()

        st.success("Kullanılan barkodlar silindi.")
        st.rerun()

st.divider()

if not filtered:

    st.info("Barkod bulunamadı.")

else:

    header = st.columns([0.6, 4, 2, 1.2])

    header[0].markdown("**Seç**")
    header[1].markdown("**Barkod**")
    header[2].markdown("**Durum**")
    header[3].markdown("**Sil**")

    st.divider()

    for item in filtered:

        col0, col1, col2, col3 = st.columns([0.6, 4, 2, 1.2])

        with col0:
            secili = st.checkbox(
                "",
                value=item.id in st.session_state[selected_key],
                key=f"barkod_sec_{item.id}"
            )

            if secili and item.id not in st.session_state[selected_key]:
                st.session_state[selected_key].append(item.id)

            if not secili and item.id in st.session_state[selected_key]:
                st.session_state[selected_key].remove(item.id)

        with col1:
            st.write(item.barcode)

        with col2:
            if item.is_used:
                st.markdown("🔴 Kullanıldı")
            else:
                st.markdown("🟢 Kullanılmadı")

        with col3:
            if st.button("Sil", key=f"sil_{item.id}"):
                db.delete(item)
                db.commit()
                st.rerun()
