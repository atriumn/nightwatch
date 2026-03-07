import Link from "next/link";
import Image from "next/image";

export function Header() {
  return (
    <header className="fixed top-0 z-50 w-full border-b border-border bg-background/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-5xl items-center justify-between px-6">
        <Link href="/" className="flex items-center gap-3">
          <Image src="/logo.png" alt="Noxaudit" width={32} height={32} />
          <span className="text-lg font-semibold tracking-tight">
            Noxaudit
          </span>
        </Link>
        <nav className="flex items-center gap-8">
          <Link
            href="/benchmark"
            className="text-sm text-muted transition-colors hover:text-foreground"
          >
            Benchmark
          </Link>
          <Link
            href="https://docs.noxaudit.com"
            className="text-sm text-muted transition-colors hover:text-foreground"
          >
            Docs
          </Link>
          <Link
            href="https://github.com/atriumn/noxaudit"
            className="text-sm text-muted transition-colors hover:text-foreground"
          >
            GitHub
          </Link>
          <Link
            href="/#waitlist"
            className="rounded-lg bg-purple px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-purple-light"
          >
            Join Waitlist
          </Link>
        </nav>
      </div>
    </header>
  );
}
