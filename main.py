import os
from database import engine, Base, SessionLocal
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Product as ProductModel
from schemas import ProductCreate, Product as ProductSchema
from transformers import MarianMTModel, MarianTokenizer
import openai
from dotenv import load_dotenv

load_dotenv()

# Charger ta clé OpenAI depuis les variables d'environnement
openai.api_key = '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'
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API de l'e-commerce AI !"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/products/", response_model=ProductSchema)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = ProductModel(name=product.name, description=product.description)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/products/", response_model=list[ProductSchema])
def get_products(db: Session = Depends(get_db)):
    return db.query(ProductModel).all()

# Charger le modèle de traduction
def load_translation_model():
    model_name = "Helsinki-NLP/opus-mt-en-fr"
    model = MarianMTModel.from_pretrained(model_name)
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    return model, tokenizer

model, tokenizer = load_translation_model()

def translate_text(text: str, target_lang: str = "fr"):
    translated = model.generate(**tokenizer(text, return_tensors="pt", padding=True))
    return tokenizer.decode(translated[0], skip_special_tokens=True)

def generate_product_image(description: str):
    response = openai.images.generate(
        model="dall-e-3",  # Use DALL·E model instead of "image-alpha-001"
        prompt=description,  
        n=1,  
        size="1024x1024"
    )
    return response.data[0].url  # Updated way to get image URL

@app.put("/products/{product_id}/translate/", response_model=ProductSchema)
def translate_product_description(product_id: int, target_lang: str = "fr", db: Session = Depends(get_db)):
    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    db_product.description = translate_text(db_product.description, target_lang)
    db.commit()
    db.refresh(db_product)
    return db_product
@app.get("/ping")
def ping():
    return {"message": "pong"}


@app.put("/products/{product_id}/generate-image/", response_model=ProductSchema)
def generate_image_for_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    # Generate image URL using the new OpenAI API
    image_url = generate_product_image(db_product.description)

    # Update the product's image URL
    db_product.image_url = image_url
    db.commit()
    db.refresh(db_product)

    return db_product