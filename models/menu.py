from sqlalchemy import Column, Integer, String, Float, Boolean
from enum import Enum
from config.db.connection import Base

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
