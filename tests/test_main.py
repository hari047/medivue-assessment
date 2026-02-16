import pytest
from httpx import AsyncClient
from app.main import app

# Mark all tests as async
pytestmark = pytest.mark.anyio

async def test_create_task_success():
    """Test successful task creation with tags [cite: 58]"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/tasks", json={
            "title": "Test Task",
            "priority": 3,
            "due_date": "2030-01-01",
            "tags": ["work", "urgent"]
        })
    assert response.status_code == 201
    assert response.json()["title"] == "Test Task"

async def test_create_task_validation_error():
    """Test validation failure for priority out of range [cite: 58]"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/tasks", json={
            "title": "Invalid Priority",
            "priority": 10, # Must be 1-5 [cite: 22]
            "due_date": "2030-01-01"
        })
    assert response.status_code == 422

async def test_filter_tasks_by_priority():
    """Test filtering logic for priority [cite: 59]"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create a task
        await ac.post("/tasks", json={
            "title": "High Priority", 
            "priority": 5, 
            "due_date": "2030-01-01"
        })
        # Filter for priority 5
        response = await ac.get("/tasks?priority=5")
    
    assert response.status_code == 200
    assert all(t["priority"] == 5 for t in response.json())

async def test_partial_update_patch():
    """Test edge cases for partial updates (PATCH) [cite: 60]"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create task
        create = await ac.post("/tasks", json={"title": "Old Title", "priority": 1, "due_date": "2030-01-01"})
        task_id = create.json()["id"]
        
        # Patch only the title
        response = await ac.patch(f"/tasks/{task_id}", json={"title": "New Title"})
        
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"
    assert response.json()["priority"] == 1 # Priority should remain unchanged
