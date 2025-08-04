from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime
from config.db.connection import Base
from datetime import datetime

class StaffType(str,Enum):
    CHEF = "kucharz"
    WAITER = "kelner"
    DRIVER = "dostawca"

class TaskStatus(str,Enum):
    NEW = "nowe"
    IN_PROGRESS = "w trakcie"
    DONE = "ukonczone"

class TaskPriority(str, Enum):
    LOW = "niski"
    MID = "sredni"
    HIGH = "wysoki"



class Task(Base):
    __tablename__ = "restaurant_tasks"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String)
    staff_type = Column(String, nullable=False)
    assigned_to = Column(String)
    status = Column(String, default=TaskStatus.NEW.value)
    priority = Column(String, default=TaskPriority.MID.value)
    created_at = Column(DateTime, default=datetime.now)
    order_id = Column(Integer,primary_key=True, index=True)
    order_type = Column(String, nullable=False)
    parent_task_id = Column(Integer, nullable=True)