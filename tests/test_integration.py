"""Интеграционные тесты: проверяют работу модулей вместе."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import db
from src import fs
from src import scheduler
from src.auth import register_user, authenticate, check_permission
from src.kernel import kernel_instance


def _reset():
    """Очистить данные, оставив пользователей."""
    db.init_db()
    db.execute_delete("files", {})
    db.execute_delete("processes", {})
    db.execute_delete("syscalls_log", {})
    db.execute_delete("memory_state", {})
    db.execute_insert("memory_state", {"used": 0, "limit_": 1024})
    kernel_instance.memory_used = 0
    kernel_instance.process_counter = 0


def test_auth_then_create_file():
    """Сценарий: логин → создание файла от имени пользователя."""
    _reset()
    db.execute_delete("users", {"login": "testadmin"})
    register_user("testadmin", "secret", "admin")

    user = authenticate("testadmin", "secret")
    assert user is not None, "аутентификация не прошла"

    fid = fs.create_file("/int1.txt", "data", user["login"])
    assert fid > 0, "файл не создан"
    assert fs.read_file("/int1.txt") == "data"
    print("[PASS] auth + fs: логин и создание файла")


def test_permission_delete():
    """Сценарий: user пытается удалить файл admin — отказ."""
    _reset()
    db.execute_delete("users", {"login": "int_admin"})
    db.execute_delete("users", {"login": "int_user"})
    register_user("int_admin", "a", "admin")
    register_user("int_user", "u", "user")

    fs.create_file("/int2.txt", "x", "int_admin")
    owner = fs.get_owner("/int2.txt")
    assert owner == "int_admin"
    assert check_permission("int_user", "delete_file", owner) is False
    print("[PASS] permission: user не удаляет файл admin")


def test_exec_and_memory():
    """Сценарий: запуск процесса выделяет память ядра."""
    _reset()
    before = kernel_instance.memory_used
    pid = scheduler.create_process("int_app", "admin", 50)
    assert pid > 0
    assert kernel_instance.memory_used == before + 50

    scheduler.terminate_process(pid)
    assert kernel_instance.memory_used == before
    print("[PASS] scheduler + kernel: запуск и завершение процесса")


def test_memory_limit_blocks_process():
    """Сценарий: превышение лимита памяти не создаёт процесс."""
    _reset()
    pid = scheduler.create_process("huge", "admin", 5000)
    assert pid == -1
    assert kernel_instance.memory_used == 0
    print("[PASS] kernel: превышение лимита памяти отклонено")


def test_kill_requires_admin():
    """Сценарий: обычный user не может завершить процесс."""
    _reset()
    db.execute_delete("users", {"login": "int_user2"})
    register_user("int_user2", "u", "user")

    pid = scheduler.create_process("victim", "admin", 10)
    assert check_permission("int_user2", "kill") is False
    assert scheduler.get_process(pid) is not None  # процесс жив
    print("[PASS] permission: user не может kill")


def test_memory_state_persisted():
    """Сценарий: состояние памяти сохраняется в БД."""
    _reset()
    kernel_instance.allocate_memory(100)
    rows = db.execute_select("memory_state")
    assert rows and rows[0]["used"] == 100
    print("[PASS] kernel + db: memory_state сохраняется")


def test_round_robin_changes_state():
    """Сценарий: Round Robin переводит первый процесс в running."""
    _reset()
    scheduler.create_process("rr1", "admin", 5)
    scheduler.create_process("rr2", "admin", 5)
    running = scheduler.schedule_round_robin()
    assert running is not None
    assert running["state"] == "running"
    states = {p["name"]: p["state"] for p in scheduler.list_processes()}
    assert states["rr1"] == "running"
    assert states["rr2"] == "ready"
    print("[PASS] scheduler: Round Robin")


if __name__ == "__main__":
    test_auth_then_create_file()
    test_permission_delete()
    test_exec_and_memory()
    test_memory_limit_blocks_process()
    test_kill_requires_admin()
    test_memory_state_persisted()
    test_round_robin_changes_state()
    print("\nВсе интеграционные тесты пройдены.")