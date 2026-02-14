"""Main audit runner / orchestrator."""

from __future__ import annotations

from datetime import datetime

from nightwatch.config import NightwatchConfig
from nightwatch.decisions import filter_findings, format_decision_context, load_decisions
from nightwatch.focus import FOCUS_AREAS
from nightwatch.models import AuditResult
from nightwatch.notifications.telegram import send_telegram
from nightwatch.providers.anthropic import AnthropicProvider
from nightwatch.reporter import format_notification, generate_report, save_report


PROVIDERS = {
    "anthropic": AnthropicProvider,
}


def run_audit(
    config: NightwatchConfig,
    repo_name: str | None = None,
    focus_name: str | None = None,
    provider_name: str | None = None,
    dry_run: bool = False,
) -> list[AuditResult]:
    """Run an audit for one or more repos.

    If repo_name is None, runs for all configured repos.
    If focus_name is None, uses today's scheduled focus.
    """
    focus_name = focus_name or config.get_today_focus()
    if focus_name == "off":
        print("Today is scheduled as off. Use --focus to override.")
        return []

    if focus_name not in FOCUS_AREAS:
        available = ", ".join(FOCUS_AREAS.keys())
        raise ValueError(f"Unknown focus area: {focus_name}. Available: {available}")

    repos = config.repos
    if repo_name:
        repos = [r for r in repos if r.name == repo_name]
        if not repos:
            raise ValueError(f"Unknown repo: {repo_name}")

    results = []
    for repo in repos:
        result = _audit_repo(
            config=config,
            repo=repo,
            focus_name=focus_name,
            provider_name=provider_name,
            dry_run=dry_run,
        )
        results.append(result)

    return results


def _audit_repo(config, repo, focus_name, provider_name, dry_run):
    """Run a single audit for one repo."""
    from nightwatch.config import RepoConfig

    repo: RepoConfig

    # Set up focus area
    focus = FOCUS_AREAS[focus_name]()
    print(f"[{repo.name}] Gathering files for {focus_name} audit...")
    files = focus.gather_files(repo.path, repo.exclude_patterns)
    print(f"[{repo.name}] Found {len(files)} files")

    if not files:
        print(f"[{repo.name}] No files to audit, skipping")
        return AuditResult(
            repo=repo.name,
            focus=focus_name,
            provider="none",
            timestamp=datetime.now().isoformat(),
        )

    # Load decisions
    decisions = load_decisions(config.decisions.path)
    decision_context = format_decision_context(decisions)

    # Get prompt
    prompt = focus.get_prompt()

    if dry_run:
        print(f"[{repo.name}] DRY RUN — would send {len(files)} files to provider")
        print(f"[{repo.name}] Prompt length: {len(prompt)} chars")
        print(f"[{repo.name}] Decision context: {len(decisions)} prior decisions")
        return AuditResult(
            repo=repo.name,
            focus=focus_name,
            provider="dry-run",
            timestamp=datetime.now().isoformat(),
        )

    # Set up provider
    pname = provider_name or config.get_provider_for_repo(repo.name)
    if pname not in PROVIDERS:
        raise ValueError(f"Unknown provider: {pname}. Available: {', '.join(PROVIDERS.keys())}")

    provider = PROVIDERS[pname](model=config.model)
    print(f"[{repo.name}] Running {focus_name} audit via {pname} ({config.model})...")

    # Run the audit
    findings = provider.run_audit(files, prompt, decision_context)
    print(f"[{repo.name}] Got {len(findings)} findings")

    # Filter against decisions
    new_findings, resolved_count = filter_findings(
        findings, decisions, repo.path, config.decisions.expiry_days
    )

    result = AuditResult(
        repo=repo.name,
        focus=focus_name,
        provider=pname,
        findings=findings,
        new_findings=new_findings,
        resolved_count=resolved_count,
        timestamp=datetime.now().isoformat(),
    )

    # Generate and save report
    report = generate_report(result)
    report_path = save_report(report, config.reports_dir, repo.name, focus_name)
    print(f"[{repo.name}] Report saved to {report_path}")

    # Send notifications
    for notif in config.notifications:
        if notif.channel == "telegram":
            msg = format_notification(result)
            send_telegram(msg, chat_id=notif.target)
            print(f"[{repo.name}] Telegram notification sent")

    return result
