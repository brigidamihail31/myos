# Журнал интеграции (день 6)

## Сквозной сценарий

| Шаг | Команда | Ожидание | Результат |
|---|---|---|---|
| 1 | `whoami` | `guest` | ✅ |
| 2 | `login` → `admin / admin` | вход выполнен | ✅ |
| 3 | `create /report.txt quarterly report` | id файла | ✅ |
| 4 | `create /notes.txt my notes` | id файла | ✅ |
| 5 | `ls` | список из 2 файлов | ✅ |
| 6 | `cat /report.txt` | `quarterly report` | ✅ |
| 7 | `run editor` | PID=1 | ✅ |
| 8 | `run browser` | PID=2 | ✅ |
| 9 | `ps` | таблица с 2 процессами | ✅ |
| 10 | `kill 1` | процесс 1 завершён | ✅ |
| 11 | `mem` | `10 / 1024 МБ` | ✅ |
| 12 | `logs 10` | записи sys_* | ✅ |
| 13 | `exit` | выход | ✅ |

## Найденные и исправленные ошибки

### Ошибка 1: sys_delete_file не проверял владельца
- **Симптом:** пользователь удалял чужой файл.
- **Причина:** в `check_permission` не передавался `owner`.
- **Исправление:** добавлен вызов `fs.get_owner(path)` перед `check_permission`.

### Ошибка 2: несовпадение полей processes
- **Симптом:** `sqlite3.OperationalError: no such column: pid`.
- **Причина:** старая схема таблицы `processes` имела `id`/`memory`, а новый код — `pid`/`memory_used`.
- **Исправление:** пересоздана база (`del db/os.sqlite && python src/db.py`) с новой схемой.

### Ошибка 3: таблица memory_state отсутствовала
- **Симптом:** `sqlite3.OperationalError: no such table: memory_state`.
- **Причина:** схема БД не обновлена.
- **Исправление:** добавлено `CREATE TABLE IF NOT EXISTS memory_state` в `db.init_db()`.

## Обработка ошибок

| Сценарий | Ожидалось | Фактически |
|---|---|---|
| `login` → `nobody / anything` | «Ошибка входа» | ✅ |
| `cat /missing.txt` | «файл пуст или не существует» | ✅ |
| `kill 99999` | «Не удалось завершить процесс 99999» | ✅ |
| `delete /admin_file.txt` (под user) | «Нет прав на удаление» | ✅ |

## Рефакторинг

- Модули `src/*.py` проверены на длину: все ≤ 300 строк.
- Прямых вызовов `sqlite3.connect` вне `db.py` нет.
- Циклических импортов нет.
- Обработка исключений присутствует в `_timed()` и главном цикле `shell.main()`.