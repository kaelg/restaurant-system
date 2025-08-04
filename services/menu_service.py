from sqlalchemy.orm import Session
from fastapi import Depends
from config.db.connection import get_db
from models.menu import MenuItem
from schemas.menu import MenuItemResponse, MenuItemCreate


def get_all_items(db: Session):
    return db.query(MenuItem).all()

def get_item_by_id(db: Session, id: int):
    item = db.query(MenuItem).filter(MenuItem.id == id).first() #first sam zwraca None
    if item is None:
        return None
    return item

def create_item(db: Session, menu_item: MenuItemCreate):
    new_item = MenuItem(
        name=menu_item.name,
        category=menu_item.category.value,
        price=menu_item.price,
        prep_time_minutes=menu_item.prep_time_minutes,
        description=menu_item.description
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item
