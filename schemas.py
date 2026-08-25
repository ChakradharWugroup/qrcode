from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class GarmentQRCodeBase(BaseModel):
    qr_data: str
    company_name: str = "江西大藤制衣有限公司"
    style_no: str
    bed_no: str
    bundle_no: str
    quantity: int
    color: str
    size: str
    total_bundles: Optional[int] = None
    total_quantity: Optional[int] = None

class GarmentQRCodeCreate(GarmentQRCodeBase):
    pass

class GarmentQRCode(GarmentQRCodeBase):
    id: int
    collection_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class CollectionBase(BaseModel):
    name: str

class CollectionCreate(CollectionBase):
    pass

class Collection(CollectionBase):
    id: str
    created_at: datetime
    qr_codes: List[GarmentQRCode] = []

    class Config:
        from_attributes = True
