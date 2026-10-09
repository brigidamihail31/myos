# Верификация требований (день 6)

Проверка восьми нефункциональных требований из матрицы трассируемости.

| ID | Требование | Метод проверки | Факт | Статус |
|---|---|---|---|---|
| NFR-1 | Время syscall ≤ 50 мс | `time.perf_counter` × 100 вызовов | ~12 мс | ✅ |
| NFR-2 | 10 одновременных процессов | 10 × `sys_exec` | выдержано | ✅ |
| NFR-3 | Ошибка процесса не роняет ядро | `sys_read_file('/missing')` → `""` | ядро живо | ✅ |
| NFR-4 | Пароли — SHA-256 | `SELECT password_hash FROM users` | 64 hex-симв. | ✅ |
| NFR-5 | User не удаляет файл Admin | `sys_delete_file('/check.txt', 'user')` | `False` | ✅ |
| NFR-6 | Модули ≤ 300 строк | `wc -l src/*.py` | макс. 290 | ✅ |
| NFR-7 | Все syscalls логируются | `SELECT * FROM syscalls_log` | записи есть | ✅ |
| NFR-8 | Без внешних СУБД | `grep -r "^import\|^from" src/` | только stdlib | ✅ |

## Методики

### NFR-1. Замер времени

```bash
python -c "
import time
from src import db, fs
db.init_db()
t0 = time.perf_counter()
for i in range(100):
    fs.read_file('/nope.txt')
print((time.perf_counter()-t0)*10, 'мс/вызов')
"