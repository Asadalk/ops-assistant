"""Database operations for persisted tasks."""
from fastapi import HTTPException

from database import get_connection
from models import Task, TaskCreate, TaskStatus, now_iso


def create_tasks(items: list[TaskCreate]) -> list[Task]:
    try:
        with get_connection() as conn:
            created = []
            for item in items:
                cursor = conn.execute(
                    "INSERT INTO tasks (task, owner, deadline, priority, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (item.task, item.owner, item.deadline, item.priority, "todo", now_iso()),
                )
                row = conn.execute("SELECT * FROM tasks WHERE id = ?", (cursor.lastrowid,)).fetchone()
                created.append(Task(**dict(row)))
            conn.commit()
            return created
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Could not save extracted tasks") from exc


def list_tasks() -> list[Task]:
    try:
        with get_connection() as conn:
            rows = conn.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()
        return [Task(**dict(row)) for row in rows]
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Could not load tasks") from exc


def update_task(task_id: int, status: TaskStatus) -> Task:
    try:
        with get_connection() as conn:
            cursor = conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Task not found")
            row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
            conn.commit()
        return Task(**dict(row))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Could not update task") from exc


def delete_task(task_id: int) -> dict[str, str]:
    try:
        with get_connection() as conn:
            cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Task not found")
            conn.commit()
        return {"message": "Task deleted"}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Could not delete task") from exc
