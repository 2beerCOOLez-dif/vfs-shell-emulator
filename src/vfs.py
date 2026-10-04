"""Модуль виртуальной файловой системы в памяти."""
import base64
import json
from pathlib import Path

TYPE_KEY = "type"
DIR_TYPE = "dir"
FILE_TYPE = "file"
CHILDREN_KEY = "children"
CONTENT_KEY = "content"
NAME_KEY = "vfs_name"
ROOT_KEY = "root"
USER_KEY = "user"
DEFAULT_NAME = "my_vfs"
DEFAULT_USER = "guest"
TREE_INDENT = "    "
ROOT_PREFIX = "/"
CURRENT_DIR = "."
PARENT_DIR = ".."


class VfsError(Exception):
    """Ошибка загрузки или структуры виртуальной системы."""


class VirtualFileSystem:
    """Виртуальная файловая система, загруженная в память."""

    def __init__(self, data: dict) -> None:
        """Сохраняет данные VFS и проверяет структуру.

        Аргументы:
            data: Словарь VFS, разобранный из JSON.

        Исключения:
            VfsError: Если структура VFS некорректна.
        """
        self._name = str(data.get(NAME_KEY, DEFAULT_NAME))
        self._user = str(data.get(USER_KEY, DEFAULT_USER))
        root = data.get(ROOT_KEY, {})
        if not root:
            root = {TYPE_KEY: DIR_TYPE, CHILDREN_KEY: {}}
        self._root = root
        _validate_node(self._root, "/")

    @classmethod
    def from_json(cls, path: Path) -> "VirtualFileSystem":
        """Загружает VFS из JSON-файла целиком в память.

        Аргументы:
            path: Путь к JSON-файлу с описанием VFS.

        Возвращает:
            Новый объект VirtualFileSystem.

        Исключения:
            VfsError: Если файл не найден или JSON некорректен.
        """
        if not path.exists():
            raise VfsError(f"VFS file not found: {path}")
        raw = path.read_text(encoding="utf-8")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as error:
            raise VfsError(f"Invalid JSON: {error}") from error
        return cls(data)

    @property
    def name(self) -> str:
        """Возвращает имя виртуальной файловой системы."""
        return self._name

    @property
    def user(self) -> str:
        """Возвращает имя пользователя виртуальной системы."""
        return self._user

    def get_node(self, parts: list[str]) -> dict | None:
        """Возвращает узел по пути или None, если путь не найден.

        Аргументы:
            parts: Список компонентов пути от корня.

        Возвращает:
            Словарь узла либо None при отсутствии пути.
        """
        node = self._root
        for part in parts:
            if node.get(TYPE_KEY) != DIR_TYPE:
                return None
            children = node.get(CHILDREN_KEY, {})
            node = children.get(part)
            if node is None:
                return None
        return node

    def count_nodes(self) -> int:
        """Возвращает общее число узлов в виртуальной системе."""
        return _count_nodes(self._root)

    def render_tree(self) -> str:
        """Возвращает дерево VFS в виде строки для вывода."""
        lines = [f"{self._name}/"]
        _render_node(self._root, "", lines)
        return "\n".join(lines)

    def subtree_size(self, parts: list[str]) -> int | None:
        """Возвращает размер поддерева в байтах или None.

        Аргументы:
            parts: Список компонентов пути от корня.

        Возвращает:
            Размер файла или суммы файлов каталога либо None.

        Исключения:
            VfsError: Если base64-содержимое файла некорректно.
        """
        node = self.get_node(parts)
        if node is None:
            return None
        return _node_size(node)

    def set_node(self, parts: list[str], node: dict) -> bool:
        """Вставляет или заменяет узел по пути только в памяти.

        Аргументы:
            parts: Список компонентов пути от корня.
            node: Словарь узла для вставки.

        Возвращает:
            True при успехе, False если родитель не найден.
        """
        if not parts:
            return False
        parent = self.get_node(parts[:-1])
        if parent is None or parent.get(TYPE_KEY) != DIR_TYPE:
            return False
        parent.setdefault(CHILDREN_KEY, {})[parts[-1]] = node
        return True

    def decode_content(self, parts: list[str]) -> str:
        """Декодирует base64-содержимое файла в строку в памяти.

        Аргументы:
            parts: Список компонентов пути до файла.

        Возвращает:
            Раскодированное содержимое файла.

        Исключения:
            VfsError: Если файл не найден или base64 некорректен.
        """
        node = self.get_node(parts)
        if node is None or node.get(TYPE_KEY) != FILE_TYPE:
            raise VfsError(f"File not found: {'/'.join(parts)}")
        try:
            return base64.b64decode(node[CONTENT_KEY]).decode()
        except (ValueError, UnicodeDecodeError) as error:
            raise VfsError(f"Invalid base64: {error}") from error


