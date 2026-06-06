import streamlit as st

from utils.auth import require_login
from database.database import SessionLocal, engine
from database.models import Base, Branch, ProductDimension, Barcode, Shipment

require_login()

Base.metadata.create_all(bind=engine)

db = SessionLocal()

st.markdown("""
<style>
.page-title {
    font-size: 30px;
    font-weight: 800;
    color: #020617;
    margin-bottom: 2px;
}
.page-subtitle {
    color: #64748b;
    font-size: 14px;
    margin-bottom: 24px;
}
.top-badge {
    background: #dbeafe;
    color: #1263d8;
    padding: 10px 18px;
    border-radius: 14px;
    font-weight: 700;
    font-size: 13px;
    text-align: center;
    float: right;
}
.card {
    background: white;
    border: 1px solid #dbe3ef;
    border-radius: 18px;
    padding: 22px;
    box-shadow: 0 10px 26px rgba(15,23,42,0.04);
    margin-bottom: 20px;
}
.card-title {
    font-size: 16px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 16px;
}
.empty-box {
    border: 2px dashed #dbe3ef;
    border-radius: 16px;
    min-height: 125px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #64748b;
    font-size: 14px;
}
.cart-item {
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 12px 14px;
    margin-bottom: 10px;
    background: #f8fafc;
}
.cart-title {
    font-weight: 800;
    color: #0f172a;
    font-size: 14px;
}
.cart-sub {
    color: #64748b;
    font-size: 12px;
}
.stButton button {
    border-radius: 12px !important;
    min-height: 42px !important;
    font-weight: 800 !important;
}
.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stSelectbox div {
    border-radius: 12px !important;
    min-height: 42px !important;
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


def kalan_barkod_sayisi():
    used_in_cart = [x["barcode"] for x in st.session_state.sepet]

    barcodes = (
        db.query(Barcode)
        .filter(Barcode.is_used == False)
        .all()
    )

    count = 0

    for b in barcodes:
        if b.barcode not in used_in_cart:
            count += 1

    return count


def find_product_exact(product_name):
    products = db.query(ProductDimension).all()

    for p in products:
        if norm(p.product_name) == norm(product_name):
            return p

    return None


def product_suggestions(product_name):
    if not product_name:
        return []

    products = db.query(ProductDimension).all()
    result = []

    for p in products:
        if norm(product_name) in norm(p.product_name):
            result.append(p.product_name)

    return result[:10]


def branch_matches(search_text):
    branches = db.query(Branch).all()
    search_text = norm(search_text)

    if not search_text:
        return []

    result = []

    for b in branches:
        code_match = norm(b.branch_code).startswith(search_text)
        name_match = search_text in norm(b.branch_name)

        if code_match or name_match:
            result.append(b)

    return result[:20]


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
    <div class="top-badge">
        Havuzda {kalan_barkod_sayisi()} kullanılmamış barkod
    </div>
    <div class="page-title">Barkod Oluştur</div>
    <div class="page-subtitle">Şubeye ürün gönderimi için barkod oluşturun.</div>
    """,
    unsafe_allow_html=True
)

tab1, tab2 = st.tabs(["Tekli Gönderi", "Çoklu Gönderi"])

with tab2:
    st.info("Çoklu gönderi ekranı daha sonra eklenecek.")

with tab1:

    left, right = st.columns([1, 2.25], gap="large")

    with left:

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🏢 Alıcı (Şube)</div>', unsafe_allow_html=True)

        branch_search = st.text_input(
            "Şube kodu veya adı yazın",
            placeholder="Şube kodu veya adı yazın...",
            label_visibility="collapsed"
        )

        manual_mode = norm(branch_search) == "0000"

        selected_branch = None

        if manual_mode:
            st.info("0000 girildi. Manuel alıcı bilgisi doldurulacak.")
        else:
            matches = branch_matches(branch_search)

            if matches:
                options = [
                    f"{b.branch_code} - {b.branch_name}"
                    for b in matches
                ]

                selected_label = st.selectbox(
                    "Eşleşen Şubeler",
                    options
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

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Ürün Bilgileri</div>', unsafe_allow_html=True)

        product_name = st.text_input(
            "Ürün İçeriği (max 30)",
            placeholder="Örn: Erkek T-Shirt M",
            max_chars=30
        )

        suggestions = product_suggestions(product_name)

        if suggestions:
            selected_product = st.selectbox(
                "Ürün Önerileri",
                suggestions
            )

            if st.button("Öneriyi Kullan", use_container_width=True):
                st.session_state["selected_product_from_suggestion"] = selected_product
                st.rerun()

        if "selected_product_from_suggestion" in st.session_state:
            product_name = st.session_state["selected_product_from_suggestion"]

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

                    if "selected_product_from_suggestion" in st.session_state:
                        del st.session_state["selected_product_from_suggestion"]

                    st.success(f"{adet} kutu eklendi.")
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    with right:

        st.markdown('<div class="card">', unsafe_allow_html=True)

        h1, h2 = st.columns([3, 1])

        with h1:
            st.markdown(
                f'<div class="card-title">📦 Eklenen Kutular ({len(st.session_state.sepet)})</div>',
                unsafe_allow_html=True
            )

        with h2:
            if st.button("💾 Tümünü Kaydet", use_container_width=True):
                save_cart()

        if not st.session_state.sepet:
            st.markdown(
                '<div class="empty-box">Henüz kutu eklenmedi.</div>',
                unsafe_allow_html=True
            )

        else:
            for index, item in enumerate(st.session_state.sepet):

                st.markdown(
                    f"""
                    <div class="cart-item">
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

                c1, c2, c3 = st.columns([5, 1, 1])

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

        st.markdown('</div>', unsafe_allow_html=True)
