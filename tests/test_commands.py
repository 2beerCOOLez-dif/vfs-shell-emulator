"""Тесты для модуля команд эмулятора."""
from src.commands import (
    VFS_NOT_LOADED_MESSAGE,
    dispatch_command,
)
from src.shell import Shell
from src.vfs import VirtualFileSystem

SMALL_DATA = {
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


def _make_shell() -> Shell:
    """Создаёт сессию с загруженной тестовой VFS.

    Возвращает:
        Объект Shell с загруженной виртуальной системой.
    """
    return Shell(VirtualFileSystem(SMALL_DATA))


def test_ls_lists_children():
    """Проверяет вывод содержимого корневого каталога."""
    result = dispatch_command("ls", [], _make_shell())
    assert result == "a.txt\nsub"


def test_ls_missing_path():
    """Проверяет ошибку ls для несуществующего пути."""
    result = dispatch_command("ls", ["nope"], _make_shell())
    assert result == "Error: no such path: nope"


def test_ls_on_file_prints_name():
    """Проверяет, что ls для файла печатает его имя."""
    result = dispatch_command("ls", ["a.txt"], _make_shell())
    assert result == "a.txt"


def test_ls_without_vfs():
    """Проверяет сообщение ls при незагруженной VFS."""
    result = dispatch_command("ls", [], Shell())
    assert result == VFS_NOT_LOADED_MESSAGE


def test_cd_changes_cwd_and_pwd():
    """Проверяет смену каталога и вывод pwd."""
    shell = _make_shell()
    assert dispatch_command("cd", ["sub"], shell) == ""
    assert dispatch_command("pwd", [], shell) == "/sub"


def test_cd_missing_path():
    """Проверяет ошибку cd для несуществующего пути."""
    result = dispatch_command("cd", ["nope"], _make_shell())
    assert result == "Error: no such path: nope"


def test_cd_not_a_directory():
    """Проверяет ошибку cd при переходе в файл."""
    result = dispatch_command("cd", ["a.txt"], _make_shell())
    assert result == "Error: not a directory: a.txt"


def test_cd_without_args_returns_root():
    """Проверяет возврат cd без аргументов в корень."""
    shell = _make_shell()
    dispatch_command("cd", ["sub"], shell)
    dispatch_command("cd", [], shell)
    assert dispatch_command("pwd", [], shell) == "/"


def test_du_subtree_size():
    """Проверяет вычисление размера поддерева."""
    shell = _make_shell()
    assert dispatch_command("du", [], shell) == "4 bytes /"
    assert dispatch_command("du", ["sub"], shell) == "2 bytes sub"


def test_du_missing_path():
    """Проверяет ошибку du для несуществующего пути."""
    result = dispatch_command("du", ["nope"], _make_shell())
    assert result == "Error: no such path: nope"


def test_du_without_vfs():
    """Проверяет сообщение du при незагруженной VFS."""
    result = dispatch_command("du", [], Shell())
    assert result == VFS_NOT_LOADED_MESSAGE


def test_whoami_returns_user():
    """Проверяет вывод имени пользователя из VFS."""
    assert dispatch_command("whoami", [], _make_shell()) == "tester"


def test_dispatch_unknown_command():
    """Проверяет сообщение об неизвестной команде."""
    result = dispatch_command("boom", [], Shell())
    assert result == "Error: unknown command 'boom'"


def test_cp_file_to_new_name():
    """Проверяет копирование файла под новым именем."""
    shell = _make_shell()
    assert dispatch_command("cp", ["a.txt", "copy.txt"], shell) == ""
    assert "copy.txt" in dispatch_command("ls", [], shell)
    assert dispatch_command("du", [], shell) == "6 bytes /"


def test_cp_file_into_dir():
    """Проверяет копирование файла внутрь каталога."""
    shell = _make_shell()
    assert dispatch_command("cp", ["a.txt", "sub"], shell) == ""
    assert "a.txt" in dispatch_command("ls", ["sub"], shell)


def test_cp_dir_recursive():
    """Проверяет рекурсивное копирование каталога."""
    shell = _make_shell()
    assert dispatch_command("cp", ["sub", "copy"], shell) == ""
    assert "b.txt" in dispatch_command("ls", ["copy"], shell)


def test_cp_missing_source():
    """Проверяет ошибку cp при отсутствии источника."""
    result = dispatch_command("cp", ["nope", "x"], _make_shell())
    assert result == "Error: no such path: nope"


def test_cp_wrong_args_count():
    """Проверяет подсказку использования cp при одном аргументе."""
    result = dispatch_command("cp", ["a.txt"], _make_shell())
    assert result == "Usage: cp <source> <destination>"


def test_cp_dir_into_itself():
    """Проверяет запрет копирования каталога в самого себя."""
    result = dispatch_command("cp", ["sub", "sub"], _make_shell())
    assert result == "Error: cannot copy directory into itself: sub"


def test_cp_without_vfs():
    """Проверяет сообщение cp при незагруженной VFS."""
    result = dispatch_command("cp", ["a", "b"], Shell())
    assert result == VFS_NOT_LOADED_MESSAGE
