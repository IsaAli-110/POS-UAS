from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models, database, crud, schemas
from .routers import auth, products, transactions

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Smart POS System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(transactions.router)

@app.on_event("startup")
def startup_event():
    db = database.SessionLocal()
    
    # 1. Create Admin User
    user = crud.get_user_by_username(db, "admin")
    if not user:
        admin_data = schemas.UserCreate(username="admin", password="admin123", role="admin")
        crud.create_user(db, admin_data)
        print("Admin user created: admin/admin123")
    db.close()

    # 2. Auto-seed Products & Data
    try:
        from .seed_data import seed_data
        seed_data()
        print("Auto-seeding check complete.")
    except Exception as e:
        print(f"Auto-seeding skipped/failed: {e}")

@app.get("/")
def read_root():
    return {"message": "Welcome to Smart POS System API"}
