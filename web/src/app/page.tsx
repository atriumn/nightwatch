import Image from "next/image";
import { WaitlistForm } from "@/components/waitlist-form";

const features = [
  {
    title: "7 Focus Areas",
    description:
      "Security, patterns, docs, hygiene, performance, dependencies, and testing — each with specialized prompts tuned to find real issues.",
    icon: (
      <svg className="h-6 w-6 text-teal" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75m-3-7.036A11.959 11.959 0 0 1 3.598 6 11.99 11.99 0 0 0 3 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285Z" />
      </svg>
    ),
  },
  {
    title: "Decision Memory",
    description:
      "Record decisions on findings so they don't resurface. Decisions expire after 90 days or when the underlying file changes.",
    icon: (
      <svg className="h-6 w-6 text-teal" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 18v-5.25m0 0a6.01 6.01 0 0 0 1.5-.189m-1.5.189a6.01 6.01 0 0 1-1.5-.189m3.75 7.478a12.06 12.06 0 0 1-4.5 0m3.75 2.383a14.406 14.406 0 0 1-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 1 0-7.517 0c.85.493 1.509 1.333 1.509 2.316V18" />
      </svg>
    ),
  },
  {
    title: "Multi-Model Intelligence",
    description:
      "Different models catch different things. We pick the right model for each job — cheap daily scans, deep dives when it matters.",
    icon: (
      <svg className="h-6 w-6 text-teal" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 21 3 16.5m0 0L7.5 12M3 16.5h13.5m0-13.5L21 7.5m0 0L16.5 12M21 7.5H7.5" />
      </svg>
    ),
  },
  {
    title: "Costs Under Control",
    description:
      "$0.03 per daily audit. Batch API discounts, budget caps, and pre-pass optimization keep costs predictable.",
    icon: (
      <svg className="h-6 w-6 text-teal" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v12m-3-2.818.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
      </svg>
    ),
  },
];

const scorecard = [
  { model: "gpt-5-mini", findings: 39, cost: "$0.03", consensus: "5/6", tier: "Daily" },
  { model: "gpt-5.4", findings: 84, cost: "$0.26", consensus: "5/6", tier: "Deep dive" },
  { model: "claude-sonnet-4-6", findings: 78, cost: "$0.38", consensus: "6/6", tier: null },
  { model: "claude-opus-4-6", findings: 91, cost: "$0.65", consensus: "6/6", tier: "Premium" },
];

export default function Home() {
  return (
    <>
      {/* Hero */}
      <section className="relative flex min-h-screen flex-col items-center justify-center px-6 pt-16">
        <div className="pointer-events-none absolute inset-0 overflow-hidden">
          <video
            autoPlay
            loop
            muted
            playsInline
            className="absolute inset-0 h-full w-full object-cover opacity-60"
            poster="/lighthouse-far.png"
          >
            <source src="/lighthouse-far.mp4" type="video/mp4" />
          </video>
          <div className="absolute inset-0 bg-gradient-to-r from-background via-background/80 to-transparent" />
          <div className="absolute inset-0 bg-gradient-to-t from-background via-transparent to-background/60" />
        </div>

        <div className="relative z-10 mx-auto max-w-3xl text-center">
          <Image
            src="/logo.png"
            alt="Noxaudit"
            width={80}
            height={80}
            className="mx-auto mb-8"
            priority
          />
          <h1 className="mb-6 text-5xl font-bold leading-tight tracking-tight sm:text-6xl">
            Find real issues.
            <br />
            <span className="bg-gradient-to-r from-purple-light to-teal bg-clip-text text-transparent">
              Not noise.
            </span>
          </h1>
          <p className="mx-auto mb-10 max-w-xl text-lg leading-relaxed text-muted">
            Noxaudit runs nightly AI-powered audits across your codebase — security,
            patterns, docs, and more. It remembers what you&apos;ve reviewed so you only
            see what&apos;s new.
          </p>

          <div id="waitlist" className="relative flex justify-center">
            <WaitlistForm />
          </div>

          <p className="mt-16 text-sm text-muted">
            Open source &middot; MIT licensed &middot; $0.03/audit
          </p>
        </div>
      </section>

      {/* Features */}
      <section className="border-t border-border py-24">
        <div className="mx-auto max-w-5xl px-6">
          <h2 className="mb-4 text-center text-3xl font-bold tracking-tight">
            How it works
          </h2>
          <p className="mx-auto mb-16 max-w-2xl text-center text-muted">
            Noxaudit scans your codebase with focused AI prompts, filters against
            your decision history, and surfaces only genuinely new findings.
          </p>
          <div className="grid gap-8 sm:grid-cols-2">
            {features.map((feature) => (
              <div
                key={feature.title}
                className="rounded-xl border border-border bg-surface p-6 transition-colors hover:border-purple/30"
              >
                <div className="mb-4">{feature.icon}</div>
                <h3 className="mb-2 text-lg font-semibold">{feature.title}</h3>
                <p className="text-sm leading-relaxed text-muted">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benchmark preview */}
      <section className="border-t border-border py-24">
        <div className="mx-auto max-w-5xl px-6">
          <h2 className="mb-4 text-center text-3xl font-bold tracking-tight">
            Benchmarked, not guessed
          </h2>
          <p className="mx-auto mb-12 max-w-2xl text-center text-muted">
            We tested 10 models on real repos and measured what they actually find.
            Total spend: $2.13.
          </p>

          <div className="overflow-x-auto rounded-xl border border-border bg-surface">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-border text-muted">
                  <th className="px-6 py-4 font-medium">Model</th>
                  <th className="px-6 py-4 text-right font-medium">Findings</th>
                  <th className="px-6 py-4 text-right font-medium">Cost</th>
                  <th className="px-6 py-4 text-right font-medium">Consensus</th>
                  <th className="px-6 py-4 text-right font-medium">Tier</th>
                </tr>
              </thead>
              <tbody>
                {scorecard.map((row) => (
                  <tr key={row.model} className="border-b border-border last:border-0">
                    <td className="px-6 py-4 font-mono text-sm">{row.model}</td>
                    <td className="px-6 py-4 text-right">{row.findings}</td>
                    <td className="px-6 py-4 text-right text-teal">{row.cost}</td>
                    <td className="px-6 py-4 text-right">{row.consensus}</td>
                    <td className="px-6 py-4 text-right">
                      {row.tier && (
                        <span className="rounded-full bg-purple/15 px-3 py-1 text-xs font-medium text-purple-light">
                          {row.tier}
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="mt-6 text-center">
            <a
              href="/benchmark"
              className="text-sm text-purple-light transition-colors hover:text-purple"
            >
              See full benchmark results &rarr;
            </a>
          </p>
        </div>
      </section>

      {/* Bottom CTA */}
      <section className="border-t border-border py-24">
        <div className="mx-auto max-w-2xl px-6 text-center">
          <h2 className="mb-4 text-3xl font-bold tracking-tight">
            Ship with confidence
          </h2>
          <p className="mb-10 text-muted">
            Get nightly audits that catch what linters miss. Join the waitlist for
            early access to the hosted service.
          </p>
          <div className="relative flex justify-center">
            <WaitlistForm />
          </div>
        </div>
      </section>
    </>
  );
}
