import streamlit as st
import pandas as pd
from utils.auth import require_login

require_login()
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from database.database import SessionLocal, engine
from database.models import Base, Shipment

Base.metadata.create_all(bind=engine)

st.title("PDF Etiket")

db = SessionLocal()

gonderiler = (
    db.query(Shipment)
    .filter(Shipment.is_printed == False)
    .all()
)

if not gonderiler:

    st.info("Yazdırılacak gönderi yok.")

else:

    secilenler = []

    for item in gonderiler:

        if st.checkbox(
            f"{item.recipient_name} | {item.tracking_number}",
            key=f"pdf_{item.id}"
        ):
            secilenler.append(item)

    if st.button("PDF Oluştur"):

        pdf_file = "etiketler.pdf"

        c = canvas.Canvas(
            pdf_file,
            pagesize=(100 * mm, 150 * mm)
        )

        for item in secilenler:

            c.setFont("Helvetica-Bold", 12)

            c.drawString(
                20,
                400,
                "PTT GENEL MÜDÜRLÜĞÜ KARGO ETİKETİ"
            )

            c.rect(
                20,
                340,
                250,
                50
            )

            c.drawString(
                25,
                370,
                "GÖNDERİCİ BİLGİLERİ"
            )

            c.rect(
                290,
                340,
                250,
                50
            )

            c.drawString(
                295,
                370,
                "PTT KABUL MERKEZİ"
            )

            c.rect(
                20,
                240,
                520,
                80
            )

            c.drawString(
                25,
                295,
                item.recipient_name
            )

            c.drawString(
                25,
                275,
                item.address
            )

            c.drawString(
                25,
                255,
                f"{item.district} / {item.city}"
            )

            c.rect(20, 180, 100, 40)
            c.rect(120, 180, 100, 40)
            c.rect(220, 180, 100, 40)
            c.rect(320, 180, 100, 40)

            c.drawString(
                25,
                200,
                str(item.width)
            )

            c.drawString(
                125,
                200,
                str(item.length)
            )

            c.drawString(
                225,
                200,
                str(item.height)
            )

            c.drawString(
                325,
                200,
                str(item.weight)
            )

            c.rect(
                20,
                120,
                520,
                40
            )

            c.drawString(
                25,
                140,
                item.product_name
            )

            c.rect(
                20,
                20,
                520,
                80
            )

            c.drawString(
                25,
                70,
                f"BARKOD: {item.barcode}"
            )

            c.drawString(
                25,
                45,
                f"TAKİP NO: {item.tracking_number}"
            )

            item.is_printed = True

            c.showPage()

        db.commit()

        c.save()

        with open(
            pdf_file,
            "rb"
        ) as f:

            st.download_button(
                "PDF İndir",
                f,
                file_name=pdf_file,
                mime="application/pdf"
            )

        st.success(
            f"{len(secilenler)} etiket oluşturuldu."
        )
