from enum import Enum
from sqlalchemy import Column, Integer, String, Float, Boolean
from config.db.connection import Base

class OrderStatus(str, Enum):
    NEW = "nowe"
    IN_PREPARATION = "w przygotowaniu"
    READY = "gotowe"
    DELIVERED = "dostarczone"
    CANCELLED = "anulowane"

class OrderType(str, Enum):
    DINE_IN = "na_sale"
    DELIVERY = "na_dowoz"

class RestaurantOrder(Base):
    __tablename__ = "restaurant_orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)
    status = Column(String, nullable=False)
    items = Column(String, nullable=False)
    total_price = Column(Float, nullable=False)
    ready = Column(Boolean, default=False)
    delivered = Column(Boolean, default=False)
    order_type = Column(String, nullable=False)
    table_number = Column(Integer, nullable=True)
    delivery_address = Column(String, nullable=True)