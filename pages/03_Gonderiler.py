import os
from io import BytesIO
from datetime import datetime

import pandas as pd
import streamlit as st

from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code128
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from sqlalchemy import text

from utils.auth import require_login
from database.database import SessionLocal, engine
from database.models import Base, Shipment

require_login()

Base.metadata.create_all(bind=engine)


def ensure_columns():
    try:
        with engine.connect() as conn:
            columns = conn.execute(
                text("PRAGMA table_info(shipments)")
            ).fetchall()

            column_names = [
                col[1]
                for col in columns
            ]

            if "is_edited" not in column_names:
                conn.execute(
                    text(
                        "ALTER TABLE shipments "
                        "ADD COLUMN is_edited BOOLEAN DEFAULT 0"
                    )
                )
                conn.commit()

    except Exception:
        pass


ensure_columns()

db = SessionLocal()

try:
    if os.path.exists("fonts/DejaVuSans.ttf"):
        pdfmetrics.registerFont(
            TTFont(
                "DejaVu",
                "fonts/DejaVuSans.ttf"
            )
        )
        PDF_FONT = "DejaVu"
    else:
        PDF_FONT = "Helvetica"

    if os.path.exists("fonts/DejaVuSans-Bold.ttf"):
        pdfmetrics.registerFont(
            TTFont(
                "DejaVu-Bold",
                "fonts/DejaVuSans-Bold.ttf"
            )
        )
        PDF_FONT_BOLD = "DejaVu-Bold"
    else:
        PDF_FONT_BOLD = "Helvetica-Bold"

except Exception:
    PDF_FONT = "Helvetica"
    PDF_FONT_BOLD = "Helvetica-Bold"


