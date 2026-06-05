import streamlit as st
import pandas as pd

from database.database import SessionLocal, engine
from database.models import Base, Branch, ProductDimension, Barcode, Shipment

Base.metadata.create_all(bind=engine)

st.title("Gönderi Oluştur")

db = SessionLocal()

if "sepet" not in st.session_state:
    st.session_state.sepet = []


def temizle(text):
    return str(text or "").strip().lower()


def urun_olcusu_bul(urun_adi):
    urunler = db.query(ProductDimension).all()
    for urun in urunler:
        if temizle(urun.product_name) == temizle(urun_adi):
            return urun
    return None


def sube_bul(kod, ad):
    kod = temizle(kod)
    ad = temizle(ad)

    subeler = db.query(Branch).all()

    if kod == "0000":
        return None

    for sube in subeler:
        if kod and temizle(sube.branch_code).startswith(kod):
            return sube

    for sube in subeler:
        if ad and ad in temizle(sube.branch_name):
            return sube

    return None


def bos_barkodlari_getir(adet):
    sepetteki_barkodlar = [
        item["barcode"]
        for item in st.session_state.sepet
    ]

    barkodlar = (
        db.query(Barcode)
        .filter(Barcode.is_used == False)
        .all()
    )

    uygunlar = []

    for barkod in barkodlar:
        if barkod.barcode not in sepetteki_barkodlar:
            uygunlar.append(barkod)

        if len(uygunlar) == adet:
            break

    return uygunlar


st.subheader("Alıcı / Şube Bilgileri")

col1, col2 = st.columns(2)

with col1:
    arama_kodu = st.text_input("Şube Kodu")

with col2:
    arama_adi = st.text_input("Şube Adı")

secilen_sube = sube_bul(arama_kodu, arama_adi)

manuel_gonderi = temizle(arama_kodu) == "0000" or secilen_sube is None

if secilen_sube:
    st.success(
        f"Seçilen Şube: {secilen_sube.branch_code} - {secilen_sube.branch_name}"
    )

    branch_code = secilen_sube.branch_code
    branch_name = secilen_sube.branch_name

    default_recipient = secilen_sube.branch_name
    default_address = secilen_sube.address
    default_district = secilen_sube.district
    default_city = secilen_sube.city

else:
    branch_code = arama_kodu
    branch_name = arama_adi

    default_recipient = arama_adi
    default_address = ""
    default_district = ""
    default_city = ""

    if temizle(arama_kodu) == "0000":
        st.info("0000 girildi. Manuel alıcı bilgisi doldurulacak.")
    elif arama_kodu or arama_adi:
        st.warning("Şube bulunamadı. Manuel bilgiyle devam edebilirsiniz.")

col1, col2 = st.columns(2)

with col1:
    recipient_name = st.text_input(
        "Alıcı Adı",
        value=default_recipient or "",
        key=f"recipient_{branch_code}_{branch_name}"
    )

    recipient_phone = st.text_input("Telefon")

with col2:
    recipient_district = st.text_input(
        "İlçe",
        value=default_district or "",
        key=f"district_{branch_code}_{branch_name}"
    )

    recipient_city = st.text_input(
        "İl",
        value=default_city or "",
        key=f"city_{branch_code}_{branch_name}"
    )

recipient_address = st.text_area(
    "Adres",
    value=default_address or "",
    key=f"address_{branch_code}_{branch_name}"
)

st.divider()

st.subheader("Ürün Bilgileri")

urun_adi = st.text_input("Ürün İçeriği")

bulunan_olcu = urun_olcusu_bul(urun_adi)

