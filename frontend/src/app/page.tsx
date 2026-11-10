import Link from "next/link";

const features = [
  {
    icon: "◈",
    title: "Personal Finance",
    description:
      "Bring your accounts, transactions, budgets and savings goals together in one intelligent workspace.",
  },
  {
    icon: "↗",
    title: "Smart Investing",
    description:
      "Explore investments, monitor portfolios and understand how your assets are performing.",
  },
  {
    icon: "✳",
    title: "AI Financial Intelligence",
    description:
      "Turn complex financial information into understandable insights and actionable guidance.",
  },
];

export default function Home() {
  return (
    <main className="min-h-screen overflow-hidden bg-[#071521] text-white">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6 lg:px-10">
        <Link href="/" className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#19B78A] text-2xl font-bold text-[#071521]">
            S
          </span>
          <span className="text-xl font-bold tracking-tight">
            Shell<span className="text-[#19B78A]">Finance</span>
          </span>
        </Link>

        <div className="hidden items-center gap-8 text-sm text-slate-300 md:flex">
          <a href="#features" className="transition hover:text-[#19B78A]">
            Features
          </a>
          <a href="#about" className="transition hover:text-[#19B78A]">
            About
          </a>
          <a href="#security" className="transition hover:text-[#19B78A]">
            Security
          </a>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/login"
            className="hidden rounded-lg px-4 py-2 text-sm text-slate-300 transition hover:text-white sm:block"
          >
            Log in
          </Link>
          <Link
            href="/register"
            className="rounded-lg bg-[#19B78A] px-5 py-3 text-sm font-semibold text-[#071521] transition hover:bg-[#28d4a4]"
          >
            Get started
          </Link>
        </div>
      </nav>

      <section className="relative mx-auto grid max-w-7xl items-center gap-16 px-6 py-24 lg:grid-cols-2 lg:px-10 lg:py-32">
        <div className="pointer-events-none absolute -left-40 top-10 h-96 w-96 rounded-full bg-[#19B78A]/10 blur-[120px]" />

        <div className="relative z-10">
          <div className="mb-8 inline-flex items-center gap-2 rounded-full border border-[#19B78A]/30 bg-[#19B78A]/10 px-4 py-2 text-xs font-medium text-[#42D9AE]">
            <span className="h-2 w-2 rounded-full bg-[#19B78A]" />
            A smarter way to manage your money
          </div>

          <h1 className="max-w-2xl text-5xl font-bold leading-[1.1] tracking-tight md:text-7xl">
            Your money.
            <br />
            Your future.
            <br />
            <span className="text-[#19B78A]">Your control.</span>
          </h1>

          <p className="mt-8 max-w-xl text-lg leading-8 text-slate-400">
            Take control of your financial life with intelligent money
            management, investment insights and a clearer picture of your
            financial future.
          </p>

          <div className="mt-10 flex flex-wrap gap-4">
            <Link
              href="/register"
              className="rounded-xl bg-[#19B78A] px-7 py-4 font-semibold text-[#071521] transition hover:-translate-y-1 hover:bg-[#28d4a4]"
            >
              Start your journey →
            </Link>

            <a
              href="#features"
              className="rounded-xl border border-white/10 px-7 py-4 font-semibold text-white transition hover:border-[#19B78A]/60"
            >
              Explore features
            </a>
          </div>

          <div className="mt-12 flex flex-wrap gap-6 text-sm text-slate-500">
            <span>✦ Financial clarity</span>
            <span>✦ Smarter decisions</span>
            <span>✦ Global vision</span>
          </div>
        </div>

        <div className="relative">
          <div className="absolute inset-0 rounded-full bg-[#19B78A]/10 blur-[100px]" />

          <div className="relative rounded-3xl border border-white/10 bg-[#102536]/90 p-6 shadow-2xl shadow-black/30 backdrop-blur-xl">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Financial overview</p>
                <h2 className="mt-1 text-xl font-semibold">
                  Your dashboard
                </h2>
              </div>
              <span className="rounded-xl bg-[#19B78A]/10 px-3 py-2 text-xs text-[#42D9AE]">
                Concept preview
              </span>
            </div>

            <div className="mt-8 rounded-2xl border border-white/5 bg-[#091B29] p-6">
              <p className="text-sm text-slate-400">
                Total financial position
              </p>
              <p className="mt-3 text-4xl font-bold tracking-tight">
                $24,850.00
              </p>
              <p className="mt-2 text-sm text-[#42D9AE]">
                Illustrative data · Not a live balance
              </p>

              <div className="mt-8 flex h-32 items-end gap-2">
                {[35, 48, 42, 65, 55, 76, 68, 90, 72, 100, 85, 110].map(
                  (height, index) => (
                    <div
                      key={index}
                      className="flex-1 rounded-t-md bg-gradient-to-t from-[#087B63] to-[#36D9AB]"
                      style={{ height: `${height}px` }}
                    />
                  )
                )}
              </div>
            </div>

            <div className="mt-4 grid grid-cols-2 gap-4">
              <div className="rounded-2xl border border-white/5 bg-[#091B29] p-5">
                <p className="text-sm text-slate-400">Investments</p>
                <p className="mt-3 text-2xl font-semibold">$18,500</p>
                <p className="mt-2 text-xs text-slate-500">
                  Illustrative allocation
                </p>
              </div>
              <div className="rounded-2xl border border-white/5 bg-[#091B29] p-5">
                <p className="text-sm text-slate-400">Savings</p>
                <p className="mt-3 text-2xl font-semibold">$6,350</p>
                <p className="mt-2 text-xs text-slate-500">
                  Illustrative allocation
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="features" className="border-t border-white/5 bg-[#091B29] px-6 py-24 lg:px-10">
        <div className="mx-auto max-w-7xl">
          <div className="max-w-2xl">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-[#19B78A]">
              Everything connected
            </p>
            <h2 className="mt-5 text-4xl font-bold tracking-tight md:text-5xl">
              A complete picture of your financial world.
            </h2>
            <p className="mt-5 leading-7 text-slate-400">
              One platform. Multiple financial tools. Better visibility into
              the decisions that shape your future.
            </p>
          </div>

          <div className="mt-14 grid gap-6 md:grid-cols-3">
            {features.map((feature) => (
              <article
                key={feature.title}
                className="rounded-2xl border border-white/10 bg-[#102536] p-8 transition duration-300 hover:-translate-y-2 hover:border-[#19B78A]/50"
              >
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-[#19B78A]/10 text-2xl text-[#19B78A]">
                  {feature.icon}
                </div>
                <h3 className="mt-7 text-xl font-semibold">
                  {feature.title}
                </h3>
                <p className="mt-4 leading-7 text-slate-400">
                  {feature.description}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section id="about" className="px-6 py-24 text-center lg:px-10">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-[#19B78A]">
          Built around your financial future
        </p>
        <h2 className="mx-auto mt-5 max-w-3xl text-4xl font-bold md:text-5xl">
          Make every financial decision count.
        </h2>
        <p className="mx-auto mt-6 max-w-2xl leading-8 text-slate-400">
          ShellFinance brings together the tools, information and intelligence
          you need to make more informed financial decisions.
        </p>
      </section>

      <section id="security" className="border-t border-white/10 bg-[#091B29] px-6 py-20 lg:px-10">
        <div className="mx-auto max-w-7xl">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-[#19B78A]">
            Security and privacy
          </p>
          <h2 className="mt-5 text-3xl font-bold">
            Security is part of the foundation.
          </h2>
          <p className="mt-5 max-w-3xl leading-8 text-slate-400">
            ShellFinance is currently in its foundation phase. Authentication,
            secure account management and financial-data protection are being
            developed before real user financial information is accepted.
          </p>
          <p className="mt-4 max-w-3xl text-sm leading-7 text-slate-500">
            Do not submit banking credentials or sensitive financial
            information through this demonstration website.
          </p>
        </div>
      </section>

      <footer className="border-t border-white/10 px-6 py-10 lg:px-10">
        <div className="mx-auto flex max-w-7xl flex-col justify-between gap-5 text-sm text-slate-500 md:flex-row">
          <p>© 2026 ShellFinance.</p>
          <p>Built for a more financially informed world.</p>
        </div>
      </footer>
    </main>
  );
}
