"""
Integration Tests for MediVue Task API
Uses a module-scoped fixture to ensure a stable event loop and 
database connection during the test session.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

BASE_URL = "http://test"

@pytest.fixture(scope="module")
async def client():
    """
    Provides a single AsyncClient instance for all tests in this module.
    This prevents the 'attached to a different loop' error.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as ac:
        yield ac

@pytest.mark.anyio
async def test_create_task_success(client):
    """Scenario: Successfully create a task with tags."""
    response = await client.post("/tasks", json={
        "title": "Integration Test Task",
        "priority": 3,
        "due_date": "2030-01-01",
        "tags": ["testing", "async"]
    })
    assert response.status_code == 201
    assert response.json()["title"] == "Integration Test Task"

@pytest.mark.anyio
async def test_create_task_validation_error(client):
    """Scenario: Ensure custom validation error shape is returned."""
    response = await client.post("/tasks", json={
        "title": "Invalid Priority",
        "priority": 10, 
        "due_date": "2030-01-01"
    })
    assert response.status_code == 422
    # Verify the custom error handler is working
    assert response.json()["error"] == "Validation Failed"

@pytest.mark.anyio
async def test_filter_tasks_by_priority(client):
    """Scenario: Verify GET filtering logic."""
    await client.post("/tasks", json={
        "title": "Priority 5 Task", 
        "priority": 5, 
        "due_date": "2030-01-01"
    })
    response = await client.get("/tasks", params={"priority": 5})
    assert response.status_code == 200
    tasks = response.json()
    assert all(t["priority"] == 5 for t in tasks)

@pytest.mark.anyio
async def test_partial_update_patch(client):
    """Scenario: Verify partial updates (PATCH) work as expected."""
    create = await client.post("/tasks", json={
        "title": "Old Title", 
        "priority": 1, 
        "due_date": "2030-01-01"
    })
    task_id = create.json()["id"]
    response = await client.patch(f"/tasks/{task_id}", json={"title": "New Title"})
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"