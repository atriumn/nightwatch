"use client";

import { useState } from "react";

export function WaitlistForm() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [message, setMessage] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus("loading");

    try {
      const res = await fetch("/api/waitlist", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      if (res.ok) {
        setStatus("success");
        setMessage("You're on the list. We'll be in touch.");
        setEmail("");
      } else {
        const data = await res.json();
        setStatus("error");
        setMessage(data.error || "Something went wrong. Try again.");
      }
    } catch {
      setStatus("error");
      setMessage("Something went wrong. Try again.");
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex w-full max-w-md flex-col gap-3 sm:flex-row">
      <input
        type="email"
        required
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="you@company.com"
        disabled={status === "loading" || status === "success"}
        className="flex-1 rounded-lg border border-border bg-surface px-4 py-3 text-sm text-foreground placeholder:text-muted focus:border-purple focus:outline-none focus:ring-1 focus:ring-purple disabled:opacity-50"
      />
      <button
        type="submit"
        disabled={status === "loading" || status === "success"}
        className="rounded-lg bg-purple px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-purple-light disabled:opacity-50"
      >
        {status === "loading" ? "Joining..." : status === "success" ? "Joined" : "Join Waitlist"}
      </button>
      {message && (
        <p
          className={`absolute mt-14 text-sm ${status === "success" ? "text-teal" : "text-red-400"}`}
        >
          {message}
        </p>
      )}
    </form>
  );
}