st.markdown("""
<style>
.block-container {
    padding-top: 1.6rem !important;
    padding-left: 1.8rem !important;
    padding-right: 1.8rem !important;
    max-width: 100% !important;
}

h1 {
    font-size: 30px !important;
    font-weight: 800 !important;
    margin-bottom: 0 !important;
}

h2, h3 {
    font-size: 17px !important;
    font-weight: 800 !important;
}

.page-subtitle {
    color: #64748b;
    font-size: 13px;
    margin-top: 6px;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 18px !important;
    background: #ffffff !important;
    border: 1px solid #dbe3ef !important;
    box-shadow: 0 12px 34px rgba(15,23,42,0.05) !important;
}

.stTextInput label,
.stSelectbox label,
.stNumberInput label {
    font-size: 12px !important;
    color: #334155 !important;
    font-weight: 700 !important;
}

.stTextInput input,
.stNumberInput input,
.stSelectbox div[data-baseweb="select"] > div {
    background: #f8fafc !important;
    border: 1px solid #dbe3ef !important;
    border-radius: 12px !important;
    min-height: 42px !important;
    font-size: 13px !important;
}

.stButton button,
.stDownloadButton button {
    border-radius: 12px !important;
    min-height: 40px !important;
    font-weight: 800 !important;
    border: 1px solid #dbe3ef !important;
}

.stButton button:hover,
.stDownloadButton button:hover {
    border-color: #1672f3 !important;
    color: #1672f3 !important;
}

div[data-testid="stButton"] button[kind="primary"] {
    background: #1669f2 !important;
    color: white !important;
    border: 1px solid #1669f2 !important;
}

.clean-title {
    font-size: 17px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 14px;
}

.top-info {
    background: #dbeafe;
    color: #1263d8;
    padding: 10px 16px;
    border-radius: 14px;
    font-weight: 800;
    font-size: 13px;
    text-align: center;
}

.shipment-card {
    background: #ffffff;
    border: 1px solid #dbe3ef;
    border-radius: 18px;
    padding: 16px;
    margin-bottom: 12px;
    box-shadow: 0 10px 28px rgba(15,23,42,0.04);
}

.shipment-title {
    font-size: 15px;
    font-weight: 800;
    color: #0f172a;
}

.shipment-sub {
    font-size: 12px;
    color: #64748b;
    margin-top: 4px;
}

.status-green {
    background: #e8f8ee;
    color: #17623a;
    padding: 7px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 800;
    text-align: center;
}

.status-red {
    background: #ffe8e8;
    color: #8a1f1f;
    padding: 7px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 800;
    text-align: center;
}

.status-yellow {
    background: #fff6db;
    color: #8a6100;
    padding: 7px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 800;
    text-align: center;
}

.mini-label {
    color: #64748b;
    font-size: 11px;
    font-weight: 700;
}

.mini-value {
    color: #0f172a;
    font-size: 13px;
    font-weight: 700;
}

.empty-box {
    border: 2px dashed #dbe3ef;
    border-radius: 16px;
    min-height: 180px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #64748b;
    font-size: 14px;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)


def kisalt(text, limit):
    return str(text or "")[:limit]


def bool_value(value):
    return bool(value) if value is not None else False


def get_status(item):
    if bool_value(getattr(item, "is_edited", False)):
        return "Düzenlendi"

    if bool_value(getattr(item, "is_printed", False)):
        return "Yazdırıldı"

    return "Yazdırılmadı"


def status_html(status):
    if status == "Düzenlendi":
        return '<div class="status-yellow">🟡 Düzenlendi</div>'

    if status == "Yazdırıldı":
        return '<div class="status-red">🔴 Yazdırıldı</div>'

    return '<div class="status-green">🟢 Yazdırılmadı</div>'


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

    pd.DataFrame(rows).to_excel(
        output,
        index=False
    )

    output.seek(0)

    return output


def draw_wrapped(
    c,
    text,
    x,
    y,
    max_chars,
    max_lines,
    font=None,
    size=8,
    gap=9
):
    if font is None:
        font = PDF_FONT

    text = str(text or "").strip()
    words = text.split()

    lines = []
    line = ""

    for word in words:
        test = f"{line} {word}".strip()

        if len(test) <= max_chars:
            line = test
        else:
            if line:
                lines.append(line)

            line = word

    if line:
        lines.append(line)

    c.setFont(font, size)

    for line in lines[:max_lines]:
        c.drawString(x, y, line)
        y -= gap


def create_pdf(shipments):
    output = BytesIO()

    page_width = 100 * mm
    page_height = 110 * mm

    c = canvas.Canvas(
        output,
        pagesize=(page_width, page_height)
    )

    for item in shipments:
        c.setLineWidth(0.8)

        c.rect(
            4 * mm,
            4 * mm,
            92 * mm,
            102 * mm
        )

        c.setFont(PDF_FONT_BOLD, 13)
        c.drawCentredString(
            50 * mm,
            101 * mm,
            "PTT GENEL MÜDÜRLÜĞÜ KARGO ETİKETİ"
        )

        c.setFont(PDF_FONT_BOLD, 6.2)
        c.drawCentredString(
            50 * mm,
            96.5 * mm,
            "***PTT GENEL MÜDÜRLÜĞÜ'NÜN 08/03/2011 VE 1918 SAYILI İZNİYLE BASILMIŞTIR.***"
        )

        c.line(
            4 * mm,
            93 * mm,
            96 * mm,
            93 * mm
        )

        c.rect(4 * mm, 77 * mm, 64 * mm, 16 * mm)
        c.rect(68 * mm, 77 * mm, 28 * mm, 16 * mm)

        c.setFont(PDF_FONT_BOLD, 6.5)
        c.drawString(6 * mm, 90 * mm, "GÖNDERİCİ")

        c.setFont(PDF_FONT, 6.5)
        c.drawString(
            6 * mm,
            86.5 * mm,
            "Ziraat Katılım Bankası A.Ş. (Hadımköy Lojistik Merkezi)"
        )
        c.drawString(
            6 * mm,
            83 * mm,
            "Ömerli Mah. Nusret Cad. No:21 (2. Bodrum Kat)"
        )
        c.drawString(
            6 * mm,
            79.5 * mm,
            "Arnavutköy / İstanbul"
        )

        c.setFont(PDF_FONT_BOLD, 6.5)
        c.drawString(70 * mm, 90 * mm, "KAB. MRKZ")

        c.setFont(PDF_FONT, 6.5)
        c.drawString(70 * mm, 86.5 * mm, "Avrupa Yakası K.I.M")
        c.drawString(70 * mm, 83 * mm, "KAB.T: K.at.Zira")
        c.drawString(70 * mm, 79.5 * mm, "S.NO: 1")

        c.rect(4 * mm, 50 * mm, 92 * mm, 27 * mm)

        c.setFont(PDF_FONT_BOLD, 6.5)
        c.drawString(6 * mm, 73.5 * mm, "ALICI")

        draw_wrapped(
            c,
            item.recipient_name,
            6 * mm,
            69.5 * mm,
            max_chars=42,
            max_lines=2,
            font=PDF_FONT_BOLD,
            size=10,
            gap=10
        )

        draw_wrapped(
            c,
            item.address,
            6 * mm,
            61 * mm,
            max_chars=58,
            max_lines=2,
            font=PDF_FONT_BOLD,
            size=7.6,
            gap=8
        )

        c.setFont(PDF_FONT_BOLD, 9.5)
        c.drawString(
            6 * mm,
            52.5 * mm,
            kisalt(
                f"{item.district or ''} / {item.city or ''}",
                45
            )
        )

        c.rect(4 * mm, 39 * mm, 23 * mm, 11 * mm)
        c.rect(27 * mm, 39 * mm, 28 * mm, 11 * mm)
        c.rect(55 * mm, 39 * mm, 23 * mm, 11 * mm)
        c.rect(78 * mm, 39 * mm, 18 * mm, 11 * mm)

        c.setFont(PDF_FONT_BOLD, 6)
        c.drawString(6 * mm, 47 * mm, "TARİH")
        c.drawString(29 * mm, 47 * mm, "EBAT/DESİ")
        c.drawString(57 * mm, 47 * mm, "AĞIRLIK (GR)")
        c.drawString(80 * mm, 47 * mm, "ŞUBE KODU")

        c.setFont(PDF_FONT_BOLD, 9.5)
        c.drawCentredString(
            15.5 * mm,
            42 * mm,
            datetime.now().strftime("%d.%m.%Y")
        )

        c.setFont(PDF_FONT_BOLD, 6.5)
        c.drawCentredString(
            41 * mm,
            43.2 * mm,
            f"{item.width}x{item.length}x{item.height}"
        )
        c.drawCentredString(
            41 * mm,
            40.3 * mm,
            "(Ds:1)"
        )

        c.setFont(PDF_FONT_BOLD, 10.5)
        c.drawCentredString(
            66.5 * mm,
            42 * mm,
            str(int(item.weight or 0))
        )

        c.setFont(PDF_FONT_BOLD, 9.5)
        c.drawCentredString(
            87 * mm,
            42 * mm,
            str(item.branch_code or "")
        )

        c.rect(4 * mm, 27 * mm, 56 * mm, 12 * mm)
        c.rect(60 * mm, 27 * mm, 18 * mm, 12 * mm)
        c.rect(78 * mm, 27 * mm, 18 * mm, 12 * mm)

        c.setFont(PDF_FONT_BOLD, 6)
        c.drawString(6 * mm, 36 * mm, "ÜRÜN İÇERİĞİ")
        c.drawString(62 * mm, 36 * mm, "EK HİZMETLER")
        c.drawString(80 * mm, 36 * mm, "BEYAN DEĞERİ")

        c.setFont(PDF_FONT_BOLD, 8.5)
        c.drawString(
            6 * mm,
            31.5 * mm,
            kisalt(item.product_name, 34)
        )

        c.setFont(PDF_FONT, 8.5)
        c.drawCentredString(69 * mm, 31.5 * mm, "-")
        c.drawCentredString(87 * mm, 31.5 * mm, "-")

        c.rect(4 * mm, 4 * mm, 92 * mm, 23 * mm)

        barcode_value = str(
            item.tracking_number
            or item.barcode
            or ""
        )

        barcode = code128.Code128(
            barcode_value,
            barHeight=17 * mm,
            barWidth=0.68
        )

        barcode.drawOn(
            c,
            18 * mm,
            9 * mm
        )

        c.setFont(PDF_FONT_BOLD, 13)
        c.drawCentredString(
            50 * mm,
            5.8 * mm,
            barcode_value
        )

        c.showPage()

    c.save()

    output.seek(0)

    return output


def mark_printed(ids):
    items = (
        db.query(Shipment)
        .filter(Shipment.id.in_(ids))
        .all()
    )

    for item in items:
        item.is_printed = True
        item.is_edited = False

    db.commit()


st.title("Oluşturulan Barkodlar")

st.markdown(
    '<div class="page-subtitle">Oluşturulan gönderileri görüntüleyin, yazdırın ve dışa aktarın.</div>',
    unsafe_allow_html=True
)

st.write("")

with st.container(border=True):
    st.markdown(
        '<div class="clean-title">Filtreler</div>',
        unsafe_allow_html=True
    )

    f1, f2, f3, f4, f5 = st.columns(
        [1.2, 1.2, 1.2, 1.2, 1.1]
    )

    with f1:
        filtre_alici = st.text_input("Alıcı Adı")

    with f2:
        filtre_urun = st.text_input("Ürün İçeriği")

    with f3:
        filtre_takip = st.text_input("Takip No")

    with f4:
        filtre_kullanici = st.text_input("Kullanıcı Adı")

    with f5:
        durum = st.selectbox(
            "Durum",
            [
                "Tümü",
                "Yazdırılmadı",
                "Yazdırıldı",
                "Düzenlendi"
            ]
        )

gonderiler = (
    db.query(Shipment)
    .order_by(Shipment.id.desc())
    .all()
)

filtered = []

for item in gonderiler:
    if filtre_alici and filtre_alici.lower() not in str(item.recipient_name or "").lower():
        continue

    if filtre_urun and filtre_urun.lower() not in str(item.product_name or "").lower():
        continue

    if filtre_takip and filtre_takip.lower() not in str(item.tracking_number or "").lower():
        continue

    if filtre_kullanici and filtre_kullanici.lower() not in str(item.created_by or "").lower():
        continue

    item_status = get_status(item)

    if durum != "Tümü" and item_status != durum:
        continue

    filtered.append(item)

filtered_ids = [
    item.id
    for item in filtered
]

selected_ids = []

for item_id in filtered_ids:
    if st.session_state.get(f"sec_{item_id}", False):
        selected_ids.append(item_id)

selected_items = [
    item
    for item in filtered
    if item.id in selected_ids
]

st.write("")

with st.container(border=True):
    a1, a2, a3, a4, a5, a6 = st.columns(
        [1.1, 1.1, 1.3, 1.3, 1.2, 1.2]
    )

    with a1:
        st.markdown(
            f'<div class="top-info">Toplam: {len(filtered)}</div>',
            unsafe_allow_html=True
        )

    with a2:
        st.markdown(
            f'<div class="top-info">Seçili: {len(selected_ids)}</div>',
            unsafe_allow_html=True
        )

    with a3:
        if st.button("✓ Tümünü Seç", use_container_width=True):
            for item_id in filtered_ids:
                st.session_state[f"sec_{item_id}"] = True

            st.rerun()

    with a4:
        if st.button("✕ Temizle", use_container_width=True):
            for item_id in filtered_ids:
                st.session_state[f"sec_{item_id}"] = False

            st.rerun()

    with a5:
        if selected_items:
            st.download_button(
                "🖨️ Yazdır",
                create_pdf(selected_items),
                file_name="secilen_etiketler.pdf",
                mime="application/pdf",
                use_container_width=True,
                on_click=mark_printed,
                args=([item.id for item in selected_items],)
            )
        else:
            st.button(
                "🖨️ Yazdır",
                use_container_width=True,
                disabled=True
            )

    with a6:
        if selected_items:
            st.download_button(
                "📊 Excel",
                create_excel(selected_items),
                file_name="gonderiler.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else:
            st.button(
                "📊 Excel",
                use_container_width=True,
                disabled=True
            )

    s1, s2 = st.columns([1.2, 5])

    with s1:
        if selected_items:
            if st.button("🗑️ Sil", use_container_width=True):
                for item in selected_items:
                    db.delete(item)

                db.commit()

                for item_id in selected_ids:
                    st.session_state[f"sec_{item_id}"] = False

                st.rerun()
        else:
            st.button(
                "🗑️ Sil",
                use_container_width=True,
                disabled=True
            )

st.write("")

if not filtered:
    st.markdown(
        '<div class="empty-box">Kayıt bulunamadı.</div>',
        unsafe_allow_html=True
    )

else:
    for item in filtered:
        status = get_status(item)

        st.markdown(
            '<div class="shipment-card">',
            unsafe_allow_html=True
        )

        c0, c1, c2, c3, c4 = st.columns(
            [0.35, 2.2, 1.4, 1.2, 1.2]
        )

        with c0:
            st.checkbox(
                "",
                key=f"sec_{item.id}"
            )

        with c1:
            st.markdown(
                f'<div class="shipment-title">{kisalt(item.recipient_name, 55)}</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="shipment-sub">{item.branch_code or ""} - {item.branch_name or ""}</div>',
                unsafe_allow_html=True
            )

        with c2:
            st.markdown(
                f'<div class="mini-label">Ürün</div><div class="mini-value">{kisalt(item.product_name, 38)}</div>',
                unsafe_allow_html=True
            )

        with c3:
            st.markdown(
                f'<div class="mini-label">Takip No</div><div class="mini-value">{item.tracking_number or ""}</div>',
                unsafe_allow_html=True
            )

        with c4:
            st.markdown(
                status_html(status),
                unsafe_allow_html=True
            )

        d1, d2, d3, d4, d5 = st.columns(
            [1.3, 1.3, 1.3, 1.3, 4]
        )

        with d1:
            if st.button(
                "Detay",
                key=f"detay_{item.id}",
                use_container_width=True
            ):
                st.session_state[f"detay_{item.id}"] = not st.session_state.get(
                    f"detay_{item.id}",
                    False
                )

                st.rerun()

        with d2:
            st.download_button(
                "PDF",
                create_pdf([item]),
                file_name=f"etiket_{item.tracking_number}.pdf",
                mime="application/pdf",
                key=f"pdf_{item.id}",
                use_container_width=True,
                on_click=mark_printed,
                args=([item.id],)
            )

        with d3:
            if st.button(
                "Düzenle",
                key=f"duzenle_{item.id}",
                use_container_width=True
            ):
                st.session_state[f"edit_{item.id}"] = not st.session_state.get(
                    f"edit_{item.id}",
                    False
                )

                st.rerun()

        with d4:
            if st.button(
                "Sil",
                key=f"sil_{item.id}",
                use_container_width=True
            ):
                db.delete(item)
                db.commit()
                st.rerun()

        if st.session_state.get(f"detay_{item.id}", False):
            st.info(
                f"""
Şube Kodu: {item.branch_code}

Şube Adı: {item.branch_name}

Adres: {item.address}

İlçe: {item.district}

İl: {item.city}

Telefon: {item.phone}

En: {item.width}

Boy: {item.length}

Yükseklik: {item.height}

Ağırlık: {item.weight}

Kullanıcı: {item.created_by}
"""
            )

        if st.session_state.get(f"edit_{item.id}", False):
            with st.form(f"edit_form_{item.id}"):
                e1, e2 = st.columns(2)

                with e1:
                    recipient_name = st.text_input(
                        "Alıcı Adı",
                        value=item.recipient_name or ""
                    )

                    product_name = st.text_input(
                        "Ürün İçeriği",
                        value=item.product_name or ""
                    )

                    phone = st.text_input(
                        "Telefon",
                        value=item.phone or ""
                    )

                with e2:
                    address = st.text_input(
                        "Adres",
                        value=item.address or ""
                    )

                    district = st.text_input(
                        "İlçe",
                        value=item.district or ""
                    )

                    city = st.text_input(
                        "İl",
                        value=item.city or ""
                    )

                o1, o2, o3, o4 = st.columns(4)

                with o1:
                    width = st.number_input(
                        "En",
                        value=float(item.width or 0)
                    )

                with o2:
                    length = st.number_input(
                        "Boy",
                        value=float(item.length or 0)
                    )

                with o3:
                    height = st.number_input(
                        "Yükseklik",
                        value=float(item.height or 0)
                    )

                with o4:
                    weight = st.number_input(
                        "Ağırlık",
                        value=float(item.weight or 0)
                    )

                kaydet = st.form_submit_button(
                    "Düzenlemeyi Kaydet"
                )

                if kaydet:
                    item.recipient_name = recipient_name
                    item.product_name = product_name
                    item.phone = phone
                    item.address = address
                    item.district = district
                    item.city = city
                    item.width = width
                    item.length = length
                    item.height = height
                    item.weight = weight
                    item.is_edited = True
                    item.is_printed = False

                    db.commit()

                    st.session_state[f"edit_{item.id}"] = False

                    st.success("Gönderi düzenlendi.")
                    st.rerun()

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )
