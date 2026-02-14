"""Anthropic (Claude) provider."""

from __future__ import annotations

import json
import os

import anthropic

from nightwatch.models import FileContent, Finding, Severity
from nightwatch.providers.base import BaseProvider

FINDING_SCHEMA = {
    "type": "object",
    "properties": {
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "severity": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                    },
                    "file": {"type": "string"},
                    "line": {"type": ["integer", "null"]},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "suggestion": {"type": ["string", "null"]},
                },
                "required": ["severity", "file", "title", "description"],
            },
        }
    },
    "required": ["findings"],
}


class AnthropicProvider(BaseProvider):
    name = "anthropic"

    def __init__(self, model: str = "claude-sonnet-4-5-20250929"):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def run_audit(
        self,
        files: list[FileContent],
        system_prompt: str,
        decision_context: str,
    ) -> list[Finding]:
        file_contents = self._format_files(files)

        user_message = f"""Review the following codebase files and report any findings.

{decision_context}

## Files

{file_contents}

Respond with a JSON object matching this schema:
```json
{json.dumps(FINDING_SCHEMA, indent=2)}
```

Return ONLY the JSON object, no other text."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )

        return self._parse_response(response)

    def _format_files(self, files: list[FileContent]) -> str:
        parts = []
        for f in files:
            parts.append(f"### `{f.path}`\n```\n{f.content}\n```")
        return "\n\n".join(parts)

    def _parse_response(self, response: anthropic.types.Message) -> list[Finding]:
        text = response.content[0].text

        # Extract JSON from response (handle markdown code blocks)
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]

        data = json.loads(text.strip())
        findings = []

        for f in data.get("findings", []):
            finding = Finding(
                id=self._make_finding_id(f),
                severity=Severity(f["severity"]),
                file=f["file"],
                line=f.get("line"),
                title=f["title"],
                description=f["description"],
                suggestion=f.get("suggestion"),
            )
            findings.append(finding)

        return findings

    def _make_finding_id(self, raw: dict) -> str:
        import hashlib

        key = f"{raw['file']}:{raw['title']}:{raw.get('line', '')}"
        return hashlib.sha256(key.encode()).hexdigest()[:12]
