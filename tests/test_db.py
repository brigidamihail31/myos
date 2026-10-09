"""Модульные тесты слоя данных."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import db


def setup():
    """Очищаем тестовую запись перед запуском."""
    db.execute_delete("users", {"login": "db_test"})


def test_insert():
    user_id = db.execute_insert("users", {
        "login": "db_test",
        "password_hash": "x",
        "role": "user",
        "created_at": "2025-01-01",
    })
    assert user_id > 0
    print(f"[PASS] TC-01: создание записи, id={user_id}")


def test_select():
    users = db.execute_select("users", {"login": "db_test"})
    assert len(users) == 1
    assert users[0]["login"] == "db_test"
    print("[PASS] TC-02: выборка по условию")


def test_select_all():
    users = db.execute_select("users")
    assert isinstance(users, list)
    assert len(users) >= 1
    print("[PASS] выборка всех записей")


def test_update():
    db.execute_update("users", {"role": "admin"}, {"login": "db_test"})
    users = db.execute_select("users", {"login": "db_test"})
    assert users[0]["role"] == "admin"
    print("[PASS] TC-03: обновление записи")


def test_delete():
    db.execute_delete("users", {"login": "db_test"})
    users = db.execute_select("users", {"login": "db_test"})
    assert len(users) == 0
    print("[PASS] TC-04: удаление записи")


def test_select_empty():
    users = db.execute_select("users", {"login": "nonexistent_user_xyz"})
    assert users == []
    print("[PASS] выборка несуществующей записи возвращает пустой список")


if __name__ == "__main__":
    db.init_db()
    setup()
    test_insert()
    test_select()
    test_select_all()
    test_update()
    test_delete()
    test_select_empty()
    print("\nВсе тесты db.py пройдены.")