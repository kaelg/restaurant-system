from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from models.tasks import StaffType, TaskStatus, TaskPriority

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
