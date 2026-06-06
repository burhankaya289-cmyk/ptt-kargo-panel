import pandas as pd
import streamlit as st
from io import BytesIO

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
    padding: 10px 18px;
    border-radius: 14px;
    font-weight: 800;
    font-size: 13px;
    text-align: center;
    min-width: 260px;
    margin-top: 8px;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 18px !important;
    background: #ffffff !important;
    border: 1px solid #dbe3ef !important;
    box-shadow: 0 12px 34px rgba(15,23,42,0.05) !important;
}

.stTextInput label,
.stNumberInput label,
.stFileUploader label,
.stSelectbox label {
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
    min-height: 44px !important;
    font-size: 13px !important;
}

.stButton button,
.stDownloadButton button {
    border-radius: 12px !important;
    min-height: 42px !important;
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

.selected-info {
    background: #eaf7ef;
    color: #17623a;
    border-radius: 12px;
    padding: 10px 12px;
    font-size: 12px;
    font-weight: 700;
    margin-top: 8px;
}

.error-box {
    background: #fff1f2;
    color: #991b1b;
    border: 1px solid #fecdd3;
    border-radius: 14px;
    padding: 12px;
    font-size: 13px;
    font-weight: 700;
}

.ok-box {
    background: #ecfdf5;
    color: #166534;
    border: 1px solid #bbf7d0;
    border-radius: 14px;
    padding: 12px;
    font-size: 13px;
    font-weight: 700;
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


def sayi(value, default=0.0):
    try:
        if pd.isna(value):
            return default
        if str(value).strip() == "":
            return default
        return float(value)
    except Exception:
        return default


def adet_sayi(value):
    try:
        if pd.isna(value):
            return 1
        value = int(float(value))
        return max(value, 1)
    except Exception:
        return 1


def all_branches():
    return db.query(Branch).order_by(Branch.branch_code.asc()).all()


def all_products():
    return db.query(ProductDimension).order_by(ProductDimension.product_name.asc()).all()


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


def find_branch(search_text):
    search = norm(search_text)

    if not search:
        return None

    branches = all_branches()

    for b in branches:
        full_label = f"{b.branch_code} - {b.branch_name}"

        if (
            norm(b.branch_code) == search
            or norm(b.branch_name) == search
            or norm(full_label) == search
        ):
            return b

    for b in branches:
        full_label = f"{b.branch_code} - {b.branch_name}"

        if (
            norm(b.branch_code).startswith(search)
            or search in norm(b.branch_name)
            or search in norm(full_label)
        ):
            return b

    return None


def find_product(search_text):
    search = norm(search_text)

    if not search:
        return None

    products = all_products()

    for p in products:
        if norm(p.product_name) == search:
            return p

    for p in products:
        if search in norm(p.product_name):
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
            is_printed=False,
            is_edited=False
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


def excel_output(df):
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return output


def excel_template():
    df = pd.DataFrame([
        {
            "Şube Kodu": "0001",
            "Şube Adı": "",
            "Ürün İçeriği": "KALEM",
            "Adet": 1,
            "En": "",
            "Boy": "",
            "Yükseklik": "",
            "Ağırlık": "",
            "Telefon": ""
        }
    ])

    return excel_output(df)


def create_bulk_shipments(df):
    created = 0
    errors = []

    required_columns = [
        "Şube Kodu",
        "Şube Adı",
        "Ürün İçeriği",
        "Adet",
        "En",
        "Boy",
        "Yükseklik",
        "Ağırlık"
    ]

    for col in required_columns:
        if col not in df.columns:
            errors.append({
                "Satır": "-",
                "Hata": f"Eksik kolon: {col}"
            })

    if errors:
        return created, errors

    needed_barcodes = 0

    for _, row in df.iterrows():
        needed_barcodes += adet_sayi(row.get("Adet", 1))

    available_barcodes = get_available_barcodes(needed_barcodes)

    if len(available_barcodes) < needed_barcodes:
        errors.append({
            "Satır": "-",
            "Hata": f"Yetersiz barkod. Gerekli: {needed_barcodes}, Kalan: {len(available_barcodes)}"
        })
        return created, errors

    barcode_index = 0

    for index, row in df.iterrows():
        row_no = index + 2

        try:
            branch_code_excel = temizle(row.get("Şube Kodu", ""))
            branch_name_excel = temizle(row.get("Şube Adı", ""))
            product_name_excel = temizle(row.get("Ürün İçeriği", ""))

            if not branch_code_excel and not branch_name_excel:
                errors.append({
                    "Satır": row_no,
                    "Hata": "Şube Kodu veya Şube Adı boş."
                })
                continue

            if not product_name_excel:
                errors.append({
                    "Satır": row_no,
                    "Hata": "Ürün İçeriği boş."
                })
                continue

            branch = find_branch(branch_code_excel) or find_branch(branch_name_excel)

            if branch:
                branch_code = branch.branch_code
                branch_name = branch.branch_name
                recipient_name = branch.branch_name
                address = branch.address or ""
                district = branch.district or ""
                city = branch.city or ""
            else:
                branch_code = branch_code_excel
                branch_name = branch_name_excel
                recipient_name = branch_name_excel or branch_code_excel
                address = ""
                district = ""
                city = ""

            product = find_product(product_name_excel)

            if product:
                product_name = product.product_name
                default_width = float(product.width or 0)
                default_length = float(product.length or 0)
                default_height = float(product.height or 0)
                default_weight = float(product.weight or 0)
            else:
                product_name = product_name_excel
                default_width = 0.0
                default_length = 0.0
                default_height = 0.0
                default_weight = 0.0

            width = sayi(row.get("En", ""), default_width)
            length = sayi(row.get("Boy", ""), default_length)
            height = sayi(row.get("Yükseklik", ""), default_height)
            weight = sayi(row.get("Ağırlık", ""), default_weight)
            adet = adet_sayi(row.get("Adet", 1))
            phone = temizle(row.get("Telefon", ""))

            for _ in range(adet):
                barcode = available_barcodes[barcode_index]
                barcode_index += 1

                shipment = Shipment(
                    barcode=barcode.barcode,
                    tracking_number=barcode.barcode,
                    branch_code=branch_code,
                    branch_name=branch_name,
                    recipient_name=recipient_name,
                    address=address,
                    district=district,
                    city=city,
                    phone=phone,
                    product_name=product_name,
                    width=width,
                    length=length,
                    height=height,
                    weight=weight,
                    created_by=st.session_state.get("username", "admin"),
                    is_printed=False,
                    is_edited=False
                )

                db.add(shipment)
                barcode.is_used = True
                created += 1

        except Exception as e:
            errors.append({
                "Satır": row_no,
                "Hata": str(e)
            })

    if created > 0:
        db.commit()

    return created, errors


top_left, top_right = st.columns([4, 1], vertical_alignment="center")

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

tab1, tab2 = st.tabs(["Tekli Gönderi", "Toplu Gönderi"])

with tab1:
    left, right = st.columns([1, 1.38], gap="large")

    with left:
        with st.container(border=True):
            st.markdown('<div class="clean-title">Alıcı (Şube)</div>', unsafe_allow_html=True)

            branch_search = st.text_input(
                "Şube kodu veya adı yazın",
                placeholder="Şube kodu veya adı yazın..."
            )

            selected_branch = find_branch(branch_search)

            if selected_branch:
                default_branch_code = selected_branch.branch_code
                default_branch_name = selected_branch.branch_name
                default_recipient = selected_branch.branch_name
                default_address = selected_branch.address or ""
                default_district = selected_branch.district or ""
                default_city = selected_branch.city or ""

                st.markdown(
                    f"""
                    <div class="selected-info">
                        Seçili Şube: {default_branch_code} - {default_branch_name}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:
                default_branch_code = branch_search
                default_branch_name = branch_search
                default_recipient = branch_search
                default_address = ""
                default_district = ""
                default_city = ""

        with st.container(border=True):
            st.markdown('<div class="clean-title">Ürün Bilgileri</div>', unsafe_allow_html=True)

            product_search = st.text_input(
                "Ürün İçeriği",
                placeholder="Ürün içeriği yazın...",
                max_chars=30
            )

            selected_product = find_product(product_search)

            if selected_product:
                product_name = selected_product.product_name
                default_width = float(selected_product.width or 0)
                default_length = float(selected_product.length or 0)
                default_height = float(selected_product.height or 0)
                default_weight = float(selected_product.weight or 0)

                st.markdown(
                    f"""
                    <div class="selected-info">
                        Ürün ölçüsü bulundu: {product_name}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:
                product_name = product_search
                default_width = 0.0
                default_length = 0.0
                default_height = 0.0
                default_weight = 0.0

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

with tab2:
    left_bulk, right_bulk = st.columns([1, 1.25], gap="large")

    with left_bulk:
        with st.container(border=True):
            st.markdown('<div class="clean-title">Excel Şablonu</div>', unsafe_allow_html=True)

            st.write(
                "Toplu gönderi için Excel dosyanız aşağıdaki kolonları içermelidir:"
            )

            st.code(
                "Şube Kodu | Şube Adı | Ürün İçeriği | Adet | En | Boy | Yükseklik | Ağırlık | Telefon"
            )

            st.download_button(
                "📥 Excel Şablonu İndir",
                excel_template(),
                file_name="toplu_gonderi_sablonu.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        with st.container(border=True):
            st.markdown('<div class="clean-title">Excel Yükle</div>', unsafe_allow_html=True)

            uploaded_file = st.file_uploader(
                "Toplu Gönderi Excel Dosyası",
                type=["xlsx"]
            )

    with right_bulk:
        with st.container(border=True):
            st.markdown('<div class="clean-title">Aktarım Durumu</div>', unsafe_allow_html=True)

            if uploaded_file is None:
                st.markdown(
                    '<div class="cart-empty">Henüz Excel yüklenmedi.</div>',
                    unsafe_allow_html=True
                )

            else:
                try:
                    df = pd.read_excel(uploaded_file)

                    st.markdown(
                        f'<div class="ok-box">{len(df)} satır okundu.</div>',
                        unsafe_allow_html=True
                    )

                    st.write("")
                    st.dataframe(df.head(20), use_container_width=True)

                    toplam_adet = 0

                    if "Adet" in df.columns:
                        for _, row in df.iterrows():
                            toplam_adet += adet_sayi(row.get("Adet", 1))

                    st.info(f"Bu dosyadan yaklaşık {toplam_adet} gönderi oluşturulacak.")

                    if st.button("🚀 Toplu Gönderileri Oluştur", use_container_width=True, type="primary"):
                        created, errors = create_bulk_shipments(df)

                        if created:
                            st.success(f"{created} gönderi oluşturuldu.")

                        if errors:
                            st.warning(f"{len(errors)} hata bulundu.")
                            error_df = pd.DataFrame(errors)
                            st.dataframe(error_df, use_container_width=True)

                            st.download_button(
                                "Hata Raporu İndir",
                                excel_output(error_df),
                                file_name="toplu_gonderi_hata_raporu.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )

                except Exception as e:
                    st.markdown(
                        f'<div class="error-box">Excel okunamadı: {e}</div>',
                        unsafe_allow_html=True
                    )
