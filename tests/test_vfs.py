"""Тесты для модуля виртуальной файловой системы."""
import json
from pathlib import Path

import pytest

from src.vfs import (
    CHILDREN_KEY,
    CONTENT_KEY,
    DEFAULT_USER,
    DIR_TYPE,
    FILE_TYPE,
    NAME_KEY,
    ROOT_KEY,
    TYPE_KEY,
    USER_KEY,
    VfsError,
    VirtualFileSystem,
    copy_node,
    resolve_path,
)

TEST_VFS_NAME = "TestVFS"
TEST_USER = "tester"
TEST_FILE_A = "a.txt"
TEST_FILE_B = "b.txt"
TEST_DIR_SUB = "sub"
TEST_CONTENT_B64 = "aGk="
TEST_CONTENT_DECODED = "hi"
EXPECTED_NODE_COUNT = 4
EXPECTED_TOTAL_SIZE = 4
EXPECTED_SUB_SIZE = 2
EXPECTED_TREE_ROOT = "TestVFS/"
EXPECTED_TREE_SUB = "sub/"
MISSING_NODE_NAME = "nope"
MISSING_INNER_NAME = "inner"
MISSING_FILE_NAME = "missing.json"
BAD_JSON_FILE_NAME = "bad.json"
BAD_JSON_CONTENT = "{not json"
UNKNOWN_NODE_TYPE = "socket"
TEMP_VFS_FILE_NAME = "vfs.json"
ROOTED_HOME_USER = "/home/user"
DOCS_NAME = "docs"
PARENT_ETC_PATH = "../etc"
HOME_PARTS = ["home"]
HOME_USER_PARTS = ["home", "user"]
HOME_DOCS_PARTS = ["home", "docs"]
HOME_ETC_PARTS = ["home", "etc"]
EMPTY_PARTS: list[str] = []
COPY_TARGET_PARTS = ["sub", "copy.txt"]
MISSING_PARENT_PARTS = ["nope", "x.txt"]
NEW_FILE_NAME = "new.txt"
EMPTY_CONTENT_B64 = ""

MINIMAL_DATA = {
    NAME_KEY: TEST_VFS_NAME,
    USER_KEY: TEST_USER,
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


def test_resolve_absolute_and_relative():
    """Проверяет преобразование строк пути в компоненты."""
    first = resolve_path(ROOTED_HOME_USER, EMPTY_PARTS)
    assert first == HOME_USER_PARTS
    assert resolve_path(DOCS_NAME, HOME_PARTS) == HOME_DOCS_PARTS
    second = resolve_path(PARENT_ETC_PATH, HOME_USER_PARTS)
    assert second == HOME_ETC_PARTS


def test_subtree_size():
    """Проверяет вычисление размера поддерева."""
    vfs = VirtualFileSystem(MINIMAL_DATA)
    assert vfs.subtree_size(EMPTY_PARTS) == EXPECTED_TOTAL_SIZE
    assert vfs.subtree_size([TEST_DIR_SUB]) == EXPECTED_SUB_SIZE
    assert vfs.subtree_size([MISSING_NODE_NAME]) is None


def test_user_property():
    """Проверяет чтение имени пользователя из данных."""
    assert VirtualFileSystem(MINIMAL_DATA).user == TEST_USER
    assert VirtualFileSystem({}).user == DEFAULT_USER


def test_set_node_inserts_copy():
    """Проверяет вставку узла по указанному пути."""
    vfs = VirtualFileSystem(MINIMAL_DATA)
    node = copy_node(vfs.get_node([TEST_FILE_A]))
    assert vfs.set_node(COPY_TARGET_PARTS, node)
    assert vfs.get_node(COPY_TARGET_PARTS) is not None
    assert not vfs.set_node(MISSING_PARENT_PARTS, node)


def test_copy_node_independence():
    """Проверяет независимость копии от исходного узла."""
    vfs = VirtualFileSystem(MINIMAL_DATA)
    original = vfs.get_node([TEST_DIR_SUB])
    copied = copy_node(original)
    copied[CHILDREN_KEY][NEW_FILE_NAME] = {
        TYPE_KEY: FILE_TYPE,
        CONTENT_KEY: EMPTY_CONTENT_B64,
    }
    assert NEW_FILE_NAME not in original[CHILDREN_KEY]
