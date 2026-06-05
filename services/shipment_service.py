from database.models import Barcode


def get_available_barcodes(db, count):

    barkodlar = (
        db.query(Barcode)
        .filter(Barcode.is_used == False)
        .limit(count)
        .all()
    )

    return barkodlar
