"""Base focus area."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from nightwatch.models import FileContent


# Max file size to include (skip large generated/vendored files)
MAX_FILE_SIZE = 50_000  # ~50KB


class BaseFocus(ABC):
    """Base class for audit focus areas."""

    name: str = "base"
    description: str = ""

    @abstractmethod
    def get_file_patterns(self) -> list[str]:
        """Return glob patterns for files to include."""
        ...

    @abstractmethod
    def get_prompt(self) -> str:
        """Return the system prompt for this focus area."""
        ...

    def gather_files(
        self,
        repo_path: str | Path,
        exclude_patterns: list[str] | None = None,
    ) -> list[FileContent]:
        """Gather files from repo matching this focus area's patterns."""
        repo = Path(repo_path)
        exclude = set(exclude_patterns or [])
        # Always exclude these
        exclude.update(["node_modules", ".git", "__pycache__", ".venv", "venv", "dist", "build"])

        files = []
        for pattern in self.get_file_patterns():
            for path in sorted(repo.glob(pattern)):
                if not path.is_file():
                    continue
                if path.stat().st_size > MAX_FILE_SIZE:
                    continue
                rel = str(path.relative_to(repo))
                if any(ex in rel for ex in exclude):
                    continue
                try:
                    content = path.read_text(errors="replace")
                    files.append(FileContent(path=rel, content=content))
                except (PermissionError, OSError):
                    continue

        return files

    def get_prompt_from_file(self, prompt_name: str) -> str:
        """Load a prompt template from the focus_prompts directory."""
        prompt_file = Path(__file__).parent.parent.parent / "focus_prompts" / f"{prompt_name}.md"
        if prompt_file.exists():
            return prompt_file.read_text()
        return self.get_prompt()
