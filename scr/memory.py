"""Подсистема управления памятью (учёт выделения по процессам)."""
from . import db

PAGE_SIZE = 4096


def alloc(pid: int, size: int) -> int:
    """Выделить процессу size байт. Возвращает новое значение memory."""
    if size <= 0:
        raise ValueError("размер должен быть положительным")
    pages = (size + PAGE_SIZE - 1) // PAGE_SIZE
    total = pages * PAGE_SIZE
    with db.cursor() as cur:
        cur.execute("SELECT memory FROM processes WHERE id = ?", (pid,))
        row = cur.fetchone()
        if row is None:
            raise LookupError(f"процесс {pid} не найден")
        new_mem = row["memory"] + total
        cur.execute("UPDATE processes SET memory = ? WHERE id = ?", (new_mem, pid))
        return new_mem


def free(pid: int) -> bool:
    """Освободить всю память процесса."""
    with db.cursor() as cur:
        cur.execute("UPDATE processes SET memory = 0 WHERE id = ?", (pid,))
        return cur.rowcount > 0