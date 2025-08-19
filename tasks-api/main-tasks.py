import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from config.db.connection import get_db
from models.tasks import Task
from schemas.tasks import TaskStatus, TaskPriority, TaskCreate, TaskResponse, TaskUpdate

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