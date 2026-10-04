"""Модуль интерактивного цикла REPL эмулятора оболочки."""
from src.commands import EXIT_COMMAND, GOODBYE_MESSAGE, dispatch_command
from src.parser import parse_input
from src.shell import Shell


def run_repl(shell: Shell | None = None) -> None:
    """Запускает интерактивный цикл REPL эмулятора.

    Цикл читает команды пользователя, направляет их обработчику
    и печатает результат. Завершается по команде exit или по
    сочетанию клавиш прерывания ввода.

    Аргументы:
        shell: Сессия эмулятора или None для пустой сессии.
    """
    if shell is None:
        shell = Shell()
    name = shell.prompt_name
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
        result = dispatch_command(command, args, shell)
        if result:
            print(result)
