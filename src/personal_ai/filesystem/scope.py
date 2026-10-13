from pathlib import Path


class FilesystemAccessScope:
    """Define the explicitly authorized filesystem path boundary."""

    def __init__(self, authorized_roots: list[str | Path]) -> None:
        self._authorized_roots = tuple(
            Path(root).expanduser().resolve()
            for root in authorized_roots
        )

    @property
    def authorized_roots(self) -> tuple[Path, ...]:
        return self._authorized_roots

    def resolve_allowed_path(self, path: str | Path) -> Path | None:
        """Resolve a path once and return it only when it is in scope."""
        if not isinstance(path, (str, Path)):
            raise ValueError("path must be a string or Path")

        try:
            resolved_path = Path(path).expanduser().resolve()
        except (OSError, RuntimeError, ValueError):
            return None

        if any(
            self._is_within_root(resolved_path, root)
            for root in self._authorized_roots
        ):
            return resolved_path

        return None

    def is_allowed(self, path: str | Path) -> bool:
        return self.resolve_allowed_path(path) is not None

    @staticmethod
    def _is_within_root(path: Path, root: Path) -> bool:
        try:
            path.relative_to(root)
        except ValueError:
            return False
        return True
