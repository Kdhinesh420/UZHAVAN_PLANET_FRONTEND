from sqlalchemy.orm import Session
from db.session import SessionLocal, engine
from models.Category import Category

def seed_data():
    db = SessionLocal()
    
    try:
        # 1. Seed Categories (ONLY SEEDS)
        categories = [
            {"name": "Vegetable Seeds", "description": "Seeds for growing fresh vegetables"},
            {"name": "Flower Seeds", "description": "Beautiful flower seeds for your garden"},
            {"name": "Fruit Seeds", "description": "Seeds for delicious fruits"},
            {"name": "Herb Seeds", "description": "Medicinal and culinary herb seeds"},
            {"name": "Grain Seeds", "description": "Rice, Wheat, and other grains"}
        ]
        
        print("Seeding Seed Categories...")
        for cat_data in categories:
            existing = db.query(Category).filter(Category.name == cat_data["name"]).first()
            if not existing:
                cat = Category(name=cat_data["name"], description=cat_data["description"])
                db.add(cat)
                print(f"Added category: {cat_data['name']}")
            else:
                print(f"Category exists: {cat_data['name']}")
        
        db.commit()
        print("Seeding completed successfully! 🌱")
        
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