if bulunan_olcu:
    st.success("Ürün ölçüsü bulundu.")
    default_width = float(bulunan_olcu.width or 0)
    default_length = float(bulunan_olcu.length or 0)
    default_height = float(bulunan_olcu.height or 0)
    default_weight = float(bulunan_olcu.weight or 0)
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

    elif not urun_adi.strip():
        st.error("Ürün içeriği boş olamaz.")

    else:
        barkodlar = bos_barkodlari_getir(int(adet))

        if len(barkodlar) < int(adet):
            st.error(
                f"Yetersiz barkod. İstenen: {adet}, Kullanılabilir: {len(barkodlar)}"
            )

        else:
            for barkod in barkodlar:
                st.session_state.sepet.append(
                    {
                        "barcode": barkod.barcode,
                        "tracking_number": barkod.barcode,
                        "branch_code": branch_code,
                        "branch_name": branch_name,
                        "recipient_name": recipient_name,
                        "address": recipient_address,
                        "district": recipient_district,
                        "city": recipient_city,
                        "phone": recipient_phone,
                        "product_name": urun_adi,
                        "width": width,
                        "length": length,
                        "height": height,
                        "weight": weight,
                    }
                )

            st.success(f"{adet} gönderi sepete eklendi.")
            st.rerun()

st.divider()

st.subheader(f"Sepet ({len(st.session_state.sepet)})")

if not st.session_state.sepet:
    st.info("Sepet boş.")

else:
    grup = {}

    for item in st.session_state.sepet:
        alici = item["recipient_name"] or "Alıcı Yok"
        if alici not in grup:
            grup[alici] = []
        grup[alici].append(item)

    for alici, kayitlar in grup.items():
        with st.expander(f"{alici} ({len(kayitlar)} gönderi)", expanded=True):

            for item in kayitlar:
                real_index = st.session_state.sepet.index(item)

                col1, col2, col3 = st.columns([8, 2, 1])

                with col1:
                    st.write(
                        f"{item['barcode']} | "
                        f"{item['product_name']} | "
                        f"{item['width']}x{item['length']}x{item['height']} | "
                        f"{item['weight']} gr"
                    )

                with col2:
                    if st.button("Düzenle", key=f"duzenle_{real_index}"):
                        st.session_state[f"edit_{real_index}"] = True
                        st.rerun()

                with col3:
                    if st.button("❌", key=f"sil_{real_index}"):
                        st.session_state.sepet.pop(real_index)
                        st.rerun()

                if st.session_state.get(f"edit_{real_index}", False):
                    e1, e2, e3, e4 = st.columns(4)

                    with e1:
                        yeni_urun = st.text_input(
                            "Ürün",
                            value=item["product_name"],
                            key=f"edit_urun_{real_index}"
                        )

                    with e2:
                        yeni_en = st.number_input(
                            "En",
                            value=float(item["width"]),
                            key=f"edit_en_{real_index}"
                        )

                    with e3:
                        yeni_boy = st.number_input(
                            "Boy",
                            value=float(item["length"]),
                            key=f"edit_boy_{real_index}"
                        )

                    with e4:
                        yeni_yukseklik = st.number_input(
                            "Yükseklik",
                            value=float(item["height"]),
                            key=f"edit_yukseklik_{real_index}"
                        )

                    yeni_agirlik = st.number_input(
                        "Ağırlık",
                        value=float(item["weight"]),
                        key=f"edit_agirlik_{real_index}"
                    )

                    if st.button("Düzenlemeyi Kaydet", key=f"edit_kaydet_{real_index}"):
                        st.session_state.sepet[real_index]["product_name"] = yeni_urun
                        st.session_state.sepet[real_index]["width"] = yeni_en
                        st.session_state.sepet[real_index]["length"] = yeni_boy
                        st.session_state.sepet[real_index]["height"] = yeni_yukseklik
                        st.session_state.sepet[real_index]["weight"] = yeni_agirlik
                        st.session_state[f"edit_{real_index}"] = False
                        st.rerun()

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Sepeti Temizle", use_container_width=True):
            st.session_state.sepet = []
            st.rerun()

    with col2:
        if st.button("Gönderileri Kaydet", use_container_width=True):
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

                barkod = (
                    db.query(Barcode)
                    .filter(Barcode.barcode == item["barcode"])
                    .first()
                )

                if barkod:
                    barkod.is_used = True

            db.commit()
            st.session_state.sepet = []
            st.success("Gönderiler kaydedildi.")
            st.rerun()
