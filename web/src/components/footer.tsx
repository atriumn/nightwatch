import Link from "next/link";

export function Footer() {
  return (
    <footer className="border-t border-border py-12">
      <div className="mx-auto max-w-5xl px-6">
        <div className="flex flex-col items-center justify-between gap-6 sm:flex-row">
          <div className="text-sm text-muted">
            &copy; {new Date().getFullYear()} Atriumn. MIT License.
          </div>
          <div className="flex gap-6">
            <Link
              href="https://github.com/atriumn/noxaudit"
              className="text-sm text-muted transition-colors hover:text-foreground"
            >
              GitHub
            </Link>
            <Link
              href="https://docs.noxaudit.com"
              className="text-sm text-muted transition-colors hover:text-foreground"
            >
              Docs
            </Link>
            <Link
              href="mailto:hello@atriumn.com"
              className="text-sm text-muted transition-colors hover:text-foreground"
            >
              Contact
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
