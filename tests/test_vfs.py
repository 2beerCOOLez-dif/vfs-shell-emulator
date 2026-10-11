"""Тесты для модуля виртуальной файловой системы."""
import json
from pathlib import Path

import pytest

from src.vfs import (
    CHILDREN_KEY,
    CONTENT_KEY,
    DIR_TYPE,
    FILE_TYPE,
    NAME_KEY,
    ROOT_KEY,
    TYPE_KEY,
    VfsError,
    VirtualFileSystem,
)

TEST_VFS_NAME = "TestVFS"
TEST_FILE_A = "a.txt"
TEST_FILE_B = "b.txt"
TEST_DIR_SUB = "sub"
TEST_CONTENT_B64 = "aGk="
TEST_CONTENT_DECODED = "hi"
EXPECTED_NODE_COUNT = 4
EXPECTED_TREE_ROOT = "TestVFS/"
EXPECTED_TREE_SUB = "sub/"
MISSING_NODE_NAME = "nope"
MISSING_INNER_NAME = "inner"
MISSING_FILE_NAME = "missing.json"
BAD_JSON_FILE_NAME = "bad.json"
BAD_JSON_CONTENT = "{not json"
UNKNOWN_NODE_TYPE = "socket"
TEMP_VFS_FILE_NAME = "vfs.json"

MINIMAL_DATA = {
    NAME_KEY: TEST_VFS_NAME,
    ROOT_KEY: {
        TYPE_KEY: DIR_TYPE,
        CHILDREN_KEY: {
            TEST_FILE_A: {
                TYPE_KEY: FILE_TYPE,
                CONTENT_KEY: TEST_CONTENT_B64,
            },
            TEST_DIR_SUB: {
                TYPE_KEY: DIR_TYPE,
                CHILDREN_KEY: {
                    TEST_FILE_B: {
                        TYPE_KEY: FILE_TYPE,
                        CONTENT_KEY: TEST_CONTENT_B64,
                    },
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
    path = tmp_path / TEMP_VFS_FILE_NAME
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_from_json_loads_name_and_nodes(tmp_path):
    """Проверяет загрузку имени и подсчёт узлов из файла."""
    vfs = VirtualFileSystem.from_json(
        _write_json(tmp_path, MINIMAL_DATA)
    )
    assert vfs.name == TEST_VFS_NAME
    assert vfs.count_nodes() == EXPECTED_NODE_COUNT


def test_get_node_finds_dir_and_file():
    """Проверяет поиск существующих каталога и файла."""
    vfs = VirtualFileSystem(MINIMAL_DATA)
    assert vfs.get_node([TEST_DIR_SUB])[TYPE_KEY] == DIR_TYPE
    assert vfs.get_node([TEST_FILE_A])[TYPE_KEY] == FILE_TYPE


def test_get_node_missing_paths():
    """Проверяет возврат None для несуществующих путей."""
    vfs = VirtualFileSystem(MINIMAL_DATA)
    assert vfs.get_node([MISSING_NODE_NAME]) is None
    assert vfs.get_node([TEST_FILE_A, MISSING_INNER_NAME]) is None


def test_from_json_missing_file():
    """Проверяет ошибку VfsError при отсутствии файла."""
    with pytest.raises(VfsError):
        VirtualFileSystem.from_json(Path(MISSING_FILE_NAME))


def test_from_json_bad_json(tmp_path):
    """Проверяет ошибку VfsError при некорректном JSON."""
    path = tmp_path / BAD_JSON_FILE_NAME
    path.write_text(BAD_JSON_CONTENT, encoding="utf-8")
    with pytest.raises(VfsError):
        VirtualFileSystem.from_json(path)


def test_invalid_node_type():
    """Проверяет ошибку VfsError при неизвестном типе узла."""
    bad = {
        ROOT_KEY: {TYPE_KEY: UNKNOWN_NODE_TYPE, CHILDREN_KEY: {}}
    }
    with pytest.raises(VfsError):
        VirtualFileSystem(bad)


def test_render_tree_contains_names():
    """Проверяет, что дерево содержит имена узлов."""
    tree = VirtualFileSystem(MINIMAL_DATA).render_tree()
    assert EXPECTED_TREE_ROOT in tree
    assert TEST_FILE_A in tree
    assert EXPECTED_TREE_SUB in tree


def test_decode_content():
    """Проверяет декодирование base64-содержимого файла."""
    vfs = VirtualFileSystem(MINIMAL_DATA)
    assert vfs.decode_content([TEST_FILE_A]) == TEST_CONTENT_DECODED


def test_decode_content_missing_file():
    """Проверяет ошибку VfsError при декодировании отсутствующего файла."""
    vfs = VirtualFileSystem(MINIMAL_DATA)
    with pytest.raises(VfsError):
        vfs.decode_content([MISSING_NODE_NAME])