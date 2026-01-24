from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine
from backend import models
from datetime import datetime, timedelta
import random

# Ensure tables exist
models.Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    
    # 1. Categories
    categories = ["Makanan Ringan", "Minuman Dingin", "Kopi", "Alat Tulis", "Sembako"]
    db_cats = []
    print("Creating Categories...")
    for cat_name in categories:
        existing = db.query(models.Category).filter(models.Category.name == cat_name).first()
        if not existing:
            cat = models.Category(name=cat_name)
            db.add(cat)
            db_cats.append(cat)
        else:
            db_cats.append(existing)
    db.commit()

    # Refresh to get IDs
    for cat in db_cats:
        db.refresh(cat)

    # 2. Products
    products_data = [
        {"name": "Chitato Sapi Panggang", "barcode": "899123456", "price": 12000, "stock": 50, "cat": "Makanan Ringan"},
        {"name": "Oreo Vanilla", "barcode": "899123457", "price": 8500, "stock": 40, "cat": "Makanan Ringan"},
        {"name": "Teh Pucuk Harum", "barcode": "899123458", "price": 4000, "stock": 100, "cat": "Minuman Dingin"},
        {"name": "Aqua 600ml", "barcode": "899123459", "price": 3500, "stock": 120, "cat": "Minuman Dingan"},
        {"name": "Kopi Kapal Api", "barcode": "899123460", "price": 2500, "stock": 200, "cat": "Kopi"},
        {"name": "Indomie Goreng", "barcode": "899123461", "price": 3500, "stock": 150, "cat": "Sembako"},
        {"name": "Buku Sidu 38 Lembar", "barcode": "899123462", "price": 5000, "stock": 80, "cat": "Alat Tulis"},
        {"name": "Pulpen Pilot", "barcode": "899123463", "price": 3000, "stock": 60, "cat": "Alat Tulis"},
        {"name": "Minyak Goreng 2L", "barcode": "899123464", "price": 35000, "stock": 20, "cat": "Sembako"},
        {"name": "Susu UHT Full Cream", "barcode": "899123465", "price": 18000, "stock": 30, "cat": "Minuman Dingin"},
        # Produk tambahan 11-20
        {"name": "Lays Rumput Laut", "barcode": "899123466", "price": 13000, "stock": 45, "cat": "Makanan Ringan"},
        {"name": "Pocari Sweat 500ml", "barcode": "899123467", "price": 7000, "stock": 90, "cat": "Minuman Dingin"},
        {"name": "Good Day Cappuccino", "barcode": "899123468", "price": 2000, "stock": 180, "cat": "Kopi"},
        {"name": "Beras 5kg", "barcode": "899123469", "price": 65000, "stock": 15, "cat": "Sembako"},
        {"name": "Pensil 2B Faber Castell", "barcode": "899123470", "price": 2500, "stock": 100, "cat": "Alat Tulis"},
        {"name": "Tango Wafer Coklat", "barcode": "899123471", "price": 6000, "stock": 55, "cat": "Makanan Ringan"},
        {"name": "Coca Cola 330ml", "barcode": "899123472", "price": 5500, "stock": 110, "cat": "Minuman Dingin"},
        {"name": "Nescafe Classic", "barcode": "899123473", "price": 1500, "stock": 220, "cat": "Kopi"},
        {"name": "Gula Pasir 1kg", "barcode": "899123474", "price": 15000, "stock": 35, "cat": "Sembako"},
        {"name": "Penghapus Karet Joyko", "barcode": "899123475", "price": 1500, "stock": 75, "cat": "Alat Tulis"},
    ]

    print("Creating Products...")
    db_products = []
    for p in products_data:
        existing = db.query(models.Product).filter(models.Product.barcode == p["barcode"]).first()
        
        # Find category ID
        cat_id = next((c.id for c in db_cats if c.name == p["cat"]), None)
        
        if not existing and cat_id:
            prod = models.Product(
                name=p["name"],
                barcode=p["barcode"],
                price=p["price"],
                stock=p["stock"],
                category_id=cat_id
            )
            db.add(prod)
            db_products.append(prod)
        elif existing:
            db_products.append(existing)
            
    db.commit()
    
    # Refresh Products
    for prod in db_products:
        db.refresh(prod)

    # 3. Dummy Transactions (Past 7 days)
    print("Creating Dummy Transactions...")
    
    # Get Admin User ID for cashier
    admin = db.query(models.User).filter(models.User.username == "admin").first()
    if not admin:
        print("Please restart backend first to create admin user.")
        return

    for i in range(20):
        # Random date within last 7 days
        days_ago = random.randint(0, 7)
        txn_date = datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(0, 12))
        
        txn = models.Transaction(
            cashier_id=admin.id,
            total_amount=0,
            created_at=txn_date
        )
        db.add(txn)
        db.commit()
        db.refresh(txn)
        
        # Add random items
        total = 0
        num_items = random.randint(1, 4)
        selected_products = random.sample(db_products, num_items)
        
        for prod in selected_products:
            qty = random.randint(1, 3)
            price = prod.price
            total += price * qty
            
            item = models.TransactionItem(
                transaction_id=txn.id,
                product_id=prod.id,
                quantity=qty,
                price_at_sale=price
            )
            db.add(item)
            
            # Reduce stock if we cared about logic here but this is dummy data
            
        txn.total_amount = total
        db.commit()

    db.close()
    print("Data Seeding Complete!")

if __name__ == "__main__":
    seed_data()
