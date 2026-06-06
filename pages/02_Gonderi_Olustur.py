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
    padding-top: 1.5rem !important;
}

h1 {
    font-size: 30px !important;
    font-weight: 800 !important;
}

h2, h3 {
    font-size: 17px !important;
}

.stButton button {
    border-radius: 12px !important;
    min-height: 40px !important;
    font-weight: 700 !important;
}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stSelectbox div {
    border-radius: 12px !important;
    min-height: 40px !important;
    font-size: 13px !important;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 18px !important;
    background: white !important;
    border: 1px solid #dbe3ef !important;
    box-shadow: 0 8px 24px rgba(15,23,42,0.04) !important;
}

.small-muted {
    color: #64748b;
    font-size: 13px;
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

.top-badge {
    background: #dbeafe;
    color: #1263d8;
    padding: 9px 16px;
    border-radius: 14px;
    font-weight: 800;
    font-size: 13px;
    text-align: center;
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


def branch_exact(search_text):
    search_text = norm(search_text)

    if not search_text:
        return None

    branches = db.query(Branch).all()

    for b in branches:
        if norm(b.branch_code) == search_text or norm(b.branch_name) == search_text:
            return b

    return None


def branch_matches(search_text):
    search_text = norm(search_text)

    if not search_text:
        return []

    branches = db.query(Branch).order_by(Branch.branch_code.asc()).all()

    result = []

    for b in branches:
        code_match = norm(b.branch_code).startswith(search_text)
        name_match = search_text in norm(b.branch_name)

        if code_match or name_match:
            result.append(b)

    return result[:20]


def find_product_exact(product_name):
    product_name = norm(product_name)

    if not product_name:
        return None

    products = db.query(ProductDimension).all()

    for p in products:
        if norm(p.product_name) == product_name:
            return p

    return None


def product_suggestions(product_name):
    product_name = norm(product_name)

    if not product_name:
        return []

    products = (
        db.query(ProductDimension)
        .order_by(ProductDimension.product_name.asc())
        .all()
    )

    result = []

    for p in products:
        if product_name in norm(p.product_name):
            result.append(p.product_name)

    return result[:15]


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
        '<div class="small-muted">Şubeye ürün gönderimi için barkod oluşturun.</div>',
        unsafe_allow_html=True
    )

with top_right:
    st.markdown(
        f'<div class="top-badge">Havuzda {kalan_barkod_sayisi()} kullanılmamış barkod</div>',
        unsafe_allow_html=True
    )

st.write("")

tab1, tab2 = st.tabs(["Tekli Gönderi", "Çoklu Gönderi"])

with tab2:
    st.info("Çoklu gönderi daha sonra eklenecek.")

with tab1:

    left, right = st.columns([1, 2.25], gap="large")

    with left:

        with st.container(border=True):

            st.subheader("Alıcı (Şube)")

            branch_search = st.text_input(
                "Şube kodu veya adı yazın",
                placeholder="Şube kodu veya adı yazın..."
            )

            selected_branch = None

            manual_mode = norm(branch_search) == "0000"

            if manual_mode:
                st.info("0000 girildi. Manuel alıcı bilgisi doldurulacak.")

            else:
                exact_branch = branch_exact(branch_search)

                if exact_branch:
                    selected_branch = exact_branch

                else:
                    matches = branch_matches(branch_search)

                    if matches:
                        options = [
                            f"{b.branch_code} - {b.branch_name}"
                            for b in matches
                        ]

                        selected_label = st.selectbox(
                            "Şube",
                            options,
                            label_visibility="collapsed"
                        )

                        selected_index = options.index(selected_label)
                        selected_branch = matches[selected_index]

                    elif branch_search:
                        st.warning("Şube bulunamadı. Manuel bilgiyle devam edebilirsiniz.")

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

        with st.container(border=True):

            st.subheader("Ürün Bilgileri")

            product_name_input = st.text_input(
                "Ürün İçeriği (max 30)",
                placeholder="Örn: Erkek T-Shirt M",
                max_chars=30
            )

            product_name = product_name_input

            exact_product = find_product_exact(product_name_input)

            if exact_product:
                product_name = exact_product.product_name

            else:
                suggestions = product_suggestions(product_name_input)

                if suggestions:
                    selected_product = st.selectbox(
                        "Ürün",
                        suggestions,
                        label_visibility="collapsed"
                    )

                    product_name = selected_product

            product = find_product_exact(product_name)

            if product:
                default_width = float(product.width or 0)
                default_length = float(product.length or 0)
                default_height = float(product.height or 0)
                default_weight = float(product.weight or 0)
                st.success("Ürün ölçüsü bulundu.")
            else:
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

                recipient_name = default_recipient
                recipient_phone = ""
                recipient_address = default_address
                recipient_district = default_district
                recipient_city = default_city

                if not temizle(recipient_name):
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
                                    "recipient_name": recipient_name,
                                    "address": recipient_address,
                                    "district": recipient_district,
                                    "city": recipient_city,
                                    "phone": recipient_phone,
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
