"""Командная оболочка MyOS.

Команды:
  help          — справка
  whoami        — текущий пользователь (из ядра)
  login         — вход (запросит логин и пароль)
  logout        — выход
  register      — регистрация нового пользователя
  create        — создать файл (запросит путь и содержимое)
  cat <путь>    — прочитать файл
  write <путь>  — перезаписать файл (запросит содержимое)
  rm <путь>     — удалить файл (с проверкой прав)
  ls [prefix]   — список файлов
  run <имя>     — запустить процесс
  ps            — список процессов
  kill <pid>    — завершить процесс
  mem           — состояние памяти ядра
  logs [N]      — последние N записей журнала
  shutdown      — корректное завершение ОС
  exit          — выход из оболочки
"""
import sys

from .kernel import kernel_instance
from .syscalls import (
    sys_login, sys_logout, sys_whoami, sys_register,
    sys_create_file, sys_read_file, sys_write_file,
    sys_delete_file, sys_list_files,
    sys_exec, sys_ps, sys_kill, sys_mem_alloc,
    sys_logs, sys_shutdown,
)


BANNER = r"""
==================================================
   MyOS v0.5  ·  fs + scheduler + memory
   Введите 'help' для списка команд.
==================================================
"""

HELP = """Команды:
  help                эта справка
  whoami              текущий пользователь
  login               войти (логин/пароль)
  logout              выйти
  register            зарегистрировать пользователя
  create              создать файл (путь + содержимое)
  cat <путь>          прочитать файл
  write <путь>        перезаписать файл
  rm <путь>           удалить файл
  ls [prefix]         список файлов (по умолчанию '/')
  run <имя>           запустить процесс
  ps                  список процессов
  kill <pid>          завершить процесс
  mem                 состояние памяти
  logs [N]            последние N записей журнала
  shutdown            корректное завершение ОС
  exit                выход из оболочки
"""


def prompt(user: str) -> str:
    return f"{user}@studyos:~$ "


def main() -> None:
    kernel_instance.boot()   # загружает БД и восстанавливает состояние памяти
    print(BANNER)

    current_user = "guest"

    while True:
        try:
            line = input(prompt(current_user)).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not line:
            continue

        parts = line.split(maxsplit=1)
        cmd = parts[0]
        arg = parts[1].strip() if len(parts) > 1 else ""

        try:
            # ---------- Справка и состояние ----------
            if cmd == "help":
                print(HELP)

            elif cmd == "whoami":
                print(sys_whoami(current_user))

            # ---------- Аутентификация ----------
            elif cmd == "login":
                login = input("Логин: ").strip()
                password = input("Пароль: ").strip()
                if sys_login(login, password, current_user):
                    current_user = login
                    print(f"Вы вошли как {login}")
                else:
                    print("Ошибка входа")

            elif cmd == "logout":
                sys_logout(current_user)
                current_user = "guest"
                print("Сессия завершена")

            elif cmd == "register":
                login = input("Логин: ").strip()
                password = input("Пароль: ").strip()
                role = input("Роль (user/admin): ").strip() or "user"
                uid = sys_register(login, password, role, current_user)
                if uid:
                    print(f"Создан пользователь id={uid}")
                else:
                    print("Логин занят или ошибка регистрации")

            # ---------- Файловая система ----------
            elif cmd == "create":
                path = input("Путь: ").strip()
                content = input("Содержимое: ")
                fid = sys_create_file(path, content, current_user)
                if fid == -1:
                    print("Файл с таким путём уже существует")
                else:
                    print(f"Создан файл с id={fid}")

            elif cmd == "cat":
                if not arg:
                    print("Укажите путь к файлу")
                else:
                    content = sys_read_file(arg, current_user)
                    print(content if content else "(файл пуст или не существует)")

            elif cmd == "write":
                if not arg:
                    print("Укажите путь к файлу")
                else:
                    content = input("Новое содержимое: ")
                    if sys_write_file(arg, content, current_user):
                        print("Файл обновлён")
                    else:
                        print("Файл не найден")

            elif cmd == "rm":
                if not arg:
                    print("Укажите путь к файлу")
                elif sys_delete_file(arg, current_user):
                    print("Файл удалён")
                else:
                    print("Нет прав на удаление или файл не найден")

            elif cmd == "ls":
                files = sys_list_files(arg or "/", current_user)
                if not files:
                    print("(Нет файлов)")
                else:
                    for f in files:
                        print(f"  {f}")

            # ---------- Процессы ----------
            elif cmd == "run":
                if not arg:
                    print("Укажите имя программы")
                else:
                    pid = sys_exec(arg, current_user)
                    if pid == -1:
                        print("Не удалось запустить: нет свободной памяти")
                    else:
                        print(f"Запущен процесс с PID={pid}")

            elif cmd == "ps":
                procs = sys_ps(current_user)
                if not procs:
                    print("(нет процессов)")
                else:
                    print(f"{'PID':<6}{'NAME':<15}{'STATE':<10}"
                          f"{'OWNER':<10}{'MEM':<8}")
                    for p in procs:
                        print(f"{p['pid']:<6}{p['name']:<15}{p['state']:<10}"
                              f"{p['owner']:<10}{p['memory_used']:<8}")

            elif cmd == "kill":
                if not arg:
                    print("Укажите PID процесса")
                else:
                    try:
                        pid = int(arg)
                    except ValueError:
                        print("PID должен быть числом")
                    else:
                        if sys_kill(pid, current_user):
                            print(f"Процесс {pid} завершён")
                        else:
                            print(f"Не удалось завершить процесс {pid}")

            # ---------- Память ----------
            elif cmd == "mem":
                info = kernel_instance.memory_info()
                print(f"Использовано: {info['used']} / {info['limit']} МБ")
                print(f"Свободно: {info['free']} МБ")

            # ---------- Журнал и завершение ----------
            elif cmd == "logs":
                try:
                    limit = int(arg) if arg else 20
                except ValueError:
                    limit = 20
                rows = sys_logs(limit, current_user)
                if not rows:
                    print("(журнал пуст)")
                else:
                    print(f"{'ID':<5}{'SYSCALL':<20}{'USER':<10}"
                          f"{'STATUS':<12}{'CREATED_AT'}")
                    for r in rows:
                        print(f"{r['id']:<5}{r['syscall']:<20}"
                              f"{(r['user'] or '-'):<10}"
                              f"{r['status']:<12}{r['created_at']}")

            elif cmd == "shutdown":
                sys_shutdown(current_user)
                print("Завершение работы MyOS...")
                break

            elif cmd == "exit":
                break

            else:
                print(f"Неизвестная команда: {cmd}. Введите 'help'.")

        except SystemExit:
            raise
        except Exception as exc:
            print(f"[shell] Ошибка: {exc}")


if __name__ == "__main__":
    main()