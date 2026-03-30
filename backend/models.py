from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Priority = Literal["high", "medium", "low"]
TaskStatus = Literal["todo", "in_progress", "done"]


class ExtractRequest(BaseModel):
    text: str = Field(..., min_length=1)


class ExtractedTask(BaseModel):
    task: str = Field(..., min_length=1)
    owner: str = Field(default="Unknown")
    deadline: str = Field(default="Not specified")
    priority: Priority = "medium"


class TaskUpdateRequest(BaseModel):
    status: TaskStatus


class Task(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task: str
    owner: str
    deadline: str
    priority: Priority
    status: TaskStatus
    created_at: str


class TaskCreate(BaseModel):
    task: str
    owner: str = "Unknown"
    deadline: str = "Not specified"
    priority: Priority = "medium"


def normalize_task(item: dict[str, object]) -> TaskCreate:
    raw_task = str(item.get("task", "")).strip()
    if not raw_task:
        raise ValueError("Task text is required")

    owner = str(item.get("owner", "Unknown")).strip() or "Unknown"
    deadline = str(item.get("deadline", "Not specified")).strip() or "Not specified"

    raw_priority = str(item.get("priority", "medium")).strip().lower()
    if raw_priority not in {"high", "medium", "low"}:
        raw_priority = "medium"

    return TaskCreate(task=raw_task, owner=owner, deadline=deadline, priority=raw_priority)


def now_iso() -> str:
    return datetime.utcnow().isoformat()
