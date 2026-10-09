"""Модуль аутентификации и управления пользователями.

Функции:
  * hash_password(password)                 — SHA-256 хэш
  * validate_password(password)             — проверка надёжности пароля
  * register_user(login, password, role)    — регистрация
  * authenticate(login, password)           — проверка логина и пароля
  * change_password(login, old_pwd, new_pwd)— смена пароля
  * get_role(login)                         — роль пользователя
  * is_admin(login)                         — является ли пользователь админом
  * check_permission(user, action, owner)   — проверка прав
  * authorize_file_access(login, owner)     — доступ к файлу
"""
import hashlib
from datetime import datetime

from . import db


# ---------------------------------------------------------------
# Хэширование и валидация
# ---------------------------------------------------------------

def hash_password(password: str) -> str:
    """Вернуть SHA-256 хэш пароля (64 hex-символа)."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def validate_password(password: str) -> bool:
    """Проверить надёжность пароля.

    Валидный пароль:
      * минимум 6 символов;
      * содержит хотя бы одну букву;
      * содержит хотя бы одну цифру.
    """
    if len(password) < 6:
        return False
    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    return has_letter and has_digit


# ---------------------------------------------------------------
# Регистрация и аутентификация
# ---------------------------------------------------------------

def register_user(login: str, password: str, role: str = "user") -> int | None:
    """Зарегистрировать нового пользователя.

    Возвращает id созданного пользователя или None, если логин занят
    либо пароль не прошёл валидацию.
    """
    if not validate_password(password):
        return None
    existing = db.execute_select("users", {"login": login})
    if existing:
        return None
    return db.execute_insert("users", {
        "login": login,
        "password_hash": hash_password(password),
        "role": role,
        "created_at": datetime.utcnow().isoformat(timespec="seconds"),
    })


def authenticate(login: str, password: str) -> dict | None:
    """Проверить логин и пароль. Вернуть запись пользователя или None."""
    users = db.execute_select("users", {"login": login})
    if not users:
        return None
    user = users[0]
    if user["password_hash"] == hash_password(password):
        return user
    return None


def change_password(login: str, old_password: str,
                    new_password: str) -> bool:
    """Сменить пароль после проверки старого.

    Возвращает True при успехе, False если пользователь не найден,
    старый пароль неверен или новый пароль слишком слабый.
    """
    user = authenticate(login, old_password)
    if user is None:
        return False
    if not validate_password(new_password):
        return False
    db.execute_update(
        "users",
        {"password_hash": hash_password(new_password)},
        {"login": login},
    )
    return True


# ---------------------------------------------------------------
# Роли и права доступа
# ---------------------------------------------------------------

def get_role(login: str) -> str | None:
    """Вернуть роль пользователя или None, если он не найден."""
    users = db.execute_select("users", {"login": login})
    return users[0]["role"] if users else None


def is_admin(login: str) -> bool:
    """Является ли пользователь администратором."""
    return get_role(login) == "admin"


def check_permission(current_user: str,
                     action: str,
                     target_owner: str | None = None) -> bool:
    """Проверить права пользователя на действие.

    Правила:
      * admin имеет полные права;
      * user не может удалять файлы, принадлежащие не ему;
      * только admin может завершать процессы;
      * создание/чтение файлов и выделение памяти разрешены
        всем авторизованным пользователям.
    """
    users = db.execute_select("users", {"login": current_user})
    if not users:
        return False
    role = users[0]["role"]
    if role == "admin":
        return True
    if action == "delete_file" and target_owner and target_owner != current_user:
        return False
    if action == "kill":
        return False
    return True


def authorize_file_access(login: str, owner: str) -> bool:
    """Доступ к файлу на чтение: admin — всё, user — только своё."""
    if is_admin(login):
        return True
    return login == owner


# ---------------------------------------------------------------
# Самопроверка: python -m src.auth
# ---------------------------------------------------------------

if __name__ == "__main__":
    db.init_db()

    print("hash       :", hash_password("secret")[:16], "...")
    print("validate ok:", validate_password("abc123"))
    print("validate ko:", validate_password("abc"))
    print("register   :", register_user("auth_test", "pass1234", "user"))
    print("duplicate  :", register_user("auth_test", "pass1234", "user"))
    print("auth ok    :", authenticate("auth_test", "pass1234") is not None)
    print("auth fail  :", authenticate("auth_test", "wrong") is None)
    print("change ok  :", change_password("auth_test", "pass1234", "new1234"))
    print("auth new   :", authenticate("auth_test", "new1234") is not None)
    print("role       :", get_role("admin"))
    print("is_admin   :", is_admin("admin"))
    print("permission :", check_permission("user", "delete_file", "admin"))