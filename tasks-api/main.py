import uvicorn
from typing import Optional
from enum import Enum
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime

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

# Database setup
Base = declarative_base()


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


class TaskCreate(BaseModel):
    title: str
    description: Optional[str]
    staff_type: StaffType
    assigned_to: Optional[str]
    order_id: int
    order_type: str
    parent_task_id: Optional[int] = None

class TaskUpdate(BaseModel):
    description: Optional[str]
    assigned_to: Optional[str]
    priority: Optional[TaskPriority]
    status: Optional[TaskStatus]

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    staff_type: StaffType
    assigned_to: Optional[str]
    priority: TaskPriority
    status: TaskStatus
    created_at: datetime
    order_id: int
    order_type: str
    parent_task_id: Optional[int]

    class Config:
        from_attributes = True # TODO: response = TaskResponse.model_validate(Task.first)


    # class YourSchema(BaseModel):
#     field1: str
#     field2: int

# Database connection (ta sama co w Orders API)
DATABASE_URL = "postgresql://postgres:postgres@localhost/api"
engine = create_engine(DATABASE_URL)

Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper functions
def not_found_exception(db_item):
    """Helper function to raise 404 if item not found"""
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

# Routes
@app.get("/")
def root():
    return {"message": "Your new API is running!"}

# TODO: Dodaj endpointy
@app.get("/tasks")
def get_all_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return tasks

@app.post("/tasks")  # wywolywany przez Orders API
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    new_task = Task(
        title=task.title,
        description=task.description,
        staff_type=task.staff_type.value,  # ← Enum → String
        assigned_to=task.assigned_to,
        order_id=task.order_id,
        order_type=task.order_type,
        parent_task_id=task.parent_task_id
        # status i priority maja defaulty
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.get("/tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    not_found_exception(task)
    return task

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)