"""Тесты для модуля команд эмулятора."""
import base64
import copy

from src.commands import (
    VFS_NOT_LOADED_MESSAGE,
    dispatch_command,
)
from src.shell import Shell
from src.vfs import (
    CHILDREN_KEY,
    CONTENT_KEY,
    DIR_TYPE,
    FILE_TYPE,
    NAME_KEY,
    ROOT_KEY,
    TYPE_KEY,
    USER_KEY,
    VirtualFileSystem,
)

TEST_VFS_NAME = "TestVFS"
TEST_USER = "tester"
TEST_FILE_A = "a.txt"
TEST_FILE_B = "b.txt"
TEST_DIR_SUB = "sub"
TEST_CONTENT_B64 = "aGk="
HIDDEN_FILE_NAME = ".hidden"
EMPTY_CONTENT_B64 = ""
BIG_FILE_NAME = "big.bin"
BIG_FILE_SIZE = 2048
BIG_FILE_BYTES = b"x"
NOPE_PATH = "nope"
BOOM_COMMAND = "boom"
EXPECTED_LS_DEFAULT = "a.txt\nsub"
EXPECTED_NO_PATH_NOPE = "Error: no such path: nope"
EXPECTED_NOT_A_DIR = "Error: not a directory: a.txt"
EXPECTED_LONG_FILE_LINE = "- 2B a.txt"
EXPECTED_LONG_DIR_LINE = "d 2B sub/"
EXPECTED_LONG_HIDDEN_LINE = "- 0B .hidden"
EXPECTED_LONG_SUB_FILE = "- 2B b.txt"
EXPECTED_HUMAN_LINE = "2.0K big.bin"
EXPECTED_DU_ROOT = "4 bytes /"
EXPECTED_DU_SUB = "2 bytes sub"
EXPECTED_DU_AFTER_COPY = "6 bytes /"
EXPECTED_ROOT_PATH = "/"
EXPECTED_SUB_PATH = "/sub"
EXPECTED_WHOAMI = "tester"
EXPECTED_UNKNOWN = "Error: unknown command 'boom'"
COPY_NAME = "copy.txt"
COPY_DIR_NAME = "copy"
CP_DEST_X = "x"
EXPECTED_CP_USAGE = "Usage: cp <source> <destination>"
EXPECTED_CP_INTO_ITSELF = (
    "Error: cannot copy directory into itself: sub"
)
CP_DUMMY_SOURCE = "a"
CP_DUMMY_DEST = "b"

