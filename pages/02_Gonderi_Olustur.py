import streamlit as st
from utils.auth import require_login

require_login()
from database.database import SessionLocal, engine
from database.models import Base, Branch, ProductDimension, Barcode, Shipment

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
html, body, [class*="css"] {
    font-size: 14px !important;
}
section[data-testid="stSidebar"] {
    min-width: 230px !important;
    max-width: 230px !important;
}
button[kind="header"] {
    display: none !important;
}
.stButton button {
    font-size: 13px !important;
    padding: 0.35rem 0.6rem !important;
}
.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stSelectbox div {
    font-size: 13px !important;
}
div[data-testid="stMarkdownContainer"] p {
    font-size: 13px !important;
}
h1 {
    font-size: 26px !important;
}
h2, h3 {
    font-size: 18px !important;
}
.cart-row {
    font-size: 13px;
    padding: 6px 0;
}
</style>
""", unsafe_allow_html=True)

Base.metadata.create_all(bind=engine)

st.title("Gönderi Oluştur")

db = SessionLocal()

if "sepet" not in st.session_state:
    st.session_state.sepet = []


def norm(value):
    return str(value or "").strip().lower()


def get_available_barcodes(count):
    used_in_cart = [x["barcode"] for x in st.session_state.sepet]

    barcodes = (
        db.query(Barcode)
        .filter(Barcode.is_used == False)
        .all()
    )

    result = []

    for b in barcodes:
        if b.barcode not in used_in_cart:
            result.append(b)

        if len(result) == count:
            break

    return result


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


def branch_matches(code_text, name_text):
    branches = db.query(Branch).all()
    code_text = norm(code_text)
    name_text = norm(name_text)

    result = []

    for b in branches:
        code_match = code_text and norm(b.branch_code).startswith(code_text)
        name_match = name_text and name_text in norm(b.branch_name)

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
            created_by="admin",
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


st.subheader("Şube / Alıcı Bilgileri")

col1, col2 = st.columns(2)

with col1:
    branch_code_search = st.text_input("Şube Kodu")

with col2:
    branch_name_search = st.text_input("Şube Adı")

manual_mode = norm(branch_code_search) == "0000"

selected_branch = None

if manual_mode:
    st.info("0000 girildi. Manuel alıcı bilgisi doldurulacak.")
else:
    matches = branch_matches(branch_code_search, branch_name_search)

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

        st.success(
            f"Seçilen Şube: {selected_branch.branch_code} - {selected_branch.branch_name}"
        )

    elif branch_code_search or branch_name_search:
        st.warning("Şube bulunamadı. Manuel bilgiyle devam edebilirsiniz.")

if selected_branch:
    default_branch_code = selected_branch.branch_code
    default_branch_name = selected_branch.branch_name
    default_recipient = selected_branch.branch_name
    default_address = selected_branch.address or ""
    default_district = selected_branch.district or ""
    default_city = selected_branch.city or ""
else:
    default_branch_code = branch_code_search
    default_branch_name = branch_name_search
    default_recipient = branch_name_search
    default_address = ""
    default_district = ""
    default_city = ""

col1, col2 = st.columns(2)

with col1:
    recipient_name = st.text_input(
        "Alıcı Adı",
        value=default_recipient,
        key=f"recipient_{default_branch_code}_{default_branch_name}"
    )

    recipient_phone = st.text_input("Telefon")

with col2:
    recipient_district = st.text_input(
        "İlçe",
        value=default_district,
        key=f"district_{default_branch_code}_{default_branch_name}"
    )

    recipient_city = st.text_input(
        "İl",
        value=default_city,
        key=f"city_{default_branch_code}_{default_branch_name}"
    )

recipient_address = st.text_area(
    "Adres",
    value=default_address,
    key=f"address_{default_branch_code}_{default_branch_name}"
)

st.divider()

st.subheader("Ürün Bilgileri")

product_name = st.text_input("Ürün İçeriği")

suggestions = product_suggestions(product_name)

if suggestions:
    selected_product = st.selectbox(
        "Ürün Önerileri",
        suggestions
    )

    if st.button("Öneriyi Kullan"):
        product_name = selected_product
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

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    width = st.number_input(
        "En",
        min_value=0.0,
        value=default_width,
        step=1.0
    )

with col2:
    length = st.number_input(
        "Boy",
        min_value=0.0,
        value=default_length,
        step=1.0
    )

with col3:
    height = st.number_input(
        "Yükseklik",
        min_value=0.0,
        value=default_height,
        step=1.0
    )

with col4:
    weight = st.number_input(
        "Ağırlık (gr)",
        min_value=0.0,
        value=default_weight,
        step=1.0
    )

with col5:
    adet = st.number_input(
        "Adet",
        min_value=1,
        value=1,
        step=1
    )

if st.button("Sepete Ekle", use_container_width=True):

    if not recipient_name.strip():
        st.error("Alıcı adı boş olamaz.")

    elif not product_name.strip():
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

            st.success(f"{adet} gönderi sepete eklendi.")
            st.rerun()

st.divider()

top1, top2 = st.columns(2)

with top1:
    st.subheader(f"Sepet ({len(st.session_state.sepet)})")

with top2:
    if st.button("Gönderileri Kaydet", use_container_width=True):
        save_cart()

if not st.session_state.sepet:
    st.info("Sepet boş.")

else:
    grouped = {}

    for item in st.session_state.sepet:
        key = item["recipient_name"] or "Alıcı Yok"

        if key not in grouped:
            grouped[key] = []

        grouped[key].append(item)

    for recipient, items in grouped.items():
        with st.expander(
            f"{recipient} ({len(items)} gönderi)",
            expanded=True
        ):
            for item in items:
                index = st.session_state.sepet.index(item)

                col1, col2, col3 = st.columns([8, 1, 1])

                with col1:
                    st.markdown(
                        f"""
                        <div class="cart-row">
                        <b>{item['barcode']}</b> |
                        {item['product_name']} |
                        {item['width']}x{item['length']}x{item['height']} |
                        {item['weight']} gr
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with col2:
                    if st.button("Düzenle", key=f"edit_{index}"):
                        st.session_state[f"edit_mode_{index}"] = not st.session_state.get(
                            f"edit_mode_{index}",
                            False
                        )
                        st.rerun()

                with col3:
                    if st.button("Sil", key=f"delete_{index}"):
                        st.session_state.sepet.pop(index)
                        st.rerun()

                if st.session_state.get(f"edit_mode_{index}", False):
                    with st.form(f"edit_form_{index}"):

                        new_product = st.text_input(
                            "Ürün İçeriği",
                            value=item["product_name"]
                        )

                        c1, c2, c3, c4 = st.columns(4)

                        with c1:
                            new_width = st.number_input(
                                "En",
                                value=float(item["width"])
                            )

                        with c2:
                            new_length = st.number_input(
                                "Boy",
                                value=float(item["length"])
                            )

                        with c3:
                            new_height = st.number_input(
                                "Yükseklik",
                                value=float(item["height"])
                            )

                        with c4:
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

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Sepeti Temizle", use_container_width=True):
            st.session_state.sepet = []
            st.rerun()

    with col2:
        if st.button("Gönderileri Kaydet ", use_container_width=True):
            save_cart()
