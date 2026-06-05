import streamlit as st
import pandas as pd

from database.database import SessionLocal, engine
from database.models import Base, Barcode

Base.metadata.create_all(bind=engine)

st.title("Barkodlar")

db = SessionLocal()

# Excel Yükleme

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

                barcode_value = str(
                    row.iloc[0]
                ).strip()

                if not barcode_value:
                    continue

                existing = (
                    db.query(Barcode)
                    .filter(
                        Barcode.barcode == barcode_value
                    )
                    .first()
                )

                if not existing:

                    db.add(
                        Barcode(
                            barcode=barcode_value,
                            is_used=False
                        )
                    )

            db.commit()

            st.success("Barkodlar aktarıldı")
            st.rerun()

    except Exception as e:

        st.error(str(e))

st.divider()

# Manuel Barkod Ekle

st.subheader("Manuel Barkod Ekle")

with st.form("barkod_form"):

    barkod = st.text_input("Barkod")

    submit = st.form_submit_button(
        "Kaydet"
    )

    if submit:

        existing = (
            db.query(Barcode)
            .filter(
                Barcode.barcode == barkod
            )
            .first()
        )

        if existing:

            st.warning(
                "Bu barkod zaten mevcut"
            )

        else:

            db.add(
                Barcode(
                    barcode=barkod,
                    is_used=False
                )
            )

            db.commit()

            st.success("Barkod eklendi")
            st.rerun()

st.divider()

# Filtre

filtre = st.selectbox(
    "Filtre",
    [
        "Tümü",
        "Kullanılanlar",
        "Kullanılmayanlar"
    ]
)

if filtre == "Kullanılanlar":

    barkodlar = (
        db.query(Barcode)
        .filter(
            Barcode.is_used == True
        )
        .all()
    )

elif filtre == "Kullanılmayanlar":

    barkodlar = (
        db.query(Barcode)
        .filter(
            Barcode.is_used == False
        )
        .all()
    )

else:

    barkodlar = (
        db.query(Barcode)
        .all()
    )

st.subheader(
    f"Kayıtlı Barkodlar ({len(barkodlar)})"
)

if barkodlar:

    data = []

    for barkod in barkodlar:

        data.append(
            {
                "Barkod": barkod.barcode,
                "Kullanıldı": (
                    "Evet"
                    if barkod.is_used
                    else "Hayır"
                )
            }
        )

    st.dataframe(
        pd.DataFrame(data),
        use_container_width=True
    )

else:

    st.info(
        "Barkod bulunamadı"
    )

st.divider()

col1, col2 = st.columns(2)

with col1:

    if st.button(
        "Kullanılanları Sil"
    ):

        (
            db.query(Barcode)
            .filter(
                Barcode.is_used == True
            )
            .delete()
        )

        db.commit()

        st.success(
            "Kullanılan barkodlar silindi"
        )

        st.rerun()

with col2:

    kullanilmayanlar = (
        db.query(Barcode)
        .filter(
            Barcode.is_used == False
        )
        .all()
    )

    if st.button(
        "Kullanılmayanları Excele Aktar"
    ):

        export_data = []

        for item in kullanilmayanlar:

            export_data.append(
                {
                    "Barkod":
                    item.barcode
                }
            )

        export_df = pd.DataFrame(
            export_data
        )

        excel_file = (
            "kullanilmayan_barkodlar.xlsx"
        )

        export_df.to_excel(
            excel_file,
            index=False
        )

        st.success(
            f"{len(export_data)} barkod hazırlandı"
        )

        with open(
            excel_file,
            "rb"
        ) as f:

            st.download_button(
                "Exceli İndir",
                f,
                file_name=excel_file
            )
