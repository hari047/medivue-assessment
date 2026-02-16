"""
SQLAlchemy models defining the database schema.
Implements Many-to-Many relationships and Soft Delete strategies.
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table, Date
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Association Table
# Facilitates the Many-to-Many relationship between Tasks and Tags.
task_tags = Table(
    "task_tags",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)

class Tag(Base):
    """Model representing a task category or tag."""
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

class Task(Base):
    """
    Model representing a work task. 
    Includes a soft-delete flag to maintain audit trails.
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String, nullable=True)
    priority = Column(Integer, nullable=False) # Range validation (1-5) enforced in Pydantic
    due_date = Column(Date, nullable=False)
    
    # Indexed for efficient filtering in GET requests
    completed = Column(Boolean, default=False, index=True) 
    
    # Soft Delete flag for data integrity and recovery
    is_deleted = Column(Boolean, default=False, index=True) 
    
    # Relationships
    tags = relationship("Tag", secondary=task_tags, backref="tasks")
