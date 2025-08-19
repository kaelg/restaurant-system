from typing import List
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from config.db.connection import get_db
from models.menu import MenuItem
from schemas.menu import  MenuItemCreate, MenuItemUpdate, MenuItemResponse
from services import menu_service

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
    menu = menu_service.get_all_items(db)
    return menu

@app.get("/menu/{item_id}", response_model = MenuItemResponse)
def get_menu_item(item_id: int, db: Session = Depends(get_db)):
    menu_item = menu_service.get_item_by_id(db,item_id)
    if menu_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return menu_item

@app.post("/menu", response_model=MenuItemResponse)
def create_menu_item(menu_item: MenuItemCreate, db: Session = Depends(get_db)):
    item = menu_service.create_item(db,menu_item)
    return MenuItemResponse.model_validate(item)#to samo co return new_menu_item ale jasno mowi ze api ma to przemapowac

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