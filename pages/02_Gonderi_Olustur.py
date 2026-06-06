import streamlit as st

from utils.auth import require_login
from database.database import SessionLocal, engine
from database.models import Base, Branch, ProductDimension, Barcode, Shipment

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
h2, h3 {
    font-size: 17px !important;
    font-weight: 800 !important;
}
.page-subtitle {
    color: #64748b;
    font-size: 13px;
    margin-top: 6px;
}
.top-badge {
    background: #dbeafe;
    color: #1263d8;
    padding: 11px 20px;
    border-radius: 14px;
    font-weight: 800;
    font-size: 13px;
    text-align: center;
    min-width: 260px;
}
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 18px !important;
    background: #ffffff !important;
    border: 1px solid #dbe3ef !important;
    box-shadow: 0 12px 34px rgba(15,23,42,0.05) !important;
}
.stTextInput label,
.stNumberInput label {
    font-size: 12px !important;
    color: #334155 !important;
    font-weight: 700 !important;
}
.stTextInput input,
.stNumberInput input {
    background: #f8fafc !important;
    border: 1px solid #dbe3ef !important;
    border-radius: 12px !important;
    min-height: 44px !important;
    font-size: 13px !important;
}
.stButton button {
    border-radius: 12px !important;
    min-height: 42px !important;
    font-weight: 800 !important;
    border: 1px solid #dbe3ef !important;
}
.stButton button:hover {
    border-color: #1672f3 !important;
    color: #1672f3 !important;
}
div[data-testid="stButton"] button[kind="primary"] {
    background: #1669f2 !important;
    color: white !important;
    border: 1px solid #1669f2 !important;
}
.cart-empty {
    border: 2px dashed #dbe3ef;
    border-radius: 16px;
    min-height: 330px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #64748b;
    font-size: 15px;
    font-weight: 600;
}
.cart-item {
    background: #f8fafc;
    border: 1px solid #dbe3ef;
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 12px;
}
.cart-item-title {
    font-size: 14px;
    font-weight: 800;
    color: #0f172a;
}
.cart-item-sub {
    color: #64748b;
    font-size: 12px;
    margin-top: 4px;
}
.clean-title {
    font-size: 17px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 18px;
}
.qty-box {
    height: 42px;
    border: 1px solid #dbe3ef;
    background: #f8fafc;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    color: #0f172a;
}
.suggestion-button button {
    justify-content: flex-start !important;
    text-align: left !important;
    background: #f8fafc !important;
}
</style>
""", unsafe_allow_html=True)

if "sepet" not in st.session_state:
    st.session_state.sepet = []

if "adet" not in st.session_state:
    st.session_state.adet = 1

if "branch_input" not in st.session_state:
    st.session_state.branch_input = ""

if "product_input" not in st.session_state:
    st.session_state.product_input = ""


def norm(value):
    return str(value or "").strip().lower()


def temizle(value):
    return str(value or "").strip()


def kalan_barkod_sayisi():
    used_in_cart = [x["barcode"] for x in st.session_state.sepet]

    barcodes = (
        db.query(Barcode)
        .filter(Barcode.is_used == False)
        .order_by(Barcode.id.asc())
        .all()
    )

    count = 0

    for b in barcodes:
        if b.barcode not in used_in_cart:
            count += 1

    return count


def get_available_barcodes(count):
    used_in_cart = [x["barcode"] for x in st.session_state.sepet]

    barcodes = (
        db.query(Barcode)
        .filter(Barcode.is_used == False)
        .order_by(Barcode.id.asc())
        .all()
    )

    result = []

    for b in barcodes:
        if b.barcode not in used_in_cart:
            result.append(b)

        if len(result) == count:
            break

    return result


def all_branches():
    return (
        db.query(Branch)
        .order_by(Branch.branch_code.asc())
        .all()
    )


def all_products():
    return (
        db.query(ProductDimension)
        .order_by(ProductDimension.product_name.asc())
        .all()
    )


def branch_exact(search_text):
    search_text_clean = temizle(search_text)
    search_text_norm = norm(search_text)

    if not search_text_norm:
        return None

    branches = all_branches()

    for b in branches:
        full_label = f"{b.branch_code} - {b.branch_name}"

        if (
            norm(b.branch_code) == search_text_norm
            or norm(b.branch_name) == search_text_norm
            or norm(full_label) == search_text_norm
        ):
            return b

    return None


def branch_matches(search_text):
    search_text_norm = norm(search_text)

    if not search_text_norm:
        return []

    branches = all_branches()

    result = []

    for b in branches:
        full_label = f"{b.branch_code} - {b.branch_name}"

        code_match = norm(b.branch_code).startswith(search_text_norm)
        name_match = search_text_norm in norm(b.branch_name)
        full_match = search_text_norm in norm(full_label)

        if code_match or name_match or full_match:
            result.append(b)

    return result[:8]


def product_exact(search_text):
    search_text_norm = norm(search_text)

    if not search_text_norm:
        return None

    products = all_products()

    for p in products:
        if norm(p.product_name) == search_text_norm:
            return p

    return None


def product_matches(search_text):
    search_text_norm = norm(search_text)

    if not search_text_norm:
        return []

    products = all_products()

    result = []

    for p in products:
        if search_text_norm in norm(p.product_name):
            result.append(p)

    return result[:8]


def save_cart():
    if not st.session_state.sepet:
        st.error("Sepet boş.")
        return

    for item in st.session_state.sepet:
        shipment = Shipment(
            barcode=item["barcode"],
            tracking_number=item["tracking_number"],
            branch_code=item["branch_code"],
            branch_name=item["branch_name"],
            recipient_name=item["recipient_name"],
            address=item["address"],
            district=item["district"],
            city=item["city"],
            phone=item["phone"],
            product_name=item["product_name"],
            width=item["width"],
            length=item["length"],
            height=item["height"],
            weight=item["weight"],
            created_by=st.session_state.get("username", "admin"),
            is_printed=False
        )

        db.add(shipment)

        barcode = (
            db.query(Barcode)
            .filter(Barcode.barcode == item["barcode"])
            .first()
        )

        if barcode:
            barcode.is_used = True

    db.commit()
    st.session_state.sepet = []
    st.success("Gönderiler kaydedildi.")
    st.rerun()


top_left, top_right = st.columns([4, 1])

with top_left:
    st.title("Barkod Oluştur")
    st.markdown(
        '<div class="page-subtitle">Şubeye ürün gönderimi için barkod oluşturun.</div>',
        unsafe_allow_html=True
    )

with top_right:
    st.markdown(
        f'<div class="top-badge">Havuzda {kalan_barkod_sayisi()} kullanılmamış barkod</div>',
        unsafe_allow_html=True
    )

st.write("")
st.write("")

tab1, tab2 = st.tabs(["Tekli Gönderi", "Çoklu Gönderi"])

with tab2:
    st.info("Çoklu gönderi daha sonra eklenecek.")

with tab1:

    left, right = st.columns([1, 1.38], gap="large")

    with left:

        with st.container(border=True):

            st.markdown('<div class="clean-title">Alıcı (Şube)</div>', unsafe_allow_html=True)

            branch_search = st.text_input(
    "Şube kodu veya adı yazın",
    value=st.session_state.get("selected_branch_label", ""),
    placeholder="Şube kodu veya adı yazın...",
    key="branch_input"
)

            selected_branch = branch_exact(branch_search)

            if selected_branch:
                default_branch_code = selected_branch.branch_code
                default_branch_name = selected_branch.branch_name
                default_recipient = selected_branch.branch_name
                default_address = selected_branch.address or ""
                default_district = selected_branch.district or ""
                default_city = selected_branch.city or ""
            else:
                default_branch_code = branch_search
                default_branch_name = branch_search
                default_recipient = branch_search
                default_address = ""
                default_district = ""
                default_city = ""

                branch_suggestions = branch_matches(branch_search)

                if branch_suggestions:
                    for b in branch_suggestions:
                        label = f"{b.branch_code} - {b.branch_name}"

                        with st.container():
                            st.markdown('<div class="suggestion-button">', unsafe_allow_html=True)

                            if st.button(label, key=f"branch_{b.id}", use_container_width=True):
                                st.session_state.selected_branch_label = label
                                st.rerun()

                            st.markdown('</div>', unsafe_allow_html=True)

        with st.container(border=True):

            st.markdown('<div class="clean-title">Ürün Bilgileri</div>', unsafe_allow_html=True)

            product_search = st.text_input(
    "Ürün İçeriği",
    value=st.session_state.get("selected_product_label", ""),
    placeholder="Ürün içeriği yazın...",
    key="product_input",
    max_chars=30
)

            selected_product = product_exact(product_search)

            if selected_product:
                product_name = selected_product.product_name
                default_width = float(selected_product.width or 0)
                default_length = float(selected_product.length or 0)
                default_height = float(selected_product.height or 0)
                default_weight = float(selected_product.weight or 0)
                st.success("Ürün ölçüsü bulundu.")
            else:
                product_name = product_search
                default_width = 0.0
                default_length = 0.0
                default_height = 0.0
                default_weight = 0.0

                product_suggestions = product_matches(product_search)

                if product_suggestions:
                    for p in product_suggestions:
                        with st.container():
                            st.markdown('<div class="suggestion-button">', unsafe_allow_html=True)

                            if st.button(p.product_name, key=f"product_{p.id}", use_container_width=True):
                                st.session_state.selected_product_label = p.product_name
                                st.rerun()

                            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("**Adet**")

            a1, a2, a3 = st.columns([1, 4, 1])

            with a1:
                if st.button("−", use_container_width=True):
                    if st.session_state.adet > 1:
                        st.session_state.adet -= 1
                    st.rerun()

            with a2:
                st.markdown(
                    f'<div class="qty-box">{st.session_state.adet}</div>',
                    unsafe_allow_html=True
                )

            with a3:
                if st.button("+", use_container_width=True):
                    st.session_state.adet += 1
                    st.rerun()

            adet = int(st.session_state.adet)

            m1, m2 = st.columns(2)

            with m1:
                width = st.number_input("En (Cm)", min_value=0.0, value=default_width, step=1.0)

            with m2:
                length = st.number_input("Boy (Cm)", min_value=0.0, value=default_length, step=1.0)

            m3, m4 = st.columns(2)

            with m3:
                height = st.number_input("Yükseklik (Cm)", min_value=0.0, value=default_height, step=1.0)

            with m4:
                weight = st.number_input("Ağırlık (G)", min_value=0.0, value=default_weight, step=1.0)

            if st.button("+  Kutu Ekle", use_container_width=True, type="primary"):

                if not temizle(default_recipient):
                    st.error("Alıcı / Şube bilgisi boş olamaz.")

                elif not temizle(product_name):
                    st.error("Ürün içeriği boş olamaz.")

                else:
                    available_barcodes = get_available_barcodes(adet)

                    if len(available_barcodes) < adet:
                        st.error(
                            f"Yetersiz barkod. İstenen: {adet}, Kalan: {len(available_barcodes)}"
                        )

                    else:
                        for barcode in available_barcodes:
                            st.session_state.sepet.append(
                                {
                                    "barcode": barcode.barcode,
                                    "tracking_number": barcode.barcode,
                                    "branch_code": default_branch_code,
                                    "branch_name": default_branch_name,
                                    "recipient_name": default_recipient,
                                    "address": default_address,
                                    "district": default_district,
                                    "city": default_city,
                                    "phone": "",
                                    "product_name": product_name,
                                    "width": width,
                                    "length": length,
                                    "height": height,
                                    "weight": weight,
                                }
                            )

                        st.success(f"{adet} kutu eklendi.")
                        st.rerun()

    with right:

        with st.container(border=True):

            h1, h2, h3 = st.columns([3, 1, 1])

            with h1:
                st.markdown(
                    f'<div class="clean-title">Eklenen Kutular ({len(st.session_state.sepet)})</div>',
                    unsafe_allow_html=True
                )

            with h2:
                if st.button("Sepeti Temizle", use_container_width=True):
                    st.session_state.sepet = []
                    st.rerun()

            with h3:
                if st.button("Tümünü Kaydet", use_container_width=True, type="primary"):
                    save_cart()

            if not st.session_state.sepet:

                st.markdown(
                    '<div class="cart-empty">Henüz kutu eklenmedi.</div>',
                    unsafe_allow_html=True
                )

            else:

                for index, item in enumerate(st.session_state.sepet):

                    st.markdown(
                        f"""
                        <div class="cart-item">
                            <div class="cart-item-title">
                                {item['barcode']} | {item['recipient_name']}
                            </div>
                            <div class="cart-item-sub">
                                {item['product_name']} |
                                {item['width']}x{item['length']}x{item['height']} |
                                {item['weight']} gr
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    c1, c2, c3 = st.columns([6, 1, 1])

                    with c2:
                        if st.button("Düzenle", key=f"edit_{index}"):
                            st.session_state[f"edit_mode_{index}"] = not st.session_state.get(
                                f"edit_mode_{index}",
                                False
                            )
                            st.rerun()

                    with c3:
                        if st.button("Sil", key=f"delete_{index}"):
                            st.session_state.sepet.pop(index)
                            st.rerun()
