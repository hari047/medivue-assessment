from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import date

# Tag Schemas
class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class TagResponse(TagBase):
    id: int
    class Config:
        from_attributes = True

# Task Schemas
class TaskBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    priority: int = Field(..., ge=1, le=5) # Enforces 1-5 [cite: 22]
    due_date: date
    completed: bool = False

    @field_validator('due_date')
    def date_must_be_future(cls, v):
        # Note: Ensure you handle timezone logic if strictly required, 
        # but for this assessment, a simple comparison works.
        if v < date.today():
            raise ValueError('Due date cannot be in the past') # [cite: 25]
        return v

class TaskCreate(TaskBase):
    tags: Optional[List[str]] = [] # Input is list of strings [cite: 24]

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    due_date: Optional[date] = None
    completed: Optional[bool] = None
    tags: Optional[List[str]] = None

class TaskResponse(TaskBase):
    id: int
    tags: List[TagResponse] = []
    
    class Config:
        from_attributes = True