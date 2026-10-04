"""Тесты для модуля виртуальной файловой системы."""
import json
from pathlib import Path

import pytest

from src.vfs import VfsError, VirtualFileSystem, resolve_path
MINIMAL_DATA = {
    "vfs_name": "TestVFS",
    "user": "tester",
    "root": {
        "type": "dir",
        "children": {
            "a.txt": {"type": "file", "content": "aGk="},
            "sub": {
                "type": "dir",
                "children": {
                    "b.txt": {"type": "file", "content": "aGk="},
                },
            },
        },
    },
}


def _write_json(tmp_path: Path, data: dict) -> Path:
    """Создаёт временный JSON-файл с данными VFS.

    Аргументы:
        tmp_path: Временный каталог, предоставляемый pytest.
        data: Словарь с описанием VFS.

    Возвращает:
        Путь к созданному JSON-файлу.
    """
    path = tmp_path / "vfs.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_from_json_loads_name_and_nodes(tmp_path):
    """Проверяет загрузку имени и подсчёт узлов из файла."""
    vfs = VirtualFileSystem.from_json(_write_json(tmp_path, MINIMAL_DATA))
    assert vfs.name == "TestVFS"
    assert vfs.count_nodes() == 4


def test_get_node_finds_dir_and_file():
    """Проверяет поиск существующих каталога и файла."""
    vfs = VirtualFileSystem(MINIMAL_DATA)
    assert vfs.get_node(["sub"])["type"] == "dir"
    assert vfs.get_node(["a.txt"])["type"] == "file"


def test_get_node_missing_paths():
    """Проверяет возврат None для несуществующих путей."""
    vfs = VirtualFileSystem(MINIMAL_DATA)
    assert vfs.get_node(["nope"]) is None
    assert vfs.get_node(["a.txt", "inner"]) is None


def test_from_json_missing_file():
    """Проверяет ошибку VfsError при отсутствии файла."""
    with pytest.raises(VfsError):
        VirtualFileSystem.from_json(Path("missing.json"))


def test_from_json_bad_json(tmp_path):
    """Проверяет ошибку VfsError при некорректном JSON."""
    path = tmp_path / "bad.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(VfsError):
        VirtualFileSystem.from_json(path)


def test_invalid_node_type():
    """Проверяет ошибку VfsError при неизвестном типе узла."""
    bad = {"root": {"type": "socket", "children": {}}}
    with pytest.raises(VfsError):
        VirtualFileSystem(bad)


def test_render_tree_contains_names():
    """Проверяет, что дерево содержит имена узлов."""
    tree = VirtualFileSystem(MINIMAL_DATA).render_tree()
    assert "TestVFS/" in tree
    assert "a.txt" in tree
    assert "sub/" in tree


def test_decode_content():
    """Проверяет декодирование base64-содержимого файла."""
    vfs = VirtualFileSystem(MINIMAL_DATA)
    assert vfs.decode_content(["a.txt"]) == "hi"


def test_decode_content_missing_file():
    """Проверяет ошибку VfsError при декодировании отсутствующего файла."""
    vfs = VirtualFileSystem(MINIMAL_DATA)
    with pytest.raises(VfsError):
        vfs.decode_content(["nope"])


def test_resolve_absolute_and_relative():
    """Проверяет преобразование строк пути в компоненты."""
    assert resolve_path("/home/user", []) == ["home", "user"]
    assert resolve_path("docs", ["home"]) == ["home", "docs"]
    assert resolve_path("../etc", ["home", "user"]) == ["home", "etc"]


def test_subtree_size():
    """Проверяет вычисление размера поддерева."""
    vfs = VirtualFileSystem(MINIMAL_DATA)
    assert vfs.subtree_size([]) == 4
    assert vfs.subtree_size(["sub"]) == 2
    assert vfs.subtree_size(["nope"]) is None


def test_user_property():
    """Проверяет чтение имени пользователя из данных."""
    assert VirtualFileSystem(MINIMAL_DATA).user == "tester"
    assert VirtualFileSystem({}).user == "guest"
