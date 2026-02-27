#!/usr/bin/env bash
# =============================================================================
#  noxaudit benchmark.sh — provider quality scorecard runner
#
#  Runs noxaudit across all provider × repo × focus tier combinations and
#  saves structured JSON results to benchmark/results/.
#
#  Usage:
#    ./scripts/benchmark.sh [options]
#
#  Options:
#    --dry-run          Show what would run without calling AI APIs
#    --skip-clone       Skip repo cloning (use existing benchmark/repos/)
#    --repo NAME        Only benchmark a specific repo (e.g. requests)
#    --model SPEC       Only benchmark a specific model (e.g. anthropic:claude-haiku-4-5)
#    --focus TIER       Only run a specific focus tier (security|does_it_work|all)
#    --runs N           Number of runs per combination (default: 2)
#    --help, -h         Show this help message
#
#  Prerequisites:
#    - noxaudit installed (uv run noxaudit or noxaudit in PATH)
#    - API keys set: ANTHROPIC_API_KEY, GEMINI_API_KEY, OPENAI_API_KEY
#    - git installed for repo cloning
#    - python3 for result post-processing
#
#  Output:
#    benchmark/results/<repo>/<provider>-<model>-<focus>-run<N>.json
#    Each JSON contains: findings, timing, token usage, cost
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
RESULTS_DIR="$REPO_ROOT/benchmark/results"
REPOS_DIR="$REPO_ROOT/benchmark/repos"

# ─── Benchmark corpus ────────────────────────────────────────────────────────
# Five repos covering size and quality spectrum
declare -A REPO_URLS
REPO_URLS["requests"]="https://github.com/psf/requests"        # Small, clean
REPO_URLS["black"]="https://github.com/psf/black"              # Small, messy (complex internals)
REPO_URLS["flask"]="https://github.com/pallets/flask"          # Medium, mixed quality
REPO_URLS["httpx"]="https://github.com/encode/httpx"           # Large, 300+ files
REPO_URLS["rich"]="https://github.com/Textualize/rich"         # Polyglot: Python + JS/TS docs

declare -A REPO_TAGS
REPO_TAGS["requests"]="small-clean"
REPO_TAGS["black"]="small-messy"
REPO_TAGS["flask"]="medium"
REPO_TAGS["httpx"]="large"
REPO_TAGS["rich"]="polyglot"

# Ordered repo list
ALL_REPOS=("requests" "black" "flask" "httpx" "rich")

# ─── Models to benchmark ─────────────────────────────────────────────────────
# Format: "provider:model" — 9 models across 3 providers
ALL_MODELS=(
    "anthropic:claude-haiku-4-5"
    "anthropic:claude-sonnet-4-6"
    "anthropic:claude-opus-4-6"
    "gemini:gemini-2.0-flash"
    "gemini:gemini-2.5-flash"
    "gemini:gemini-2.5-pro"
    "gemini:gemini-3-flash"
    "openai:gpt-5-mini"
    "openai:gpt-5.2"
)

# ─── Focus tiers ─────────────────────────────────────────────────────────────
ALL_FOCUS_TIERS=(
    "security"       # Single focus — most objective, easiest to judge true/false positives
    "does_it_work"   # Combined frame: security + testing — typical daily-use behavior
    "all"            # Full sweep: all 7 focus areas — max token pressure, cost ceiling
)

# ─── Defaults ────────────────────────────────────────────────────────────────
DRY_RUN=false
SKIP_CLONE=false
RUNS=2
REPO_FILTER=""
MODEL_FILTER=""
FOCUS_FILTER=""

# ─── Parse flags ─────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)    DRY_RUN=true ;;
        --skip-clone) SKIP_CLONE=true ;;
        --runs)       RUNS="$2"; shift ;;
        --repo)       REPO_FILTER="$2"; shift ;;
        --model)      MODEL_FILTER="$2"; shift ;;
        --focus)      FOCUS_FILTER="$2"; shift ;;
        --help|-h)
            sed -n '/^#/p' "$0" | sed 's/^# \?//' | sed 's/^#//'
            exit 0
            ;;
        *) echo "Unknown flag: $1" >&2; exit 1 ;;
    esac
    shift
done

# ─── Helpers ─────────────────────────────────────────────────────────────────
log()  { echo "[benchmark] $*"; }
info() { echo "  $*"; }
err()  { echo "[benchmark] ERROR: $*" >&2; }

# Slugify a model name for filesystem use: "claude-sonnet-4-6" → "claude-sonnet-4-6"
slug() { echo "$1" | tr '/' '-' | tr ':' '-' | tr '.' '-'; }

# Locate noxaudit binary
if command -v uv &>/dev/null && [[ -f "$REPO_ROOT/pyproject.toml" ]]; then
    NOXAUDIT="uv run --directory $REPO_ROOT noxaudit"
elif command -v noxaudit &>/dev/null; then
    NOXAUDIT="noxaudit"
else
    err "noxaudit not found. Install with: pip install noxaudit"
    exit 1
fi

