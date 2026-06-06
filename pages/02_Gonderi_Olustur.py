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
    padding-top: 1.4rem !important;
    padding-left: 1.6rem !important;
    padding-right: 1.6rem !important;
    max-width: 100% !important;
}

h1 {
    font-size: 30px !important;
    font-weight: 800 !important;
    line-height: 1.1 !important;
    margin: 0 !important;
    padding: 0 !important;
}

h2, h3 {
    font-size: 17px !important;
    font-weight: 800 !important;
}

.page-header {
    background: white;
    border: 1px solid #dbe3ef;
    border-radius: 18px;
    padding: 22px 22px;
    margin-bottom: 18px;
    box-shadow: 0 8px 24px rgba(15,23,42,0.04);
}

.page-header-grid {
    display: grid;
    grid-template-columns: 1fr auto;
    align-items: center;
    gap: 16px;
}

.page-title {
    font-size: 30px;
    font-weight: 800;
    color: #020617;
    line-height: 1.1;
}

.page-subtitle {
    color: #64748b;
    font-size: 13px;
    margin-top: 10px;
}

.top-badge {
    background: #dbeafe;
    color: #1263d8;
    padding: 11px 20px;
    border-radius: 14px;
    font-weight: 800;
    font-size: 13px;
    min-width: 260px;
    text-align: center;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 18px !important;
    background: white !important;
    border: 1px solid #dbe3ef !important;
    box-shadow: 0 8px 24px rgba(15,23,42,0.04) !important;
}

.stButton button {
    border-radius: 12px !important;
    min-height: 40px !important;
    font-weight: 800 !important;
}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stSelectbox div {
    border-radius: 12px !important;
    min-height: 40px !important;
    font-size: 13px !important;
}

.cart-card {
    background: #f8fafc;
    border: 1px solid #dbe3ef;
    border-radius: 14px;
    padding: 12px 14px;
    margin-bottom: 10px;
}

.cart-title {
    font-weight: 800;
    color: #0f172a;
    font-size: 13px;
}

.cart-sub {
    color: #64748b;
    font-size: 12px;
    margin-top: 3px;
}

.empty-cart {
    border: 2px dashed #dbe3ef;
    border-radius: 16px;
    height: 120px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #64748b;
    font-size: 14px;
    background: #ffffff;
}
</style>
""", unsafe_allow_html=True)

if "sepet" not in st.session_state:
    st.session_state.sepet = []

if "adet" not in st.session_state:
    st.session_state.adet = 1


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


def get_branch_options():
    branches = (
        db.query(Branch)
        .order_by(Branch.branch_code.asc())
        .all()
    )

    options = [""]

    for b in branches:
        options.append(
            f"{b.branch_code} - {b.branch_name}"
        )

    return options, branches


def get_product_options():
    products = (
        db.query(ProductDimension)
        .order_by(ProductDimension.product_name.asc())
        .all()
    )

    options = [""]

    for p in products:
        options.append(p.product_name)

    return options, products


def branch_from_option(option, branches):
    option = temizle(option)

    if not option:
        return None

    for b in branches:
        label = f"{b.branch_code} - {b.branch_name}"

        if option == label:
            return b

    return None


def product_from_option(option, products):
    option = temizle(option)

    if not option:
        return None

    for p in products:
        if norm(p.product_name) == norm(option):
            return p

    return None


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


st.markdown(
    f"""
    <div class="page-header">
        <div class="page-header-grid">
            <div>
                <div class="page-title">Barkod Oluştur</div>
                <div class="page-subtitle">Şubeye ürün gönderimi için barkod oluşturun.</div>
            </div>
            <div class="top-badge">
                Havuzda {kalan_barkod_sayisi()} kullanılmamış barkod
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

tab1, tab2 = st.tabs(["Tekli Gönderi", "Çoklu Gönderi"])

with tab2:
    st.info("Çoklu gönderi daha sonra eklenecek.")

