import streamlit as st

from utils.auth import require_login, is_admin
from database.database import SessionLocal, engine
from database.models import Base, Setting

require_login()

if not is_admin():
    st.error("Bu sayfaya sadece Admin erişebilir.")
    st.stop()



db = SessionLocal()

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

.clean-title {
    font-size: 17px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 14px;
}
</style>
""", unsafe_allow_html=True)


DEFAULTS = {
    "sender_name": "Ziraat Katılım Bankası A.Ş. (Hadımköy Lojistik Merkezi)",
    "sender_address_1": "Ömerli Mah. Nusret Cad. No:21 (2. Bodrum Kat)",
    "sender_address_2": "Arnavutköy / İstanbul",
    "acceptance_center_1": "Avrupa Yakası K.I.M",
    "acceptance_center_2": "KAB.T: K.at.Zira",
    "acceptance_center_3": "S.NO: 1",

    "pdf_title": "PTT GENEL MÜDÜRLÜĞÜ KARGO ETİKETİ",
    "pdf_permission_text": "***PTT GENEL MÜDÜRLÜĞÜ'NÜN 08/03/2011 VE 1918 SAYILI İZNİYLE BASILMIŞTIR.***",

    "label_width_mm": "100",
    "label_height_mm": "110",

    "font_title": "13",
    "font_permission": "6.2",
    "font_sender_label": "6.5",
    "font_sender_text": "6.5",
    "font_recipient_label": "6.5",
    "font_recipient_name": "10",
    "font_address": "7.6",
    "font_city": "9.5",
    "font_box_label": "6",
    "font_product": "8.5",
    "font_barcode_text": "13",

    "barcode_height_mm": "17",
    "barcode_width": "0.68",
}


def get_setting(key):
    item = db.query(Setting).filter(Setting.key == key).first()

    if item:
        return item.value

    return DEFAULTS.get(key, "")


def set_setting(key, value):
    item = db.query(Setting).filter(Setting.key == key).first()

    if item:
        item.value = str(value)
    else:
        db.add(
            Setting(
                key=key,
                value=str(value)
            )
        )


st.title("Sistem Ayarları")

st.markdown(
    '<div class="page-subtitle">PDF etiketi ve panel varsayılanlarını buradan yönetin.</div>',
    unsafe_allow_html=True
)

st.write("")

with st.form("settings_form"):

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown('<div class="clean-title">Gönderici Bilgileri</div>', unsafe_allow_html=True)

            sender_name = st.text_input("Gönderici Adı", value=get_setting("sender_name"))
            sender_address_1 = st.text_input("Gönderici Adres 1", value=get_setting("sender_address_1"))
            sender_address_2 = st.text_input("Gönderici Adres 2", value=get_setting("sender_address_2"))

    with col2:
        with st.container(border=True):
            st.markdown('<div class="clean-title">Kabul Merkezi</div>', unsafe_allow_html=True)

            acceptance_center_1 = st.text_input("Kabul Merkezi 1", value=get_setting("acceptance_center_1"))
            acceptance_center_2 = st.text_input("Kabul Merkezi 2", value=get_setting("acceptance_center_2"))
            acceptance_center_3 = st.text_input("Kabul Merkezi 3", value=get_setting("acceptance_center_3"))

    st.write("")

    with st.container(border=True):
        st.markdown('<div class="clean-title">PDF Başlık ve Etiket Ölçüsü</div>', unsafe_allow_html=True)

        p1, p2 = st.columns(2)

        with p1:
            pdf_title = st.text_input("PDF Başlığı", value=get_setting("pdf_title"))
            pdf_permission_text = st.text_input("İzin Yazısı", value=get_setting("pdf_permission_text"))

        with p2:
            label_width_mm = st.number_input(
                "Etiket Genişliği (mm)",
                value=float(get_setting("label_width_mm")),
                step=1.0
            )

            label_height_mm = st.number_input(
                "Etiket Yüksekliği (mm)",
                value=float(get_setting("label_height_mm")),
                step=1.0
            )

    st.write("")

    with st.container(border=True):
        st.markdown('<div class="clean-title">PDF Yazı Boyutları</div>', unsafe_allow_html=True)

        f1, f2, f3, f4 = st.columns(4)

        with f1:
            font_title = st.number_input("Başlık", value=float(get_setting("font_title")), step=0.5)
            font_permission = st.number_input("İzin Yazısı", value=float(get_setting("font_permission")), step=0.5)
            font_sender_label = st.number_input("Gönderici Başlığı", value=float(get_setting("font_sender_label")), step=0.5)

        with f2:
            font_sender_text = st.number_input("Gönderici Metni", value=float(get_setting("font_sender_text")), step=0.5)
            font_recipient_label = st.number_input("Alıcı Başlığı", value=float(get_setting("font_recipient_label")), step=0.5)
            font_recipient_name = st.number_input("Alıcı Adı", value=float(get_setting("font_recipient_name")), step=0.5)

        with f3:
            font_address = st.number_input("Adres", value=float(get_setting("font_address")), step=0.5)
            font_city = st.number_input("İl / İlçe", value=float(get_setting("font_city")), step=0.5)
            font_box_label = st.number_input("Kutu Başlıkları", value=float(get_setting("font_box_label")), step=0.5)

        with f4:
            font_product = st.number_input("Ürün İçeriği", value=float(get_setting("font_product")), step=0.5)
            font_barcode_text = st.number_input("Barkod Numarası", value=float(get_setting("font_barcode_text")), step=0.5)

    st.write("")

    with st.container(border=True):
        st.markdown('<div class="clean-title">Barkod Ayarları</div>', unsafe_allow_html=True)

        b1, b2 = st.columns(2)

        with b1:
            barcode_height_mm = st.number_input(
                "Barkod Yüksekliği (mm)",
                value=float(get_setting("barcode_height_mm")),
                step=1.0
            )

        with b2:
            barcode_width = st.number_input(
                "Barkod Kalınlığı",
                value=float(get_setting("barcode_width")),
                step=0.01,
                format="%.2f"
            )

    submitted = st.form_submit_button("Ayarları Kaydet", use_container_width=True)

    if submitted:
        values = {
            "sender_name": sender_name,
            "sender_address_1": sender_address_1,
            "sender_address_2": sender_address_2,
            "acceptance_center_1": acceptance_center_1,
            "acceptance_center_2": acceptance_center_2,
            "acceptance_center_3": acceptance_center_3,
            "pdf_title": pdf_title,
            "pdf_permission_text": pdf_permission_text,
            "label_width_mm": label_width_mm,
            "label_height_mm": label_height_mm,
            "font_title": font_title,
            "font_permission": font_permission,
            "font_sender_label": font_sender_label,
            "font_sender_text": font_sender_text,
            "font_recipient_label": font_recipient_label,
            "font_recipient_name": font_recipient_name,
            "font_address": font_address,
            "font_city": font_city,
            "font_box_label": font_box_label,
            "font_product": font_product,
            "font_barcode_text": font_barcode_text,
            "barcode_height_mm": barcode_height_mm,
            "barcode_width": barcode_width,
        }

        for key, value in values.items():
            set_setting(key, value)

        db.commit()

        st.success("Ayarlar kaydedildi.")
        st.rerun()
