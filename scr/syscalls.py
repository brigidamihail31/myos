"""Системные вызовы учебной ОС (API ядра).

Каждая функция:
  1) проверяет аргументы и права;
  2) вызывает логику соответствующей подсистемы;
  3) логируется через log_syscall() в таблицу syscalls_log.
"""
import time

from . import db
from . import fs
from . import scheduler
from .auth import authenticate, check_permission
from .kernel import kernel_instance
from .config import MAX_SYSCALL_TIME_MS


# ---------------------------------------------------------------
# Логирование и обёртка замера времени
# ---------------------------------------------------------------

def log_syscall(name: str,
                args: str = "",
                user: str = "system",
                status: str = "OK") -> None:
    """Записать системный вызов в таблицу syscalls_log."""
    db.insert_log(name, args, user, status)


def _timed(name: str, args: str, user: str, func, *fargs, **fkwargs):
    """Обёртка: замер времени выполнения + автоматическое логирование."""
    start = time.perf_counter()
    try:
        result = func(*fargs, **fkwargs)
        elapsed = (time.perf_counter() - start) * 1000
        status = "OK" if elapsed <= MAX_SYSCALL_TIME_MS else "SLOW"
        log_syscall(name, args, user, status)
        return result
    except Exception as exc:
        log_syscall(name, args, user, f"ERROR: {exc}")
        raise


# ---------------------------------------------------------------
# Аутентификация
# ---------------------------------------------------------------

def sys_login(login: str, password: str, current_user: str = "guest") -> bool:
    """Аутентификация пользователя."""
    log_syscall("sys_login", login, current_user, "check")
    user = authenticate(login, password)
    if user:
        kernel_instance.set_user(login)
        log_syscall("sys_login", login, current_user, "OK")
        return True
    log_syscall("sys_login", login, current_user, "DENIED")
    return False


def sys_logout(current_user: str = "guest") -> bool:
    """Завершить сессию."""
    log_syscall("sys_logout", "", current_user, "OK")
    kernel_instance.set_user("guest")
    return True


def sys_whoami(current_user: str = "guest") -> str:
    """Вернуть имя текущего пользователя (из ядра)."""
    log_syscall("sys_whoami", "", current_user, "OK")
    return kernel_instance.get_user()


def sys_register(login: str,
                 password: str,
                 role: str = "user",
                 current_user: str = "guest") -> int | None:
    """Зарегистрировать нового пользователя (доп. задание)."""
    from .auth import register_user
    log_syscall("sys_register", f"login={login}", current_user, "check")
    uid = register_user(login, password, role)
    if uid is None:
        log_syscall("sys_register", f"login={login}", current_user, "DENIED")
        return None
    log_syscall("sys_register", f"login={login}", current_user, "OK")
    return uid


# ---------------------------------------------------------------
# Файловая система
# ---------------------------------------------------------------

def sys_create_file(path: str,
                    content: str = "",
                    current_user: str = "guest") -> int:
    """Создать файл. Возвращает id или -1 (если путь занят)."""
    log_syscall("sys_create_file", path, current_user, "check")
    file_id = fs.create_file(path, content, current_user)
    if file_id == -1:
        log_syscall("sys_create_file", path, current_user, "EXISTS")
        return -1
    log_syscall("sys_create_file", path, current_user, "OK")
    return file_id


def sys_read_file(path: str, current_user: str = "guest") -> str:
    """Прочитать файл. Возвращает содержимое или пустую строку."""
    log_syscall("sys_read_file", path, current_user, "check")
    content = fs.read_file(path)
    log_syscall("sys_read_file", path, current_user, "OK")
    return content


def sys_write_file(path: str,
                   content: str,
                   current_user: str = "guest") -> bool:
    """Записать новое содержимое в файл."""
    log_syscall("sys_write_file", path, current_user, "check")
    ok = fs.write_file(path, content)
    log_syscall("sys_write_file", path, current_user, "OK" if ok else "NOT_FOUND")
    return ok


