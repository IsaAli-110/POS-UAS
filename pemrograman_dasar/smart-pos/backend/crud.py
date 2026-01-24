from sqlalchemy.orm import Session
from . import models, schemas
from .auth import get_password_hash

# User
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Category
def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Category).offset(skip).limit(limit).all()

def create_category(db: Session, category: schemas.CategoryCreate):
    db_category = models.Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if category:
        db.delete(category)
        db.commit()
    return category

# Product
def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Product).offset(skip).limit(limit).all()

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_product_by_barcode(db: Session, barcode: str):
    return db.query(models.Product).filter(models.Product.barcode == barcode).first()

def update_product_stock(db: Session, product_id: int, quantity_sold: int):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product:
        product.stock -= quantity_sold
        db.commit()
        db.refresh(product)
    return product

def delete_product(db: Session, product_id: int):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product:
        db.delete(product)
        db.commit()
    return product

# Transaction
def create_transaction(db: Session, transaction: schemas.TransactionCreate, cashier_id: int):
    # Calculate total and verify stock
    total_amount = 0
    
    # Create transaction record
    db_transaction = models.Transaction(cashier_id=cashier_id, total_amount=0) # Update total later
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    for item in transaction.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product:
            continue # Should handle error
        if product.stock < item.quantity:
            continue # Should handle error
        
        # Deduct stock
        product.stock -= item.quantity
        
        # Add item
        price = product.price
        total_amount += price * item.quantity
        
        db_item = models.TransactionItem(
            transaction_id=db_transaction.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_sale=price
        )
        db.add(db_item)
    
    db_transaction.total_amount = total_amount
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_transactions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Transaction).offset(skip).limit(limit).all()

def delete_transaction(db: Session, transaction_id: int):
    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if transaction:
        db.delete(transaction)
        db.commit()
    return transaction