def resolve_path(raw: str, cwd: list[str]) -> list[str]:
    """Преобразует строку пути в список компонентов.

    Поддерживает абсолютные пути, начинающиеся с '/', и
    относительные пути с элементами '.' и '..'.

    Аргументы:
        raw: Строка пути.
        cwd: Компоненты текущего каталога.

    Возвращает:
        Список компонентов пути без служебных элементов.
    """
    if raw.startswith(ROOT_PREFIX):
        parts: list[str] = []
    else:
        parts = list(cwd)
    for token in raw.split(ROOT_PREFIX):
        if token in ("", CURRENT_DIR):
            continue
        if token == PARENT_DIR:
            if parts:
                parts.pop()
            continue
        parts.append(token)
    return parts


def copy_node(node: dict) -> dict:
    """Создаёт глубокую копию узла VFS в памяти.

    Аргументы:
        node: Словарь узла для копирования.

    Возвращает:
        Новый узел с рекурсивно скопированными детьми.
    """
    result = {TYPE_KEY: node.get(TYPE_KEY)}
    if node.get(TYPE_KEY) == DIR_TYPE:
        children = {}
        for name, child in node.get(CHILDREN_KEY, {}).items():
            children[name] = copy_node(child)
        result[CHILDREN_KEY] = children
    else:
        result[CONTENT_KEY] = node.get(CONTENT_KEY, "")
    return result


def _validate_node(node: dict, path: str) -> None:
    """Рекурсивно проверяет корректность структуры узла VFS.

    Аргументы:
        node: Словарь узла для проверки.
        path: Путь узла для сообщения об ошибке.

    Исключения:
        VfsError: Если тип узла или его содержимое некорректны.
    """
    if not isinstance(node, dict):
        raise VfsError(f"Node is not an object: {path}")
    node_type = node.get(TYPE_KEY)
    if node_type == DIR_TYPE:
        children = node.get(CHILDREN_KEY, {})
        if not isinstance(children, dict):
            raise VfsError(f"Invalid children: {path}")
        for name, child in children.items():
            _validate_node(child, f"{path}{name}/")
    elif node_type == FILE_TYPE:
        if not isinstance(node.get(CONTENT_KEY, ""), str):
            raise VfsError(f"Invalid file content: {path}")
    else:
        raise VfsError(f"Unknown node type: {path}")


def _count_nodes(node: dict) -> int:
    """Рекурсивно считает число узлов в поддереве.

    Аргументы:
        node: Словарь узла, с которого начинается подсчёт.

    Возвращает:
        Число узлов, включая сам переданный узел.
    """
    total = 1
    for child in node.get(CHILDREN_KEY, {}).values():
        total += _count_nodes(child)
    return total


def _node_size(node: dict) -> int:
    """Вычисляет размер поддерева узла в байтах.

    Аргументы:
        node: Словарь узла для вычисления размера.

    Возвращает:
        Размер файла или сумма размеров детей для каталога.

    Исключения:
        VfsError: Если base64-содержимое файла некорректно.
    """
    if node.get(TYPE_KEY) == FILE_TYPE:
        try:
            return len(base64.b64decode(node.get(CONTENT_KEY, "")))
        except ValueError as error:
            raise VfsError(f"Invalid base64: {error}") from error
    total = 0
    for child in node.get(CHILDREN_KEY, {}).values():
        total += _node_size(child)
    return total


def _render_node(node: dict, prefix: str, lines: list[str]) -> None:
    """Рекурсивно формирует строки дерева VFS.

    Аргументы:
        node: Словарь узла для отрисовки.
        prefix: Строка отступа текущего уровня вложенности.
        lines: Список накопленных строк дерева.
    """
    for name, child in node.get(CHILDREN_KEY, {}).items():
        if child.get(TYPE_KEY) == DIR_TYPE:
            lines.append(f"{prefix}{name}/")
            _render_node(child, prefix + TREE_INDENT, lines)
        else:
            lines.append(f"{prefix}{name}")
