"""Главная точка входа эмулятора оболочки VFS."""
import sys
from pathlib import Path

from src.config import AppConfig, parse_args
from src.repl import run_repl
from src.script_runner import run_script

EXIT_ERROR_CODE = 1


def main() -> None:
    """Запускает эмулятор в режиме скрипта или интерактивном режиме."""
    config = parse_args()
    print_debug_info(config)
    if config.script_path is not None:
        run_script_or_exit(config.script_path)
        return
    run_repl()


def print_debug_info(config: AppConfig) -> None:
    """Выводит отладочную информацию о заданных параметрах запуска."""
    print("VFS Shell Emulator")
    print(f"VFS path: {config.vfs_path}")
    print(f"Script path: {config.script_path}")


def run_script_or_exit(script_path: Path) -> None:
    """Выполняет стартовый скрипт, при ошибке завершает программу."""
    try:
        run_script(script_path)
    except FileNotFoundError as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(EXIT_ERROR_CODE)


if __name__ == "__main__":
    main()
