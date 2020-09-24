from pydantic import BaseModel
from typing import Optional

from uuid import UUID
from datetime import date, datetime

class BaseTask(BaseModel):
    name: str
    description: str
    username: str
    priority: int
    duration: int
    due_date: date
    completed_at: Optional[datetime]

class Task(BaseTask):
    id: UUID

class User(BaseModel):
    username: str
    name: str
    password: str

class TaskComment(BaseModel):
    id: UUID
    task_id: UUID
    contents: str
    created_at: datetime