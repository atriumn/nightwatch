"""Testing and coverage focus area."""

from __future__ import annotations

from noxaudit.focus.base import BaseFocus


class TestingFocus(BaseFocus):
    name = "testing"
    description = "Test coverage gaps, untested critical paths, flaky patterns, missing edge cases"

    def get_file_patterns(self) -> list[str]:
        return [
            # Test files
            "**/*.test.*",
            "**/*.spec.*",
            "**/__tests__/**",
            "**/test_*.py",
            "**/tests/**",
            "**/test/**",
            "**/*_test.dart",
            # Source code (to identify untested paths)
            "**/*.py",
            "**/*.ts",
            "**/*.tsx",
            "**/*.js",
            "**/*.jsx",
            "**/*.go",
            "**/*.rs",
            "**/*.dart",
            # Test config
            "**/jest.config.*",
            "**/vitest.config.*",
            "**/pytest.ini",
            "**/pyproject.toml",
            "**/setup.cfg",
            "**/.nycrc*",
            "**/coverage/**",
        ]

    def get_prompt(self) -> str:
        return self.get_prompt_from_file("testing")
