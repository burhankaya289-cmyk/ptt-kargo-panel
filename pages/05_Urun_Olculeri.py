import streamlit as st
import pandas as pd
from utils.auth import require_login

require_login()
from database.database import SessionLocal, engine
from database.models import Base, ProductDimension

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
/* GENEL */
html, body, div, span, p, label, input, textarea, button {
    font-size: 12px !important;
}

/* ANA ALAN */
.block-container {
    padding-top: 1rem !important;
    padding-left: 1.2rem !important;
    padding-right: 1.2rem !important;
    max-width: 100% !important;
}

/* BAŞLIKLAR */
h1 {
    font-size: 22px !important;
    margin-bottom: 8px !important;
}

h2, h3 {
    font-size: 15px !important;
    margin-top: 8px !important;
    margin-bottom: 6px !important;
}

/* SOL MENÜ */
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

/* INPUT */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stSelectbox div,
.stFileUploader label {
    font-size: 12px !important;
}

/* LABEL */
label {
    font-size: 12px !important;
}

/* BUTON */
.stButton button,
.stDownloadButton button,
button {
    font-size: 12px !important;
    padding: 0.22rem 0.45rem !important;
    min-height: 28px !important;
}

/* ALERT */
[data-testid="stAlert"] div {
    font-size: 12px !important;
}

/* DATAFRAME */
[data-testid="stDataFrame"] * {
    font-size: 11px !important;
}

/* MARKDOWN */
div[data-testid="stMarkdownContainer"] p {
    font-size: 12px !important;
    margin-bottom: 0.2rem !important;
}

/* KOLON BOŞLUK */
div[data-testid="column"] {
    padding: 0 3px !important;
}

/* DİVIDER BOŞLUK */
hr {
    margin-top: 0.5rem !important;
    margin-bottom: 0.5rem !important;
}
</style>
""", unsafe_allow_html=True)



st.title("Ürün Ölçüleri")

db = SessionLocal()


def temizle(value):
    return str(value or "").strip()


def sayi(value):
    try:
        if pd.isna(value):
            return 0.0
        return float(value)
    except Exception:
        return 0.0


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

                product_name = temizle(row.get("Ürün Adı", ""))

                width = sayi(row.get("En", 0))
                length = sayi(row.get("Boy", 0))
                height = sayi(row.get("Yükseklik", 0))
                weight = sayi(row.get("Ağırlık", 0))

                if not product_name:
                    atlanan += 1
                    continue

                existing = None

                for item in db.query(ProductDimension).all():
                    if temizle(item.product_name).lower() == product_name.lower():
                        existing = item
                        break

                if existing:
                    existing.width = width
                    existing.length = length
                    existing.height = height
                    existing.weight = weight
                    guncellenen += 1

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
                    eklenen += 1

            db.commit()

            st.success(
                f"Excel aktarıldı. Eklenen: {eklenen} | Güncellenen: {guncellenen} | Atlanan: {atlanan}"
            )

            st.rerun()

    except Exception as e:
        st.error(f"Hata: {e}")

st.divider()

st.subheader("Manuel Ürün Ekle / Güncelle")

with st.form("urun_form"):

    product_name = st.text_input("Ürün Adı")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        width = st.number_input("En", min_value=0.0, value=0.0, step=1.0)

    with col2:
        length = st.number_input("Boy", min_value=0.0, value=0.0, step=1.0)

    with col3:
        height = st.number_input("Yükseklik", min_value=0.0, value=0.0, step=1.0)

    with col4:
        weight = st.number_input("Ağırlık (Gram)", min_value=0.0, value=0.0, step=1.0)

    submit = st.form_submit_button("Kaydet")

    if submit:

        product_name = temizle(product_name)

        if not product_name:
            st.error("Ürün adı zorunludur.")

        else:
            existing = None

            for item in db.query(ProductDimension).all():
                if temizle(item.product_name).lower() == product_name.lower():
                    existing = item
                    break

            if existing:
                existing.product_name = product_name
                existing.width = width
                existing.length = length
                existing.height = height
                existing.weight = weight

                db.commit()
                st.success("Ürün güncellendi.")

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
                st.success("Ürün kaydedildi.")

            st.rerun()

st.divider()

st.subheader("Kayıtlı Ürünler")

filtre1, filtre2 = st.columns(2)

with filtre1:
    filtre_urun = st.text_input("Ürün Adı Ara")

with filtre2:
    siralama = st.selectbox(
        "Sıralama",
        [
            "Ürün Adı A-Z",
            "Ürün Adı Z-A"
        ]
    )

urunler = db.query(ProductDimension).all()

filtered = []

for urun in urunler:
    if filtre_urun and filtre_urun.lower() not in str(urun.product_name or "").lower():
        continue

    filtered.append(urun)

reverse_sort = siralama == "Ürün Adı Z-A"

filtered = sorted(
    filtered,
    key=lambda x: str(x.product_name or "").lower(),
    reverse=reverse_sort
)

st.write(f"Toplam Ürün: {len(filtered)}")

if not filtered:

    st.info("Kayıt bulunamadı.")

else:

    header = st.columns([4, 1.2, 1.2, 1.4, 1.4, 1.1, 1.1])

    header[0].markdown("**Ürün Adı**")
    header[1].markdown("**En**")
    header[2].markdown("**Boy**")
    header[3].markdown("**Yükseklik**")
    header[4].markdown("**Ağırlık**")
    header[5].markdown("**Düzenle**")
    header[6].markdown("**Sil**")

    st.divider()

    for urun in filtered:

        col1, col2, col3, col4, col5, col6, col7 = st.columns(
            [4, 1.2, 1.2, 1.4, 1.4, 1.1, 1.1]
        )

        with col1:
            st.write(urun.product_name)

        with col2:
            st.write(urun.width)

        with col3:
            st.write(urun.length)

        with col4:
            st.write(urun.height)

        with col5:
            st.write(urun.weight)

        with col6:
            if st.button("Düzenle", key=f"edit_{urun.id}"):
                st.session_state[f"edit_urun_{urun.id}"] = not st.session_state.get(
                    f"edit_urun_{urun.id}",
                    False
                )
                st.rerun()

        with col7:
            if st.button("Sil", key=f"sil_{urun.id}"):
                db.delete(urun)
                db.commit()
                st.success("Ürün silindi.")
                st.rerun()

        if st.session_state.get(f"edit_urun_{urun.id}", False):

            with st.expander("Ürün Düzenle", expanded=True):

                with st.form(f"edit_form_{urun.id}"):

                    edit_name = st.text_input(
                        "Ürün Adı",
                        value=urun.product_name or ""
                    )

                    e1, e2, e3, e4 = st.columns(4)

                    with e1:
                        edit_width = st.number_input(
                            "En",
                            value=float(urun.width or 0)
                        )

                    with e2:
                        edit_length = st.number_input(
                            "Boy",
                            value=float(urun.length or 0)
                        )

                    with e3:
                        edit_height = st.number_input(
                            "Yükseklik",
                            value=float(urun.height or 0)
                        )

                    with e4:
                        edit_weight = st.number_input(
                            "Ağırlık",
                            value=float(urun.weight or 0)
                        )

                    save_edit = st.form_submit_button("Güncelle")

                    if save_edit:
                        urun.product_name = temizle(edit_name)
                        urun.width = edit_width
                        urun.length = edit_length
                        urun.height = edit_height
                        urun.weight = edit_weight

                        db.commit()

                        st.session_state[f"edit_urun_{urun.id}"] = False

                        st.success("Ürün güncellendi.")
                        st.rerun()
