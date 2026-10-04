"""Тесты для модуля разбора ввода."""
from src.parser import parse_input


def test_parse_empty_input():
    """Проверяет разбор пустой строки и строки из пробелов."""
    assert parse_input("") == ("", [])
    assert parse_input("   ") == ("", [])


def test_parse_single_command():
    """Проверяет разбор одиночной команды без аргументов."""
    assert parse_input("ls") == ("ls", [])


def test_parse_command_with_args():
    """Проверяет разбор команды с несколькими аргументами."""
    assert parse_input("cd folder") == ("cd", ["folder"])
    assert parse_input("ls -l -a") == ("ls", ["-l", "-a"])


def test_parse_command_with_extra_spaces():
    """Проверяет удаление лишних пробелов при разборе."""
    assert parse_input("  ls   folder  ") == ("ls", ["folder"])
