from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table, Date
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

# Many-to-Many Association Table
task_tags = Table(
    "task_tags",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String, nullable=True)
    priority = Column(Integer, nullable=False) # Validation 1-5 happens in Pydantic
    due_date = Column(Date, nullable=False)
    completed = Column(Boolean, default=False, index=True) # Index for filtering
    is_deleted = Column(Boolean, default=False) # Soft delete
    
    # Relationship
    tags = relationship("Tag", secondary=task_tags, backref="tasks")