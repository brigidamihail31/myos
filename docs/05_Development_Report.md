# Отчёт по дню 5

## Что сделано
- Создан модуль `src/fs.py` с шестью функциями: `create_file`,
  `read_file`, `write_file`, `delete_file`, `list_files`, `get_owner`.
- Создан модуль `src/scheduler.py` с шестью функциями: `create_process`,
  `list_processes`, `get_process`, `terminate_process`,
  `schedule_round_robin`, `process_count`.
- Расширен `kernel.py` методами `save_memory_state`, `load_memory_state`.
- Добавлена таблица `memory_state` в `db.py`.
- Обновлён `syscalls.py`: файловые и процессные вызовы используют
  реальные модули.
- Обновлён `shell.py`: команды `cat`, `run`, `kill`, `ls`, `create`.
- Написаны тесты `test_fs.py` и `test_scheduler.py`.

## Проверки
- Сквозной сценарий: вход, создание двух файлов, чтение, запуск двух
  процессов, `kill`, `mem`.
- Записи в `syscalls_log`: `sys_create_file`, `sys_read_file`,
  `sys_exec`, `sys_ps`, `sys_kill`.
- Тесты ФС: 6 из 6 пройдены.
- Тесты планировщика: 6 из 6 пройдены.
- Память освобождается при завершении процесса.

## Замечания
- При попытке создать файл с существующим путём возвращается `-1`
  и статус `EXISTS`.
- Round Robin упрощён: выбирает первый процесс из очереди.