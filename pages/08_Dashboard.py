import streamlit as st
from datetime import datetime

from utils.auth import require_login
from database.database import SessionLocal, engine
from database.models import Base, Shipment, Barcode, Branch, ProductDimension, User

require_login()

Base.metadata.create_all(bind=engine)

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


shipments = db.query(Shipment).all()
barcodes = db.query(Barcode).all()
branches = db.query(Branch).all()
products = db.query(ProductDimension).all()
users = db.query(User).all()

total_shipments = len(shipments)
printed = len([x for x in shipments if x.is_printed])
not_printed = len([x for x in shipments if not x.is_printed])
edited = len([x for x in shipments if getattr(x, "is_edited", False)])

unused_barcodes = len([x for x in barcodes if not x.is_used])
used_barcodes = len([x for x in barcodes if x.is_used])

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
        st.markdown(f'<div class="metric-value">{len(branches)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-sub">Kayıtlı şube</div>', unsafe_allow_html=True)

with m7:
    with st.container(border=True):
        st.markdown('<div class="metric-title">ÜRÜN ÖLÇÜSÜ</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(products)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-sub">Kayıtlı ürün ölçüsü</div>', unsafe_allow_html=True)

with m8:
    with st.container(border=True):
        st.markdown('<div class="metric-title">KULLANICI</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(users)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-sub">Panel kullanıcısı</div>', unsafe_allow_html=True)

st.write("")

left, right = st.columns([1.35, 1], gap="large")

with left:
    with st.container(border=True):
        st.markdown('<div class="clean-title">Son 10 Gönderi</div>', unsafe_allow_html=True)

        latest = (
            db.query(Shipment)
            .order_by(Shipment.id.desc())
            .limit(10)
            .all()
        )

        if not latest:
            st.info("Henüz gönderi yok.")
        else:
            for item in latest:
                status = "Yazdırıldı" if item.is_printed else "Yazdırılmadı"

                st.markdown(
                    f"""
                    <div class="row-card">
                        <div class="row-title">{item.recipient_name or ""}</div>
                        <div class="row-sub">
                            {item.tracking_number or ""} · {item.product_name or ""} · {status}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

with right:
    with st.container(border=True):
        st.markdown('<div class="clean-title">Kullanıcı Bazlı Gönderi</div>', unsafe_allow_html=True)

        user_counts = {}

        for item in shipments:
            key = item.created_by or "Bilinmiyor"
            user_counts[key] = user_counts.get(key, 0) + 1

        if not user_counts:
            st.info("Kayıt yok.")
        else:
            sorted_users = sorted(
                user_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )

            for username, count in sorted_users[:10]:
                st.markdown(
                    f"""
                    <div class="row-card">
                        <div class="row-title">{username}</div>
                        <div class="row-sub">{count} gönderi oluşturdu</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

st.write("")

with st.container(border=True):
    st.markdown('<div class="clean-title">En Çok Gönderi Alan Şubeler</div>', unsafe_allow_html=True)

    branch_counts = {}

    for item in shipments:
        key = item.branch_name or item.recipient_name or "Bilinmiyor"
        branch_counts[key] = branch_counts.get(key, 0) + 1

    if not branch_counts:
        st.info("Kayıt yok.")
    else:
        sorted_branches = sorted(
            branch_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        for branch_name, count in sorted_branches[:10]:
            st.markdown(
                f"""
                <div class="row-card">
                    <div class="row-title">{branch_name}</div>
                    <div class="row-sub">{count} gönderi</div>
                </div>
                """,
                unsafe_allow_html=True
            )
