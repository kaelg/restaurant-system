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
    menu_item = menu_service.get_item_by_id(db, item_id)
    return menu_item

@app.post("/menu", response_model=MenuItemResponse)
def create_menu_item(menu_item: MenuItemCreate, db: Session = Depends(get_db)):
    item = menu_service.create_item(db, menu_item)
    return MenuItemResponse.model_validate(item)#to samo co return new_menu_item ale jasno mowi ze api ma to przemapowac

@app.put("/menu/{item_id}", response_model=MenuItemResponse)
def update_menu_item(item_id: int, menu_item_update: MenuItemUpdate, db: Session = Depends(get_db)):
    menu_item_response = menu_service.update_item(db, item_id, menu_item_update)
    return MenuItemResponse.model_validate(menu_item_response)

@app.delete("/menu/{item_id}")
def delete_menu_item(item_id: int, db: Session = Depends(get_db)):
    return menu_service.delete_item(db, item_id)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)