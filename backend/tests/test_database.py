from database import get_connection, init_db


def test_database_init_and_task_crud(database_path):
    init_db()
    with get_connection() as conn:
        inserted = conn.execute(
            "INSERT INTO tasks (task, owner, deadline, priority, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            ("Review plan", "Mina", "Monday", "medium", "todo", "now"),
        )
        task_id = inserted.lastrowid
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        assert row["task"] == "Review plan"
        conn.execute("UPDATE tasks SET status = ? WHERE id = ?", ("done", task_id))
        assert conn.execute("SELECT status FROM tasks WHERE id = ?", (task_id,)).fetchone()[0] == "done"
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        assert conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone() is None
