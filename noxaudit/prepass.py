"""Pre-pass file classification to reduce audit costs."""

from __future__ import annotations

from noxaudit.models import FileClassification, FileContent, PrepassResult

# Classification prompt: asks provider to identify relevant files as "findings"
# so we can reuse the existing run_audit() interface without a new provider method.
CLASSIFICATION_PROMPT = """You are a file relevance classifier for a code audit tool.

Audit focus areas: {focus_names}

Review the provided files and identify which are relevant for auditing the specified focus areas.

For each file that IS relevant, output a finding with:
  - severity: "low"
  - title: "audit-relevant"
  - file: <exact file path as provided — do not change the path>
  - description: one-sentence reason why this file is worth auditing for {focus_names}

For files that are clearly NOT relevant (auto-generated files, lock files, binary build
artifacts, or configs completely unrelated to {focus_names}), omit them entirely.

When in doubt, INCLUDE the file. The goal is to filter only obviously irrelevant files
to reduce API costs — not to perform a detailed analysis."""


def build_classification_prompt(focus_names: list[str]) -> str:
    """Build the system prompt for pre-pass classification."""
    focus_str = ", ".join(focus_names)
    return CLASSIFICATION_PROMPT.format(focus_names=focus_str)


def run_prepass(
    files: list[FileContent],
    focus_names: list[str],
    provider,
) -> PrepassResult:
    """Run pre-pass classification to filter files before the main audit.

    Sends files to the provider with a lightweight classification prompt.
    Files that the provider marks as relevant (via findings) are retained;
    the rest are filtered out, reducing token cost for the main audit.

    Args:
        files: All files gathered for the audit.
        focus_names: Focus area names (e.g. ["security", "performance"]).
        provider: An initialised provider instance (AnthropicProvider, etc.).

    Returns:
        PrepassResult with classified files and counts.
    """
    if not files:
        return PrepassResult(classified=[], original_count=0, retained_count=0)

    print(f"  Pre-pass: classifying {len(files)} files for relevance...")
    prompt = build_classification_prompt(focus_names)

    # Run classification: the provider returns "findings" where each finding's
    # file field identifies a file the LLM considers relevant to the focus areas.
    classification_findings = provider.run_audit(files, prompt, "")

    # Collect relevant file paths from the classification findings
    relevant_paths = {f.file for f in classification_findings}

    # Build per-file classification results
    classified = []
    for fc in files:
        relevant = fc.path in relevant_paths
        reason = None
        if relevant:
            for finding in classification_findings:
                if finding.file == fc.path:
                    reason = finding.description
                    break
        classified.append(FileClassification(path=fc.path, relevant=relevant, reason=reason))

    retained_count = sum(1 for fc in classified if fc.relevant)
    print(f"  Pre-pass: {retained_count}/{len(files)} files retained for main audit")

    return PrepassResult(
        classified=classified,
        original_count=len(files),
        retained_count=retained_count,
    )
