from sqlalchemy import Column, String, Integer, Float, Date, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class POHeader(Base):
    __tablename__ = "po_headers"

    po_no = Column(String, primary_key=True, index=True)
    supplier_name = Column(String)
    order_date = Column(String)

    items = relationship("POItem", back_populates="header", cascade="all, delete")

class POItem(Base):
    __tablename__ = "po_items"

    id = Column(Integer, primary_key=True, index=True)
    po_no = Column(String, ForeignKey("po_headers.po_no"))

    seq = Column(Integer)
    product_code = Column(String)
    product_name_cn = Column(String)
    product_name_pt = Column(String)
    ncm = Column(String)

    qty = Column(Float)
    unit_price_rmb = Column(Float)
    line_total_rmb = Column(Float)

    header = relationship("POHeader", back_populates="items")
