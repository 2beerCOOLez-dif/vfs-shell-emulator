"""Тесты для модуля команд эмулятора."""
from src.commands import (
    VFS_NOT_LOADED_MESSAGE,
    dispatch_command,
)
from src.shell import Shell
from src.vfs import VirtualFileSystem
import base64
import copy

from src.vfs import (
    CHILDREN_KEY,
    CONTENT_KEY,
    FILE_TYPE,
    ROOT_KEY,
    TYPE_KEY,
)

HIDDEN_FILE_NAME = ".hidden"
EMPTY_CONTENT_B64 = ""
TEST_DIR_SUB = "sub"
BIG_FILE_NAME = "big.bin"
BIG_FILE_SIZE = 2048
BIG_FILE_BYTES = b"x"
EXPECTED_LONG_FILE_LINE = "- 2B a.txt"
EXPECTED_LONG_DIR_LINE = "d 2B sub/"
EXPECTED_LONG_HIDDEN_LINE = "- 0B .hidden"
EXPECTED_LONG_SUB_FILE = "- 2B b.txt"
EXPECTED_HUMAN_LINE = "2.0K big.bin"

SMALL_DATA = {
    "vfs_name": "TestVFS",
    "user": "tester",
    "root": {
        "type": "dir",
        "children": {
            HIDDEN_FILE_NAME: {
                "type": "file",
                "content": EMPTY_CONTENT_B64,
            },
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


def _make_shell_with_big_file() -> Shell:
    """Создаёт сессию с файлом размером 2 КиБ.

    Возвращает:
        Объект Shell с VFS, содержащей большой файл.
    """
    data = copy.deepcopy(SMALL_DATA)
    content = base64.b64encode(
        BIG_FILE_BYTES * BIG_FILE_SIZE
    ).decode()
    data[ROOT_KEY][CHILDREN_KEY][BIG_FILE_NAME] = {
        TYPE_KEY: FILE_TYPE,
        CONTENT_KEY: content,
    }
    return Shell(VirtualFileSystem(data))


def test_ls_hides_dot_files_by_default():
    """Проверяет, что скрытые файлы не видны без флага -a."""
    result = dispatch_command("ls", [], _make_shell())
    assert HIDDEN_FILE_NAME not in result


def test_ls_flag_a_shows_dot_files():
    """Проверяет показ скрытых файлов с флагом -a."""
    result = dispatch_command("ls", ["-a"], _make_shell())
    assert HIDDEN_FILE_NAME in result


def test_ls_flag_l_long_format():
    """Проверяет длинный формат вывода с флагом -l."""
    result = dispatch_command("ls", ["-l"], _make_shell())
    assert EXPECTED_LONG_FILE_LINE in result
    assert EXPECTED_LONG_DIR_LINE in result


def test_ls_flag_h_human_sizes():
    """Проверяет человекочитаемые размеры с флагами -lh."""
    shell = _make_shell_with_big_file()
    result = dispatch_command("ls", ["-lh"], shell)
    assert EXPECTED_HUMAN_LINE in result


def test_ls_combined_flags_la():
    """Проверяет сочетание флагов -l и -a."""
    result = dispatch_command("ls", ["-la"], _make_shell())
    assert EXPECTED_LONG_HIDDEN_LINE in result
    assert EXPECTED_LONG_FILE_LINE in result


def test_ls_flags_with_path():
    """Проверяет флаги вместе с путём до каталога."""
    shell = _make_shell()
    result = dispatch_command("ls", ["-l", TEST_DIR_SUB], shell)
    assert EXPECTED_LONG_SUB_FILE in result