# ─── Prerequisites check ─────────────────────────────────────────────────────
log "Checking prerequisites..."

if [[ "$DRY_RUN" == "false" ]]; then
    missing_keys=()
    [[ -z "${ANTHROPIC_API_KEY:-}" ]] && missing_keys+=("ANTHROPIC_API_KEY")
    [[ -z "${GEMINI_API_KEY:-}"    ]] && missing_keys+=("GEMINI_API_KEY")
    [[ -z "${OPENAI_API_KEY:-}"    ]] && missing_keys+=("OPENAI_API_KEY")

    if [[ ${#missing_keys[@]} -gt 0 ]]; then
        err "Missing API keys: ${missing_keys[*]}"
        err "Set them or use --dry-run to test without API calls"
        exit 1
    fi
fi

# ─── Directory setup ─────────────────────────────────────────────────────────
mkdir -p "$RESULTS_DIR" "$REPOS_DIR"

# ─── Apply filters ───────────────────────────────────────────────────────────
REPOS=("${ALL_REPOS[@]}")
MODELS=("${ALL_MODELS[@]}")
FOCUS_TIERS=("${ALL_FOCUS_TIERS[@]}")

if [[ -n "$REPO_FILTER" ]]; then
    REPOS=("$REPO_FILTER")
fi
if [[ -n "$MODEL_FILTER" ]]; then
    MODELS=("$MODEL_FILTER")
fi
if [[ -n "$FOCUS_FILTER" ]]; then
    FOCUS_TIERS=("$FOCUS_FILTER")
fi

# ─── Clone / update repos ────────────────────────────────────────────────────
if [[ "$SKIP_CLONE" == "false" ]]; then
    log "Cloning benchmark repos..."
    for repo_name in "${REPOS[@]}"; do
        repo_url="${REPO_URLS[$repo_name]}"
        repo_path="$REPOS_DIR/$repo_name"

        if [[ -d "$repo_path/.git" ]]; then
            info "$repo_name: already cloned, pulling latest..."
            git -C "$repo_path" pull --quiet --ff-only 2>/dev/null || \
                info "$repo_name: pull skipped (detached HEAD or conflicts)"
        else
            info "$repo_name: cloning from $repo_url..."
            git clone --quiet --depth=1 "$repo_url" "$repo_path"
        fi
    done
    log "Repos ready."
fi

# ─── Benchmark loop ──────────────────────────────────────────────────────────
TOTAL_RUNS=$(( ${#REPOS[@]} * ${#MODELS[@]} * ${#FOCUS_TIERS[@]} * RUNS ))
CURRENT_RUN=0
FAILED_RUNS=0
START_TIME=$(date +%s)

log "Starting benchmark: ${#REPOS[@]} repos × ${#MODELS[@]} models × ${#FOCUS_TIERS[@]} focus tiers × ${RUNS} runs = $TOTAL_RUNS total runs"
[[ "$DRY_RUN" == "true" ]] && log "(DRY RUN — no API calls)"
echo ""

for repo_name in "${REPOS[@]}"; do
    repo_path="$REPOS_DIR/$repo_name"
    repo_tag="${REPO_TAGS[$repo_name]}"
    results_repo_dir="$RESULTS_DIR/$repo_name"
    mkdir -p "$results_repo_dir"

    if [[ ! -d "$repo_path" ]] && [[ "$SKIP_CLONE" == "true" ]]; then
        err "Repo not found: $repo_path (remove --skip-clone to clone)"
        continue
    fi

    for model_spec in "${MODELS[@]}"; do
        provider="${model_spec%%:*}"
        model="${model_spec##*:}"
        model_slug="$(slug "$model")"

        for focus in "${FOCUS_TIERS[@]}"; do
            focus_slug="$(slug "$focus")"

            for run_num in $(seq 1 "$RUNS"); do
                CURRENT_RUN=$(( CURRENT_RUN + 1 ))
                result_file="$results_repo_dir/${provider}-${model_slug}-${focus_slug}-run${run_num}.json"

                log "[$CURRENT_RUN/$TOTAL_RUNS] $repo_name | $provider:$model | focus=$focus | run=$run_num"

                # Skip if result already exists (resume support)
                if [[ -f "$result_file" ]]; then
                    info "Already complete — skipping (delete to re-run)"
                    continue
                fi

                # Create isolated working directory for this run
                run_dir="$(mktemp -d)"
                trap "rm -rf '$run_dir'" EXIT

                # Write minimal noxaudit config for this run
                cat > "$run_dir/noxaudit.yml" <<YAML
repos:
  - name: ${repo_name}
    path: ${repo_path}
    provider_rotation: [${provider}]

schedule:
  monday: security
  tuesday: security
  wednesday: security
  thursday: security
  friday: security
  saturday: security
  sunday: security

model: ${model}

budget:
  max_per_run_usd: 5.00

decisions:
  path: ${run_dir}/.noxaudit/decisions.jsonl

reports_dir: ${run_dir}/.noxaudit/reports
YAML

                if [[ "$DRY_RUN" == "true" ]]; then
                    info "DRY RUN: would run noxaudit --focus $focus --provider $provider --model $model"
                    # Write a placeholder result
                    python3 - <<PYEOF
import json, time
result = {
    "repo": "$repo_name",
    "repo_tag": "$repo_tag",
    "provider": "$provider",
    "model": "$model",
    "focus": "$focus",
    "run_number": $run_num,
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "duration_seconds": 0,
    "exit_code": 0,
    "dry_run": True,
    "findings_count": 0,
    "high_severity_count": 0,
    "medium_severity_count": 0,
    "low_severity_count": 0,
    "input_tokens": 0,
    "output_tokens": 0,
    "cache_read_tokens": 0,
    "cost_usd": 0.0,
    "findings": [],
}
with open("$result_file", "w") as f:
    json.dump(result, f, indent=2)
print("  Placeholder written to $result_file")
PYEOF
                    continue
                fi

                # Time the run
                run_start=$(date +%s%3N)
                exit_code=0

                $NOXAUDIT \
                    --config "$run_dir/noxaudit.yml" \
                    run \
                    --repo "$repo_name" \
                    --focus "$focus" \
                    --provider "$provider" \
                    --model "$model" \
                    2>&1 | tee "$run_dir/noxaudit.log" || exit_code=$?

                run_end=$(date +%s%3N)
                duration_ms=$(( run_end - run_start ))
                duration_sec=$(python3 -c "print(round($duration_ms / 1000, 2))")

                if [[ $exit_code -ne 0 ]]; then
                    err "Run failed (exit $exit_code). Log: $run_dir/noxaudit.log"
                    FAILED_RUNS=$(( FAILED_RUNS + 1 ))
                fi

                # Collect results from the run's .noxaudit/ directory
                latest_findings="$run_dir/.noxaudit/latest-findings.json"
                cost_ledger="$run_dir/.noxaudit/cost-ledger.jsonl"

                # Merge findings + timing + cost into benchmark result JSON
                python3 - <<PYEOF
import json, os, sys

latest_findings_path = "$latest_findings"
cost_ledger_path = "$cost_ledger"
result_file = "$result_file"

# Load findings
findings_data = {}
if os.path.exists(latest_findings_path):
    try:
        findings_data = json.loads(open(latest_findings_path).read())
    except (json.JSONDecodeError, OSError):
        pass

findings = findings_data.get("findings", [])
findings_count = len(findings)
high_count = sum(1 for f in findings if f.get("severity") == "high")
medium_count = sum(1 for f in findings if f.get("severity") == "medium")
low_count = sum(1 for f in findings if f.get("severity") == "low")

# Load last cost ledger entry
ledger_entry = {}
if os.path.exists(cost_ledger_path):
    try:
        lines = [l.strip() for l in open(cost_ledger_path) if l.strip()]
        if lines:
            ledger_entry = json.loads(lines[-1])
    except (json.JSONDecodeError, OSError):
        pass

result = {
    "repo": "$repo_name",
    "repo_tag": "$repo_tag",
    "provider": "$provider",
    "model": "$model",
    "focus": "$focus",
    "run_number": $run_num,
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "duration_seconds": $duration_sec,
    "exit_code": $exit_code,
    "dry_run": False,
    "findings_count": findings_count,
    "high_severity_count": high_count,
    "medium_severity_count": medium_count,
    "low_severity_count": low_count,
    "input_tokens": ledger_entry.get("input_tokens", 0),
    "output_tokens": ledger_entry.get("output_tokens", 0),
    "cache_read_tokens": ledger_entry.get("cache_read_tokens", 0),
    "cost_usd": ledger_entry.get("cost_estimate_usd", 0.0),
    "findings": findings,
}

with open(result_file, "w") as f:
    json.dump(result, f, indent=2)

print(f"  Saved: {findings_count} findings, {result['duration_seconds']}s, \${result['cost_usd']:.4f}")
PYEOF

                # Clean up temp dir for this run
                trap - EXIT
                rm -rf "$run_dir"

                info "Done: $result_file"
            done
        done
    done
    echo ""
done

# ─── Summary ─────────────────────────────────────────────────────────────────
END_TIME=$(date +%s)
ELAPSED=$(( END_TIME - START_TIME ))
ELAPSED_MIN=$(( ELAPSED / 60 ))
ELAPSED_SEC=$(( ELAPSED % 60 ))

echo "════════════════════════════════════════════════════════════"
echo "  Benchmark complete"
echo "  Total runs:    $CURRENT_RUN / $TOTAL_RUNS"
echo "  Failed runs:   $FAILED_RUNS"
echo "  Elapsed:       ${ELAPSED_MIN}m ${ELAPSED_SEC}s"
echo "  Results dir:   $RESULTS_DIR"
echo ""
echo "  Next steps:"
echo "    uv run python scripts/benchmark_analyze.py"
echo "    cat benchmark/scorecard.md"
echo "════════════════════════════════════════════════════════════"
