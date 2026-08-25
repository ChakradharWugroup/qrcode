from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
import string
import random
from datetime import datetime, timedelta

def get_china_time():
    return datetime.utcnow() + timedelta(hours=8)

def generate_collection_id():
    # Generates a random 6-character ID like 'ABC123'
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(6))

class Collection(Base):
    __tablename__ = "collections"

    id = Column(String(255), primary_key=True, default=generate_collection_id, index=True)
    name = Column(String(255), index=True)
    created_at = Column(DateTime(timezone=True), default=get_china_time)

    qr_codes = relationship("GarmentQRCode", back_populates="collection")

class GarmentQRCode(Base):
    __tablename__ = "garment_qr_codes"

    id = Column(Integer, primary_key=True, index=True)
    collection_id = Column(String(255), ForeignKey("collections.id"))
    
    qr_data = Column(String(1000), index=True) # The actual decoded URL/text from the QR
    
    # Label specific data
    company_name = Column(String(255), default="江西大藤制衣有限公司")
    style_no = Column(String(255))
    bed_no = Column(String(255))
    bundle_no = Column(String(255))
    quantity = Column(Integer)
    color = Column(String(255))
    size = Column(String(255))
    total_bundles = Column(Integer, nullable=True)
    total_quantity = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), default=get_china_time)

    collection = relationship("Collection", back_populates="qr_codes")
