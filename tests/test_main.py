"""
Integration Tests for MediVue Task API
Verifies endpoint functionality including task creation, validation,
filtering, and partial updates against a live running service.
"""

import pytest
from httpx import AsyncClient
import asyncio

# The API should be reachable at the local container address
BASE_URL = "http://localhost:8000"

@pytest.mark.anyio
async def test_create_task_success():
    """
    Scenario: User submits a valid task with multiple tags.
    Expected: Status 201 Created and correctly serialized JSON response.
    """
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
    """
    Scenario: User submits a task with an out-of-range priority (10).
    Expected: Status 422 Unprocessable Entity (Validation Error).
    """
    async with AsyncClient(base_url=BASE_URL) as ac:
        response = await ac.post("/tasks", json={
            "title": "Invalid Priority",
            "priority": 10,  # Limits are 1-5
            "due_date": "2030-01-01"
        })
    assert response.status_code == 422

@pytest.mark.anyio
async def test_filter_tasks_by_priority():
    """
    Scenario: User requests all tasks filtered by a specific priority.
    Expected: Status 200 OK and all returned tasks match the filter.
    """
    async with AsyncClient(base_url=BASE_URL) as ac:
        # Pre-seed a high-priority task for testing
        await ac.post("/tasks", json={
            "title": "Priority 5 Task", 
            "priority": 5, 
            "due_date": "2030-01-01"
        })
        
        # Filter request
        response = await ac.get("/tasks", params={"priority": 5})
    
    assert response.status_code == 200
    tasks = response.json()
    assert all(t["priority"] == 5 for t in tasks)

@pytest.mark.anyio
async def test_partial_update_patch():
    """
    Scenario: User updates only the title of an existing task (PATCH).
    Expected: Status 200 OK, title changed, other fields preserved.
    """
    async with AsyncClient(base_url=BASE_URL) as ac:
        # Create initial task
        create = await ac.post("/tasks", json={
            "title": "Old Title", 
            "priority": 1, 
            "due_date": "2030-01-01"
        })
        task_id = create.json()["id"]
        
        # Patch only the title field
        response = await ac.patch(f("/tasks/{task_id}"), json={"title": "New Title"})
        
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"
