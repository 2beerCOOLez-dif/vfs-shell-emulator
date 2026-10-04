"""Модуль для выполнения стартовых скриптов эмулятора."""
from pathlib import Path

from src.commands import EXIT_COMMAND, GOODBYE_MESSAGE, dispatch_command
from src.parser import parse_input
from src.shell import Shell

COMMENT_PREFIX = "#"
SCRIPT_START_TEMPLATE = "Running script: {path}"
SCRIPT_FINISH_MESSAGE = "Script finished"


def run_script(
    script_path: Path,
    shell: Shell | None = None,
) -> None:
    """Выполняет команды из файла стартового скрипта.

    Каждая непустая строка файла трактуется как команда эмулятора.
    Строки, начинающиеся с символа комментария, пропускаются.

    Аргументы:
        script_path: Путь к файлу стартового скрипта.
        shell: Сессия эмулятора или None для пустой сессии.

    Исключения:
        FileNotFoundError: Если файл скрипта не существует.
    """
    if not script_path.exists():
        raise FileNotFoundError(
            f"Script file not found: {script_path}"
        )
    if shell is None:
        shell = Shell()

    name = shell.prompt_name
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
            result = dispatch_command(command, args, shell)
            if result:
                print(result)

    print(SCRIPT_FINISH_MESSAGE)
