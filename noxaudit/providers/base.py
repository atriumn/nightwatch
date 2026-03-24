"""Abstract base provider."""

from __future__ import annotations

import hashlib
import json
import re
import time
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

    def _poll_batch(
        self,
        batch_id: str,
        default_focus: str | None = None,
        poll_interval: int = 60,
        max_consecutive_errors: int = 5,
    ) -> list[Finding]:
        """Poll retrieve_batch until done, with retry on transient errors."""
        consecutive_errors = 0

        while True:
            try:
                result = self.retrieve_batch(batch_id, default_focus=default_focus)
                consecutive_errors = 0
            except Exception as e:
                consecutive_errors += 1
                if consecutive_errors >= max_consecutive_errors:
                    raise RuntimeError(
                        f"Batch poll failed {max_consecutive_errors} times "
                        f"consecutively for {self.name}: {e}"
                    ) from e
                backoff = 30 * consecutive_errors
                print(
                    f"  Poll error ({consecutive_errors}/"
                    f"{max_consecutive_errors}): {e} — retrying in {backoff}s"
                )
                time.sleep(backoff)
                continue

            if result["status"] == "ended":
                return result.get("findings", [])

            processing = result["request_counts"]["processing"]
            print(f"  Waiting... ({processing} processing)")
            time.sleep(poll_interval)

    @staticmethod
    def make_finding_id(raw: dict) -> str:
        """Generate a deterministic finding ID from finding metadata."""
        key = f"{raw['file']}:{raw['title']}:{raw.get('line', '')}"
        if raw.get("focus"):
            key = f"{raw['focus']}:{key}"
        return hashlib.sha256(key.encode()).hexdigest()[:12]

    @staticmethod
    def _safe_json_loads(text: str) -> dict:
        """Parse JSON from LLM output, handling common malformation issues."""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Fix invalid backslash escapes (e.g. \n inside already-quoted strings
        # that the LLM didn't properly escape)
        try:
            fixed = re.sub(r'(?<!\\)\\(?!["\\/bfnrtu])', r"\\\\", text)
            return json.loads(fixed)
        except (json.JSONDecodeError, re.error):
            pass

        # Fix unterminated strings by removing control characters
        try:
            cleaned = text.replace("\r\n", "\\n").replace("\r", "\\n")
            # Replace literal newlines inside JSON string values
            cleaned = re.sub(
                r'(?<=": ")(.*?)(?="[,}\]])',
                lambda m: m.group().replace("\n", "\\n"),
                cleaned,
                flags=re.DOTALL,
            )
            return json.loads(cleaned)
        except (json.JSONDecodeError, re.error):
            pass

        # Last resort: return empty findings
        return {"findings": []}
