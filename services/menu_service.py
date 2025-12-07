from sqlalchemy.orm import Session
from fastapi import Depends
from config.db.connection import get_db
from models.menu import MenuItem
from schemas.menu import MenuItemResponse, MenuItemCreate, MenuItemUpdate
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException
def get_all_items(db: Session):
    return db.query(MenuItem).all()

def get_item_by_id(db: Session, id: int):
    item = db.query(MenuItem).filter(MenuItem.id == id).first() #first sam zwraca None
    if item is None:
        return None
    return item

def create_item(db: Session, menu_item: MenuItemCreate) -> MenuItem:
    db.add(menu_item)
    db.commit()
    db.refresh(menu_item)
    return menu_item

def update_item(db: Session, item_id: int, menu_update: MenuItemUpdate)-> MenuItem:
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

def delete_item(db: Session, item_id: int):
    db_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404,
                            detail="Menu item not found")
    db.delete(db_item)
    db.commit()
    return {"id": db_item.id, "Order": "deleted"}