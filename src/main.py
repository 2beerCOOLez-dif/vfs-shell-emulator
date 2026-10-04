"""Главная точка входа эмулятора оболочки VFS."""
import sys
from pathlib import Path

from src.config import AppConfig, parse_args
from src.repl import run_repl
from src.script_runner import run_script
from src.vfs import VfsError, VirtualFileSystem

EXIT_ERROR_CODE = 1


def main() -> None:
    """Запускает эмулятор в режиме скрипта или интерактивном режиме."""
    config = parse_args()
    vfs = load_vfs_or_exit(config.vfs_path)
    print_debug_info(config, vfs)
    if config.script_path is not None:
        run_script_or_exit(config.script_path, vfs)
        return
    run_repl(vfs)


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


def print_debug_info(
    config: AppConfig,
    vfs: VirtualFileSystem | None,
) -> None:
    """Выводит отладочную информацию о параметрах запуска.

    Аргументы:
        config: Разобранные параметры командной строки.
        vfs: Загруженная виртуальная файловая система или None.
    """
    print("VFS Shell Emulator")
    print(f"VFS path: {config.vfs_path}")
    print(f"Script path: {config.script_path}")
    if vfs is not None:
        print(f"VFS name: {vfs.name}")
        print(f"VFS nodes: {vfs.count_nodes()}")


def run_script_or_exit(
    script_path: Path,
    vfs: VirtualFileSystem | None,
) -> None:
    """Выполняет стартовый скрипт, завершая программу при ошибке.

    Аргументы:
        script_path: Путь к файлу стартового скрипта.
        vfs: Загруженная виртуальная файловая система или None.
    """
    try:
        run_script(script_path, vfs)
    except FileNotFoundError as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(EXIT_ERROR_CODE)


if __name__ == "__main__":
    main()
