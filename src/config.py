"""Модуль обработки аргументов командной строки и конфигурации."""
import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AppConfig:
    """Хранит все параметры конфигурации эмулятора.

    Атрибуты:
        vfs_path: Путь к файлу виртуальной файловой системы.
        script_path: Путь к файлу стартового скрипта.
    """

    vfs_path: Path | None
    script_path: Path | None


def parse_args() -> AppConfig:
    """Разбирает аргументы командной строки и возвращает конфигурацию.

    Возвращает:
        Экземпляр AppConfig с разобранными параметрами запуска.
    """
    parser = argparse.ArgumentParser(
        description="VFS Shell Emulator"
    )
    parser.add_argument(
        "--vfs-path",
        type=Path,
        default=None,
        help="Path to the virtual file system file",
    )
    parser.add_argument(
        "--script",
        type=Path,
        default=None,
        help="Path to the startup script file",
    )
    args = parser.parse_args()
    return AppConfig(
        vfs_path=args.vfs_path,
        script_path=args.script,
    )
