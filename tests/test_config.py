"""Тесты для модуля конфигурации."""
import sys
from pathlib import Path

from src.config import parse_args


def test_parse_args_defaults(monkeypatch):
    """Проверяет значения по умолчанию при отсутствии аргументов."""
    monkeypatch.setattr(sys, "argv", ["main.py"])
    config = parse_args()
    assert config.vfs_path is None
    assert config.script_path is None


def test_parse_args_with_vfs_path(monkeypatch):
    """Проверяет разбор аргумента --vfs-path."""
    monkeypatch.setattr(
        sys, "argv", ["main.py", "--vfs-path", "data/test.json"]
    )
    config = parse_args()
    assert config.vfs_path == Path("data/test.json")
    assert config.script_path is None


def test_parse_args_with_script(monkeypatch):
    """Проверяет разбор аргумента --script."""
    monkeypatch.setattr(
        sys, "argv", ["main.py", "--script", "scripts/run.sh"]
    )
    config = parse_args()
    assert config.vfs_path is None
    assert config.script_path == Path("scripts/run.sh")


def test_parse_args_with_both(monkeypatch):
    """Проверяет разбор обоих аргументов одновременно."""
    monkeypatch.setattr(
        sys,
        "argv",
        ["main.py", "--vfs-path", "v.json", "--script", "s.sh"],
    )
    config = parse_args()
    assert config.vfs_path == Path("v.json")
    assert config.script_path == Path("s.sh")
