"""Модуль с командами-заглушками эмулятора оболочки."""

NO_ARGS_LABEL = "none"


def execute_ls(args: list[str]) -> str:
    """Выполняет заглушку команды ls.

    Args:
        args: Список аргументов команды.

    Returns:
        Строка с именем команды и переданными аргументами.
    """
    args_str = ", ".join(args) if args else NO_ARGS_LABEL
    return f"ls called with args: {args_str}"


def execute_cd(args: list[str]) -> str:
    """Выполняет заглушку команды cd.

    Args:
        args: Список аргументов команды.

    Returns:
        Строка с именем команды и переданными аргументами.
    """
    args_str = ", ".join(args) if args else NO_ARGS_LABEL
    return f"cd called with args: {args_str}"
