import pytest
from httpx import AsyncClient
import asyncio

# Use the actual address of your running container
BASE_URL = "http://localhost:8000"

@pytest.mark.anyio
async def test_create_task_success():
    """Test successful task creation with tags"""
    async with AsyncClient(base_url=BASE_URL) as ac:
        response = await ac.post("/tasks", json={
            "title": "Integration Test Task",
            "priority": 3,
            "due_date": "2030-01-01",
            "tags": ["testing", "async"]
        })
    assert response.status_code == 201
    assert response.json()["title"] == "Integration Test Task"
    assert "tags" in response.json()

@pytest.mark.anyio
async def test_create_task_validation_error():
    """Test validation failure for priority out of range"""
    async with AsyncClient(base_url=BASE_URL) as ac:
        response = await ac.post("/tasks", json={
            "title": "Invalid Priority",
            "priority": 10, # Must be 1-5
            "due_date": "2030-01-01"
        })
    assert response.status_code == 422

@pytest.mark.anyio
async def test_filter_tasks_by_priority():
    """Test filtering logic for priority"""
    async with AsyncClient(base_url=BASE_URL) as ac:
        # First, ensure a task exists
        await ac.post("/tasks", json={
            "title": "Priority 5 Task", 
            "priority": 5, 
            "due_date": "2030-01-01"
        })
        # Filter for priority 5
        response = await ac.get("/tasks", params={"priority": 5})
    
    assert response.status_code == 200
    tasks = response.json()
    assert all(t["priority"] == 5 for t in tasks)

@pytest.mark.anyio
async def test_partial_update_patch():
    """Test edge cases for partial updates (PATCH)"""
    async with AsyncClient(base_url=BASE_URL) as ac:
        # Create task
        create = await ac.post("/tasks", json={"title": "Old Title", "priority": 1, "due_date": "2030-01-01"})
        task_id = create.json()["id"]
        
        # Patch only the title
        response = await ac.patch(f"/tasks/{task_id}", json={"title": "New Title"})
        
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"