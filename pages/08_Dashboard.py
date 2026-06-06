import streamlit as st
from datetime import datetime

from sqlalchemy import func

from utils.auth import require_login
from database.database import SessionLocal
from database.models import Shipment, Barcode, Branch, ProductDimension, User

require_login()

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

.metric-title {
    color: #64748b;
    font-size: 12px;
    font-weight: 800;
}

.metric-value {
    color: #0f172a;
    font-size: 30px;
    font-weight: 900;
    margin-top: 6px;
}

.metric-sub {
    color: #64748b;
    font-size: 12px;
    margin-top: 4px;
}

.clean-title {
    font-size: 17px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 14px;
}

.row-card {
    background: #f8fafc;
    border: 1px solid #dbe3ef;
    border-radius: 14px;
    padding: 12px 14px;
    margin-bottom: 10px;
}

.row-title {
    font-size: 13px;
    font-weight: 800;
    color: #0f172a;
}

.row-sub {
    font-size: 12px;
    color: #64748b;
    margin-top: 3px;
}
</style>
""", unsafe_allow_html=True)


def today_str():
    return datetime.now().strftime("%d.%m.%Y")


total_shipments = db.query(func.count(Shipment.id)).scalar() or 0
printed = db.query(func.count(Shipment.id)).filter(Shipment.is_printed == True).scalar() or 0
not_printed = db.query(func.count(Shipment.id)).filter(Shipment.is_printed == False).scalar() or 0
edited = db.query(func.count(Shipment.id)).filter(Shipment.is_edited == True).scalar() or 0

unused_barcodes = db.query(func.count(Barcode.id)).filter(Barcode.is_used == False).scalar() or 0
used_barcodes = db.query(func.count(Barcode.id)).filter(Barcode.is_used == True).scalar() or 0

branch_count = db.query(func.count(Branch.id)).scalar() or 0
product_count = db.query(func.count(ProductDimension.id)).scalar() or 0
user_count = db.query(func.count(User.id)).scalar() or 0

st.title("Dashboard")
st.markdown(
    f'<div class="page-subtitle">Genel panel özeti · {today_str()}</div>',
    unsafe_allow_html=True
)

st.write("")

m1, m2, m3, m4 = st.columns(4)

with m1:
    with st.container(border=True):
        st.markdown('<div class="metric-title">TOPLAM GÖNDERİ</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{total_shipments}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-sub">Sistemde kayıtlı gönderi</div>', unsafe_allow_html=True)

with m2:
    with st.container(border=True):
        st.markdown('<div class="metric-title">YAZDIRILMADI</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{not_printed}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-sub">PDF etiketi bekleyen</div>', unsafe_allow_html=True)

with m3:
    with st.container(border=True):
        st.markdown('<div class="metric-title">YAZDIRILDI</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{printed}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-sub">Etiketi oluşturulan</div>', unsafe_allow_html=True)

with m4:
    with st.container(border=True):
        st.markdown('<div class="metric-title">KALAN BARKOD</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{unused_barcodes}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-sub">Kullanılan: {used_barcodes}</div>', unsafe_allow_html=True)

st.write("")

m5, m6, m7, m8 = st.columns(4)

with m5:
    with st.container(border=True):
        st.markdown('<div class="metric-title">DÜZENLENEN</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{edited}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-sub">Değişiklik yapılan gönderi</div>', unsafe_allow_html=True)

with m6:
    with st.container(border=True):
        st.markdown('<div class="metric-title">ŞUBE SAYISI</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{branch_count}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-sub">Kayıtlı şube</div>', unsafe_allow_html=True)

with m7:
    with st.container(border=True):
        st.markdown('<div class="metric-title">ÜRÜN ÖLÇÜSÜ</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{product_count}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-sub">Kayıtlı ürün ölçüsü</div>', unsafe_allow_html=True)

with m8:
    with st.container(border=True):
        st.markdown('<div class="metric-title">KULLANICI</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{user_count}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-sub">Panel kullanıcısı</div>', unsafe_allow_html=True)

st.write("")

with st.container(border=True):
    st.markdown('<div class="clean-title">Kullanıcı Bazlı Gönderi</div>', unsafe_allow_html=True)

    user_counts = (
        db.query(
            Shipment.created_by,
            func.count(Shipment.id)
        )
        .group_by(Shipment.created_by)
        .order_by(func.count(Shipment.id).desc())
        .limit(10)
        .all()
    )

    if not user_counts:
        st.info("Kayıt yok.")
    else:
        for username, count in user_counts:
            st.markdown(
                f"""
                <div class="row-card">
                    <div class="row-title">{username or "Bilinmiyor"}</div>
                    <div class="row-sub">{count} gönderi oluşturdu</div>
                </div>
                """,
                unsafe_allow_html=True
            )

st.write("")

with st.container(border=True):
    st.markdown('<div class="clean-title">En Çok Gönderi Alan Şubeler</div>', unsafe_allow_html=True)

    branch_counts = (
        db.query(
            Shipment.branch_name,
            func.count(Shipment.id)
        )
        .group_by(Shipment.branch_name)
        .order_by(func.count(Shipment.id).desc())
        .limit(10)
        .all()
    )

    if not branch_counts:
        st.info("Kayıt yok.")
    else:
        for branch_name, count in branch_counts:
            st.markdown(
                f"""
                <div class="row-card">
                    <div class="row-title">{branch_name or "Bilinmiyor"}</div>
                    <div class="row-sub">{count} gönderi</div>
                </div>
                """,
                unsafe_allow_html=True
            )

db.close()
