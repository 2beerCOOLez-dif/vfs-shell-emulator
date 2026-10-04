"""Модуль состояния сессии эмулятора."""
from src.vfs import DEFAULT_USER, VirtualFileSystem, resolve_path

DEFAULT_VFS_NAME = "my_vfs"
ROOT_DISPLAY = "/"
SLASH = "/"


class Shell:
    """Сессия эмулятора: ссылка на VFS и текущий каталог."""

    def __init__(self, vfs: VirtualFileSystem | None = None) -> None:
        """Создаёт сессию с необязательной виртуальной системой.

        Аргументы:
            vfs: Загруженная в память виртуальная система или None.
        """
        self._vfs = vfs
        self._cwd: list[str] = []

    @property
    def vfs(self) -> VirtualFileSystem | None:
        """Возвращает загруженную виртуальную систему или None."""
        return self._vfs

    @property
    def cwd(self) -> list[str]:
        """Возвращает копию компонентов текущего каталога."""
        return list(self._cwd)

    @property
    def prompt_name(self) -> str:
        """Возвращает имя виртуальной системы для приглашения."""
        if self._vfs is None:
            return DEFAULT_VFS_NAME
        return self._vfs.name

    @property
    def user(self) -> str:
        """Возвращает имя пользователя виртуальной системы."""
        if self._vfs is None:
            return DEFAULT_USER
        return self._vfs.user

    def chdir(self, parts: list[str]) -> None:
        """Устанавливает текущий каталог по списку компонентов.

        Аргументы:
            parts: Список компонентов пути от корня.
        """
        self._cwd = list(parts)

    def cwd_display(self) -> str:
        """Возвращает строковое представление текущего пути."""
        if not self._cwd:
            return ROOT_DISPLAY
        return SLASH + SLASH.join(self._cwd)

    def resolve(self, raw: str) -> list[str]:
        """Разрешает строку пути относительно текущего каталога.

        Аргументы:
            raw: Строка пути, абсолютного или относительного.

        Возвращает:
            Список компонентов пути.
        """
        return resolve_path(raw, self._cwd)
