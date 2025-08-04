from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from models.reservations import ReservationStatus

class ReservationCreate(BaseModel):
    customer_name: str
    customer_phone: str
    table_number: int
    reservation_date: str  # "2025-06-18"
    reservation_time: str  # "19:30"
    guests_count: Optional[int] = 2


class ReservationUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    table_number: Optional[int] = None
    reservation_date: Optional[str] = None
    reservation_time: Optional[str] = None
    guests_count: Optional[int] = None
    status: Optional[ReservationStatus] = None


class ReservationResponse(BaseModel):
    id: int
    customer_name: str
    customer_phone: str
    table_number: int
    reservation_date: str
    reservation_time: str
    guests_count: int
    status: ReservationStatus
    created_at: datetime

    class Config:
        from_attributes = True