with tab1:

    left, right = st.columns([1, 2.25], gap="large")

    with left:

        with st.container(border=True):

            st.subheader("Alıcı (Şube)")

            branch_options, branches = get_branch_options()

            selected_branch_label = st.selectbox(
                "Şube kodu veya adı yazın",
                branch_options,
                index=0,
                placeholder="Şube kodu veya adı yazın..."
            )

            selected_branch = branch_from_option(
                selected_branch_label,
                branches
            )

            if selected_branch:
                default_branch_code = selected_branch.branch_code
                default_branch_name = selected_branch.branch_name
                default_recipient = selected_branch.branch_name
                default_address = selected_branch.address or ""
                default_district = selected_branch.district or ""
                default_city = selected_branch.city or ""
            else:
                default_branch_code = ""
                default_branch_name = ""
                default_recipient = ""
                default_address = ""
                default_district = ""
                default_city = ""

        with st.container(border=True):

            st.subheader("Ürün Bilgileri")

            product_options, products = get_product_options()

            selected_product_label = st.selectbox(
                "Ürün İçeriği (max 30)",
                product_options,
                index=0,
                placeholder="Ürün içeriği yazın..."
            )

            product = product_from_option(
                selected_product_label,
                products
            )

            if product:
                product_name = product.product_name
                default_width = float(product.width or 0)
                default_length = float(product.length or 0)
                default_height = float(product.height or 0)
                default_weight = float(product.weight or 0)
                st.success("Ürün ölçüsü bulundu.")
            else:
                product_name = selected_product_label
                default_width = 0.0
                default_length = 0.0
                default_height = 0.0
                default_weight = 0.0

            st.write("Adet")

            a1, a2, a3 = st.columns([1, 5, 1])

            with a1:
                if st.button("−", use_container_width=True):
                    if st.session_state.adet > 1:
                        st.session_state.adet -= 1
                    st.rerun()

            with a2:
                adet = st.number_input(
                    "Adet",
                    min_value=1,
                    value=int(st.session_state.adet),
                    step=1,
                    label_visibility="collapsed"
                )

                st.session_state.adet = int(adet)

            with a3:
                if st.button("+", use_container_width=True):
                    st.session_state.adet += 1
                    st.rerun()

            m1, m2 = st.columns(2)

            with m1:
                width = st.number_input(
                    "En (Cm)",
                    min_value=0.0,
                    value=default_width,
                    step=1.0
                )

            with m2:
                length = st.number_input(
                    "Boy (Cm)",
                    min_value=0.0,
                    value=default_length,
                    step=1.0
                )

            m3, m4 = st.columns(2)

            with m3:
                height = st.number_input(
                    "Yükseklik (Cm)",
                    min_value=0.0,
                    value=default_height,
                    step=1.0
                )

            with m4:
                weight = st.number_input(
                    "Ağırlık (G)",
                    min_value=0.0,
                    value=default_weight,
                    step=1.0
                )

            if st.button("+  Kutu Ekle", use_container_width=True):

                if not selected_branch:
                    st.error("Alıcı / Şube seçimi boş olamaz.")

                elif not temizle(product_name):
                    st.error("Ürün içeriği boş olamaz.")

                else:
                    available_barcodes = get_available_barcodes(int(adet))

                    if len(available_barcodes) < int(adet):
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

            h1, h2 = st.columns([3, 1])

            with h1:
                st.subheader(f"Eklenen Kutular ({len(st.session_state.sepet)})")

            with h2:
                if st.button("Tümünü Kaydet", use_container_width=True):
                    save_cart()

            if not st.session_state.sepet:

                st.markdown(
                    '<div class="empty-cart">Henüz kutu eklenmedi.</div>',
                    unsafe_allow_html=True
                )

            else:

                for index, item in enumerate(st.session_state.sepet):

                    st.markdown(
                        f"""
                        <div class="cart-card">
                            <div class="cart-title">
                                {item['barcode']} | {item['recipient_name']}
                            </div>
                            <div class="cart-sub">
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

                    if st.session_state.get(f"edit_mode_{index}", False):

                        with st.form(f"edit_form_{index}"):

                            new_product = st.text_input(
                                "Ürün İçeriği",
                                value=item["product_name"]
                            )

                            e1, e2, e3, e4 = st.columns(4)

                            with e1:
                                new_width = st.number_input(
                                    "En",
                                    value=float(item["width"])
                                )

                            with e2:
                                new_length = st.number_input(
                                    "Boy",
                                    value=float(item["length"])
                                )

                            with e3:
                                new_height = st.number_input(
                                    "Yükseklik",
                                    value=float(item["height"])
                                )

                            with e4:
                                new_weight = st.number_input(
                                    "Ağırlık",
                                    value=float(item["weight"])
                                )

                            save_edit = st.form_submit_button("Kaydet")

                            if save_edit:
                                st.session_state.sepet[index]["product_name"] = new_product
                                st.session_state.sepet[index]["width"] = new_width
                                st.session_state.sepet[index]["length"] = new_length
                                st.session_state.sepet[index]["height"] = new_height
                                st.session_state.sepet[index]["weight"] = new_weight
                                st.session_state[f"edit_mode_{index}"] = False
                                st.rerun()

                st.divider()

                t1, t2 = st.columns(2)

                with t1:
                    if st.button("Sepeti Temizle", use_container_width=True):
                        st.session_state.sepet = []
                        st.rerun()

                with t2:
                    if st.button("Gönderileri Kaydet", use_container_width=True):
                        save_cart()
