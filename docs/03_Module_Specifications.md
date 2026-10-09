# 03. Спецификации модулей и матрица трассируемости

## 1. Модуль `db.py`

### Назначение
Обеспечивает подключение к SQLite, создание таблиц при первом запуске
и предоставление соединения другим модулям.

### Публичный интерфейс
- `get_connection() -> sqlite3.Connection` — возвращает соединение.
- `init_db() -> None` — создаёт таблицы, если их нет.
- `cursor()` — контекстный менеджер для операций.
- `execute_query(sql, params) -> list` — выполняет запрос, возвращает результат.
- `hash_password(password) -> str` — SHA-256.
- `fetch_users()`, `fetch_user_by_login()`, `insert_log()`, `fetch_logs()`,
  `fetch_processes()`, `fetch_files()` — выборки.

### Внутренние зависимости
Не зависит от других модулей проекта. Использует стандартный `sqlite3`.

### Обработка ошибок
- `sqlite3.OperationalError` — повтор попытки через 100 мс (до 3 раз).
- `sqlite3.IntegrityError` — нарушено ограничение UNIQUE, вернуть `None`.

### Побочные эффекты
- Создание файла `db/os.sqlite` при первом запуске.
- Создание таблиц `users`, `processes`, `files`, `syscalls_log`.
- Запись/чтение строк в этих таблицах.

---

## 2. Модуль `syscalls.py`

### Назначение
Единый интерфейс для оболочки. Каждая функция проверяет аргументы,
вызывает логику ядра и записывает вызов в журнал.

### Публичный интерфейс
- `log_syscall(name, args, user, status) -> None`
- `check_permission(current_user, action, target_owner=None) -> bool`
- `sys_login(login, password, current_user) -> bool`
- `sys_logout(current_user) -> bool`
- `sys_whoami(current_user) -> str`
- `sys_create_file(path, content, current_user) -> int`
- `sys_read_file(path, current_user) -> str`
- `sys_delete_file(path, current_user, owner=None) -> bool`
- `sys_list_files(path, current_user) -> list`
- `sys_exec(name, current_user) -> int`
- `sys_ps(current_user) -> list`
- `sys_kill(pid, current_user) -> bool`
- `sys_mem_alloc(size, current_user) -> int`
- `sys_logs(limit, current_user) -> list`
- `sys_shutdown(current_user) -> bool`

### Внутренние зависимости
- `db.py` — для записи в `syscalls_log`.
- `kernel.py` — для вызова логики подсистем.
- `auth.py` — для `check_permission` (косвенно).

### Обработка ошибок
- Если пользователь не авторизован, `sys_create_file` возвращает `-1`.
- Если файл не найден, `sys_read_file` возвращает пустую строку.
- Если pid не существует, `sys_kill` возвращает `False`.
- Если у пользователя нет прав на удаление файла — `sys_delete_file`
  возвращает `False` и пишет в лог статус `DENIED`.
- Если у пользователя нет прав на завершение процесса — `sys_kill`
  возвращает `False` и пишет в лог статус `DENIED`.

### Побочные эффекты
Каждый вызов записывает строку в `syscalls_log` с полями:
имя вызова, аргументы, пользователь, статус, время.

---

## 3. Модуль `kernel.py`

### Назначение
Ядро: связывает подсистемы, инициализирует БД, проксирует вызовы
от `syscalls.py` к `scheduler.py`, `memory.py`, `fs.py`, `auth.py`.

### Публичный интерфейс
- `Kernel.boot() -> None`
- `Kernel.spawn(name, owner, memory) -> int`
- `Kernel.kill(pid) -> bool`
- `Kernel.processes() -> list`
- `Kernel.allocate(pid, size) -> int`
- `Kernel.create_file(path, content, owner) -> int`
- `Kernel.read_file(path) -> dict`
- `Kernel.delete_file(path) -> bool`
- `Kernel.list_files() -> list`
- `Kernel.authenticate(login, password) -> bool`

### Внутренние зависимости
`db.py`, `scheduler.py`, `memory.py`, `fs.py`, `auth.py`.

