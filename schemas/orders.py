from typing import Optional
from pydantic import BaseModel
from models.orders import OrderStatus, OrderType

class CustomerOrder(BaseModel):
    customer_name: str
    customer_phone: str
    items: str
    total_price: float
    order_type: OrderType
    table_number: Optional[int] = None
    delivery_address: Optional[str] = None

class RestaurantOrderUpdate(BaseModel):
    customer_name: str
    customer_phone: str
    status: str
    items: str
    total_price: float
    ready: bool
    delivered: bool

class StatusUpdate(BaseModel):
    new_status: OrderStatus

