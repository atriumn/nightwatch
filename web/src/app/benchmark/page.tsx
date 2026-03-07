import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Benchmark Results - Noxaudit",
  description:
    "10 models benchmarked on real repos. See which AI models actually find real issues vs. generate noise.",
};

const fullScorecard = [
  { model: "gpt-5-nano", dotenv: 4, noxaudit: 6, total: 10, cost: "$0.01", perFinding: "$0.001" },
  { model: "gpt-5-mini", dotenv: 15, noxaudit: 24, total: 39, cost: "$0.03", perFinding: "$0.001" },
  { model: "gemini-2.5-flash", dotenv: 18, noxaudit: 16, total: 34, cost: "$0.07", perFinding: "$0.002" },
  { model: "gemini-3-flash-preview", dotenv: 8, noxaudit: 10, total: 18, cost: "$0.10", perFinding: "$0.005" },
  { model: "claude-haiku-4-5", dotenv: 24, noxaudit: 15, total: 39, cost: "$0.11", perFinding: "$0.003" },
  { model: "o4-mini", dotenv: 8, noxaudit: 6, total: 14, cost: "$0.20", perFinding: "$0.014" },
  { model: "gpt-5.4", dotenv: 32, noxaudit: 52, total: 84, cost: "$0.26", perFinding: "$0.003" },
  { model: "gemini-2.5-pro", dotenv: 17, noxaudit: 21, total: 38, cost: "$0.33", perFinding: "$0.009" },
  { model: "claude-sonnet-4-6", dotenv: 30, noxaudit: 48, total: 78, cost: "$0.38", perFinding: "$0.005" },
  { model: "claude-opus-4-6", dotenv: 40, noxaudit: 51, total: 91, cost: "$0.65", perFinding: "$0.007" },
];

const quality = [
  { model: "claude-sonnet-4-6", consensus: "6/6", noise: "Low", cost: "$0.38", verdict: "Best precision" },
  { model: "gpt-5.4", consensus: "5/6", noise: "Low", cost: "$0.26", verdict: "Best mid-tier" },
  { model: "gpt-5-mini", consensus: "5/6", noise: "Low", cost: "$0.03", verdict: "Best daily value" },
  { model: "claude-opus-4-6", consensus: "6/6", noise: "Moderate", cost: "$0.65", verdict: "Most findings overall" },
  { model: "claude-haiku-4-5", consensus: "4/6", noise: "Moderate", cost: "$0.11", verdict: "Decent but pads with nits" },
  { model: "gemini-2.5-pro", consensus: "3/6", noise: "Low", cost: "$0.33", verdict: "Poor value vs gpt-5.4" },
  { model: "o4-mini", consensus: "3/6", noise: "Moderate", cost: "$0.20", verdict: "Reasoning tokens wasted" },
  { model: "gemini-2.5-flash", consensus: "2/6", noise: "Moderate", cost: "$0.07", verdict: "Misses too much" },
  { model: "gemini-3-flash-preview", consensus: "2/6", noise: "Low", cost: "$0.10", verdict: "Preview quality" },
  { model: "gpt-5-nano", consensus: "2/6", noise: "Low", cost: "$0.01", verdict: "Too shallow" },
];

const consensusIssues = [
  { issue: "get_cli_string shell injection risk", models: 8, verdict: "Genuine security concern" },
  { issue: "test_list uses builtin format instead of output_format", models: 6, verdict: "Actual code bug" },
  { issue: "Duplicate files (README/CHANGELOG/CONTRIBUTING in docs/)", models: 6, verdict: "Maintenance burden" },
  { issue: "Broken mkdocs link (empty href)", models: 5, verdict: "Broken documentation" },
  { issue: "Unpinned dev dependencies", models: 5, verdict: "Reproducibility issue" },
  { issue: "Incorrect pre-commit command (precommit vs pre-commit)", models: 4, verdict: "Wrong package name" },
];

const tiers = [
  { tier: "Daily", model: "gpt-5-mini", cost: "$0.03", rationale: "5/6 consensus issues, minimal noise, cheapest viable model" },
  { tier: "Deep dive", model: "gpt-5.4", cost: "$0.26", rationale: "84 findings total, beats Sonnet quality at 68% the cost" },
  { tier: "Premium", model: "claude-opus-4-6", cost: "$0.65", rationale: "Most findings overall, best for maximum depth" },
];

function Table({ children }: { children: React.ReactNode }) {
  return (
    <div className="overflow-x-auto rounded-xl border border-border bg-surface">
      <table className="w-full text-left text-sm">{children}</table>
    </div>
  );
}