### Обработка ошибок
Пробрасывает исключения подсистем наверх без подавления.

### Побочные эффекты
Инициализация схемы БД при `boot()`.

---

## 4. Модуль `scheduler.py`

### Назначение
Подсистема планирования процессов: создание, смена состояний,
выбор следующего процесса, завершение.

### Публичный интерфейс
- `create_process(name, owner, memory) -> int`
- `list_processes() -> list`
- `set_state(pid, state) -> bool`
- `kill_process(pid) -> bool`
- `pick_next() -> dict | None`

### Внутренние зависимости
`db.py` — для таблицы `processes`.

### Обработка ошибок
- При превышении `MAX_PROCESSES` — `RuntimeError`.
- При отсутствии pid — `kill_process` возвращает `False`.

### Побочные эффекты
Записи в таблице `processes`.

---

## 5. Модуль `memory.py`

### Назначение
Учёт выделения памяти процессам. Минимальная единица — страница
`PAGE_SIZE = 4096` байт.

### Публичный интерфейс
- `alloc(pid, size) -> int`
- `free(pid) -> bool`

### Внутренние зависимости
`db.py` — обновление поля `memory` в `processes`.

### Обработка ошибок
- `size <= 0` → `ValueError`.
- Нет такого pid → `LookupError`.

### Побочные эффекты
Изменение поля `memory` в таблице `processes`.

---

## 6. Модуль `fs.py`

### Назначение
Файловая система. Отвечает за создание, чтение, запись и удаление
файлов. Работает с таблицей `files`.

### Публичный интерфейс
- `create_file(path, content, owner) -> int`
- `read_file(path) -> dict`
- `delete_file(path) -> bool`
- `list_files() -> list`

### Внутренние зависимости
`db.py` — для работы с таблицей `files`.

### Обработка ошибок
- Если файл уже существует, `create_file` возвращает `-1`.
- Если файл не найден, `read_file` бросает `FileNotFoundError`.
- Если нет прав, `delete_file` возвращает `False`.

### Побочные эффекты
- Создание, изменение или удаление записи в таблице `files`.
- Запись в `syscalls_log` (косвенно, через `syscalls.py`).

---

## 7. Модуль `auth.py`

### Назначение
Аутентификация (SHA-256) и авторизация по ролям.

### Публичный интерфейс
- `authenticate(login, password) -> bool`
- `get_role(login) -> str | None`
- `is_admin(login) -> bool`
- `authorize_file_access(login, owner) -> bool`
- `check_permission(current_user, action, target_owner=None) -> bool`

### Внутренние зависимости
`db.py` — для чтения таблицы `users`.

### Обработка ошибок
- Пользователь не найден → `authenticate` возвращает `False`.
- Неизвестная роль трактуется как `user`.

### Побочные эффекты
Нет (только чтение).

---

## 8. Модуль `shell.py`

### Назначение
Командная оболочка: цикл ввода, приглашение `user@studyos:~$`,
обработка команд, вызов системных вызовов.

### Публичный интерфейс
Функции-обработчики команд: `help`, `whoami`, `login`, `logout`,
`create`, `cat`, `rm`, `ls`, `exec`, `ps`, `kill`, `mem`, `logs`,
`shutdown`, `exit`.

### Внутренние зависимости
`syscalls.py`, `kernel.py`.

### Обработка ошибок
- Неизвестная команда — сообщение об ошибке.
- Любое исключение из syscall — вывод `[shell] Ошибка: ...`, оболочка
  не завершается.

### Побочные эффекты
Вывод в stdout, изменения в БД через syscalls.

---

# Матрица трассируемости требований

