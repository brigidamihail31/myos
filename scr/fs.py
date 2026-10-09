"""Файловая система поверх SQLite."""
from datetime import datetime

from . import db


def create_file(path: str, content: str, owner: str) -> int:
    now = datetime.utcnow().isoformat(timespec="seconds")
    with db.cursor() as cur:
        cur.execute(
            "INSERT INTO files (path, content, owner, created_at) "
            "VALUES (?, ?, ?, ?)",
            (path, content, owner, now),
        )
        return cur.lastrowid


def read_file(path: str) -> dict:
    with db.cursor() as cur:
        cur.execute("SELECT * FROM files WHERE path = ?", (path,))
        row = cur.fetchone()
        if row is None:
            raise FileNotFoundError(f"файл не найден: {path}")
        return dict(row)


def delete_file(path: str) -> bool:
    with db.cursor() as cur:
        cur.execute("DELETE FROM files WHERE path = ?", (path,))
        return cur.rowcount > 0


def list_files() -> list[dict]:
    return db.fetch_files()
"""Файловая система на SQLite."""
from datetime import datetime

from . import db


def create_file(path: str, content: str, owner: str) -> int:
    """Создать файл. Возвращает id или -1, если путь занят."""
    existing = db.execute_select("files", {"path": path})
    if existing:
        return -1
    return db.execute_insert("files", {
        "path": path,
        "content": content,
        "owner": owner,
        "created_at": datetime.utcnow().isoformat(timespec="seconds"),
    })


def read_file(path: str) -> str:
    """Вернуть содержимое файла или пустую строку."""
    rows = db.execute_select("files", {"path": path})
    if not rows:
        return ""
    return rows[0]["content"]


def write_file(path: str, content: str) -> bool:
    """Обновить содержимое существующего файла."""
    rows = db.execute_select("files", {"path": path})
    if not rows:
        return False
    db.execute_update("files", {"content": content}, {"path": path})
    return True


def delete_file(path: str) -> bool:
    """Удалить файл по пути."""
    affected = db.execute_delete("files", {"path": path})
    return affected > 0


def list_files(prefix: str = "/") -> list[str]:
    """Список путей, начинающихся с prefix."""
    sql_prefix = prefix if prefix else ""
    with db.cursor() as cur:
        cur.execute("SELECT path FROM files WHERE path LIKE ? ORDER BY path",
                    (sql_prefix + "%",))
        return [row["path"] for row in cur.fetchall()]


def get_owner(path: str) -> str | None:
    """Вернуть логин владельца файла или None."""
    rows = db.execute_select("files", {"path": path})
    if not rows:
        return None
    return rows[0]["owner"]


def get_file_info(path: str) -> dict | None:
    """Вернуть полную запись о файле."""
    rows = db.execute_select("files", {"path": path})
    return rows[0] if rows else None


def count_files() -> int:
    """Количество файлов в системе (доп. задание)."""
    return len(db.execute_select("files"))