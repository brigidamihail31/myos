"""Тесты файловой системы."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import db, fs


def _clean(paths):
    for p in paths:
        db.execute_delete("files", {"path": p})


def test_create_and_read():
    _clean(["/t1.txt"])
    fs.create_file("/t1.txt", "content1", "admin")
    assert fs.read_file("/t1.txt") == "content1"
    print("[PASS] создание и чтение файла")


def test_duplicate_path():
    _clean(["/t2.txt"])
    fs.create_file("/t2.txt", "a", "admin")
    assert fs.create_file("/t2.txt", "b", "admin") == -1
    print("[PASS] дубликат пути отклонён")


def test_update():
    _clean(["/t3.txt"])
    fs.create_file("/t3.txt", "old", "admin")
    fs.write_file("/t3.txt", "new")
    assert fs.read_file("/t3.txt") == "new"
    print("[PASS] обновление содержимого")


def test_delete():
    _clean(["/t4.txt"])
    fs.create_file("/t4.txt", "x", "admin")
    fs.delete_file("/t4.txt")
    assert fs.read_file("/t4.txt") == ""
    print("[PASS] удаление файла")


def test_owner():
    _clean(["/t5.txt"])
    fs.create_file("/t5.txt", "x", "admin")
    assert fs.get_owner("/t5.txt") == "admin"
    assert fs.get_owner("/missing.txt") is None
    print("[PASS] получение владельца")


def test_list():
    _clean(["/list1.txt", "/list2.txt"])
    fs.create_file("/list1.txt", "a", "admin")
    fs.create_file("/list2.txt", "b", "admin")
    files = fs.list_files("/list")
    assert "/list1.txt" in files
    assert "/list2.txt" in files
    print("[PASS] список файлов по префиксу")


if __name__ == "__main__":
    db.init_db()
    test_create_and_read()
    test_duplicate_path()
    test_update()
    test_delete()
    test_owner()
    test_list()
    print("\nВсе тесты файловой системы пройдены.")