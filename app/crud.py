from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from . import models, schemas

async def get_task(db: AsyncSession, task_id: int):
    """Fetches a task, ensuring tags are loaded and soft-deletes are respected."""
    query = select(models.Task).options(selectinload(models.Task.tags)).filter(
        models.Task.id == task_id, 
        models.Task.is_deleted == False
    )
    result = await db.execute(query)
    return result.scalars().first()

async def get_tasks(db: AsyncSession, skip: int = 0, limit: int = 10, completed: bool = None, priority: int = None, tags: str = None):
    """Retrieves tasks with pagination and tag/priority filtering."""
    query = select(models.Task).options(selectinload(models.Task.tags)).filter(models.Task.is_deleted == False)
    
    if completed is not None:
        query = query.filter(models.Task.completed == completed)
    if priority is not None:
        query = query.filter(models.Task.priority == priority)
    
    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
        for tag_name in tag_list:
            query = query.filter(models.Task.tags.any(models.Tag.name == tag_name))
            
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

async def create_task(db: AsyncSession, task: schemas.TaskCreate):
    """Persists a new task and its associated tags."""
    db_task = models.Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        due_date=task.due_date,
        completed=task.completed
    )
    
    if task.tags:
        for tag_name in task.tags:
            tag_result = await db.execute(select(models.Tag).filter(models.Tag.name == tag_name))
            tag = tag_result.scalars().first()
            if not tag:
                tag = models.Tag(name=tag_name)
            db_task.tags.append(tag)
            
    db.add(db_task)
    # Flush ensures IDs are generated before the final commit/refresh cycle
    await db.flush() 
    await db.commit()
    return await get_task(db, db_task.id)

async def update_task(db: AsyncSession, task_id: int, task_update: schemas.TaskUpdate):
    """Updates task fields and handles tag relationship refreshes."""
    db_task = await get_task(db, task_id)
    if not db_task:
        return None
    
    # Using model_dump to comply with Pydantic V2 standards
    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "tags":
            db_task.tags = []
            for tag_name in value:
                tag_result = await db.execute(select(models.Tag).filter(models.Tag.name == tag_name))
                tag = tag_result.scalars().first()
                if not tag:
                    tag = models.Tag(name=tag_name)
                db_task.tags.append(tag)
        else:
            setattr(db_task, key, value)
            
    await db.flush()
    await db.commit()
    return await get_task(db, task_id)

async def delete_task(db: AsyncSession, task_id: int):
    """Performs a soft delete."""
    db_task = await get_task(db, task_id)
    if db_task:
        db_task.is_deleted = True
        await db.commit()
    return db_task