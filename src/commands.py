"""Модуль с командами эмулятора и диспетчером команд."""
from src.vfs import VirtualFileSystem

NO_ARGS_LABEL = "none"
DEFAULT_VFS_NAME = "my_vfs"
LS_COMMAND = "ls"
CD_COMMAND = "cd"
TREE_COMMAND = "tree"
EXIT_COMMAND = "exit"
GOODBYE_MESSAGE = "Goodbye!"
VFS_NOT_LOADED_MESSAGE = "Error: VFS is not loaded"
UNKNOWN_COMMAND_TEMPLATE = "Error: unknown command '{command}'"


def execute_ls(args: list[str]) -> str:
    """Выполняет заглушку команды ls.

    Аргументы:
        args: Список аргументов команды.

    Возвращает:
        Строка с именем команды и переданными аргументами.
    """
    args_str = ", ".join(args) if args else NO_ARGS_LABEL
    return f"ls called with args: {args_str}"


def execute_cd(args: list[str]) -> str:
    """Выполняет заглушку команды cd.

    Аргументы:
        args: Список аргументов команды.

    Возвращает:
        Строка с именем команды и переданными аргументами.
    """
    args_str = ", ".join(args) if args else NO_ARGS_LABEL
    return f"cd called with args: {args_str}"


def execute_tree(vfs: VirtualFileSystem | None) -> str:
    """Возвращает дерево VFS или сообщение об отсутствии VFS.

    Аргументы:
        vfs: Объект виртуальной файловой системы или None.

    Возвращает:
        Строка с деревом VFS либо сообщение, что VFS не загружена.
    """
    if vfs is None:
        return VFS_NOT_LOADED_MESSAGE
    return vfs.render_tree()


def dispatch_command(
    command: str,
    args: list[str],
    vfs: VirtualFileSystem | None,
) -> str:
    """Направляет команду соответствующему обработчику.

    Аргументы:
        command: Имя команды.
        args: Список аргументов команды.
        vfs: Виртуальная файловая система или None.

    Возвращает:
        Строковый результат выполнения команды.
    """
    if command == LS_COMMAND:
        return execute_ls(args)
    if command == CD_COMMAND:
        return execute_cd(args)
    if command == TREE_COMMAND:
        return execute_tree(vfs)
    return UNKNOWN_COMMAND_TEMPLATE.format(command=command)
