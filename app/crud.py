from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from . import models, schemas
from datetime import datetime

# 1. Create a Task
def create_task(db: Session, task: schemas.TaskCreate):
    # Convert tag strings to Tag objects
    db_tags = []
    if task.tags:
        for tag_name in task.tags:
            # Check if tag exists, if not create it
            tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
            if not tag:
                tag = models.Tag(name=tag_name)
                db.add(tag)
                db.commit()
                db.refresh(tag)
            db_tags.append(tag)

    # Create the task
    db_task = models.Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        due_date=task.due_date,
        tags=db_tags
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# 2. Get Single Task
def get_task(db: Session, task_id: int):
    # Filter out soft-deleted tasks
    return db.query(models.Task).filter(models.Task.id == task_id, models.Task.is_deleted == False).first()

# 3. Get All Tasks (Filtering Logic)
def get_tasks(
    db: Session, 
    skip: int = 0, 
    limit: int = 10, 
    completed: bool = None, 
    priority: int = None, 
    tags: str = None
):
    query = db.query(models.Task).filter(models.Task.is_deleted == False)

    # Filter by completion status
    if completed is not None:
        query = query.filter(models.Task.completed == completed)

    # Filter by priority
    if priority is not None:
        query = query.filter(models.Task.priority == priority)
    
    # Filter by tags (CSV format)
    if tags:
        tag_list = tags.split(",")
        # Join with tags table and filter where tag name is in our list
        query = query.join(models.Task.tags).filter(models.Tag.name.in_(tag_list)).distinct()

    return query.offset(skip).limit(limit).all()

# 4. Update Task
def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate):
    db_task = get_task(db, task_id)
    if not db_task:
        return None

    # Update simple fields
    update_data = task_update.dict(exclude_unset=True)
    
    # Handle tags separately if they are being updated
    if "tags" in update_data:
        tag_names = update_data.pop("tags")
        new_tags = []
        for name in tag_names:
            tag = db.query(models.Tag).filter(models.Tag.name == name).first()
            if not tag:
                tag = models.Tag(name=name)
                db.add(tag) # Add new tag to DB
            new_tags.append(tag)
        db_task.tags = new_tags

    # Update remaining fields
    for key, value in update_data.items():
        setattr(db_task, key, value)

    db.commit()
    db.refresh(db_task)
    return db_task

# 5. Soft Delete Task
def delete_task(db: Session, task_id: int):
    db_task = get_task(db, task_id)
    if db_task:
        db_task.is_deleted = True # Soft delete
        db.commit()
    return db_task