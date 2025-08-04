from typing import Optional
from models.menu import MenuCategory
from pydantic import BaseModel


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