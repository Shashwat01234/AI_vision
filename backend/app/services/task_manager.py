"""
Task Manager — in-memory task status tracking with thread-safe access.
Used for tracking background processing jobs.
"""
import asyncio
import logging
import threading
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TaskStatus(str, Enum):
    UPLOADED = "uploaded"
    VALIDATING = "validating"
    PROCESSING = "processing"
    GENERATING_EXPLANATION = "generating_explanation"
    GENERATING_AUDIO = "generating_audio"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TaskInfo:
    task_id: str
    upload_id: int
    status: TaskStatus = TaskStatus.UPLOADED
    progress: int = 0
    message: str = ""
    error: Optional[str] = None
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "upload_id": self.upload_id,
            "status": self.status.value,
            "progress": self.progress,
            "message": self.message,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class TaskManager:
    """In-memory task tracker. Thread-safe across event loops and threads."""

    def __init__(self):
        self._tasks: Dict[str, TaskInfo] = {}
        self._lock = threading.Lock()

    async def register(self, task_id: str, upload_id: int) -> TaskInfo:
        with self._lock:
            task = TaskInfo(task_id=task_id, upload_id=upload_id)
            self._tasks[task_id] = task
            logger.info(f"Task registered: {task_id}")
            return task

    async def update(
        self,
        task_id: str,
        status: TaskStatus,
        progress: int = None,
        message: str = "",
        error: str = None,
    ) -> None:
        with self._lock:
            task = self._tasks.get(task_id)
            if task:
                task.status = status
                task.message = message
                task.updated_at = utc_now()
                if progress is not None:
                    task.progress = progress
                if error is not None:
                    task.error = error
                logger.info(f"Task {task_id}: {status.value} — {message}")

    async def get(self, task_id: str) -> Optional[TaskInfo]:
        with self._lock:
            return self._tasks.get(task_id)

    async def remove(self, task_id: str) -> None:
        with self._lock:
            self._tasks.pop(task_id, None)


# Global singleton
task_manager = TaskManager()
