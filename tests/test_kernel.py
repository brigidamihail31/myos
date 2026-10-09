"""Тесты ядра."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.kernel import Kernel


def test_user_state():
    k = Kernel()
    assert k.get_user() == "guest"
    k.set_user("admin")
    assert k.get_user() == "admin"
    print("[PASS] состояние пользователя")


def test_allocate_pid():
    k = Kernel()
    assert k.allocate_pid() == 1
    assert k.allocate_pid() == 2
    print("[PASS] выдача PID")


def test_memory_limit():
    k = Kernel()
    assert k.allocate_memory(100) is True
    assert k.allocate_memory(5000) is False
    info = k.memory_info()
    assert info["used"] == 100
    assert info["free"] == 924
    print("[PASS] лимит памяти")


def test_free_memory():
    k = Kernel()
    k.allocate_memory(200)
    k.free_memory(200)
    assert k.memory_info()["used"] == 0
    print("[PASS] освобождение памяти")


def test_reset():
    k = Kernel()
    k.set_user("admin")
    k.allocate_memory(500)
    k.reset()
    assert k.get_user() == "guest"
    assert k.memory_info()["used"] == 0
    print("[PASS] reset")


if __name__ == "__main__":
    test_user_state()
    test_allocate_pid()
    test_memory_limit()
    test_free_memory()
    test_reset()
    print("\nВсе тесты ядра пройдены.")