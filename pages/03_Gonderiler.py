import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code128

from database.database import SessionLocal, engine
from database.models import Base, Shipment

Base.metadata.create_all(bind=engine)

st.title("Gönderiler")

db = SessionLocal()

if "selected_shipments" not in st.session_state:
    st.session_state.selected_shipments = []


def create_excel(shipments):
    rows = []

    for item in shipments:
        rows.append({
            "A": "",
            "B": item.recipient_name,
            "C": item.address,
            "D": item.district,
            "E": item.city,
            "F": item.weight,
            "G": item.phone,
            "H": "",
            "I": item.product_name,
            "J": "",
            "K": "",
            "L": item.tracking_number,
            "M": "",
            "N": "",
            "O": "",
            "P": "",
            "Q": "",
            "R": "",
            "S": item.width,
            "T": item.length,
            "U": item.height,
        })

    output = BytesIO()
    pd.DataFrame(rows).to_excel(output, index=False)
    output.seek(0)
    return output


def create_pdf(shipments):
    output = BytesIO()
    page_width = 40 * mm
    page_height = 50 * mm

    c = canvas.Canvas(output, pagesize=(page_width, page_height))

    for item in shipments:
        c.setLineWidth(0.4)
        c.rect(1 * mm, 1 * mm, 38 * mm, 48 * mm)

        c.setFont("Helvetica-Bold", 5.5)
        c.drawCentredString(20 * mm, 47 * mm, "PTT GENEL MÜDÜRLÜĞÜ KARGO ETİKETİ")

        c.rect(1 * mm, 39 * mm, 24 * mm, 7 * mm)
        c.rect(25 * mm, 39 * mm, 14 * mm, 7 * mm)

        c.setFont("Helvetica-Bold", 4)
        c.drawString(2 * mm, 44 * mm, "GÖNDERİCİ")
        c.setFont("Helvetica", 3.7)
        c.drawString(2 * mm, 42 * mm, "Ziraat Katılım Bankası A.Ş.")
        c.drawString(2 * mm, 40 * mm, "Hadımköy Lojistik Merkezi")

        c.setFont("Helvetica-Bold", 4)
        c.drawString(26 * mm, 44 * mm, "PTT KABUL")
        c.drawString(26 * mm, 42 * mm, "MERKEZİ")

        c.rect(1 * mm, 27 * mm, 38 * mm, 12 * mm)

        c.setFont("Helvetica-Bold", 4)
        c.drawString(2 * mm, 37 * mm, "ALICI")

        c.setFont("Helvetica-Bold", 4.3)
        c.drawString(2 * mm, 35 * mm, str(item.recipient_name or "")[:38])

        c.setFont("Helvetica", 3.7)
        c.drawString(2 * mm, 32 * mm, str(item.address or "")[:45])
        c.drawString(2 * mm, 29 * mm, f"{item.district or ''} / {item.city or ''}"[:45])

        box_y = 22 * mm
        box_h = 5 * mm
        box_w = 9.5 * mm

        titles = ["TARİH", "ÖLÇÜ", "AĞIRLIK", "ŞUBE"]
        values = [
            datetime.now().strftime("%d.%m.%Y"),
            f"{item.width}x{item.length}x{item.height}",
            f"{item.weight} gr",
            item.branch_code or "",
        ]

        for i in range(4):
            x = 1 * mm + i * box_w
            c.rect(x, box_y, box_w, box_h)
            c.setFont("Helvetica-Bold", 3.3)
            c.drawString(x + 0.6 * mm, box_y + 3.2 * mm, titles[i])
            c.setFont("Helvetica", 3.1)
            c.drawString(x + 0.6 * mm, box_y + 1.2 * mm, str(values[i])[:12])

        c.rect(1 * mm, 16 * mm, 38 * mm, 6 * mm)
        c.setFont("Helvetica-Bold", 4)
        c.drawString(2 * mm, 20 * mm, "ÜRÜN İÇERİĞİ")
        c.setFont("Helvetica", 4.2)
        c.drawString(2 * mm, 17.7 * mm, str(item.product_name or "")[:38])

        c.rect(1 * mm, 1 * mm, 38 * mm, 15 * mm)

        barcode_value = str(item.tracking_number or item.barcode or "")
        barcode = code128.Code128(barcode_value, barHeight=7 * mm, barWidth=0.35)
        barcode.drawOn(c, 4 * mm, 6 * mm)

        c.setFont("Helvetica-Bold", 5)
        c.drawCentredString(20 * mm, 3 * mm, barcode_value)

        item.is_printed = True
        c.showPage()

    db.commit()
    c.save()
    output.seek(0)
    return output


col1, col2, col3, col4 = st.columns(4)

with col1:
    filtre_alici = st.text_input("Alıcı Adı")

with col2:
    filtre_urun = st.text_input("Ürün İçeriği")

with col3:
    filtre_takip = st.text_input("Takip No")

with col4:
    filtre_kullanici = st.text_input("Kullanıcı Adı")

durum = st.selectbox("Durum", ["Tümü", "Yazdırılmadı", "Yazdırıldı"])

gonderiler = db.query(Shipment).order_by(Shipment.id.desc()).all()

filtered = []

