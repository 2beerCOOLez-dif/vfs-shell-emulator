"""Модуль интерактивного цикла REPL эмулятора оболочки."""
from src.commands import (
    DEFAULT_VFS_NAME,
    EXIT_COMMAND,
    GOODBYE_MESSAGE,
    dispatch_command,
)
from src.parser import parse_input
from src.vfs import VirtualFileSystem


def run_repl(vfs: VirtualFileSystem | None = None) -> None:
    """Запускает интерактивный цикл REPL эмулятора.

    Цикл читает команды пользователя, направляет их обработчику
    и печатает результат. Завершается по команде exit или по
    сочетанию клавиш прерывания ввода.

    Аргументы:
        vfs: Загруженная в память виртуальная система или None.
    """
    name = vfs.name if vfs is not None else DEFAULT_VFS_NAME
    print(f"Welcome to {name} emulator!")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input(f"{name}> ")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            break

        command, args = parse_input(user_input)
        if not command:
            continue

        if command == EXIT_COMMAND:
            print(GOODBYE_MESSAGE)
            break
        print(dispatch_command(command, args, vfs))
