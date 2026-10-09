"""Модульные тесты ядра.

Проверяют:
  * выдачу PID;
  * выделение и освобождение памяти;
  * соблюдение лимита памяти;
  * установку/сброс пользователя;
  * сохранение и загрузку состояния памяти в БД.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.kernel import Kernel
from src import db


# ---------------------------------------------------------------
# PID
# ---------------------------------------------------------------

def test_pid_increments():
    """TC-05: каждый следующий PID больше предыдущего на 1."""
    k = Kernel()
    pid1 = k.allocate_pid()
    pid2 = k.allocate_pid()
    assert pid2 == pid1 + 1
    print(f"[PASS] TC-05: PID увеличивается {pid1} -> {pid2}")


# ---------------------------------------------------------------
# Память
# ---------------------------------------------------------------

def test_memory_allocate():
    """Выделение памяти увеличивает memory_used."""
    k = Kernel()
    assert k.allocate_memory(100) is True
    assert k.memory_info()["used"] == 100
    print("[PASS] выделение памяти")


def test_memory_limit():
    """TC-06: превышение лимита (5000 > 1024) отклоняется."""
    k = Kernel()
    assert k.allocate_memory(5000) is False
    assert k.memory_info()["used"] == 0
    print("[PASS] TC-06: лимит памяти соблюдается")


def test_free_memory():
    """TC-07: освобождение памяти уменьшает memory_used."""
    k = Kernel()
    k.allocate_memory(100)
    k.free_memory(100)
    assert k.memory_info()["used"] == 0
    print("[PASS] TC-07: память освобождена")


def test_free_more_than_used():
    """Освобождение большего объёма не даёт отрицательного значения."""
    k = Kernel()
    k.allocate_memory(50)
    k.free_memory(100)
    assert k.memory_info()["used"] == 0
    print("[PASS] освобождение большего объёма не даёт отрицательного значения")


def test_memory_info_fields():
    """memory_info() возвращает used / limit / free."""
    k = Kernel()
    k.allocate_memory(300)
    info = k.memory_info()
    assert info["used"] == 300
    assert info["limit"] == 1024
    assert info["free"] == 724
    print("[PASS] memory_info возвращает корректные поля")


# ---------------------------------------------------------------
# Пользователь
# ---------------------------------------------------------------

def test_set_user():
    """Установка текущего пользователя."""
    k = Kernel()
    assert k.get_user() == "guest"
    k.set_user("admin")
    assert k.get_user() == "admin"
    print("[PASS] установка текущего пользователя")


def test_reset():
    """reset() возвращает guest и освобождает память."""
    k = Kernel()
    k.set_user("admin")
    k.allocate_memory(500)
    k.reset()
    assert k.get_user() == "guest"
    assert k.memory_info()["used"] == 0
    print("[PASS] reset сбрасывает пользователя и память")


# ---------------------------------------------------------------
# Сохранение / загрузка состояния в БД
# ---------------------------------------------------------------

def test_save_memory_state():
    """save_memory_state() пишет used в таблицу memory_state."""
    db.init_db()
    k = Kernel()
    k.allocate_memory(100)
    k.save_memory_state()
    states = db.execute_select("memory_state")
    assert len(states) >= 1
    assert states[0]["used"] == 100
    print("[PASS] состояние памяти сохранено в БД")


def test_load_memory_state():
    """load_memory_state() восстанавливает used из таблицы memory_state."""
    db.init_db()

    # Сначала сохраняем состояние через один экземпляр
    k1 = Kernel()
    k1.allocate_memory(250)
    k1.save_memory_state()

    # Новый экземпляр — пустой, пока не загрузит из БД
    k2 = Kernel()
    assert k2.memory_info()["used"] == 0  # по умолчанию

    k2.load_memory_state()
    assert k2.memory_info()["used"] == 250
    print("[PASS] состояние памяти восстановлено из БД")


# ---------------------------------------------------------------
# Запуск всех тестов
# ---------------------------------------------------------------

if __name__ == "__main__":
    db.init_db()

    test_pid_increments()
    test_memory_allocate()
    test_memory_limit()
    test_free_memory()
    test_free_more_than_used()
    test_memory_info_fields()
    test_set_user()
    test_reset()
    test_save_memory_state()
    test_load_memory_state()

    print("\nВсе тесты kernel.py пройдены.")