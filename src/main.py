"""Основная точка входа эмулятора оболочки VFS."""
from src.repl import run_repl


def main() -> None:
    """Запускает основную логику приложения."""
    run_repl()


if __name__ == "__main__":
    main()
