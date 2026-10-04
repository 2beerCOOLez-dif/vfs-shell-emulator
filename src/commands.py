"""Модуль с командами эмулятора и диспетчером команд."""
from src.shell import Shell
from src.vfs import CHILDREN_KEY, DIR_TYPE, TYPE_KEY, VfsError

LS_COMMAND = "ls"
CD_COMMAND = "cd"
TREE_COMMAND = "tree"
DU_COMMAND = "du"
PWD_COMMAND = "pwd"
WHOAMI_COMMAND = "whoami"
EXIT_COMMAND = "exit"
GOODBYE_MESSAGE = "Goodbye!"
VFS_NOT_LOADED_MESSAGE = "Error: VFS is not loaded"
UNKNOWN_COMMAND_TEMPLATE = "Error: unknown command '{command}'"
NO_SUCH_PATH_TEMPLATE = "Error: no such path: {path}"
NOT_A_DIR_TEMPLATE = "Error: not a directory: {path}"
DU_TEMPLATE = "{size} bytes {path}"


def execute_ls(shell: Shell, args: list[str]) -> str:
    """Выводит содержимое каталога виртуальной системы.

    Аргументы:
        shell: Сессия эмулятора с загруженной VFS.
        args: Аргументы команды: необязательный путь.

    Возвращает:
        Имена узлов через перенос строки или сообщение об ошибке.
    """
    if shell.vfs is None:
        return VFS_NOT_LOADED_MESSAGE
    raw = args[0] if args else ""
    node = shell.vfs.get_node(shell.resolve(raw))
    if node is None:
        return NO_SUCH_PATH_TEMPLATE.format(path=raw)
    if node.get(TYPE_KEY) != DIR_TYPE:
        return shell.resolve(raw)[-1]
    return "\n".join(sorted(node.get(CHILDREN_KEY, {})))


def execute_cd(shell: Shell, args: list[str]) -> str:
    """Меняет текущий каталог сессии эмулятора.

    Аргументы:
        shell: Сессия эмулятора с загруженной VFS.
        args: Аргументы команды: необязательный путь.

    Возвращает:
        Пустая строка при успехе или сообщение об ошибке.
    """
    if shell.vfs is None:
        return VFS_NOT_LOADED_MESSAGE
    if not args:
        shell.chdir([])
        return ""
    raw = args[0]
    parts = shell.resolve(raw)
    node = shell.vfs.get_node(parts)
    if node is None:
        return NO_SUCH_PATH_TEMPLATE.format(path=raw)
    if node.get(TYPE_KEY) != DIR_TYPE:
        return NOT_A_DIR_TEMPLATE.format(path=raw)
    shell.chdir(parts)
    return ""


def execute_du(shell: Shell, args: list[str]) -> str:
    """Выводит размер поддерева виртуальной системы в байтах.

    Аргументы:
        shell: Сессия эмулятора с загруженной VFS.
        args: Аргументы команды: необязательный путь.

    Возвращает:
        Строка с размером и путём или сообщение об ошибке.
    """
    if shell.vfs is None:
        return VFS_NOT_LOADED_MESSAGE
    raw = args[0] if args else ""
    display = raw if args else shell.cwd_display()
    try:
        size = shell.vfs.subtree_size(shell.resolve(raw))
    except VfsError as error:
        return str(error)
    if size is None:
        return NO_SUCH_PATH_TEMPLATE.format(path=display)
    return DU_TEMPLATE.format(size=size, path=display)


def execute_pwd(shell: Shell) -> str:
    """Возвращает строковое представление текущего пути.

    Аргументы:
        shell: Сессия эмулятора.

    Возвращает:
        Текущий путь, начиная с корня.
    """
    return shell.cwd_display()


def execute_whoami(shell: Shell) -> str:
    """Возвращает имя пользователя виртуальной системы.

    Аргументы:
        shell: Сессия эмулятора.

    Возвращает:
        Имя пользователя из VFS или значение по умолчанию.
    """
    return shell.user


def execute_tree(shell: Shell) -> str:
    """Возвращает дерево VFS или сообщение об отсутствии VFS.

    Аргументы:
        shell: Сессия эмулятора с загруженной VFS.

    Возвращает:
        Строка с деревом VFS либо сообщение, что VFS не загружена.
    """
    if shell.vfs is None:
        return VFS_NOT_LOADED_MESSAGE
    return shell.vfs.render_tree()


def dispatch_command(command: str, args: list[str], shell: Shell) -> str:
    """Направляет команду соответствующему обработчику.

    Аргументы:
        command: Имя команды.
        args: Список аргументов команды.
        shell: Сессия эмулятора с загруженной VFS.

    Возвращает:
        Строковый результат выполнения команды.
    """
    if command == LS_COMMAND:
        return execute_ls(shell, args)
    if command == CD_COMMAND:
        return execute_cd(shell, args)
    if command == TREE_COMMAND:
        return execute_tree(shell)
    if command == DU_COMMAND:
        return execute_du(shell, args)
    if command == PWD_COMMAND:
        return execute_pwd(shell)
    if command == WHOAMI_COMMAND:
        return execute_whoami(shell)
    return UNKNOWN_COMMAND_TEMPLATE.format(command=command)
