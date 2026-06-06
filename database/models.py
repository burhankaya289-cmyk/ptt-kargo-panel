from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Float, Boolean


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    username = Column(String, unique=True)
    password = Column(String)

    role = Column(String)


class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True)

    branch_code = Column(String)
    branch_name = Column(String)

    address = Column(String)
    district = Column(String)
    city = Column(String)


class ProductDimension(Base):
    __tablename__ = "product_dimensions"

    id = Column(Integer, primary_key=True)

    product_name = Column(String)

    width = Column(Float)
    length = Column(Float)
    height = Column(Float)
    weight = Column(Float)


class Barcode(Base):
    __tablename__ = "barcodes"

    id = Column(Integer, primary_key=True)

    barcode = Column(String)

    is_used = Column(Boolean, default=False)


class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True)

    barcode = Column(String)
    tracking_number = Column(String)

    branch_code = Column(String)
    branch_name = Column(String)

    recipient_name = Column(String)

    address = Column(String)
    district = Column(String)
    city = Column(String)

    phone = Column(String)

    product_name = Column(String)

    width = Column(Float)
    length = Column(Float)
    height = Column(Float)
    weight = Column(Float)

    created_by = Column(String)

    is_printed = Column(Boolean, default=False)
    is_edited = Column(Boolean, default=False)
