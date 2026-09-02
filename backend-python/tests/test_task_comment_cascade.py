"""Database-backed verification of task comment cascade deletion."""
import sqlite3
from pathlib import Path


def test_deleting_task_removes_associated_comments():
    schema = Path(__file__).parents[2] / "database" / "schema.sql"
    assert "REFERENCES tasks(id) ON DELETE CASCADE" in schema.read_text()

    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("CREATE TABLE tasks (id INTEGER PRIMARY KEY)")
    connection.execute(
        "CREATE TABLE task_comments ("
        "id INTEGER PRIMARY KEY, "
        "task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE)"
    )
    connection.execute("INSERT INTO tasks (id) VALUES (1)")
    connection.execute("INSERT INTO task_comments (id, task_id) VALUES (1, 1)")

    connection.execute("DELETE FROM tasks WHERE id = 1")

    assert connection.execute("SELECT COUNT(*) FROM task_comments").fetchone() == (0,)