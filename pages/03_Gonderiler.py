import streamlit as st
import pandas as pd
from utils.auth import require_login

require_login()
from io import BytesIO
from datetime import datetime

from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code128

from database.database import SessionLocal, engine
from database.models import Base, Shipment

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
.status-red {
    background:#ffe8e8;
    color:#8a1f1f;
    padding:5px 6px;
    border-radius:6px;
    font-weight:600;
    font-size:12px;
    text-align:center;
}
.status-green {
    background:#e8f8ee;
    color:#18713a;
    padding:5px 6px;
    border-radius:6px;
    font-weight:600;
    font-size:12px;
    text-align:center;
}
hr {
    margin-top: 0.5rem !important;
    margin-bottom: 0.5rem !important;
}
</style>
""", unsafe_allow_html=True)

Base.metadata.create_all(bind=engine)

st.title("Gönderiler")

db = SessionLocal()

if "selected_shipments" not in st.session_state:
    st.session_state.selected_shipments = []

if "pdf_file" not in st.session_state:
    st.session_state.pdf_file = None

if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = "etiketler.pdf"


def kisalt(text, limit):
    text = str(text or "")
    if len(text) <= limit:
        return text
    return text[:limit]


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


def draw_wrapped(c, text, x, y, max_chars, max_lines, font="Helvetica", size=3.5, line_gap=3.2):
    text = str(text or "").strip()
    lines = []

    while text:
        lines.append(text[:max_chars])
        text = text[max_chars:]

    c.setFont(font, size)

    for line in lines[:max_lines]:
        c.drawString(x, y, line)
        y -= line_gap * mm


def create_pdf(shipments):
    output = BytesIO()

    page_width = 40 * mm
    page_height = 50 * mm

    c = canvas.Canvas(output, pagesize=(page_width, page_height))

    for item in shipments:
        c.setLineWidth(0.35)

        c.rect(1 * mm, 1 * mm, 38 * mm, 48 * mm)

        c.setFont("Helvetica-Bold", 4.8)
        c.drawCentredString(
            20 * mm,
            47.2 * mm,
            "PTT GENEL MÜDÜRLÜĞÜ KARGO ETİKETİ"
        )

        c.rect(1 * mm, 39.5 * mm, 25 * mm, 6.8 * mm)
        c.rect(26 * mm, 39.5 * mm, 13 * mm, 6.8 * mm)

        c.setFont("Helvetica-Bold", 3.4)
        c.drawString(2 * mm, 44.4 * mm, "GÖNDERİCİ")
        c.setFont("Helvetica", 3.15)
        c.drawString(2 * mm, 42.6 * mm, "Ziraat Katılım Bankası A.Ş.")
        c.drawString(2 * mm, 40.9 * mm, "Hadımköy Lojistik Merkezi")

        c.setFont("Helvetica-Bold", 3.4)
        c.drawString(27 * mm, 44.2 * mm, "PTT KABUL")
        c.drawString(27 * mm, 42.2 * mm, "MERKEZİ")

        c.rect(1 * mm, 27 * mm, 38 * mm, 12.5 * mm)

        c.setFont("Helvetica-Bold", 3.5)
        c.drawString(2 * mm, 37.6 * mm, "ALICI")

        draw_wrapped(
            c,
            item.recipient_name,
            2 * mm,
            35.7 * mm,
            max_chars=34,
            max_lines=1,
            font="Helvetica-Bold",
            size=3.8,
            line_gap=2.8
        )

        draw_wrapped(
            c,
            item.address,
            2 * mm,
            33.2 * mm,
            max_chars=42,
            max_lines=2,
            font="Helvetica",
            size=3.2,
            line_gap=2.6
        )

        c.setFont("Helvetica", 3.2)
        c.drawString(
            2 * mm,
            28.1 * mm,
            kisalt(f"{item.district or ''} / {item.city or ''}", 42)
        )

        box_y = 21.8 * mm
        box_h = 5.2 * mm
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
            c.setFont("Helvetica-Bold", 2.9)
            c.drawCentredString(x + (box_w / 2), box_y + 3.5 * mm, titles[i])
            c.setFont("Helvetica", 2.8)
            c.drawCentredString(x + (box_w / 2), box_y + 1.2 * mm, kisalt(values[i], 11))

        c.rect(1 * mm, 15.8 * mm, 38 * mm, 6 * mm)
        c.setFont("Helvetica-Bold", 3.5)
        c.drawString(2 * mm, 19.8 * mm, "ÜRÜN İÇERİĞİ")
        c.setFont("Helvetica", 3.8)
        c.drawString(2 * mm, 17.4 * mm, kisalt(item.product_name, 38))

        c.rect(1 * mm, 1 * mm, 38 * mm, 14.8 * mm)

        barcode_value = str(item.tracking_number or item.barcode or "")

        barcode = code128.Code128(
            barcode_value,
            barHeight=7.2 * mm,
            barWidth=0.31
        )

        barcode.drawOn(c, 4.2 * mm, 6.2 * mm)

        c.setFont("Helvetica-Bold", 4.7)
        c.drawCentredString(
            20 * mm,
            3.2 * mm,
            barcode_value
        )

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
        if not selected_items:
            st.error("Seçili gönderi yok.")
        else:
            st.session_state.pdf_file = create_pdf(selected_items)
            st.session_state.pdf_name = "etiketler.pdf"
            st.rerun()

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

if st.session_state.pdf_file is not None:
    st.download_button(
        "PDF İndir",
        st.session_state.pdf_file,
        file_name=st.session_state.pdf_name,
        mime="application/pdf",
        use_container_width=True,
    )

st.divider()

header = st.columns([0.5, 1.4, 3.2, 3.2, 2.6, 1.8, 1, 1, 1])

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
        [0.5, 1.4, 3.2, 3.2, 2.6, 1.8, 1, 1, 1]
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
            st.markdown('<div class="status-red">Yazdırıldı</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-green">Yazdırılmadı</div>', unsafe_allow_html=True)

    with col2:
        st.write(kisalt(item.recipient_name, 45))

    with col3:
        st.write(kisalt(item.product_name, 45))

    with col4:
        st.write(str(item.tracking_number or ""))

    with col5:
        st.write(str(item.created_by or ""))

    with col6:
        if st.button("Detay", key=f"detay_{item.id}"):
            st.session_state[f"detay_{item.id}"] = not st.session_state.get(
                f"detay_{item.id}",
                False
            )
            st.rerun()

    with col7:
        if st.button("PDF", key=f"pdf_{item.id}"):
            st.session_state.pdf_file = create_pdf([item])
            st.session_state.pdf_name = f"etiket_{item.tracking_number}.pdf"
            st.rerun()

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
