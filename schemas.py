from pydantic import BaseModel

class ProductBase(BaseModel):
    name: str
    description: str

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    class Config:
        orm_mode = True
# The Pydantic models in schemas.py are used to define the data that can be sent or received by the API.