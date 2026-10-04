"""Модуль интерактивного цикла REPL эмулятора оболочки."""
from src.commands import execute_cd, execute_ls
from src.parser import parse_input

VFS_NAME = "my_vfs"
EXIT_COMMAND = "exit"
GOODBYE_MESSAGE = "Goodbye!"


def run_repl() -> None:
    """Запускает интерактивный цикл REPL эмулятора.

    Цикл читает команды пользователя, передаёт их заглушкам
    команд и печатает результат. Завершается по команде exit
    или по сочетанию клавиш прерывания ввода.
    """
    print(f"Welcome to {VFS_NAME} emulator!")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input(f"{VFS_NAME}> ")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            break

        command, args = parse_input(user_input)
        if not command:
            continue

        if command == EXIT_COMMAND:
            print(GOODBYE_MESSAGE)
            break
        if command == "ls":
            print(execute_ls(args))
        elif command == "cd":
            print(execute_cd(args))
        else:
            print(f"Error: unknown command '{command}'")
