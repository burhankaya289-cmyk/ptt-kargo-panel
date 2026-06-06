import sqlite3
from io import BytesIO

import pandas as pd
import streamlit as st

from utils.auth import require_login
from database.database import SessionLocal
from database.models import (
    User,
    Branch,
    Barcode,
    Shipment,
    ProductDimension
)

require_login()

db = SessionLocal()

st.markdown("""
<style>
.block-container {
    padding-top: 1.6rem !important;
}

.page-subtitle {
    color: #64748b;
    font-size: 13px;
}

.clean-title {
    font-size: 17px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 14px;
}

.download-card {
    padding: 12px;
    border-radius: 16px;
    border: 1px solid #dbe3ef;
    background: #f8fafc;
}
</style>
""", unsafe_allow_html=True)

st.title("Yedekleme")

st.markdown(
    '<div class="page-subtitle">Sistem verilerini dışa aktarın ve yedekleyin.</div>',
    unsafe_allow_html=True
)

st.write("")


def dataframe_download(data):
    output = BytesIO()

    pd.DataFrame(data).to_excel(
        output,
        index=False
    )

    output.seek(0)

    return output


with st.container(border=True):

    st.markdown(
        '<div class="clean-title">Veritabanı Yedeği</div>',
        unsafe_allow_html=True
    )

    try:
        with open("database/database.db", "rb") as f:
            st.download_button(
                "💾 Veritabanını İndir",
                f.read(),
                file_name="ptt_panel_backup.db",
                mime="application/octet-stream",
                use_container_width=True
            )
    except:
        st.warning("Veritabanı dosyası bulunamadı.")

st.write("")

col1, col2 = st.columns(2)

with col1:

    with st.container(border=True):

        st.markdown(
            '<div class="clean-title">Gönderiler</div>',
            unsafe_allow_html=True
        )

        shipments = db.query(Shipment).all()

        rows = []

        for x in shipments:
            rows.append({
                "Takip No": x.tracking_number,
                "Barkod": x.barcode,
                "Şube Kodu": x.branch_code,
                "Şube Adı": x.branch_name,
                "Alıcı": x.recipient_name,
                "Adres": x.address,
                "İlçe": x.district,
                "İl": x.city,
                "Telefon": x.phone,
                "Ürün": x.product_name,
                "En": x.width,
                "Boy": x.length,
                "Yükseklik": x.height,
                "Ağırlık": x.weight,
                "Kullanıcı": x.created_by,
                "Yazdırıldı": x.is_printed
            })

        st.download_button(
            "📦 Gönderileri Excel İndir",
            dataframe_download(rows),
            file_name="gonderiler.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

with col2:

    with st.container(border=True):

        st.markdown(
            '<div class="clean-title">Şubeler</div>',
            unsafe_allow_html=True
        )

        branches = db.query(Branch).all()

        rows = []

        for x in branches:
            rows.append({
                "Şube Kodu": x.branch_code,
                "Şube Adı": x.branch_name,
                "Adres": x.address,
                "İlçe": x.district,
                "İl": x.city
            })

        st.download_button(
            "🏢 Şubeleri Excel İndir",
            dataframe_download(rows),
            file_name="subeler.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

st.write("")

col3, col4 = st.columns(2)

with col3:

    with st.container(border=True):

        st.markdown(
            '<div class="clean-title">Barkodlar</div>',
            unsafe_allow_html=True
        )

        barcodes = db.query(Barcode).all()

        rows = []

        for x in barcodes:
            rows.append({
                "Barkod": x.barcode,
                "Kullanıldı": x.is_used
            })

        st.download_button(
            "🏷️ Barkodları Excel İndir",
            dataframe_download(rows),
            file_name="barkodlar.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

with col4:

    with st.container(border=True):

        st.markdown(
            '<div class="clean-title">Ürün Ölçüleri</div>',
            unsafe_allow_html=True
        )

        products = db.query(ProductDimension).all()

        rows = []

        for x in products:
            rows.append({
                "Ürün": x.product_name,
                "En": x.width,
                "Boy": x.length,
                "Yükseklik": x.height,
                "Ağırlık": x.weight
            })

        st.download_button(
            "📐 Ürün Ölçülerini İndir",
            dataframe_download(rows),
            file_name="urun_olculeri.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

st.write("")

with st.container(border=True):

    st.markdown(
        '<div class="clean-title">Kullanıcılar</div>',
        unsafe_allow_html=True
    )

    users = db.query(User).all()

    rows = []

    for x in users:
        rows.append({
            "Kullanıcı": x.username,
            "Rol": x.role
        })

    st.download_button(
        "👥 Kullanıcıları İndir",
        dataframe_download(rows),
        file_name="kullanicilar.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
