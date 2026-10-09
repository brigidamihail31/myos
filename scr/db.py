"""Слой доступа к базе данных SQLite.

Роль SQLite в учебной ОС:
  * файловая система (таблица files)
  * журнал системных вызовов (таблица syscalls_log)
  * реестр процессов (таблица processes)
  * хранилище пользователей (таблица users)
  * состояние памяти ядра (таблица memory_state)
"""
import sqlite3
import hashlib
from datetime import datetime
from contextlib import contextmanager

from .config import DB_PATH, PASSWORD_HASH_ALGO

# Единое соединение (см. риск блокировок SQLite в УП.02)
_connection: sqlite3.Connection | None = None


# ---------------------------------------------------------------
# Соединение и курсор
# ---------------------------------------------------------------

def get_connection() -> sqlite3.Connection:
    """Вернуть единственное соединение с БД, создав его при необходимости."""
    global _connection
    if _connection is None:
        _connection = sqlite3.connect(DB_PATH, check_same_thread=False)
        _connection.row_factory = sqlite3.Row
        _connection.execute("PRAGMA foreign_keys = ON;")
    return _connection


@contextmanager
def cursor():
    """Контекстный менеджер для работы с курсором и автоматического коммита."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()


# ---------------------------------------------------------------
# Хэширование паролей
# ---------------------------------------------------------------

def hash_password(password: str) -> str:
    """Необратимое хэширование пароля (SHA-256)."""
    return hashlib.new(PASSWORD_HASH_ALGO, password.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------
# Инициализация схемы
# ---------------------------------------------------------------

def init_db() -> None:
    """Создать все таблицы, если их нет, и наполнить базовыми данными."""
    with cursor() as cur:
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                login         TEXT    UNIQUE NOT NULL,
                password_hash TEXT    NOT NULL,
                role          TEXT    NOT NULL DEFAULT 'user',
                created_at    TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS processes (
                pid         INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL,
                state       TEXT    NOT NULL DEFAULT 'ready',
                owner       TEXT    NOT NULL,
                memory_used INTEGER NOT NULL DEFAULT 0,
                created_at  TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS files (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                path       TEXT    UNIQUE NOT NULL,
                content    TEXT    NOT NULL DEFAULT '',
                owner      TEXT    NOT NULL,
                created_at TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS syscalls_log (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                syscall    TEXT    NOT NULL,
                args       TEXT,
                user       TEXT,
                status     TEXT    NOT NULL,
                created_at TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS memory_state (
                id     INTEGER PRIMARY KEY AUTOINCREMENT,
                used   INTEGER DEFAULT 0,
                limit_ INTEGER DEFAULT 1024
            );
            """
        )

    # Базовые пользователи (если ещё нет)
    now = datetime.utcnow().isoformat(timespec="seconds")
    with cursor() as cur:
        cur.execute(
            "INSERT OR IGNORE INTO users (login, password_hash, role, created_at) "
            "VALUES (?, ?, ?, ?)",
            ("admin", hash_password("admin"), "admin", now),
        )
        cur.execute(
            "INSERT OR IGNORE INTO users (login, password_hash, role, created_at) "
            "VALUES (?, ?, ?, ?)",
            ("user", hash_password("user"), "user", now),
        )

    # Начальное состояние памяти (если ещё нет)
    with cursor() as cur:
        cur.execute("SELECT COUNT(*) AS c FROM memory_state")
        if cur.fetchone()["c"] == 0:
            cur.execute(
                "INSERT INTO memory_state (used, limit_) VALUES (?, ?)",
                (0, 1024),
            )


# ---------------------------------------------------------------
# Универсальные CRUD-функции
# ---------------------------------------------------------------

def execute_insert(table: str, data: dict) -> int:
    """Вставить запись в таблицу. data = {поле: значение}. Возвращает id."""
    keys = ", ".join(data.keys())
    placeholders = ", ".join(["?"] * len(data))
    sql = f"INSERT INTO {table} ({keys}) VALUES ({placeholders})"
    with cursor() as cur:
        cur.execute(sql, tuple(data.values()))
        return cur.lastrowid


def execute_select(table: str, conditions: dict | None = None) -> list[dict]:
    """Вернуть записи из таблицы. conditions = {поле: значение}."""
    sql = f"SELECT * FROM {table}"
    params: tuple = ()
    if conditions:
        where = " AND ".join([f"{k} = ?" for k in conditions.keys()])
        sql += f" WHERE {where}"
        params = tuple(conditions.values())
    with cursor() as cur:
        cur.execute(sql, params)
        return [dict(row) for row in cur.fetchall()]


def execute_update(table: str, data: dict, conditions: dict) -> int:
    """Обновить записи. data = что менять, conditions = по какому условию."""
    set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
    where_clause = " AND ".join([f"{k} = ?" for k in conditions.keys()])
    sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
    with cursor() as cur:
        cur.execute(sql, tuple(data.values()) + tuple(conditions.values()))
        return cur.rowcount


def execute_delete(table: str, conditions: dict) -> int:
    """Удалить записи по условию. Возвращает число удалённых строк."""
    if conditions:
        where_clause = " AND ".join([f"{k} = ?" for k in conditions.keys()])
        sql = f"DELETE FROM {table} WHERE {where_clause}"
        params = tuple(conditions.values())
    else:
        # Пустой словарь = удалить все записи
        sql = f"DELETE FROM {table}"
        params = ()
    with cursor() as cur:
        cur.execute(sql, params)
        return cur.rowcount


# ---------------------------------------------------------------
# Функции удобства (для совместимости со старым кодом)
# ---------------------------------------------------------------

def fetch_users() -> list[dict]:
    """Вернуть список пользователей (без хэшей)."""
    with cursor() as cur:
        cur.execute("SELECT id, login, role, created_at FROM users ORDER BY id")
        return [dict(row) for row in cur.fetchall()]


def fetch_user_by_login(login: str) -> dict | None:
    """Вернуть запись пользователя по логину или None."""
    with cursor() as cur:
        cur.execute("SELECT * FROM users WHERE login = ?", (login,))
        row = cur.fetchone()
        return dict(row) if row else None


def insert_log(syscall: str, args: str, user: str | None, status: str) -> None:
    """Записать системный вызов в журнал."""
    now = datetime.utcnow().isoformat(timespec="seconds")
    with cursor() as cur:
        cur.execute(
            "INSERT INTO syscalls_log (syscall, args, user, status, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (syscall, args, user, status, now),
        )


def fetch_logs(limit: int = 50) -> list[dict]:
    """Вернуть последние записи журнала системных вызовов."""
    with cursor() as cur:
        cur.execute(
            "SELECT * FROM syscalls_log ORDER BY id DESC LIMIT ?", (limit,)
        )
        return [dict(row) for row in cur.fetchall()]


def fetch_processes() -> list[dict]:
    """Вернуть список процессов."""
    with cursor() as cur:
        cur.execute("SELECT * FROM processes ORDER BY pid")
        return [dict(row) for row in cur.fetchall()]


def fetch_files() -> list[dict]:
    """Вернуть список файлов."""
    with cursor() as cur:
        cur.execute("SELECT * FROM files ORDER BY id")
        return [dict(row) for row in cur.fetchall()]


# ---------------------------------------------------------------
# Запуск напрямую: python src/db.py
# ---------------------------------------------------------------

if __name__ == "__main__":
    init_db()
    print(f"[db] База данных инициализирована: {DB_PATH}")
    print("[db] Таблицы: users, processes, files, syscalls_log, memory_state")