function Th({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <th className={`px-5 py-3.5 font-medium text-muted ${className}`}>{children}</th>;
}

function Td({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <td className={`px-5 py-3.5 ${className}`}>{children}</td>;
}

export default function BenchmarkPage() {
  return (
    <div className="mx-auto max-w-5xl px-6 pb-24 pt-28">
      <h1 className="mb-4 text-4xl font-bold tracking-tight">Benchmark Results</h1>
      <p className="mb-12 max-w-2xl text-lg text-muted">
        We benchmarked 10 models on real repositories to understand which ones actually
        find real issues vs. generate noise. Total spend: $2.13.
      </p>

      {/* Methodology */}
      <section className="mb-16">
        <h2 className="mb-6 text-2xl font-semibold tracking-tight">Methodology</h2>
        <div className="rounded-xl border border-border bg-surface p-6">
          <ul className="space-y-2 text-sm text-muted">
            <li><strong className="text-foreground">Repos:</strong> python-dotenv (34 files, ~52K tokens) and noxaudit (88 files, ~126K tokens)</li>
            <li><strong className="text-foreground">Focus:</strong> All 7 areas (security, docs, patterns, testing, hygiene, dependencies, performance)</li>
            <li><strong className="text-foreground">Method:</strong> Batch API on all providers (50% discount), 1 run per model per repo</li>
            <li><strong className="text-foreground">Quality validation:</strong> Cross-model consensus — issues found by 4+ models are considered &quot;real&quot;</li>
          </ul>
        </div>
      </section>

      {/* Scorecard */}
      <section className="mb-16">
        <h2 className="mb-6 text-2xl font-semibold tracking-tight">Scorecard</h2>
        <Table>
          <thead>
            <tr className="border-b border-border">
              <Th>Model</Th>
              <Th className="text-right">dotenv</Th>
              <Th className="text-right">noxaudit</Th>
              <Th className="text-right">Total</Th>
              <Th className="text-right">Cost</Th>
              <Th className="text-right">$/finding</Th>
            </tr>
          </thead>
          <tbody>
            {fullScorecard.map((row) => (
              <tr key={row.model} className="border-b border-border last:border-0">
                <Td className="font-mono">{row.model}</Td>
                <Td className="text-right">{row.dotenv}</Td>
                <Td className="text-right">{row.noxaudit}</Td>
                <Td className="text-right font-semibold">{row.total}</Td>
                <Td className="text-right text-teal">{row.cost}</Td>
                <Td className="text-right text-muted">{row.perFinding}</Td>
              </tr>
            ))}
          </tbody>
        </Table>
      </section>

      {/* Consensus Issues */}
      <section className="mb-16">
        <h2 className="mb-4 text-2xl font-semibold tracking-tight">Quality Validation</h2>
        <p className="mb-6 text-sm text-muted">
          python-dotenv served as a canary — 6 confirmed real issues found by 4+ models out of 10.
        </p>
        <Table>
          <thead>
            <tr className="border-b border-border">
              <Th>Issue</Th>
              <Th className="text-right">Models</Th>
              <Th>Verdict</Th>
            </tr>
          </thead>
          <tbody>
            {consensusIssues.map((row) => (
              <tr key={row.issue} className="border-b border-border last:border-0">
                <Td className="font-mono text-xs">{row.issue}</Td>
                <Td className="text-right">{row.models}/10</Td>
                <Td className="text-muted">{row.verdict}</Td>
              </tr>
            ))}
          </tbody>
        </Table>
      </section>

      {/* Per-Model Quality */}
      <section className="mb-16">
        <h2 className="mb-6 text-2xl font-semibold tracking-tight">Per-Model Quality</h2>
        <Table>
          <thead>
            <tr className="border-b border-border">
              <Th>Model</Th>
              <Th className="text-right">Consensus</Th>
              <Th className="text-right">Noise</Th>
              <Th className="text-right">Cost</Th>
              <Th>Verdict</Th>
            </tr>
          </thead>
          <tbody>
            {quality.map((row) => (
              <tr key={row.model} className="border-b border-border last:border-0">
                <Td className="font-mono">{row.model}</Td>
                <Td className="text-right">{row.consensus}</Td>
                <Td className="text-right">{row.noise}</Td>
                <Td className="text-right text-teal">{row.cost}</Td>
                <Td className="font-medium">{row.verdict}</Td>
              </tr>
            ))}
          </tbody>
        </Table>
      </section>

      {/* Recommended Tiers */}
      <section className="mb-16">
        <h2 className="mb-6 text-2xl font-semibold tracking-tight">Recommended Tiers</h2>
        <Table>
          <thead>
            <tr className="border-b border-border">
              <Th>Tier</Th>
              <Th>Model</Th>
              <Th className="text-right">Cost/Run</Th>
              <Th>Rationale</Th>
            </tr>
          </thead>
          <tbody>
            {tiers.map((row) => (
              <tr key={row.tier} className="border-b border-border last:border-0">
                <Td>
                  <span className="rounded-full bg-purple/15 px-3 py-1 text-xs font-medium text-purple-light">
                    {row.tier}
                  </span>
                </Td>
                <Td className="font-mono">{row.model}</Td>
                <Td className="text-right text-teal">{row.cost}</Td>
                <Td className="text-muted">{row.rationale}</Td>
              </tr>
            ))}
          </tbody>
        </Table>
      </section>

      {/* Dropped Models */}
      <section>
        <h2 className="mb-6 text-2xl font-semibold tracking-tight">Dropped Models</h2>
        <div className="rounded-xl border border-border bg-surface p-6">
          <ul className="space-y-3 text-sm text-muted">
            <li>
              <strong className="text-foreground">o3:</strong> 0 findings on python-dotenv, 7 on noxaudit at $0.33. Reasoning tokens wasted on non-reasoning task. Removed.
            </li>
            <li>
              <strong className="text-foreground">gemini-2.0-flash:</strong> Deprecated. Returns errors in batch API.
            </li>
          </ul>
        </div>
        <p className="mt-6 text-xs text-muted">
          All costs include 50% batch API discount. Different models genuinely find different things — only 6 issues had cross-model consensus.
        </p>
      </section>
    </div>
  );
}
