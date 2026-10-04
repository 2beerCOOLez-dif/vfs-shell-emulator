"""Тесты для модуля выполнения стартовых скриптов."""
from pathlib import Path

import pytest

from src.script_runner import run_script
from src.shell import Shell


def _write_script(tmp_path: Path, content: str) -> Path:
    """Создаёт временный файл скрипта для тестов.

    Аргументы:
        tmp_path: Временный каталог, предоставляемый pytest.
        content: Содержимое файла скрипта.

    Возвращает:
        Путь к созданному файлу скрипта.
    """
    script = tmp_path / "test.sh"
    script.write_text(content, encoding="utf-8")
    return script


def test_run_script_with_comments(capsys, tmp_path):
    """Проверяет, что комментарии пропускаются при выполнении."""
    script = _write_script(tmp_path, "# THIS_IS_COMMENT\npwd\n")
    run_script(script, Shell())
    captured = capsys.readouterr()
    assert "my_vfs> pwd" in captured.out
    assert "# THIS_IS_COMMENT" not in captured.out


def test_run_script_with_exit(capsys, tmp_path):
    """Проверяет, что команда exit останавливает выполнение."""
    content = "pwd\nexit\npwd\n"
    script = _write_script(tmp_path, content)
    run_script(script, Shell())
    captured = capsys.readouterr()
    assert captured.out.count("my_vfs> pwd") == 1


def test_run_script_file_not_found():
    """Проверяет ошибку FileNotFoundError при отсутствии файла."""
    with pytest.raises(FileNotFoundError):
        run_script(Path("nonexistent.sh"), Shell())


def test_run_script_empty_file(capsys, tmp_path):
    """Проверяет, что пустой скрипт завершается без ошибок."""
    script = _write_script(tmp_path, "")
    run_script(script, Shell())
    captured = capsys.readouterr()
    assert "Script finished" in captured.out
