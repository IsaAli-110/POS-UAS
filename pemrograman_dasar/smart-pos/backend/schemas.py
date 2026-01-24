from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

# Token
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# User
class UserBase(BaseModel):
    username: str
    role: str = "cashier"

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

# Category
class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int

    class Config:
        orm_mode = True

# Product
class ProductBase(BaseModel):
    name: str
    barcode: str
    price: float
    stock: int
    category_id: int

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    category: Optional[Category] = None

    class Config:
        orm_mode = True

# TransactionItem
class TransactionItemBase(BaseModel):
    product_id: int
    quantity: int

class TransactionItemCreate(TransactionItemBase):
    pass

class TransactionItem(TransactionItemBase):
    id: int
    price_at_sale: float
    product: Optional[Product] = None

    class Config:
        orm_mode = True

# Transaction
class TransactionCreate(BaseModel):
    items: List[TransactionItemCreate]

class Transaction(BaseModel):
    id: int
    cashier_id: int
    total_amount: float
    created_at: datetime
    items: List[TransactionItem]
    cashier: Optional[User] = None

    class Config:
        orm_mode = True
