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
FLAG_PREFIX = "-"
FLAG_PREFIX_LEN = 1
ALL_FLAG = "a"
LONG_FLAG = "l"
HUMAN_FLAG = "h"
HIDDEN_PREFIX = "."
DIR_MARKER = "d"
FILE_MARKER = "-"
DIR_SUFFIX = "/"
LONG_LINE_TEMPLATE = "{marker} {size} {name}"
BYTES_IN_KB = 1024
BYTES_IN_MB = 1048576
BYTES_TEMPLATE = "{value}B"
HUMAN_KB_TEMPLATE = "{value:.1f}K"
HUMAN_MB_TEMPLATE = "{value:.1f}M"


def _parse_ls_flags(args: list[str]) -> tuple[set[str], list[str]]:
    """Разделяет аргументы ls на флаги и пути.

    Аргументы:
        args: Все аргументы команды ls.

    Возвращает:
        Кортеж из множества символов флагов и списка путей.
    """
    flags: set[str] = set()
    paths: list[str] = []
    for arg in args:
        if arg.startswith(FLAG_PREFIX) and len(arg) > FLAG_PREFIX_LEN:
            flags.update(arg[FLAG_PREFIX_LEN:])
        else:
            paths.append(arg)
    return flags, paths


def _ls_names(node: dict, flags: set[str]) -> list[str]:
    """Возвращает отсортированные имена узлов каталога.

    Аргументы:
        node: Словарь каталога.
        flags: Множество символов флагов команды ls.

    Возвращает:
        Имена детей; скрытые имена только с флагом -a.
    """
    names = sorted(node.get(CHILDREN_KEY, {}))
    if ALL_FLAG in flags:
        return names
    return [n for n in names if not n.startswith(HIDDEN_PREFIX)]


def _human_size(size: int) -> str:
    """Возвращает человекочитаемое представление размера.

    Аргументы:
        size: Размер в байтах.

    Возвращает:
        Строка вида 12B, 2.0K или 3.5M.
    """
    if size >= BYTES_IN_MB:
        return HUMAN_MB_TEMPLATE.format(value=size / BYTES_IN_MB)
    if size >= BYTES_IN_KB:
        return HUMAN_KB_TEMPLATE.format(value=size / BYTES_IN_KB)
    return BYTES_TEMPLATE.format(value=size)


def _ls_long_line(
    shell: Shell,
    parent_parts: list[str],
    name: str,
    flags: set[str],
) -> str:
    """Формирует строку длинного формата для одного узла.

    Аргументы:
        shell: Сессия эмулятора с загруженной VFS.
        parent_parts: Компоненты пути родительского каталога.
        name: Имя узла.
        flags: Множество символов флагов команды ls.

    Возвращает:
        Строка вида «тип размер имя».
    """
    parts = parent_parts + [name]
    node = shell.vfs.get_node(parts)
    is_dir = node.get(TYPE_KEY) == DIR_TYPE
    size = shell.vfs.subtree_size(parts) or 0
    if HUMAN_FLAG in flags:
        shown = _human_size(size)
    else:
        shown = BYTES_TEMPLATE.format(value=size)
    marker = DIR_MARKER if is_dir else FILE_MARKER
    suffix = DIR_SUFFIX if is_dir else ""
    return LONG_LINE_TEMPLATE.format(
        marker=marker, size=shown, name=f"{name}{suffix}"
    )


def execute_ls(shell: Shell, args: list[str]) -> str:
    """Выводит содержимое каталога виртуальной системы.

    Аргументы:
        shell: Сессия эмулятора с загруженной VFS.
        args: Аргументы команды: флаги и необязательный путь.

    Возвращает:
        Имена узлов или строки длинного формата либо ошибку.
    """
    if shell.vfs is None:
        return VFS_NOT_LOADED_MESSAGE
    flags, paths = _parse_ls_flags(args)
    raw = paths[0] if paths else ""
    node = shell.vfs.get_node(shell.resolve(raw))
    if node is None:
        return NO_SUCH_PATH_TEMPLATE.format(path=raw)
    if node.get(TYPE_KEY) != DIR_TYPE:
        return shell.resolve(raw)[-1]
    names = _ls_names(node, flags)
    if LONG_FLAG not in flags:
        return "\n".join(names)
    lines = [
        _ls_long_line(shell, shell.resolve(raw), n, flags)
        for n in names
    ]
    return "\n".join(lines)


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
    return UNKNOWN_COMMAND_TEMPLATE.format(command=command)
