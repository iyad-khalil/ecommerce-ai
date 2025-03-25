from sqlalchemy import Column, Integer, String
from database import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    description = Column(String(1000))
    image_url = Column(String(1024), nullable=True)