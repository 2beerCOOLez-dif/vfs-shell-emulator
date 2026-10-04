"""Модуль для выполнения стартовых скриптов эмулятора."""
from pathlib import Path

from src.commands import execute_cd, execute_ls
from src.parser import parse_input
from src.repl import EXIT_COMMAND, GOODBYE_MESSAGE, VFS_NAME

COMMENT_PREFIX = "#"
SCRIPT_START_TEMPLATE = "Running script: {path}"
SCRIPT_FINISH_MESSAGE = "Script finished"
UNKNOWN_COMMAND_TEMPLATE = "Error: unknown command '{command}'"


def run_script(script_path: Path) -> None:
    """Выполняет команды из файла стартового скрипта.

    Каждая непустая строка файла трактуется как команда эмулятора.
    Строки, начинающиеся с символа комментария, пропускаются.

    Аргументы:
        script_path: Путь к файлу стартового скрипта.

    Исключения:
        FileNotFoundError: Если файл скрипта не существует.
    """
    if not script_path.exists():
        raise FileNotFoundError(
            f"Script file not found: {script_path}"
        )

    print(SCRIPT_START_TEMPLATE.format(path=script_path))

    with open(script_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith(COMMENT_PREFIX):
                continue
            print(f"{VFS_NAME}> {line}")
            command, args = parse_input(line)
            if command == EXIT_COMMAND:
                print(GOODBYE_MESSAGE)
                break
            if command == "ls":
                print(execute_ls(args))
            elif command == "cd":
                print(execute_cd(args))
            else:
                print(
                    UNKNOWN_COMMAND_TEMPLATE.format(command=command)
                )

    print(SCRIPT_FINISH_MESSAGE)
