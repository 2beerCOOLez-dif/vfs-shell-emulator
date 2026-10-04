"""Тесты для модуля состояния сессии эмулятора."""
from src.shell import Shell
from src.vfs import VirtualFileSystem

SMALL_DATA = {
    "vfs_name": "TestVFS",
    "user": "tester",
    "root": {"type": "dir", "children": {}},
}


def test_prompt_name_without_vfs():
    """Проверяет имя приглашения без загруженной VFS."""
    assert Shell().prompt_name == "my_vfs"


def test_prompt_name_with_vfs():
    """Проверяет имя приглашения с загруженной VFS."""
    shell = Shell(VirtualFileSystem(SMALL_DATA))
    assert shell.prompt_name == "TestVFS"


def test_chdir_and_cwd_display():
    """Проверяет смену каталога и строковое представление пути."""
    shell = Shell()
    assert shell.cwd_display() == "/"
    shell.chdir(["home", "user"])
    assert shell.cwd_display() == "/home/user"
    assert shell.cwd == ["home", "user"]


def test_resolve_relative():
    """Проверяет разрешение относительного пути с '..'."""
    shell = Shell()
    shell.chdir(["home", "user"])
    assert shell.resolve("..") == ["home"]
    assert shell.resolve("/etc") == ["etc"]
