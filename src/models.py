from pydantic import BaseModel
from typing import Any, Optional

from uuid import UUID
from datetime import date, datetime

class BaseAPIResponse(BaseModel):
    status: int
    data: Optional[Any]
    message: Optional[str]

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
    
class UserPayload(BaseModel):
    username: str
    password: str
    name: str