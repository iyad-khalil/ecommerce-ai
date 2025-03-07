from database import engine, Base, SessionLocal # Importer le moteur de base de données, la base de données et la session
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Product
from schemas import ProductCreate, Product
from transformers import MarianMTModel, MarianTokenizer # Importer les classes MarianMTModel et MarianTokenizer de la librairie transformers
import openai
openai.api_key = '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'

# Créer les tables en base de données
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API de l'e-commerce AI !"}


# Dépendance pour obtenir une session de base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Route pour ajouter un produit
@app.post("/products/", response_model=Product)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(name=product.name, description=product.description)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# Route pour récupérer tous les produits
@app.get("/products/", response_model=list[Product])
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()



# Charger le modèle de traduction
def load_translation_model():
    model_name = "Helsinki-NLP/opus-mt-en-fr"  # Traduction de l'anglais vers le français (tu peux changer pour d'autres langues)
    model = MarianMTModel.from_pretrained(model_name)
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    return model, tokenizer

model, tokenizer = load_translation_model()


# Fonction de traduction
def translate_text(text: str, target_lang: str = "fr"):
    translated = model.generate(**tokenizer(text, return_tensors="pt", padding=True))
    return tokenizer.decode(translated[0], skip_special_tokens=True)

# Fonction de génération d'image avec DALL-E
def generate_product_image(description: str):
    response = openai.Image.create(
        prompt=description,
        n=1,
        size="256x256"
    )
    image_url = response['data'][0]['url']
    return image_url


# Route pour traduire la description d'un produit
@app.put("/products/{product_id}/translate/")
def translate_product_description(product_id: int, target_lang: str = "fr", db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    translated_description = translate_text(db_product.description, target_lang)
    db_product.description = translated_description
    db.commit()
    db.refresh(db_product)
    return db_product


# Route pour générer une image pour un produit
@app.put("/products/{product_id}/generate-image/")
def generate_image_for_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    image_url = generate_product_image(db_product.description)
    db_product.image_url = image_url  # Ajoute un champ image_url à ta table `products`
    db.commit()
    db.refresh(db_product)
    return db_product