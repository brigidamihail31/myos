"""Планировщик процессов."""
from . import db
from .kernel import kernel_instance


def create_process(name: str, owner: str, memory_size: int = 10) -> int:
    """Создать процесс. Возвращает pid или -1 при нехватке памяти."""
    if not kernel_instance.allocate_memory(memory_size):
        return -1
    pid = kernel_instance.allocate_pid()
    db.execute_insert("processes", {
        "pid": pid,
        "name": name,
        "state": "ready",
        "owner": owner,
        "memory_used": memory_size,
    })
    return pid


def list_processes() -> list[dict]:
    return db.execute_select("processes")


def get_process(pid: int) -> dict | None:
    rows = db.execute_select("processes", {"pid": pid})
    return rows[0] if rows else None


def terminate_process(pid: int) -> bool:
    """Завершить процесс и освободить память."""
    process = get_process(pid)
    if not process:
        return False
    kernel_instance.free_memory(process["memory_used"])
    db.execute_delete("processes", {"pid": pid})
    return True


def schedule_round_robin() -> dict | None:
    """Упрощённый Round Robin: все → ready, первый → running."""
    processes = db.execute_select("processes")
    if not processes:
        return None
    for p in processes:
        db.execute_update("processes", {"state": "ready"}, {"pid": p["pid"]})
    first = processes[0]
    db.execute_update("processes", {"state": "running"}, {"pid": first["pid"]})
    return get_process(first["pid"])


def process_count() -> int:
    return len(list_processes())