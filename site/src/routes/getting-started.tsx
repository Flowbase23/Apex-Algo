import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { STRIPE_LINKS } from "~/lib/stripe";

export const Route = createFileRoute("/getting-started")({
  component: GettingStarted,
});

function GettingStarted() {
  const [activeStep, setActiveStep] = useState(0);

  const steps = [
    {
      title: "System Requirements",
      icon: "💻",
      content: (
        <div className="space-y-4 text-gray-300">
          <p>
            Before you begin, make sure your machine meets the minimum requirements
            to run the Apex Algo trading engine.
          </p>
          <div className="rounded-xl border border-white/10 bg-gray-900/60 p-6">
            <h4 className="mb-3 text-sm font-semibold text-white">Minimum Requirements</h4>
            <ul className="space-y-2 text-sm">
              <li className="flex items-start gap-2">
                <span className="mt-0.5 text-emerald-400">•</span>
                <span><strong className="text-white">Python 3.10+</strong> — the engine
                requires Python 3.10 or newer</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-0.5 text-emerald-400">•</span>
                <span><strong className="text-white">8 GB RAM</strong> recommended —
                backtesting large datasets is memory-intensive</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-0.5 text-emerald-400">•</span>
                <span><strong className="text-white">Git</strong> — to clone the repository</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-0.5 text-emerald-400">•</span>
                <span><strong className="text-white">macOS, Linux, or Windows (WSL2)</strong> —
                all major platforms are supported</span>
              </li>
            </ul>
          </div>
          <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4">
            <p className="text-sm text-emerald-300">
              <strong>💡 Tip:</strong> We recommend using a virtual environment
              (<code className="rounded bg-emerald-500/10 px-1.5 py-0.5 text-xs">python3 -m venv venv</code>)
              to keep dependencies isolated.
            </p>
          </div>
        </div>
      ),
    },
    {
      title: "Clone the Repo",
      icon: "📦",
      content: (
        <div className="space-y-4 text-gray-300">
          <p>
            Clone the Apex Algo repository from GitHub. This gives you the full trading
            engine source code and all configuration files.
          </p>
          <div className="rounded-xl border border-white/10 bg-gray-900/60 p-6">
            <h4 className="mb-3 text-sm font-semibold text-white">Clone Command</h4>
            <CodeBlock
              label="Terminal"
              code="git clone https://github.com/Flowbase23/Apex-Algo.git"
            />
            <p className="mt-4 text-sm text-gray-400">
              This creates an <code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">Apex-Algo/</code>{" "}
              directory with two subdirectories:
            </p>
            <ul className="mt-2 space-y-1 text-sm">
              <li className="flex items-start gap-2">
                <span className="mt-0.5 text-emerald-400">•</span>
                <span><code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">engine/</code> — the Python trading engine</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-0.5 text-emerald-400">•</span>
                <span><code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">site/</code> — this marketing website</span>
              </li>
            </ul>
          </div>
        </div>
      ),
    },
    {
      title: "Install Dependencies",
      icon: "📥",
      content: (
        <div className="space-y-4 text-gray-300">
          <p>
            Navigate into the engine directory and install all required Python packages.
            All dependencies are listed in <code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">requirements.txt</code>.
          </p>
          <div className="rounded-xl border border-white/10 bg-gray-900/60 p-6">
            <h4 className="mb-3 text-sm font-semibold text-white">Install Commands</h4>
            <CodeBlock
              label="Terminal"
              code="cd engine
pip install -r requirements.txt"
            />
          </div>
          <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4">
            <p className="text-sm text-emerald-300">
              <strong>📦 Included packages:</strong> Pandas, NumPy, scikit-learn (Random Forest),
              TensorFlow (Neural Networks), and broker SDKs for NinjaTrader and QuantConnect.
            </p>
          </div>
        </div>
      ),
    },
    {
      title: "Run the Demo",
      icon: "▶️",
      content: (
        <div className="space-y-4 text-gray-300">
          <p>
            Verify everything is installed correctly by running the built-in demo script.
            This will execute a sample backtest and confirm all components are working.
          </p>
          <div className="rounded-xl border border-white/10 bg-gray-900/60 p-6">
            <h4 className="mb-3 text-sm font-semibold text-white">Run Demo</h4>
            <CodeBlock
              label="Terminal"
              code="python demo.py"
            />
          </div>
          <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4">
            <p className="text-sm text-emerald-300">
              <strong>✅ Expected output:</strong> The demo runs a quick backtest on sample data
              and prints a performance summary including Sharpe ratio, win rate, and total return.
              If you see these metrics, your installation is ready.
            </p>
          </div>
        </div>
      ),
    },
    {
      title: "Configure Your Broker",
      icon: "🔑",
      content: (
        <div className="space-y-4 text-gray-300">
          <p>
            Add your broker API credentials so the engine can connect to your trading
            account. Edit the settings file to enter your keys.
          </p>
          <div className="rounded-xl border border-white/10 bg-gray-900/60 p-6">
            <h4 className="mb-3 text-sm font-semibold text-white">Broker Configuration</h4>
            <p className="mb-3 text-sm text-gray-400">
              Open <code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">config/settings.py</code>{" "}
              and fill in your broker credentials:
            </p>
            <CodeBlock
              label="config/settings.py"
              code={`# NinjaTrader API credentials
NINJATRADER_CLIENT_ID = "your-client-id"
NINJATRADER_CLIENT_SECRET = "your-client-secret"

# QuantConnect API credentials
QUANTCONNECT_USER_ID = "your-user-id"
QUANTCONNECT_API_TOKEN = "your-api-token"

# Market data provider (Alpha Vantage or Polygon)
DATA_PROVIDER = "polygon"  # or "alpha_vantage"
POLYGON_API_KEY = "your-polygon-key"
ALPHA_VANTAGE_API_KEY = "your-av-key"`}
            />
          </div>
          <div className="rounded-xl border border-yellow-500/20 bg-yellow-500/5 p-4">
            <p className="text-sm text-yellow-300">
              <strong>🔒 Security:</strong> Never commit <code className="rounded bg-yellow-500/10 px-1.5 py-0.5 text-xs">config/settings.py</code>{" "}
              with real credentials to version control. The file is already in{" "}
              <code className="rounded bg-yellow-500/10 px-1.5 py-0.5 text-xs">.gitignore</code>.
            </p>
          </div>
        </div>
      ),
    },
    {
      title: "Paper Trade First",
      icon: "🧪",
      content: (
        <div className="space-y-4 text-gray-300">
          <p>
            Always start with paper trading — simulated trades with virtual money.
            This validates your strategy under live market conditions with zero risk.
          </p>
          <div className="rounded-xl border border-white/10 bg-gray-900/60 p-6">
            <h4 className="mb-3 text-sm font-semibold text-white">Start Paper Trading</h4>
            <CodeBlock
              label="Python"
              code={`from paper_trading.simulator import PaperSimulator

sim = PaperSimulator(
    strategy="ensemble",
    markets=["ES", "NQ"],
    initial_capital=100000,
)
sim.run()`}
            />
          </div>
          <div className="rounded-xl border border-yellow-500/20 bg-yellow-500/5 p-4">
            <p className="text-sm text-yellow-300">
              <strong>⚠️ Important:</strong> Run paper trading for at least 2–4 weeks before
              going live. Monitor drawdown, win rate, and strategy behavior across
              different market conditions.
            </p>
          </div>
        </div>
      ),
    },
    {
      title: "Go Live",
      icon: "🚀",
      content: (
        <div className="space-y-4 text-gray-300">
          <p>
            When you're confident after paper trading, switch to live mode. The AI will
            execute trades autonomously during daytime hours using your broker connection.
          </p>
          <div className="rounded-xl border border-white/10 bg-gray-900/60 p-6">
            <h4 className="mb-3 text-sm font-semibold text-white">Live Trading</h4>
            <CodeBlock
              label="Terminal"
              code={`python trade.py --mode live \\
  --strategy ensemble \\
  --markets ES,NQ \\
  --risk-per-trade 1.0 \\
  --max-drawdown 5.0`}
            />
            <p className="mt-3 text-sm text-gray-400">
              Key flags explained:
            </p>
            <ul className="mt-2 space-y-1 text-sm">
              <li><code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">--risk-per-trade</code> — % of account risked per trade (default: 1.0%)</li>
              <li><code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">--max-drawdown</code> — auto-stop if drawdown exceeds this %</li>
              <li><code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">--trading-hours</code> — restrict to specific hours (e.g. 09:30-16:00)</li>
              <li><code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">--broker</code> — <code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">ninjatrader</code> or <code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">quantconnect</code></li>
            </ul>
          </div>
          <div className="rounded-xl border border-white/10 bg-gray-900/60 p-6">
            <h4 className="mb-3 text-sm font-semibold text-white">Supported Brokers</h4>
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="rounded-lg border border-white/5 bg-white/5 p-4">
                <h5 className="font-semibold text-white">NinjaTrader</h5>
                <p className="mt-1 text-xs text-gray-400">
                  Direct FIX API connection. Futures & forex supported. Configure via{" "}
                  <code className="rounded bg-white/5 px-1 py-0.5 text-xs">config/settings.py</code>.
                </p>
              </div>
              <div className="rounded-lg border border-white/5 bg-white/5 p-4">
                <h5 className="font-semibold text-white">QuantConnect</h5>
                <p className="mt-1 text-xs text-gray-400">
                  Cloud-based execution via LEAN engine. Multi-asset strategies supported.
                  Configure in <code className="rounded bg-white/5 px-1 py-0.5 text-xs">config/settings.py</code>.
                </p>
              </div>
            </div>
          </div>
        </div>
      ),
    },
  ];

  return (
    <div className="min-h-dvh bg-gray-950">
      {/* Navigation */}
      <nav className="fixed top-0 z-50 w-full border-b border-white/5 bg-gray-950/80 backdrop-blur-lg">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <a href="/" className="flex items-center gap-2">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-600 text-lg font-bold text-white">
              A
            </span>
            <span className="text-lg font-bold text-white">Apex Algo</span>
          </a>
          <div className="hidden items-center gap-8 text-sm font-medium text-gray-400 md:flex">
            <a href="/#features" className="transition hover:text-white">Features</a>
            <a href="/#how-it-works" className="transition hover:text-white">How It Works</a>
            <a href="/#pricing" className="transition hover:text-white">Pricing</a>
            <a href="/getting-started" className="text-emerald-400 transition hover:text-emerald-300">Getting Started</a>
          </div>
          <a
            href="/#pricing"
            className="rounded-lg bg-emerald-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-500"
          >
            View Plans
          </a>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative overflow-hidden pt-32 pb-16 sm:pt-40">
        <div className="bg-gradient-glow pointer-events-none absolute inset-0" />
        <div className="relative mx-auto max-w-4xl px-6 text-center">
          <div className="mx-auto mb-6 inline-flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-4 py-1.5 text-sm font-medium text-emerald-400">
            <span className="glow-dot h-1.5 w-1.5 rounded-full bg-emerald-400" />
            Setup Guide
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-5xl lg:text-6xl">
            Get Started with{" "}
            <span className="text-gradient">Apex Algo Trading</span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-gray-400">
            Follow this step-by-step guide to install, configure, and launch the Apex Algo
            trading engine on your local machine. From clone to live trading in under 30 minutes.
          </p>
        </div>
      </section>

      {/* Pricing CTA for new subscribers */}
      <section className="border-t border-white/5 py-12">
        <div className="mx-auto max-w-4xl px-6">
          <div className="rounded-2xl border border-emerald-500/20 bg-gradient-card p-8 text-center sm:p-12">
            <h2 className="text-2xl font-bold text-white sm:text-3xl">
              Don't Have a Subscription Yet?
            </h2>
            <p className="mt-3 text-gray-400">
              Choose a plan below to access the full trading engine. After payment you'll be
              redirected right back here to complete your setup.
            </p>
            <div className="mt-8 grid gap-4 sm:grid-cols-3">
              <a
                href={STRIPE_LINKS.starter}
                target="_blank"
                rel="noopener noreferrer"
                className="rounded-xl border border-white/10 bg-gray-900/60 px-6 py-4 text-center transition hover:border-emerald-500/30 hover:bg-gray-900/80"
              >
                <div className="text-lg font-bold text-white">Starter</div>
                <div className="mt-1 text-2xl font-bold text-emerald-400">$49<span className="text-sm text-gray-500">/mo</span></div>
                <div className="mt-2 text-xs text-gray-500">Up to 2 markets</div>
              </a>
              <a
                href={STRIPE_LINKS.pro}
                target="_blank"
                rel="noopener noreferrer"
                className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-6 py-4 text-center transition hover:border-emerald-500/50 hover:bg-emerald-500/15"
              >
                <div className="rounded-full bg-emerald-600 px-3 py-0.5 text-xs font-semibold text-white mx-auto inline-block mb-1">Most Popular</div>
                <div className="text-lg font-bold text-white">Professional</div>
                <div className="mt-1 text-2xl font-bold text-emerald-400">$149<span className="text-sm text-gray-500">/mo</span></div>
                <div className="mt-2 text-xs text-gray-500">Up to 10 markets</div>
              </a>
              <a
                href={STRIPE_LINKS.enterprise}
                target="_blank"
                rel="noopener noreferrer"
                className="rounded-xl border border-white/10 bg-gray-900/60 px-6 py-4 text-center transition hover:border-emerald-500/30 hover:bg-gray-900/80"
              >
                <div className="text-lg font-bold text-white">Enterprise</div>
                <div className="mt-1 text-2xl font-bold text-emerald-400">$499<span className="text-sm text-gray-500">/mo</span></div>
                <div className="mt-2 text-xs text-gray-500">All markets, unlimited</div>
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Step-by-step setup */}
      <section className="border-t border-white/5 py-16">
        <div className="mx-auto max-w-4xl px-6">
          <div className="mb-12 text-center">
            <h2 className="text-2xl font-bold text-white sm:text-3xl">
              Quick Start Steps
            </h2>
            <p className="mt-3 text-gray-400">
              Already subscribed? Follow the steps below to get the engine running.
            </p>
          </div>

          {/* Step navigation */}
          <div className="mb-10 overflow-x-auto">
            <div className="flex min-w-max gap-2 rounded-xl border border-white/5 bg-gray-900/50 p-1.5">
              {steps.map((step, i) => (
                <button
                  key={i}
                  onClick={() => setActiveStep(i)}
                  className={`flex items-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium transition ${
                    i === activeStep
                      ? "bg-emerald-600 text-white shadow-lg shadow-emerald-600/25"
                      : "text-gray-400 hover:bg-white/5 hover:text-white"
                  }`}
                >
                  <span>{step.icon}</span>
                  <span className="hidden sm:inline">{i + 1}. {step.title}</span>
                  <span className="sm:hidden">{step.title}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Active step content */}
          <div className="rounded-2xl border border-white/10 bg-gray-900/50 p-6 backdrop-blur sm:p-8">
            <div className="mb-6 flex items-center gap-3">
              <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500/10 text-xl">
                {steps[activeStep].icon}
              </span>
              <div>
                <span className="text-xs font-medium text-emerald-400">
                  Step {activeStep + 1} of {steps.length}
                </span>
                <h3 className="text-xl font-bold text-white">{steps[activeStep].title}</h3>
              </div>
            </div>
            {steps[activeStep].content}
          </div>

          {/* Step navigation buttons */}
          <div className="mt-6 flex items-center justify-between">
            <button
              onClick={() => setActiveStep(Math.max(0, activeStep - 1))}
              disabled={activeStep === 0}
              className="rounded-lg border border-white/10 px-4 py-2.5 text-sm font-medium text-gray-400 transition hover:border-white/20 hover:text-white disabled:cursor-not-allowed disabled:opacity-30"
            >
              ← Previous
            </button>
            <span className="text-sm text-gray-600">
              {activeStep + 1} / {steps.length}
            </span>
            <button
              onClick={() => setActiveStep(Math.min(steps.length - 1, activeStep + 1))}
              disabled={activeStep === steps.length - 1}
              className="rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-30"
            >
              Next →
            </button>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="border-t border-white/5 py-16">
        <div className="mx-auto max-w-4xl px-6">
          <div className="mb-10 text-center">
            <h2 className="text-2xl font-bold text-white sm:text-3xl">
              Frequently Asked Questions
            </h2>
            <p className="mt-3 text-gray-400">
              Quick answers to common questions about setup and trading.
            </p>
          </div>
          <div className="space-y-4">
            <details className="group rounded-xl border border-white/10 bg-gray-900/50">
              <summary className="cursor-pointer px-6 py-4 text-sm font-medium text-white transition hover:text-emerald-400">
                How do I connect my broker?
              </summary>
              <div className="border-t border-white/5 px-6 py-4 text-sm text-gray-400 space-y-3">
                <p>
                  Open <code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">config/settings.py</code>{" "}
                  and add your broker API credentials:
                </p>
                <ul className="space-y-1">
                  <li className="flex items-start gap-2">
                    <span className="mt-0.5 text-emerald-400">•</span>
                    <span><strong className="text-white">NinjaTrader:</strong> Set{" "}
                    <code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">NINJATRADER_CLIENT_ID</code> and{" "}
                    <code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">NINJATRADER_CLIENT_SECRET</code></span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-0.5 text-emerald-400">•</span>
                    <span><strong className="text-white">QuantConnect:</strong> Set{" "}
                    <code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">QUANTCONNECT_USER_ID</code> and{" "}
                    <code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">QUANTCONNECT_API_TOKEN</code></span>
                  </li>
                </ul>
                <p>
                  You must also enable API trading in your broker's account settings.
                  Test the connection with:{" "}
                  <code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">python trade.py --mode test-connection --broker ninjatrader</code>
                </p>
              </div>
            </details>
            <details className="group rounded-xl border border-white/10 bg-gray-900/50">
              <summary className="cursor-pointer px-6 py-4 text-sm font-medium text-white transition hover:text-emerald-400">
                Can I trade multiple markets?
              </summary>
              <div className="border-t border-white/5 px-6 py-4 text-sm text-gray-400 space-y-3">
                <p>
                  Yes! The engine supports multiple futures and forex markets simultaneously.
                  Simply list them in the <code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">--markets</code> flag:
                </p>
                <CodeBlock
                  code="python trade.py --mode live --markets ES,NQ,CL,GC,6E"
                />
                <p>
                  Supported symbols include: <strong>ES</strong> (S&P 500), <strong>NQ</strong> (Nasdaq),
                  <strong> CL</strong> (Crude Oil), <strong>GC</strong> (Gold), <strong>6E</strong> (Euro FX),
                  and more. See <code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">config/markets.py</code>{" "}
                  for the full list.
                </p>
                <p>
                  The number of markets you can trade simultaneously depends on your plan:
                  Starter (2), Professional (10), or Enterprise (unlimited).
                </p>
              </div>
            </details>
            <details className="group rounded-xl border border-white/10 bg-gray-900/50">
              <summary className="cursor-pointer px-6 py-4 text-sm font-medium text-white transition hover:text-emerald-400">
                What about risk management?
              </summary>
              <div className="border-t border-white/5 px-6 py-4 text-sm text-gray-400 space-y-3">
                <p>
                  Apex Algo has built-in risk management at every level of the trading pipeline:
                </p>
                <ul className="space-y-2">
                  <li className="flex items-start gap-2">
                    <span className="mt-0.5 text-emerald-400">•</span>
                    <span><strong className="text-white">Per-trade risk:</strong> Controlled via{" "}
                    <code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">--risk-per-trade</code>{" "}
                    (default 1.0% of account per trade)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-0.5 text-emerald-400">•</span>
                    <span><strong className="text-white">Max drawdown:</strong> Set with{" "}
                    <code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">--max-drawdown</code>{" "}
                    (engine auto-stops if exceeded)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-0.5 text-emerald-400">•</span>
                    <span><strong className="text-white">Position sizing:</strong> Automatically
                    calculated based on account size and risk parameters</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-0.5 text-emerald-400">•</span>
                    <span><strong className="text-white">Stop-loss:</strong> Every trade
                    includes an automated stop-loss order</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="mt-0.5 text-emerald-400">•</span>
                    <span><strong className="text-white">Trading hours:</strong> Restrict
                    to specific windows with <code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">--trading-hours</code></span>
                  </li>
                </ul>
                <p>
                  We strongly recommend running paper trading for 2–4 weeks before going live
                  so you can observe how these risk controls behave in different market conditions.
                </p>
              </div>
            </details>
            <details className="group rounded-xl border border-white/10 bg-gray-900/50">
              <summary className="cursor-pointer px-6 py-4 text-sm font-medium text-white transition hover:text-emerald-400">
                What markets are supported?
              </summary>
              <div className="border-t border-white/5 px-6 py-4 text-sm text-gray-400 space-y-3">
                <p>
                  Apex Algo supports futures and forex markets. Here are the major symbols:
                </p>
                <div className="grid gap-3 sm:grid-cols-2">
                  <div className="rounded-lg border border-white/5 bg-white/5 p-3">
                    <h5 className="text-xs font-semibold text-emerald-400">Futures</h5>
                    <p className="mt-1 text-xs text-gray-400">
                      ES (S&P 500), NQ (Nasdaq), CL (Crude Oil), GC (Gold), RTY (Russell),
                      ZB (Treasury Bonds)
                    </p>
                  </div>
                  <div className="rounded-lg border border-white/5 bg-white/5 p-3">
                    <h5 className="text-xs font-semibold text-emerald-400">Forex</h5>
                    <p className="mt-1 text-xs text-gray-400">
                      6E (EUR/USD), 6J (USD/JPY), 6B (GBP/USD), 6C (USD/CAD),
                      6A (AUD/USD)
                    </p>
                  </div>
                </div>
                <p>
                  The full list is in <code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">config/markets.py</code>.
                  You can also add custom symbols by editing that file.
                </p>
              </div>
            </details>
          </div>
        </div>
      </section>

      {/* Support CTA */}
      <section className="border-t border-white/5 py-16">
        <div className="mx-auto max-w-3xl px-6 text-center">
          <div className="mx-auto mb-6 inline-flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-4 py-1.5 text-sm font-medium text-emerald-400">
            Support
          </div>
          <h2 className="text-2xl font-bold text-white sm:text-3xl">
            Need Help?
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-gray-400">
            Our team is here to help. Priority support is included with
            Professional and Enterprise plans.
          </p>
          <div className="mt-8 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <a
              href="mailto:support@apexalgotrading.com"
              className="rounded-xl bg-emerald-600 px-8 py-4 text-base font-semibold text-white shadow-lg shadow-emerald-600/25 transition hover:bg-emerald-500 hover:shadow-emerald-500/25"
            >
              Contact Support
            </a>
            <a
              href="/#pricing"
              className="rounded-xl border border-white/10 bg-white/5 px-8 py-4 text-base font-semibold text-gray-300 transition hover:bg-white/10 hover:text-white"
            >
              View Pricing
            </a>
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
              <a href="#" className="transition hover:text-gray-300">Terms</a>
              <a href="#" className="transition hover:text-gray-300">Privacy</a>
              <a href="#" className="transition hover:text-gray-300">Docs</a>
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

/* ── Reusable code block ── */

function CodeBlock({ code, label }: { code: string; label?: string }) {
  return (
    <div className="rounded-lg border border-white/10 bg-gray-950 overflow-hidden mt-3 first:mt-0">
      {label && (
        <div className="border-b border-white/5 px-4 py-2 text-xs font-medium text-gray-500">
          {label}
        </div>
      )}
      <pre className="overflow-x-auto p-4 text-xs leading-relaxed text-gray-300">
        <code>{code}</code>
      </pre>
    </div>
  );
}
