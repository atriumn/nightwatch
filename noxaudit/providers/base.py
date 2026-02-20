"""Abstract base provider."""

from __future__ import annotations

from abc import ABC, abstractmethod

from noxaudit.models import FileContent, Finding


class BaseProvider(ABC):
    """Base class for AI providers."""

    name: str = "base"

    @abstractmethod
    def run_audit(
        self,
        files: list[FileContent],
        system_prompt: str,
        decision_context: str,
    ) -> list[Finding]:
        """Run an audit and return findings."""
        ...

    def get_last_usage(self) -> dict:
        """Return token usage from the last API call.

        Returns dict with keys: input_tokens, output_tokens, cache_read_tokens, cache_write_tokens.
        """
        return {
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
        }
