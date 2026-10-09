"""Модульные тесты аутентификации."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import db
from src.auth import (
    hash_password, register_user, authenticate,
    check_permission, validate_password, change_password,
)


def test_hash_password():
    h = hash_password("secret")
    assert len(h) == 64
    assert h != "secret"
    print("[PASS] TC-08: хэширование пароля")


def test_register_unique():
    db.execute_delete("users", {"login": "unit_test1"})
    register_user("unit_test1", "secret123", "user")
    result = register_user("unit_test1", "another123", "user")
    assert result is None
    print("[PASS] TC-09: уникальность логина")


def test_validate_password():
    assert validate_password("abc123") is True
    assert validate_password("abc") is False
    assert validate_password("123456") is False
    assert validate_password("abcdef") is False
    print("[PASS] TC-10: проверка надёжности пароля")


def test_authenticate():
    db.execute_delete("users", {"login": "unit_test2"})
    register_user("unit_test2", "pass1234", "user")
    assert authenticate("unit_test2", "pass1234") is not None
    assert authenticate("unit_test2", "wrong") is None
    print("[PASS] аутентификация")


def test_check_permission():
    assert check_permission("admin", "kill") is True
    assert check_permission("user", "kill") is False
    print("[PASS] TC-11: разграничение прав (kill)")


def test_check_permission_own_file():
    assert check_permission("user", "delete_file", "user") is True
    assert check_permission("user", "delete_file", "admin") is False
    print("[PASS] проверка прав на файл")


def test_change_password():
    db.execute_delete("users", {"login": "unit_test3"})
    register_user("unit_test3", "old1234", "user")
    assert change_password("unit_test3", "old1234", "new1234") is True
    assert authenticate("unit_test3", "new1234") is not None
    assert authenticate("unit_test3", "old1234") is None
    print("[PASS] смена пароля")


def test_change_password_wrong_old():
    db.execute_delete("users", {"login": "unit_test4"})
    register_user("unit_test4", "real1234", "user")
    assert change_password("unit_test4", "wrong", "new1234") is False
    print("[PASS] смена пароля с неверным старым паролем отклонена")


if __name__ == "__main__":
    db.init_db()
    test_hash_password()
    test_register_unique()
    test_validate_password()
    test_authenticate()
    test_check_permission()
    test_check_permission_own_file()
    test_change_password()
    test_change_password_wrong_old()
    print("\nВсе тесты auth.py пройдены.")