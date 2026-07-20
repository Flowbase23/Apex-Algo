import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { submitWaitlist } from "~/routes/api/waitlist";

export const Route = createFileRoute("/")({
  component: Home,
});

function Home() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<
    "idle" | "loading" | "success" | "error"
  >("idle");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) return;

    setStatus("loading");
    setMessage("");

    try {
      const result = await submitWaitlist({ email });

      if (!result.success) {
        throw new Error(result.error || "Something went wrong. Please try again.");
      }

      setStatus("success");
      setMessage("Thanks! You're on the list.");
      setEmail("");
    } catch (err) {
      setStatus("error");
      setMessage(
        err instanceof Error ? err.message : "Something went wrong. Please try again.",
      );
    }
  };

  return (
    <div className="min-h-dvh bg-gray-950">
      {/* Navigation */}
      <nav className="fixed top-0 z-50 w-full border-b border-white/5 bg-gray-950/80 backdrop-blur-lg">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-600 text-lg font-bold text-white">
              A
            </span>
            <span className="text-lg font-bold text-white">Apex Algo</span>
          </div>
          <div className="hidden items-center gap-8 text-sm font-medium text-gray-400 md:flex">
            <a href="#features" className="transition hover:text-white">
              Features
            </a>
            <a href="#how-it-works" className="transition hover:text-white">
              How It Works
            </a>
            <a href="#pricing" className="transition hover:text-white">
              Pricing
            </a>
            <a href="#contact" className="transition hover:text-white">
              Contact
            </a>
          </div>
          <a
            href="#contact"
            className="rounded-lg bg-emerald-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-500"
          >
            Get Early Access
          </a>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden pt-32 pb-24 sm:pb-32 sm:pt-40">
        <div className="bg-gradient-glow pointer-events-none absolute inset-0" />
        <div className="relative mx-auto max-w-7xl px-6 text-center">
          <div className="mx-auto mb-6 inline-flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-4 py-1.5 text-sm font-medium text-emerald-400">
            <span className="glow-dot h-1.5 w-1.5 rounded-full bg-emerald-400" />
            AI-Powered Trading Platform
          </div>
          <h1 className="mx-auto max-w-4xl text-4xl font-extrabold tracking-tight text-white sm:text-6xl lg:text-7xl">
            Trade Futures & Forex{" "}
            <span className="text-gradient">Without the Emotions</span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-gray-400 sm:text-xl">
            Apex Algo combines Random Forest & Neural Networks to execute disciplined,
            backtested trading strategies during daytime hours. No emotion. No guesswork.
            Just data-driven decisions.
          </p>
          <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <a
              href="#contact"
              className="rounded-xl bg-emerald-600 px-8 py-4 text-base font-semibold text-white shadow-lg shadow-emerald-600/25 transition hover:bg-emerald-500 hover:shadow-emerald-500/25"
            >
              Start Free Trial
            </a>
            <a
              href="#how-it-works"
              className="rounded-xl border border-white/10 bg-white/5 px-8 py-4 text-base font-semibold text-gray-300 transition hover:bg-white/10 hover:text-white"
            >
              See How It Works
            </a>
          </div>
          <div className="mt-16 grid grid-cols-2 gap-8 border-t border-white/5 pt-12 text-center sm:grid-cols-4">
            <div>
              <div className="text-2xl font-bold text-white sm:text-3xl">99.9%</div>
              <div className="mt-1 text-sm text-gray-500">Uptime SLA</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-white sm:text-3xl">5+</div>
              <div className="mt-1 text-sm text-gray-500">Years Backtested</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-white sm:text-3xl">3</div>
              <div className="mt-1 text-sm text-gray-500">Asset Classes</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-white sm:text-3xl">24/7</div>
              <div className="mt-1 text-sm text-gray-500">Infrastructure</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="border-t border-white/5 py-24">
        <div className="mx-auto max-w-7xl px-6">
          <div className="mx-auto max-w-2xl text-center">
            <span className="inline-flex items-center rounded-full border border-emerald-500/20 bg-emerald-500/10 px-4 py-1.5 text-sm font-medium text-emerald-400">
              Platform Features
            </span>
            <h2 className="mt-4 text-3xl font-bold tracking-tight text-white sm:text-4xl">
              Built for Serious Traders
            </h2>
            <p className="mt-4 text-gray-400">
              Every component of Apex Algo is engineered for reliability, performance,
              and risk management.
            </p>
          </div>
          <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <FeatureCard
              icon="🧠"
              title="Dual AI Models"
              description="Combines Random Forest for pattern recognition and Neural Networks for market prediction — two layers of analysis on every trade."
            />
            <FeatureCard
              icon="🔄"
              title="Full Backtesting Suite"
              description="Strategies are validated against years of historical data on NinjaTrader and QuantConnect before ever going live."
            />
            <FeatureCard
              icon="⚡"
              title="Real-Time Execution"
              description="Low-latency execution engine connects to your broker via FIX API, placing trades within milliseconds of signal generation."
            />
            <FeatureCard
              icon="🛡️"
              title="Risk-First Architecture"
              description="Automated drawdown limits, position sizing, and stop-loss management keep risk within predefined thresholds."
            />
            <FeatureCard
              icon="📊"
              title="Performance Dashboard"
              description="Real-time metrics: Sharpe ratio, win rate, drawdown, and P&L. Transparent reporting so you always know your exposure."
            />
            <FeatureCard
              icon="🔌"
              title="Broker Agnostic"
              description="Works with major futures and forex brokers. Connect your existing account — no migration or capital transfer needed."
            />
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="border-t border-white/5 py-24">
        <div className="mx-auto max-w-7xl px-6">
          <div className="mx-auto max-w-2xl text-center">
            <span className="inline-flex items-center rounded-full border border-emerald-500/20 bg-emerald-500/10 px-4 py-1.5 text-sm font-medium text-emerald-400">
              How It Works
            </span>
            <h2 className="mt-4 text-3xl font-bold tracking-tight text-white sm:text-4xl">
              From Setup to Automated Trading
            </h2>
            <p className="mt-4 text-gray-400">
              Get started in minutes. Our platform handles the complexity so you don't have to.
            </p>
          </div>
          <div className="mt-16 grid gap-8 md:grid-cols-4">
            <StepCard
              step="01"
              title="Connect"
              description="Link your broker account securely via API. All credentials are encrypted at rest and in transit."
            />
            <StepCard
              step="02"
              title="Configure"
              description="Select your risk tolerance, preferred markets, and strategy parameters. Our dashboard makes setup simple."
            />
            <StepCard
              step="03"
              title="Backtest"
              description="The system validates your strategy against 5+ years of market data. View projected Sharpe ratio and drawdown."
            />
            <StepCard
              step="04"
              title="Deploy"
              description="Go live with one click. The AI executes trades autonomously during daytime hours while you monitor via dashboard."
            />
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="border-t border-white/5 py-24">
        <div className="mx-auto max-w-7xl px-6">
          <div className="mx-auto max-w-2xl text-center">
            <span className="inline-flex items-center rounded-full border border-emerald-500/20 bg-emerald-500/10 px-4 py-1.5 text-sm font-medium text-emerald-400">
              Pricing
            </span>
            <h2 className="mt-4 text-3xl font-bold tracking-tight text-white sm:text-4xl">
              Plans for Every Trader
            </h2>
            <p className="mt-4 text-gray-400">
              Start with a free trial. Upgrade when you're ready for more markets and
              advanced features.
            </p>
          </div>
          <div className="mt-16 grid gap-8 lg:grid-cols-3">
            {/* Starter */}
            <div className="rounded-2xl border border-white/10 bg-gray-900/50 p-8 backdrop-blur">
              <h3 className="text-lg font-semibold text-white">Starter</h3>
              <p className="mt-1 text-sm text-gray-400">For individual traders</p>
              <div className="mt-6 flex items-baseline gap-1">
                <span className="text-4xl font-bold text-white">$49</span>
                <span className="text-gray-500">/month</span>
              </div>
              <ul className="mt-8 space-y-4">
                <li className="flex items-start gap-3 text-sm text-gray-300">
                  <span className="mt-0.5 text-emerald-400">✓</span>
                  Up to 2 markets
                </li>
                <li className="flex items-start gap-3 text-sm text-gray-300">
                  <span className="mt-0.5 text-emerald-400">✓</span>
                  Standard backtesting
                </li>
                <li className="flex items-start gap-3 text-sm text-gray-300">
                  <span className="mt-0.5 text-emerald-400">✓</span>
                  Real-time dashboard
                </li>
                <li className="flex items-start gap-3 text-sm text-gray-300">
                  <span className="mt-0.5 text-emerald-400">✓</span>
                  Email support
                </li>
              </ul>
              <a
                href="/getting-started?tier=starter"
                className="mt-8 block rounded-xl border border-white/10 bg-white/5 px-6 py-3 text-center text-sm font-semibold text-gray-300 transition hover:bg-white/10 hover:text-white"
              >
                Subscribe — $49/mo
              </a>
            </div>

            {/* Pro — Featured */}
            <div className="relative rounded-2xl border border-emerald-500/30 bg-gray-900/80 p-8 shadow-xl shadow-emerald-600/10 backdrop-blur">
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-emerald-600 px-4 py-1 text-xs font-semibold text-white">
                Most Popular
              </div>
              <h3 className="text-lg font-semibold text-white">Professional</h3>
              <p className="mt-1 text-sm text-gray-400">For active traders</p>
              <div className="mt-6 flex items-baseline gap-1">
                <span className="text-4xl font-bold text-white">$149</span>
                <span className="text-gray-500">/month</span>
              </div>
              <ul className="mt-8 space-y-4">
                <li className="flex items-start gap-3 text-sm text-gray-300">
                  <span className="mt-0.5 text-emerald-400">✓</span>
                  Up to 10 markets
                </li>
                <li className="flex items-start gap-3 text-sm text-gray-300">
                  <span className="mt-0.5 text-emerald-400">✓</span>
                  Advanced backtesting (5+ yrs)
                </li>
                <li className="flex items-start gap-3 text-sm text-gray-300">
                  <span className="mt-0.5 text-emerald-400">✓</span>
                  Real-time dashboard + alerts
                </li>
                <li className="flex items-start gap-3 text-sm text-gray-300">
                  <span className="mt-0.5 text-emerald-400">✓</span>
                  Priority support
                </li>
                <li className="flex items-start gap-3 text-sm text-gray-300">
                  <span className="mt-0.5 text-emerald-400">✓</span>
                  Custom strategy parameters
                </li>
              </ul>
              <a
                href="/getting-started?tier=pro"
                className="mt-8 block rounded-xl bg-emerald-600 px-6 py-3 text-center text-sm font-semibold text-white shadow-lg shadow-emerald-600/25 transition hover:bg-emerald-500"
              >
                Subscribe — $149/mo
              </a>
            </div>

            {/* Enterprise */}
            <div className="rounded-2xl border border-white/10 bg-gray-900/50 p-8 backdrop-blur">
              <h3 className="text-lg font-semibold text-white">Enterprise</h3>
              <p className="mt-1 text-sm text-gray-400">For funds & institutions</p>
              <div className="mt-6 flex items-baseline gap-1">
                <span className="text-4xl font-bold text-white">$499</span>
                <span className="text-gray-500">/month</span>
              </div>
              <ul className="mt-8 space-y-4">
                <li className="flex items-start gap-3 text-sm text-gray-300">
                  <span className="mt-0.5 text-emerald-400">✓</span>
                  All markets (unlimited)
                </li>
                <li className="flex items-start gap-3 text-sm text-gray-300">
                  <span className="mt-0.5 text-emerald-400">✓</span>
                  White-label dashboard
                </li>
                <li className="flex items-start gap-3 text-sm text-gray-300">
                  <span className="mt-0.5 text-emerald-400">✓</span>
                  Dedicated account manager
                </li>
                <li className="flex items-start gap-3 text-sm text-gray-300">
                  <span className="mt-0.5 text-emerald-400">✓</span>
                  API access
                </li>
                <li className="flex items-start gap-3 text-sm text-gray-300">
                  <span className="mt-0.5 text-emerald-400">✓</span>
                  Performance-based pricing available
                </li>
              </ul>
              <a
                href="/getting-started?tier=enterprise"
                className="mt-8 block rounded-xl border border-white/10 bg-white/5 px-6 py-3 text-center text-sm font-semibold text-gray-300 transition hover:bg-white/10 hover:text-white"
              >
                Subscribe — $499/mo
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Contact / Waitlist Section */}
      <section id="contact" className="border-t border-white/5 py-24">
        <div className="mx-auto max-w-3xl px-6 text-center">
          <div className="mx-auto mb-6 inline-flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-4 py-1.5 text-sm font-medium text-emerald-400">
            Get Early Access
          </div>
          <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
            Ready to Trade Smarter?
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-gray-400">
            Join the waitlist for early access. Be among the first to experience
            AI-powered, emotion-free trading.
          </p>
          <div className="mx-auto mt-10 max-w-md">
            <form
              className="flex flex-col gap-4 sm:flex-row"
              onSubmit={handleSubmit}
            >
              <div className="flex-1">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email"
                  required
                  disabled={status === "loading"}
                  className="w-full rounded-xl border border-white/10 bg-white/5 px-5 py-3.5 text-sm text-white placeholder-gray-500 outline-none transition focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/50 disabled:opacity-50"
                />
              </div>
              <button
                type="submit"
                disabled={status === "loading"}
                className="rounded-xl bg-emerald-600 px-6 py-3.5 text-sm font-semibold text-white shadow-lg shadow-emerald-600/25 transition hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {status === "loading" ? "Submitting..." : "Join Waitlist"}
              </button>
            </form>
            {message && (
              <p
                className={`mt-4 text-sm ${
                  status === "success" ? "text-emerald-400" : "text-red-400"
                }`}
              >
                {message}
              </p>
            )}
            {!message && (
              <p className="mt-4 text-xs text-gray-600">
                No spam. Unsubscribe anytime. By signing up you agree to our Terms of Service.
              </p>
            )}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 py-12">
        <div className="mx-auto max-w-7xl px-6">
          <div className="flex flex-col items-center justify-between gap-6 sm:flex-row">
            <div className="flex items-center gap-2">
              <span className="flex h-7 w-7 items-center justify-center rounded-md bg-emerald-600 text-xs font-bold text-white">
                A
              </span>
              <span className="text-sm font-semibold text-white">Apex Algo Trading</span>
            </div>
            <div className="flex gap-6 text-sm text-gray-500">
              <a href="#" className="transition hover:text-gray-300">
                Terms
              </a>
              <a href="#" className="transition hover:text-gray-300">
                Privacy
              </a>
              <a href="#" className="transition hover:text-gray-300">
                Docs
              </a>
            </div>
            <p className="text-sm text-gray-600">
              &copy; {new Date().getFullYear()} Apex Algo Trading. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

/* ── Reusable components ── */

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: string;
  title: string;
  description: string;
}) {
  return (
    <div className="group rounded-2xl border border-white/5 bg-gradient-card p-6 transition hover:border-emerald-500/20 hover:shadow-lg hover:shadow-emerald-600/5">
      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-500/10 text-xl">
        {icon}
      </div>
      <h3 className="mt-4 text-lg font-semibold text-white">{title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-gray-400">{description}</p>
    </div>
  );
}

function StepCard({
  step,
  title,
  description,
}: {
  step: string;
  title: string;
  description: string;
}) {
  return (
    <div className="relative text-center">
      <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-emerald-500/10 text-lg font-bold text-emerald-400">
        {step}
      </div>
      <div className="mt-4">
        <h3 className="text-lg font-semibold text-white">{title}</h3>
        <p className="mt-2 text-sm leading-relaxed text-gray-400">{description}</p>
      </div>
    </div>
  );
}
