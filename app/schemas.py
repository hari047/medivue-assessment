"""
Pydantic schemas for request/response serialization and validation.
Enforces data integrity for task and tag objects.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional
from datetime import date

# Tag Schemas

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    """Schema for creating a new tag."""
    pass

class TagResponse(TagBase):
    """Schema for tag data returned by the API."""
    id: int
    model_config = ConfigDict(from_attributes=True)

# Task Schemas

class TaskBase(BaseModel):
    """
    Base properties for a Task.
    Includes validation for title length and priority range.
    """
    title: str = Field(..., max_length=200, description="Brief title of the task")
    description: Optional[str] = Field(None, description="Detailed task description")
    # Enforces 1-5 priority range
    priority: int = Field(..., ge=1, le=5, description="Priority level from 1 (lowest) to 5 (highest)")
    due_date: date = Field(..., description="The date the task must be completed")
    completed: bool = Field(False, description="Status of task completion")

    @field_validator('due_date')
    @classmethod
    def date_must_be_future(cls, v: date) -> date:
        """Ensures that a due date is not set in the past."""
        if v < date.today():
            raise ValueError('Due date cannot be in the past')
        return v

class TaskCreate(TaskBase):
    """Schema for creating a new task, including optional tag strings."""
    tags: Optional[List[str]] = Field(default=[], description="List of tag names associated with the task")

class TaskUpdate(BaseModel):
    """
    Schema for partial task updates (PATCH). 
    All fields are optional to allow single-field updates.
    """
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    due_date: Optional[date] = None
    completed: Optional[bool] = None
    tags: Optional[List[str]] = None

class TaskResponse(TaskBase):
    """Complete Task data including database ID and expanded Tag objects."""
    id: int
    tags: List[TagResponse] = []
    
    model_config = ConfigDict(from_attributes=True)
