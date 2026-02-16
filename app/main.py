"""
MediVue Task Management API
Entry point for the FastAPI application, including database initialization,
custom error handling, and task-related endpoints.
"""

import logging
from contextlib import asynccontextmanager
from typing import List, Optional

# Third-party imports
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

# Local module imports
from . import models, schemas, crud, database

# Setup basic logging for production visibility
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown.
    Creates database tables automatically on startup using SQLAlchemy's 
    asynchronous metadata.
    """
    logger.info("Starting up: Initializing database tables...")
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield
    logger.info("Shutting down application...")

# Initialize the core FastAPI application
app = FastAPI(
    title="MediVue Task API", 
    version="0.1.0",
    lifespan=lifespan
)

# CUSTOM EXCEPTION HANDLER
# Overrides the default FastAPI validation error to match the required format:
# { "error": "Validation Failed", "details": { "field": "message" } }
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Intercepts Pydantic validation errors and re-formats them for a 
    consistent client-side error experience.
    """
    details = {}
    for error in exc.errors():
        # Locates the field name and extracts the human-readable error message
        field = str(error["loc"][-1])
        message = error["msg"]
        details[field] = message

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Failed",
            "details": details
        }
    )

# API ENDPOINTS

@app.post("/tasks", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: schemas.TaskCreate, db: AsyncSession = Depends(database.get_db)):
    """
    Creates a new task.
    Supports Many-to-Many tagging logic during creation.
    """
    return await crud.create_task(db=db, task=task)

@app.get("/tasks", response_model=List[schemas.TaskResponse])
async def read_tasks(
    skip: int = 0,
    limit: int = 10,
    completed: Optional[bool] = None,
    priority: Optional[int] = None,
    tags: Optional[str] = None,
    db: AsyncSession = Depends(database.get_db)
):
    """
    Retrieves a list of tasks with pagination.
    Filtering: Completion status, Priority level, and Tag name.
    """
    return await crud.get_tasks(
        db, skip=skip, limit=limit, completed=completed, priority=priority, tags=tags
    )

@app.get("/tasks/{task_id}", response_model=schemas.TaskResponse)
async def read_task(task_id: int, db: AsyncSession = Depends(database.get_db)):
    """
    Fetches a specific task by its primary key ID.
    Raises 404 if the task is deleted or does not exist.
    """
    db_task = await crud.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@app.patch("/tasks/{task_id}", response_model=schemas.TaskResponse)
async def update_task(task_id: int, task: schemas.TaskUpdate, db: AsyncSession = Depends(database.get_db)):
    """
    Performs a partial update on a task record.
    Only fields provided in the request body will be modified.
    """
    db_task = await crud.update_task(db, task_id=task_id, task_update=task)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int, db: AsyncSession = Depends(database.get_db)):
    """
    Performs a Soft Delete by setting the is_deleted flag to True.
    Data remains in the database for audit purposes but is removed from active API views.
    """
    db_task = await crud.delete_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"detail": "Task deleted successfully"}