SMALL_DATA = {
    NAME_KEY: TEST_VFS_NAME,
    USER_KEY: TEST_USER,
    ROOT_KEY: {
        TYPE_KEY: DIR_TYPE,
        CHILDREN_KEY: {
            TEST_FILE_A: {
                TYPE_KEY: FILE_TYPE,
                CONTENT_KEY: TEST_CONTENT_B64,
            },
            HIDDEN_FILE_NAME: {
                TYPE_KEY: FILE_TYPE,
                CONTENT_KEY: EMPTY_CONTENT_B64,
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


def _make_shell() -> Shell:
    """Создаёт сессию с загруженной тестовой VFS.

    Возвращает:
        Объект Shell с загруженной виртуальной системой.
    """
    return Shell(VirtualFileSystem(SMALL_DATA))


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


def test_ls_lists_children():
    """Проверяет вывод содержимого корневого каталога."""
    result = dispatch_command("ls", [], _make_shell())
    assert result == EXPECTED_LS_DEFAULT


def test_ls_missing_path():
    """Проверяет ошибку ls для несуществующего пути."""
    result = dispatch_command("ls", [NOPE_PATH], _make_shell())
    assert result == EXPECTED_NO_PATH_NOPE


def test_ls_on_file_prints_name():
    """Проверяет, что ls для файла печатает его имя."""
    result = dispatch_command("ls", [TEST_FILE_A], _make_shell())
    assert result == TEST_FILE_A


def test_ls_without_vfs():
    """Проверяет сообщение ls при незагруженной VFS."""
    result = dispatch_command("ls", [], Shell())
    assert result == VFS_NOT_LOADED_MESSAGE


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


def test_cd_changes_cwd_and_pwd():
    """Проверяет смену каталога и вывод pwd."""
    shell = _make_shell()
    assert dispatch_command("cd", [TEST_DIR_SUB], shell) == ""
    assert dispatch_command("pwd", [], shell) == EXPECTED_SUB_PATH


def test_cd_missing_path():
    """Проверяет ошибку cd для несуществующего пути."""
    result = dispatch_command("cd", [NOPE_PATH], _make_shell())
    assert result == EXPECTED_NO_PATH_NOPE


def test_cd_not_a_directory():
    """Проверяет ошибку cd при переходе в файл."""
    result = dispatch_command("cd", [TEST_FILE_A], _make_shell())
    assert result == EXPECTED_NOT_A_DIR


def test_cd_without_args_returns_root():
    """Проверяет возврат cd без аргументов в корень."""
    shell = _make_shell()
    dispatch_command("cd", [TEST_DIR_SUB], shell)
    dispatch_command("cd", [], shell)
    assert dispatch_command("pwd", [], shell) == EXPECTED_ROOT_PATH


def test_du_subtree_size():
    """Проверяет вычисление размера поддерева."""
    shell = _make_shell()
    assert dispatch_command("du", [], shell) == EXPECTED_DU_ROOT
    result = dispatch_command("du", [TEST_DIR_SUB], shell)
    assert result == EXPECTED_DU_SUB


def test_du_missing_path():
    """Проверяет ошибку du для несуществующего пути."""
    result = dispatch_command("du", [NOPE_PATH], _make_shell())
    assert result == EXPECTED_NO_PATH_NOPE


def test_du_without_vfs():
    """Проверяет сообщение du при незагруженной VFS."""
    result = dispatch_command("du", [], Shell())
    assert result == VFS_NOT_LOADED_MESSAGE


def test_whoami_returns_user():
    """Проверяет вывод имени пользователя из VFS."""
    result = dispatch_command("whoami", [], _make_shell())
    assert result == EXPECTED_WHOAMI


def test_dispatch_unknown_command():
    """Проверяет сообщение об неизвестной команде."""
    result = dispatch_command(BOOM_COMMAND, [], Shell())
    assert result == EXPECTED_UNKNOWN


def test_cp_file_to_new_name():
    """Проверяет копирование файла под новым именем."""
    shell = _make_shell()
    result = dispatch_command("cp", [TEST_FILE_A, COPY_NAME], shell)
    assert result == ""
    assert COPY_NAME in dispatch_command("ls", [], shell)
    assert dispatch_command("du", [], shell) == EXPECTED_DU_AFTER_COPY


def test_cp_file_into_dir():
    """Проверяет копирование файла внутрь каталога."""
    shell = _make_shell()
    result = dispatch_command("cp", [TEST_FILE_A, TEST_DIR_SUB], shell)
    assert result == ""
    ls_result = dispatch_command("ls", [TEST_DIR_SUB], shell)
    assert TEST_FILE_A in ls_result


def test_cp_dir_recursive():
    """Проверяет рекурсивное копирование каталога."""
    shell = _make_shell()
    result = dispatch_command("cp", [TEST_DIR_SUB, COPY_DIR_NAME], shell)
    assert result == ""
    ls_result = dispatch_command("ls", [COPY_DIR_NAME], shell)
    assert TEST_FILE_B in ls_result


def test_cp_missing_source():
    """Проверяет ошибку cp при отсутствии источника."""
    shell = _make_shell()
    result = dispatch_command("cp", [NOPE_PATH, CP_DEST_X], shell)
    assert result == EXPECTED_NO_PATH_NOPE


def test_cp_wrong_args_count():
    """Проверяет подсказку использования cp при одном аргументе."""
    result = dispatch_command("cp", [TEST_FILE_A], _make_shell())
    assert result == EXPECTED_CP_USAGE


def test_cp_dir_into_itself():
    """Проверяет запрет копирования каталога в самого себя."""
    shell = _make_shell()
    result = dispatch_command("cp", [TEST_DIR_SUB, TEST_DIR_SUB], shell)
    assert result == EXPECTED_CP_INTO_ITSELF


def test_cp_without_vfs():
    """Проверяет сообщение cp при незагруженной VFS."""
    args = [CP_DUMMY_SOURCE, CP_DUMMY_DEST]
    result = dispatch_command("cp", args, Shell())
    assert result == VFS_NOT_LOADED_MESSAGE
