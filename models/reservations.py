from sqlalchemy import Column, Integer, String, DateTime
from enum import Enum
from config.db.connection import Base
from datetime import datetime

# Enums
class ReservationStatus(str, Enum):
    PENDING = "oczekujaca"
    CONFIRMED = "potwierdzona"
    CANCELLED = "anulowana"
    COMPLETED = "zakonczona"


# Database models
class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)
    table_number = Column(Integer, nullable=False)
    reservation_date = Column(String, nullable=False)  # "2025-06-18"
    reservation_time = Column(String, nullable=False)  # "19:30"
    guests_count = Column(Integer, default=2)
    status = Column(String, default=ReservationStatus.PENDING.value)
    created_at = Column(DateTime, default=datetime.now)