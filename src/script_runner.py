"""Модуль для выполнения стартовых скриптов эмулятора."""
from pathlib import Path

from src.commands import (
    DEFAULT_VFS_NAME,
    EXIT_COMMAND,
    GOODBYE_MESSAGE,
    dispatch_command,
)
from src.parser import parse_input
from src.vfs import VirtualFileSystem

COMMENT_PREFIX = "#"
SCRIPT_START_TEMPLATE = "Running script: {path}"
SCRIPT_FINISH_MESSAGE = "Script finished"


def run_script(
    script_path: Path,
    vfs: VirtualFileSystem | None = None,
) -> None:
    """Выполняет команды из файла стартового скрипта.

    Каждая непустая строка файла трактуется как команда эмулятора.
    Строки, начинающиеся с символа комментария, пропускаются.

    Аргументы:
        script_path: Путь к файлу стартового скрипта.
        vfs: Загруженная в память виртуальная система или None.

    Исключения:
        FileNotFoundError: Если файл скрипта не существует.
    """
    if not script_path.exists():
        raise FileNotFoundError(
            f"Script file not found: {script_path}"
        )

    name = vfs.name if vfs is not None else DEFAULT_VFS_NAME
    print(SCRIPT_START_TEMPLATE.format(path=script_path))

    with open(script_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith(COMMENT_PREFIX):
                continue
            print(f"{name}> {line}")
            command, args = parse_input(line)
            if command == EXIT_COMMAND:
                print(GOODBYE_MESSAGE)
                break
            print(dispatch_command(command, args, vfs))

    print(SCRIPT_FINISH_MESSAGE)
