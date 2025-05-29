from typing import Optional, List

import uvicorn
from enum import Enum
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from unicodedata import category

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=['*'],
)

# Database setup
Base = declarative_base()

# Enums
class MenuCategory(str, Enum):
    APPETIZER = "przystawka"
    MAIN_COURSE = "danie_glowne"
    DESSERT = "deser"
    DRINK = "napoj"

# Database models
class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    prep_time_minutes = Column(Integer, default=10)
    available = Column(Boolean, default=True)
    description = Column(String)

# Pydantic models
class MenuItemCreate(BaseModel):
    name: str
    category: MenuCategory
    price: float
    prep_time_minutes: Optional[int] = 10
    description: Optional[str] = None

class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[MenuCategory]
    price: Optional[float] = None
    prep_time_minutes: Optional[int] = None
    available: Optional[bool] = None
    description: Optional[str] = None

class MenuItemResponse(BaseModel):
    id: int
    name: str
    category: MenuCategory
    price: float
    prep_time_minutes: int
    available: bool
    description: Optional[str]

    class Config:
        from_attributes = True

# Database connection (ta sama co w Orders API)
DATABASE_URL = "postgresql://postgres:postgres@localhost/api"
engine = create_engine(DATABASE_URL)

Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper functions
def not_found_exception(db_item):
    """Helper function to raise 404 if item not found"""
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

# Routes
@app.get("/")
def root():
    return {"message": "Your new API is running!"}

@app.get("/menu", response_model = List[MenuItemResponse])
def get_all_menu_items(db: Session = Depends(get_db)):
    menu = db.query(MenuItem).all()
    return menu

@app.get("/menu/{item_id}", response_model = MenuItemResponse)
def get_menu_item(item_id: int, db: Session = Depends(get_db)):
    menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if menu_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return menu_item

@app.post("/menu", response_model=MenuItemResponse)
def create_menu_item(menu_item: MenuItemCreate, db: Session = Depends(get_db)):
    new_menu_item = MenuItem(
        name = menu_item.name,
        category = menu_item.category.value,
        price = menu_item.price,
        prep_time_minutes = menu_item.prep_time_minutes,
        description = menu_item.description
    )
    db.add(new_menu_item)
    db.commit()

    db.refresh(new_menu_item)
    return MenuItemResponse.model_validate(new_menu_item) #to samo co return new_menu_item ale jasno mowi ze api ma to przemapowac

@app.put("/menu/{item_id}", response_model=MenuItemResponse)
def update_menu_item(item_id: int, menu_update: MenuItemUpdate, db: Session = Depends(get_db)):
    db_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404,
                            detail="Menu item not found")
    if menu_update.name is not None:
        db_item.name = menu_update.name
    if menu_update.category is not None:
        db_item.category = menu_update.category.value
    if menu_update.price is not None:
        db_item.price = menu_update.price
    if menu_update.prep_time_minutes is not None:
        db_item.prep_time_minutes = menu_update.prep_time_minutes
    if menu_update.available is not None:
        db_item.available = menu_update.available
    if menu_update.description is not None:
        db_item.description = menu_update.description

    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/menu/{item_id}")
def delete_menu_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404,
                            detail="Menu item not found")
    db.delete(db_item)
    db.commit()
    return {"id": db_item.id, "Order": "deleted"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)