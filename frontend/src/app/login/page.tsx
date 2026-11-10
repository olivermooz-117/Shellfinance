import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Log in",
  description: "ShellFinance account access.",
  robots: {
    index: false,
    follow: false,
  },
};

export default function LoginPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-[#071521] px-6 py-16 text-white">
      <section className="w-full max-w-md rounded-3xl border border-white/10 bg-[#102536] p-8 shadow-2xl">
        <Link href="/" className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#19B78A] text-2xl font-bold text-[#071521]">
            S
          </span>
          <span className="text-xl font-bold">
            Shell<span className="text-[#19B78A]">Finance</span>
          </span>
        </Link>

        <h1 className="mt-10 text-3xl font-bold">Welcome back</h1>

        <p className="mt-4 leading-7 text-slate-400">
          Secure account authentication is currently under development.
          Login is not yet available.
        </p>

        <div className="mt-8 rounded-xl border border-[#19B78A]/20 bg-[#19B78A]/10 p-4">
          <p className="text-sm font-semibold text-[#42D9AE]">
            Authentication coming soon
          </p>
          <p className="mt-2 text-sm leading-6 text-slate-400">
            We are building the authentication and account security
            foundations before accepting personal financial information.
          </p>
        </div>

        <Link
          href="/"
          className="mt-8 block rounded-xl bg-[#19B78A] px-6 py-4 text-center font-semibold text-[#071521] transition hover:bg-[#28d4a4]"
        >
          Back to home
        </Link>
      </section>
    </main>
  );
}
