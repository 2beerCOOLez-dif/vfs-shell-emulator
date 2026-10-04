"""Модуль с командами эмулятора и диспетчером команд."""
from src.shell import Shell
from src.vfs import (
    CHILDREN_KEY,
    DIR_TYPE,
    FILE_TYPE,
    TYPE_KEY,
    VfsError,
    copy_node,
)

LS_COMMAND = "ls"
CD_COMMAND = "cd"
TREE_COMMAND = "tree"
DU_COMMAND = "du"
PWD_COMMAND = "pwd"
WHOAMI_COMMAND = "whoami"
CP_COMMAND = "cp"
EXIT_COMMAND = "exit"
GOODBYE_MESSAGE = "Goodbye!"
VFS_NOT_LOADED_MESSAGE = "Error: VFS is not loaded"
UNKNOWN_COMMAND_TEMPLATE = "Error: unknown command '{command}'"
NO_SUCH_PATH_TEMPLATE = "Error: no such path: {path}"
NOT_A_DIR_TEMPLATE = "Error: not a directory: {path}"
DU_TEMPLATE = "{size} bytes {path}"
CP_ARGS_COUNT = 2
CP_USAGE_MESSAGE = "Usage: cp <source> <destination>"
CP_ROOT_MESSAGE = "Error: cannot copy root directory"
CP_INTO_ITSELF_TEMPLATE = "Error: cannot copy directory into itself: {path}"
CP_OVERWRITE_DIR_TEMPLATE = (
    "Error: cannot overwrite file with directory: {path}"
)


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


def execute_cp(shell: Shell, args: list[str]) -> str:
    """Копирует узел VFS в новое место только в памяти.

    Аргументы:
        shell: Сессия эмулятора с загруженной VFS.
        args: Аргументы команды: путь источника и приёмника.

    Возвращает:
        Пустая строка при успехе или сообщение об ошибке.
    """
    if shell.vfs is None:
        return VFS_NOT_LOADED_MESSAGE
    if len(args) != CP_ARGS_COUNT:
        return CP_USAGE_MESSAGE
    source_parts = shell.resolve(args[0])
    source = shell.vfs.get_node(source_parts)
    if source is None:
        return NO_SUCH_PATH_TEMPLATE.format(path=args[0])
    if not source_parts:
        return CP_ROOT_MESSAGE
    target, error = _resolve_cp_target(
        shell, source, source_parts, args[1]
    )
    if error:
        return error
    if not shell.vfs.set_node(target, copy_node(source)):
        return NO_SUCH_PATH_TEMPLATE.format(path=args[1])
    return ""


def _resolve_cp_target(
    shell: Shell,
    source: dict,
    source_parts: list[str],
    dest_raw: str,
) -> tuple[list[str], str]:
    """Вычисляет целевой путь копирования для команды cp.

    Аргументы:
        shell: Сессия эмулятора с загруженной VFS.
        source: Словарь копируемого узла.
        source_parts: Компоненты пути источника.
        dest_raw: Строка пути приёмника.

    Возвращает:
        Кортеж из целевого пути и сообщения об ошибке;
        при успехе сообщение пустое.
    """
    dest_parts = shell.resolve(dest_raw)
    dest_node = shell.vfs.get_node(dest_parts)
    if dest_node is not None and dest_node.get(TYPE_KEY) == DIR_TYPE:
        target = dest_parts + [source_parts[-1]]
    else:
        target = dest_parts
    if source.get(TYPE_KEY) == DIR_TYPE:
        if target[: len(source_parts)] == source_parts:
            return [], CP_INTO_ITSELF_TEMPLATE.format(path=dest_raw)
        target_node = shell.vfs.get_node(target)
        if target_node is not None:
            if target_node.get(TYPE_KEY) == FILE_TYPE:
                return [], CP_OVERWRITE_DIR_TEMPLATE.format(
                    path=dest_raw
                )
    return target, ""


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


def dispatch_command(
    command: str, args: list[str], shell: Shell
) -> str:
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
    if command == CP_COMMAND:
        return execute_cp(shell, args)
    return UNKNOWN_COMMAND_TEMPLATE.format(command=command)
