from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def migrate():
    if not DATABASE_URL:
        print("Error: DATABASE_URL not found in .env")
        return

    print(f"Connecting to: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'DB'}")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("Checking for missing columns in 'products' table...")
        
        # Add image_url_2
        try:
            conn.execute(text("ALTER TABLE products ADD COLUMN image_url_2 TEXT"))
            conn.commit()
            print("Added image_url_2 column.")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                print("Column image_url_2 already exists. Skipping.")
            else:
                print(f"Error adding image_url_2: {e}")

        # Add image_url_3
        try:
            conn.execute(text("ALTER TABLE products ADD COLUMN image_url_3 TEXT"))
            conn.commit()
            print("Added image_url_3 column.")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                print("Column image_url_3 already exists. Skipping.")
            else:
                print(f"Error adding image_url_3: {e}")

        print("Migration completed.")

if __name__ == "__main__":
    migrate()
