#!/usr/bin/env python3
"""Retrieve chunked benchmark batch results and compare to unchunked."""

from __future__ import annotations

import json
import sys
from difflib import SequenceMatcher
from pathlib import Path

from noxaudit.providers.openai import OpenAIProvider
from noxaudit.runner import _merge_findings


def load_findings_from_json(path: str) -> list[dict]:
    with open(path) as f:
        return json.load(f).get("findings", [])


def exact_jaccard(f1: list[dict], f2: list[dict]) -> float:
    ids1, ids2 = {f["id"] for f in f1}, {f["id"] for f in f2}
    inter = len(ids1 & ids2)
    union = len(ids1 | ids2)
    return inter / union if union else 0


def fuzzy_jaccard(f1: list[dict], f2: list[dict], threshold: float = 0.55) -> float:
    t1, t2 = [f["title"] for f in f1], [f["title"] for f in f2]
    matched, used = 0, set()
    for a in t1:
        for j, b in enumerate(t2):
            if j not in used and SequenceMatcher(None, a, b).ratio() >= threshold:
                matched += 1
                used.add(j)
                break
    union = len(t1) + len(t2) - matched
    return matched / union if union else 0


def main() -> None:
    pending_path = Path("benchmark/chunked-pending.json")
    if not pending_path.exists():
        print("No pending batches found. Run submit first.")
        sys.exit(1)

    pending = json.loads(pending_path.read_text())
    output_dir = Path("benchmark/results/noxaudit")
    provider = OpenAIProvider(model="gpt-5-mini")

    all_done = True

    for run_key in sorted(pending.keys()):
        run_num = int(run_key.replace("run", ""))
        out_path = output_dir / f"openai-gpt-5-mini-all-chunked-run{run_num}.json"
        if out_path.exists():
            print(f"[SKIP] {run_key} already retrieved")
            continue

        batches = pending[run_key]
        all_chunk_findings = []
        run_complete = True

        for batch_info in batches:
            bid = batch_info["batch_id"]
            chunk_num = batch_info["chunk"]
            try:
                result = provider.retrieve_batch(bid, default_focus=None)
            except Exception as exc:
                print(f"  {run_key} chunk {chunk_num}: ERROR ({exc})")
                all_chunk_findings.append([])
                continue

            if result["status"] != "ended":
                counts = result.get("request_counts", {})
                print(f"  {run_key} chunk {chunk_num}: still processing ({counts})")
                run_complete = False
                all_done = False
                break

            chunk_findings = result.get("findings", [])
            all_chunk_findings.append(chunk_findings)
            print(f"  {run_key} chunk {chunk_num}: {len(chunk_findings)} findings")

        if not run_complete:
            continue

        merged = _merge_findings(all_chunk_findings)
        record = {
            "meta": {
                "repo": "noxaudit",
                "provider": "openai",
                "model": "gpt-5-mini",
                "focus": "all",
                "run": run_num,
                "chunked": True,
                "chunk_size": 10,
            },
            "findings_count": len(merged),
            "findings": [f.to_dict() for f in merged],
        }
        out_path.write_text(json.dumps(record, indent=2))
        print(f"  {run_key}: {len(merged)} total findings -> {out_path}")

    if not all_done:
        print("\nSome batches still processing. Run again later.")
        return

    # Compare
    print("\n=== COMPARISON: Unchunked vs Chunked (GPT-5-mini) ===\n")
    unchunked = [
        load_findings_from_json(f"benchmark/results/noxaudit/openai-gpt-5-mini-all-run{i}.json")
        for i in range(1, 4)
    ]
    chunked = [
        load_findings_from_json(
            f"benchmark/results/noxaudit/openai-gpt-5-mini-all-chunked-run{i}.json"
        )
        for i in range(1, 4)
    ]

    pairs = [(0, 1), (0, 2), (1, 2)]

    print(f"{'':12} {'Avg findings':>14} {'Exact Jaccard':>15} {'Fuzzy Jaccard':>15}")
    print("-" * 58)

    ue, uf = [], []
    for i, j in pairs:
        ue.append(exact_jaccard(unchunked[i], unchunked[j]))
        uf.append(fuzzy_jaccard(unchunked[i], unchunked[j]))
    avg_uc = sum(len(f) for f in unchunked) / 3
    print(f"{'Unchunked':12} {avg_uc:14.0f} {sum(ue) / 3:15.3f} {sum(uf) / 3:15.3f}")

    ce, cf = [], []
    for i, j in pairs:
        ce.append(exact_jaccard(chunked[i], chunked[j]))
        cf.append(fuzzy_jaccard(chunked[i], chunked[j]))
    avg_ch = sum(len(f) for f in chunked) / 3
    print(f"{'Chunked':12} {avg_ch:14.0f} {sum(ce) / 3:15.3f} {sum(cf) / 3:15.3f}")


if __name__ == "__main__":
    main()