for item in gonderiler:
    if filtre_alici and filtre_alici.lower() not in str(item.recipient_name).lower():
        continue

    if filtre_urun and filtre_urun.lower() not in str(item.product_name).lower():
        continue

    if filtre_takip and filtre_takip.lower() not in str(item.tracking_number).lower():
        continue

    if filtre_kullanici and filtre_kullanici.lower() not in str(item.created_by).lower():
        continue

    if durum == "Yazdırıldı" and not item.is_printed:
        continue

    if durum == "Yazdırılmadı" and item.is_printed:
        continue

    filtered.append(item)

st.write(f"Toplam Kayıt: {len(filtered)}")

tumunu_sec = st.checkbox("Tümünü Seç")

if tumunu_sec:
    st.session_state.selected_shipments = [item.id for item in filtered]

selected_items = (
    db.query(Shipment)
    .filter(Shipment.id.in_(st.session_state.selected_shipments))
    .all()
)

top1, top2, top3 = st.columns(3)

with top1:
    if st.button("Seçilenleri Yazdır", use_container_width=True):
        if selected_items:
            st.session_state["pdf_ready"] = True
        else:
            st.error("Seçili gönderi yok.")

with top2:
    if selected_items:
        excel_file = create_excel(selected_items)
        st.download_button(
            "Seçilenleri Excele Aktar",
            excel_file,
            file_name="gonderiler.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    else:
        st.button("Seçilenleri Excele Aktar", use_container_width=True, disabled=True)

with top3:
    if st.button("Seçilenleri Sil", use_container_width=True):
        for item in selected_items:
            db.delete(item)

        db.commit()
        st.session_state.selected_shipments = []
        st.rerun()

if st.session_state.get("pdf_ready", False):
    pdf_file = create_pdf(selected_items)

    st.download_button(
        "PDF İndir",
        pdf_file,
        file_name="etiketler.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

st.divider()

header = st.columns([0.6, 1.7, 3.5, 3.5, 3, 2, 1.2, 1.2, 1.2])

header[0].markdown("**Seç**")
header[1].markdown("**Durum**")
header[2].markdown("**Alıcı Adı**")
header[3].markdown("**Ürün İçeriği**")
header[4].markdown("**Takip No**")
header[5].markdown("**Kullanıcı**")
header[6].markdown("**Detay**")
header[7].markdown("**PDF**")
header[8].markdown("**Sil**")

st.divider()

for item in filtered:
    col0, col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(
        [0.6, 1.7, 3.5, 3.5, 3, 2, 1.2, 1.2, 1.2]
    )

    with col0:
        secili = st.checkbox(
            "",
            value=item.id in st.session_state.selected_shipments,
            key=f"sec_{item.id}",
        )

        if secili and item.id not in st.session_state.selected_shipments:
            st.session_state.selected_shipments.append(item.id)

        if not secili and item.id in st.session_state.selected_shipments:
            st.session_state.selected_shipments.remove(item.id)

    with col1:
        if item.is_printed:
            st.markdown("🔴 **Yazdırıldı**")
        else:
            st.markdown("🟢 **Yazdırılmadı**")

    with col2:
        st.write(str(item.recipient_name or "")[:45])

    with col3:
        st.write(str(item.product_name or "")[:45])

    with col4:
        st.write(str(item.tracking_number or ""))

    with col5:
        st.write(str(item.created_by or ""))

    with col6:
        if st.button("Detay", key=f"detay_{item.id}"):
            st.session_state[f"detay_{item.id}"] = not st.session_state.get(
                f"detay_{item.id}", False
            )
            st.rerun()

    with col7:
        if st.button("PDF", key=f"pdf_{item.id}"):
            pdf_file = create_pdf([item])

            st.download_button(
                "İndir",
                pdf_file,
                file_name=f"etiket_{item.tracking_number}.pdf",
                mime="application/pdf",
                key=f"indir_{item.id}",
            )

    with col8:
        if st.button("Sil", key=f"sil_{item.id}"):
            db.delete(item)
            db.commit()
            st.rerun()

    if st.session_state.get(f"detay_{item.id}", False):
        with st.expander("Gönderi Detayı / Düzenle", expanded=True):
            with st.form(f"edit_form_{item.id}"):

                recipient_name = st.text_input("Alıcı Adı", value=item.recipient_name or "")
                address = st.text_area("Adres", value=item.address or "")

                e1, e2, e3 = st.columns(3)

                with e1:
                    district = st.text_input("İlçe", value=item.district or "")

                with e2:
                    city = st.text_input("İl", value=item.city or "")

                with e3:
                    phone = st.text_input("Telefon", value=item.phone or "")

                product_name = st.text_input("Ürün İçeriği", value=item.product_name or "")

                o1, o2, o3, o4 = st.columns(4)

                with o1:
                    width = st.number_input("En", value=float(item.width or 0))

                with o2:
                    length = st.number_input("Boy", value=float(item.length or 0))

                with o3:
                    height = st.number_input("Yükseklik", value=float(item.height or 0))

                with o4:
                    weight = st.number_input("Ağırlık", value=float(item.weight or 0))

                kaydet = st.form_submit_button("Düzenlemeyi Kaydet")

                if kaydet:
                    item.recipient_name = recipient_name
                    item.address = address
                    item.district = district
                    item.city = city
                    item.phone = phone
                    item.product_name = product_name
                    item.width = width
                    item.length = length
                    item.height = height
                    item.weight = weight

                    if item.is_printed:
                        item.is_printed = False

                    db.commit()
                    st.success("Gönderi güncellendi.")
                    st.rerun()
