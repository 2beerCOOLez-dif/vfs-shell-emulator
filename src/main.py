"""Главная точка входа эмулятора оболочки VFS."""
import sys
from pathlib import Path

from src.config import AppConfig, parse_args
from src.repl import run_repl
from src.script_runner import run_script
from src.shell import Shell
from src.vfs import VfsError, VirtualFileSystem

EXIT_ERROR_CODE = 1


def main() -> None:
    """Запускает эмулятор в режиме скрипта или интерактивном режиме."""
    config = parse_args()
    vfs = load_vfs_or_exit(config.vfs_path)
    shell = Shell(vfs)
    print_debug_info(config, shell)
    if config.script_path is not None:
        run_script_or_exit(config.script_path, shell)
        return
    run_repl(shell)


def load_vfs_or_exit(path: Path | None) -> VirtualFileSystem | None:
    """Загружает VFS в память, завершая программу при ошибке.

    Аргументы:
        path: Путь к JSON-файлу VFS или None, если он не задан.

    Возвращает:
        Объект VirtualFileSystem либо None, если путь не задан.
    """
    if path is None:
        return None
    try:
        return VirtualFileSystem.from_json(path)
    except VfsError as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(EXIT_ERROR_CODE)


def print_debug_info(config: AppConfig, shell: Shell) -> None:
    """Выводит отладочную информацию о параметрах запуска.

    Аргументы:
        config: Разобранные параметры командной строки.
        shell: Сессия эмулятора с загруженной VFS или пустая.
    """
    print("VFS Shell Emulator")
    print(f"VFS path: {config.vfs_path}")
    print(f"Script path: {config.script_path}")
    if shell.vfs is not None:
        print(f"VFS name: {shell.vfs.name}")
        print(f"VFS nodes: {shell.vfs.count_nodes()}")
        print(f"VFS user: {shell.vfs.user}")


def run_script_or_exit(script_path: Path, shell: Shell) -> None:
    """Выполняет стартовый скрипт, завершая программу при ошибке.

    Аргументы:
        script_path: Путь к файлу стартового скрипта.
        shell: Сессия эмулятора с загруженной VFS.
    """
    try:
        run_script(script_path, shell)
    except FileNotFoundError as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(EXIT_ERROR_CODE)


if __name__ == "__main__":
    main()
