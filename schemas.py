from pydantic import BaseModel
from typing import Optional

class ProductBase(BaseModel):
    name: str
    description: str

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    image_url: Optional[str] = None

    class Config:
        from_attributes = True