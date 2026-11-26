"""
Unit tests for background TaskManager lifecycle
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import pytest
from app.services.task_manager import TaskManager, TaskStatus


@pytest.mark.anyio
async def test_task_manager_lifecycle():
    tm = TaskManager()

    # 1. Register task
    task = await tm.register("task-test-001", upload_id=42)
    assert task.task_id == "task-test-001"
    assert task.upload_id == 42
    assert task.status == TaskStatus.UPLOADED
    assert task.progress == 0

    # 2. Update progress
    await tm.update(
        "task-test-001",
        status=TaskStatus.PROCESSING,
        progress=50,
        message="Analyzing visual regions...",
    )
    updated = await tm.get("task-test-001")
    assert updated is not None
    assert updated.status == TaskStatus.PROCESSING
    assert updated.progress == 50
    assert updated.message == "Analyzing visual regions..."

    # 3. Complete task
    await tm.update(
        "task-test-001",
        status=TaskStatus.COMPLETED,
        progress=100,
        message="Finished analysis.",
    )
    completed = await tm.get("task-test-001")
    assert completed.status == TaskStatus.COMPLETED
    assert completed.progress == 100

    # 4. Remove task
    await tm.remove("task-test-001")
    assert await tm.get("task-test-001") is None


@pytest.mark.anyio
async def test_task_manager_error_handling():
    tm = TaskManager()
    await tm.register("task-test-err", upload_id=99)
    await tm.update(
        "task-test-err",
        status=TaskStatus.FAILED,
        error="Corrupted input stream",
    )
    task = await tm.get("task-test-err")
    assert task.status == TaskStatus.FAILED
    assert task.error == "Corrupted input stream"