def sys_delete_file(path: str, current_user: str = "guest") -> bool:
    """Удалить файл с проверкой прав."""
    log_syscall("sys_delete_file", path, current_user, "check")
    owner = fs.get_owner(path)
    if owner is None:
        log_syscall("sys_delete_file", path, current_user, "NOT_FOUND")
        return False
    if not check_permission(current_user, "delete_file", owner):
        log_syscall("sys_delete_file", path, current_user, "DENIED")
        return False
    fs.delete_file(path)
    log_syscall("sys_delete_file", path, current_user, "OK")
    return True


def sys_list_files(prefix: str = "/", current_user: str = "guest") -> list[str]:
    """Список файлов, начинающихся с prefix."""
    log_syscall("sys_list_files", prefix, current_user, "OK")
    return fs.list_files(prefix)


# ---------------------------------------------------------------
# Планировщик и память
# ---------------------------------------------------------------

def sys_exec(name: str,
             current_user: str = "guest",
             memory_size: int = 10) -> int:
    """Запустить процесс. Возвращает pid или -1 при нехватке памяти."""
    log_syscall("sys_exec", name, current_user, "check")
    pid = scheduler.create_process(name, current_user, memory_size)
    if pid == -1:
        log_syscall("sys_exec", name, current_user, "NO_MEMORY")
        return -1
    log_syscall("sys_exec", name, current_user, "OK")
    return pid


def sys_ps(current_user: str = "guest") -> list[dict]:
    """Список процессов."""
    log_syscall("sys_ps", "", current_user, "OK")
    return scheduler.list_processes()


def sys_kill(pid: int, current_user: str = "guest") -> bool:
    """Завершить процесс с проверкой прав."""
    log_syscall("sys_kill", str(pid), current_user, "check")
    if not check_permission(current_user, "kill"):
        log_syscall("sys_kill", str(pid), current_user, "DENIED")
        return False
    result = scheduler.terminate_process(pid)
    log_syscall("sys_kill", str(pid), current_user,
                "OK" if result else "NOT_FOUND")
    return result


def sys_mem_alloc(size: int, current_user: str = "guest") -> bool:
    """Выделить память (без процесса). Возвращает True/False."""
    log_syscall("sys_mem_alloc", str(size), current_user, "check")
    ok = kernel_instance.allocate_memory(size)
    log_syscall("sys_mem_alloc", str(size), current_user,
                "OK" if ok else "NO_MEMORY")
    return ok


# ---------------------------------------------------------------
# Журнал и завершение
# ---------------------------------------------------------------

def sys_logs(limit: int = 20, current_user: str = "guest") -> list[dict]:
    """Последние записи журнала системных вызовов."""
    return _timed("sys_logs", f"limit={limit}", current_user,
                  db.fetch_logs, limit)


def sys_shutdown(current_user: str = "guest") -> bool:
    """Корректное завершение работы ОС."""
    log_syscall("sys_shutdown", "", current_user)
    return True


# ---------------------------------------------------------------
# Самопроверка: python -m src.syscalls
# ---------------------------------------------------------------

if __name__ == "__main__":
    db.init_db()

    print("register  :", sys_register("admin", "secret", "admin"))
    print("login     :", sys_login("admin", "secret"))
    print("whoami    :", sys_whoami("admin"))
    print("create    :", sys_create_file("/test.txt", "hello", "admin"))
    print("read      :", repr(sys_read_file("/test.txt", "admin")))
    print("list      :", sys_list_files("/", "admin"))
    print("exec      :", sys_exec("app1", "admin"))
    print("ps        :", sys_ps("admin"))
    print("kill      :", sys_kill(1, "admin"))
    print("delete    :", sys_delete_file("/test.txt", "admin"))
    print("logs      :", sys_logs(5, "admin"))