from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from contextlib import asynccontextmanager

# Import local modules
from . import models, schemas, crud, database

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events.
    Ensures database tables are created when the app starts.
    """
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield

# Initialize FastAPI with the lifespan and custom title
app = FastAPI(title="MediVue Task API", lifespan=lifespan)

# --- CUSTOM EXCEPTION HANDLER ---
# This ensures validation errors match the specific shape requested:
# { "error": "Validation Failed", "details": { "field": "message" } }
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = {}
    for error in exc.errors():
        # Extracts the field name (e.g., 'priority') and the error message
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

# --- API ENDPOINTS ---

@app.post("/tasks", response_model=schemas.TaskResponse, status_code=201)
async def create_task(task: schemas.TaskCreate, db: AsyncSession = Depends(database.get_db)):
    """Creates a new task with optional tags."""
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
    """Retrieves tasks with support for filtering by status, priority, and tags."""
    return await crud.get_tasks(
        db, skip=skip, limit=limit, completed=completed, priority=priority, tags=tags
    )

@app.get("/tasks/{task_id}", response_model=schemas.TaskResponse)
async def read_task(task_id: int, db: AsyncSession = Depends(database.get_db)):
    """Retrieves a single task by its ID."""
    db_task = await crud.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@app.patch("/tasks/{task_id}", response_model=schemas.TaskResponse)
async def update_task(task_id: int, task: schemas.TaskUpdate, db: AsyncSession = Depends(database.get_db)):
    """Partially updates a task (PATCH)."""
    db_task = await crud.update_task(db, task_id=task_id, task_update=task)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int, db: AsyncSession = Depends(database.get_db)):
    """Performs a soft delete on a task."""
    db_task = await crud.delete_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"detail": "Task deleted successfully"}