| Требование | Модуль | Тест |
|---|---|---|
| NFR-1: Время обработки syscall ≤ 50 мс | `syscalls.py` (`_timed`) | TC-01 |
| NFR-2: ≥ 10 одновременных процессов | `scheduler.py` (`MAX_PROCESSES`) | TC-04 |
| NFR-3: Ошибка процесса не роняет ядро | `syscalls.py` (`_timed`) + `shell.py` | TC-05 |
| NFR-4: Пароли как SHA-256 | `db.py` (`hash_password`) + `auth.py` | TC-06 |
| NFR-5: User не может удалить файл Admin | `syscalls.py` (`check_permission`) | TC-02 |
| NFR-6: Модуль ≤ 300 строк | структура проекта | TC-03 |
| NFR-7: Все syscall логируются | `syscalls.py` (`log_syscall`) | TC-07 |
| NFR-8: Работа без внешних СУБД | `db.py` | TC-08 |

**Пояснения:**

- **NFR-4:** `auth.py` при регистрации вычисляет `hashlib.sha256(password)`
  и сохраняет в поле `password_hash` таблицы `users`. При входе хэш
  сравнивается с `db.hash_password(password)`.
- **NFR-5:** `syscalls.check_permission("guest", "delete_file", "admin")`
  возвращает `False`, `sys_delete_file` пишет в лог статус `DENIED`
  и возвращает `False`.
- **NFR-7:** каждая функция `sys_*` вызывает `log_syscall(...)` до и
  после операции.

**Проверка полноты:**
- Все 8 требований связаны хотя бы с одним модулем ✔
- Все 8 модулей связаны хотя бы с одним требованием ✔
- У всех требований есть тест-кейс ✔

---

# Тест-кейсы

## TC-01: Проверка времени обработки syscall (NFR-1)

**Шаги:**
1. Запустить интерпретатор Python.
2. Импортировать `sys_create_file` из `src.syscalls`.
3. Замерить время через `time.perf_counter()` до и после вызова.
4. Повторить 100 раз.
5. Вычислить среднее время.

**Ожидаемый результат:** среднее время ≤ 50 мс.
**Фактический результат:** ---
**Статус:** ---

---

## TC-02: Проверка разграничения прав на удаление файла (NFR-5)

**Шаги:**
1. Авторизоваться как `guest` (не входить).
2. Создать файл от имени `admin` (через `sys_create_file(..., "admin")`).
3. От имени `guest` вызвать `sys_delete_file` для этого файла.
4. Проверить возвращаемое значение.

**Ожидаемый результат:** возвращено `False`, в логе статус `DENIED`.
**Фактический результат:** ---
**Статус:** ---

---

## TC-03: Проверка размера модулей (NFR-6)

**Шаги:**
1. Открыть терминал в корне проекта.
2. Выполнить команду: `wc -l src/*.py`.
3. Проверить, что ни один файл не превышает 300 строк.

**Ожидаемый результат:** все файлы ≤ 300 строк.
**Фактический результат:** ---
**Статус:** ---

---

## TC-04: Проверка лимита процессов (NFR-2)

**Шаги:**
1. В цикле вызвать `sys_exec("p", 0, "admin")` 10 раз.
2. На 11-й раз ожидать `RuntimeError`.
3. Проверить, что в таблице `processes` ровно 10 строк.

**Ожидаемый результат:** 11-й вызов бросает `RuntimeError`.
**Фактический результат:** ---
**Статус:** ---

---

## TC-05: Проверка устойчивости ядра к ошибке процесса (NFR-3)

**Шаги:**
1. Вызвать `sys_read_file("/no_such_file.txt", "admin")`.
2. Убедиться, что исключение обработано в `_timed`, статус `ERROR`.
3. Проверить, что оболочка продолжает работать.

**Ожидаемый результат:** оболочка не падает, в логе `ERROR: not found`.
**Фактический результат:** ---
**Статус:** ---

---

# Итоги дня

**Что сделано:**
- Составлены спецификации для восьми модулей.
- Построена матрица трассируемости для восьми требований.
- Разработаны пять тест-кейсов.
- Реализована функция `check_permission`.
- Внедрена проверка прав в `sys_delete_file` и `sys_kill`.
- Написаны автоматические тесты в `tests/test_permissions.py`.
- Построена диаграмма последовательности (`docs/03_sequence_permissions.png`).