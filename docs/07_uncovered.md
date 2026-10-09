# 07. Анализ непокрытых участков кода

## db.py
- `init_db()` — вызывается косвенно при запуске, отдельного теста нет.
- `get_connection()` — используется всеми функциями, отдельного теста нет.
- `cursor()` — контекстный менеджер, покрыт косвенно.
- `hash_password()` — покрыт через `test_auth_unit.test_hash_password`.

## kernel.py
- `memory_info()` — покрыт косвенно через `test_memory_allocate`.
- `save_memory_state()` — покрыт в `test_save_memory_state`.
- `load_memory_state()` — **не покрыт** (требуется тест с перезапуском).

## auth.py
- Все основные функции покрыты.
- `get_role`, `is_admin`, `authorize_file_access` — покрыты косвенно
  через `check_permission`.

## fs.py
- `write_file()` — покрыт косвенно через `test_fs`.
- `get_file_info()`, `count_files()` — **не покрыты**.

## scheduler.py
- `get_process()`, `schedule_round_robin()` — покрыты в `test_integration`.
- `process_count()` — **не покрыт**.

## Вывод
Не покрыты отдельными тестами:
1. `kernel.load_memory_state()` — добавить тест ниже.
2. `fs.get_file_info()` и `fs.count_files()` — покрыть в день 8.
3. `scheduler.process_count()` — покрыть в день 8.