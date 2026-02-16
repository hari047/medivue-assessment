from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from . import models, schemas

async def get_task(db: AsyncSession, task_id: int):
    """
    Retrieves a single task by its unique identifier.
    Uses 'selectinload' to eagerly fetch associated tags, preventing lazy-loading errors.
    Filters out any records marked as soft-deleted.
    """
    query = select(models.Task).options(selectinload(models.Task.tags)).filter(
        models.Task.id == task_id, 
        models.Task.is_deleted == False
    )
    result = await db.execute(query)
    return result.scalars().first()

async def get_tasks(db: AsyncSession, skip: int = 0, limit: int = 10, completed: bool = None, priority: int = None, tags: str = None):
    """
    Retrieves a paginated list of tasks with support for complex filtering.
    Filters: Completion status, Priority level (1-5), and Tag names.
    """
    query = select(models.Task).options(selectinload(models.Task.tags)).filter(models.Task.is_deleted == False)
    
    if completed is not None:
        query = query.filter(models.Task.completed == completed)
    if priority is not None:
        query = query.filter(models.Task.priority == priority)
    
    # Simple tag filtering: checks if a task contains the specified tag name
    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
        for tag_name in tag_list:
            query = query.filter(models.Task.tags.any(models.Tag.name == tag_name))
            
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

async def create_task(db: AsyncSession, task: schemas.TaskCreate):
    """
    Persists a new task to the database.
    Handles 'Many-to-Many' tag logic by checking for existing tags before creating new ones.
    """
    db_task = models.Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        due_date=task.due_date,
        completed=task.completed
    )
    
    if task.tags:
        for tag_name in task.tags:
            # Prevent duplicate tags in the 'tags' table
            tag_result = await db.execute(select(models.Tag).filter(models.Tag.name == tag_name))
            tag = tag_result.scalars().first()
            if not tag:
                tag = models.Tag(name=tag_name)
            db_task.tags.append(tag)
            
    db.add(db_task)
    await db.commit()
    # Re-fetch with eager loading to ensure response includes tag objects
    return await get_task(db, db_task.id)

async def update_task(db: AsyncSession, task_id: int, task_update: schemas.TaskUpdate):
    """
    Performs a partial update (PATCH) on an existing task.
    If the 'tags' field is included, the existing relationship is replaced.
    """
    db_task = await get_task(db, task_id)
    if not db_task:
        return None
    
    update_data = task_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if key == "tags":
            db_task.tags = [] # Clear existing associations
            for tag_name in value:
                tag_result = await db.execute(select(models.Tag).filter(models.Tag.name == tag_name))
                tag = tag_result.scalars().first()
                if not tag:
                    tag = models.Tag(name=tag_name)
                db_task.tags.append(tag)
        else:
            setattr(db_task, key, value)
            
    await db.commit()
    return await get_task(db, task_id)

async def delete_task(db: AsyncSession, task_id: int):
    """
    Implements a 'Soft Delete' by setting the is_deleted flag.
    Maintains data for audit logs while removing it from standard API responses.
    """
    db_task = await get_task(db, task_id)
    if db_task:
        db_task.is_deleted = True
        await db.commit()
    return db_task
