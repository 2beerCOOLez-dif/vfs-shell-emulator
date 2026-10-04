"""Тесты для модуля команд эмулятора."""
from src.commands import (
    VFS_NOT_LOADED_MESSAGE,
    dispatch_command,
    execute_tree,
)
from src.vfs import VirtualFileSystem

SMALL_DATA = {
    "vfs_name": "TestVFS",
    "root": {
        "type": "dir",
        "children": {
            "a.txt": {"type": "file", "content": "aGk="},
        },
    },
}


def test_execute_tree_without_vfs():
    """Проверяет сообщение при незагруженной VFS."""
    assert execute_tree(None) == VFS_NOT_LOADED_MESSAGE


def test_execute_tree_with_vfs():
    """Проверяет вывод дерева при загруженной VFS."""
    vfs = VirtualFileSystem(SMALL_DATA)
    assert "a.txt" in execute_tree(vfs)


def test_dispatch_known_commands():
    """Проверяет маршрутизацию известных команд."""
    assert dispatch_command("ls", [], None).startswith("ls called")
    assert dispatch_command("cd", ["x"], None).startswith("cd called")


def test_dispatch_unknown_command():
    """Проверяет сообщение об неизвестной команде."""
    result = dispatch_command("boom", [], None)
    assert result == "Error: unknown command 'boom'"


def test_dispatch_tree_command():
    """Проверяет маршрутизацию команды tree."""
    vfs = VirtualFileSystem(SMALL_DATA)
    assert "a.txt" in dispatch_command("tree", [], vfs)
