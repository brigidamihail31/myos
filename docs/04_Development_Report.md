# Отчёт по дню 4

## Что сделано
- Расширен `db.py`: добавлены `execute_insert`, `execute_select`,
  `execute_update`, `execute_delete`.
- Создан `kernel.py` с классом `Kernel` и методами `set_user`, `get_user`,
  `allocate_pid`, `allocate_memory`, `free_memory`, `memory_info` (+ `reset`).
- Создан `auth.py` с `hash_password`, `register_user`, `authenticate`,
  `check_permission`, `is_admin`.
- Обновлён `syscalls.py`: `sys_login`, `sys_whoami`, `sys_delete_file`,
  `sys_kill` используют реальные модули и логируют статусы
  `check`, `OK`, `DENIED`.
- Обновлён `shell.py`: команды `login`, `mem`, `delete` работают.
- Написаны тесты `test_kernel.py` и `test_auth.py`.

## Проверки
- Записи в `syscalls_log`: `sys_login`, `sys_whoami`, `sys_delete_file`,
  `sys_kill`.
- Пароль в БД хранится в виде хэша длиной 64 символа.
- Права разграничены: `admin` может всё, `user` — нет.
- Отладка в VS Code: скриншот сохранён (`docs/04_debug_screenshot.png`).

## Замечания
- Пустой пароль допускается. В следующих итерациях следует добавить
  валидацию длины (не менее 4 символов).