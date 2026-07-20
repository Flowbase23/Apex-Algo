import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";

export const Route = createFileRoute("/getting-started")({
  component: GettingStarted,
});

const stripeLinks: Record<string, string> = {
  starter: "https://buy.stripe.com/9B65kCh2MgWEbXxdeB73G06",
  pro: "https://buy.stripe.com/dRmbJ0eUEdKs5z9a2p73G07",
  enterprise: "https://buy.stripe.com/fZufZg13O7m43r12zX73G08",
};

function GettingStarted() {
  const [activeStep, setActiveStep] = useState(0);

  const steps = [
    {
      title: "Prerequisites",
      icon: "📋",
      content: (
        <div className="space-y-4 text-gray-300">
          <p>
            Before installing the Apex Algo trading engine, make sure your system
            meets these requirements:
          </p>
          <div className="rounded-xl border border-white/10 bg-gray-900/60 p-6">
            <h4 className="mb-3 text-sm font-semibold text-white">System Requirements</h4>
            <ul className="space-y-2 text-sm">
              <li className="flex items-start gap-2">
                <span className="mt-0.5 text-emerald-400">•</span>
                <span><strong className="text-white">Python 3.10+</strong> — the engine is built entirely in Python</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-0.5 text-emerald-400">•</span>
                <span><strong className="text-white">pip</strong> — Python package manager (comes with Python)</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-0.5 text-emerald-400">•</span>
                <span><strong className="text-white">Git</strong> — for cloning the repository and version control</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-0.5 text-emerald-400">•</span>
                <span><strong className="text-white">8 GB RAM</strong> recommended for backtesting with large datasets</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-0.5 text-emerald-400">•</span>
                <span><strong className="text-white">macOS, Linux, or Windows (WSL2)</strong> — all major platforms supported</span>
              </li>
            </ul>
          </div>
        </div>
      ),
    },
    {
      title: "Clone & Install",
      icon: "💻",
      content: (
        <div className="space-y-4 text-gray-300">
          <p>
            Clone the Apex Algo repository and install all dependencies with a single
            setup command.
          </p>
          <div className="rounded-xl border border-white/10 bg-gray-900/60 p-6">
            <h4 className="mb-3 text-sm font-semibold text-white">Installation Commands</h4>
            <div className="space-y-3">
              <CodeBlock
                label="Clone the repository"
                code="git clone https://github.com/Flowbase23/Apex-Algo.git
cd Apex-Algo/engine"
              />
              <CodeBlock
                label="Create virtual environment (recommended)"
                code="python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or: venv\\Scripts\\activate  # Windows"
              />
              <CodeBlock
                label="Install dependencies"
                code="pip install -r requirements.txt"
              />
            </div>
          </div>
          <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4">
            <p className="text-sm text-emerald-300">
              <strong>💡 Tip:</strong> The <code className="rounded bg-emerald-500/10 px-1.5 py-0.5 text-xs">requirements.txt</code>{" "}
              includes Pandas, NumPy, scikit-learn, TensorFlow, and all broker SDKs. Installation
              typically takes 2–3 minutes on a modern machine.
            </p>
          </div>
        </div>
      ),
    },
    {
      title: "Configure API Keys",
      icon: "🔑",
      content: (
        <div className="space-y-4 text-gray-300">
          <p>
            The engine needs market data API keys to fetch real-time and historical price data.
            Copy the environment template and add your keys.
          </p>
          <div className="rounded-xl border border-white/10 bg-gray-900/60 p-6">
            <h4 className="mb-3 text-sm font-semibold text-white">API Configuration</h4>
            <CodeBlock
              label="Copy the environment template"
              code="cp .env.example .env"
            />
            <p className="mt-3 text-sm text-gray-400">
              Then edit <code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">.env</code> and add your keys:
            </p>
            <div className="mt-3 space-y-2 text-sm">
              <div className="flex items-start gap-2">
                <span className="mt-0.5 text-emerald-400">•</span>
                <span>
                  <strong className="text-white">ALPHA_VANTAGE_API_KEY</strong>{" "}
                  <span className="text-gray-500">— Free tier available at{" "}
                    <a href="https://www.alphavantage.co/support/#api-key" target="_blank" rel="noopener noreferrer" className="text-emerald-400 underline hover:text-emerald-300">
                      alphavantage.co
                    </a>
                  </span>
                </span>
              </div>
              <div className="flex items-start gap-2">
                <span className="mt-0.5 text-emerald-400">•</span>
                <span>
                  <strong className="text-white">POLYGON_API_KEY</strong>{" "}
                  <span className="text-gray-500">— Sign up at{" "}
                    <a href="https://polygon.io/" target="_blank" rel="noopener noreferrer" className="text-emerald-400 underline hover:text-emerald-300">
                      polygon.io
                    </a>
                  </span>
                </span>
              </div>
              <div className="flex items-start gap-2">
                <span className="mt-0.5 text-emerald-400">•</span>
                <span>
                  <strong className="text-white">NINJATRADER_CLIENT_ID</strong>{" "}
                  <span className="text-gray-500">— From your NinjaTrader account dashboard</span>
                </span>
              </div>
              <div className="flex items-start gap-2">
                <span className="mt-0.5 text-emerald-400">•</span>
                <span>
                  <strong className="text-white">QUANTCONNECT_USER_ID</strong> /{" "}
                  <strong className="text-white">QUANTCONNECT_API_TOKEN</strong>{" "}
                  <span className="text-gray-500">— From your QuantConnect account</span>
                </span>
              </div>
            </div>
          </div>
        </div>
      ),
    },
    {
      title: "Run Backtests",
      icon: "📊",
      content: (
        <div className="space-y-4 text-gray-300">
          <p>
            Before going live, validate your strategy against 5+ years of historical
            market data. The backtesting framework connects directly to NinjaTrader and
            QuantConnect.
          </p>
          <div className="rounded-xl border border-white/10 bg-gray-900/60 p-6">
            <h4 className="mb-3 text-sm font-semibold text-white">Running Backtests</h4>
            <CodeBlock
              label="Run the full backtest suite"
              code="python backtest.py --years 5 --markets ES,NQ,CL"
            />
            <p className="mt-3 text-sm text-gray-400">
              Flags you can use:
            </p>
            <ul className="mt-2 space-y-1 text-sm">
              <li><code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">--years</code> — how many years of historical data to test</li>
              <li><code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">--markets</code> — comma-separated symbols (ES, NQ, CL, GC, 6E, etc.)</li>
              <li><code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">--strategy</code> — which ML model to use: <code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">random_forest</code>, <code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">neural_network</code>, or <code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">ensemble</code></li>
              <li><code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">--report</code> — output format: <code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">html</code>, <code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">json</code>, or <code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">csv</code></li>
            </ul>
          </div>
          <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4">
            <p className="text-sm text-emerald-300">
              <strong>📈 Expected Output:</strong> The backtest report includes Sharpe ratio,
              max drawdown, win rate, average risk/reward, equity curve, and monthly returns
              breakdown.
            </p>
          </div>
        </div>
      ),
    },
    {
      title: "Paper Trading",
      icon: "🧪",
      content: (
        <div className="space-y-4 text-gray-300">
          <p>
            Once backtests look solid, run the engine in paper trading mode. This simulates
            live market conditions with virtual capital — no real money at risk.
          </p>
          <div className="rounded-xl border border-white/10 bg-gray-900/60 p-6">
            <h4 className="mb-3 text-sm font-semibold text-white">Start Paper Trading</h4>
            <CodeBlock
              label="Launch the paper trading simulator"
              code="python trade.py --mode paper --strategy ensemble --markets ES,NQ"
            />
            <p className="mt-3 text-sm text-gray-400">
              The paper trading engine will:
            </p>
            <ul className="mt-2 space-y-1 text-sm">
              <li className="flex items-start gap-2">
                <span className="mt-0.5 text-emerald-400">•</span>
                <span>Stream real-time market data from your configured API</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-0.5 text-emerald-400">•</span>
                <span>Generate trade signals using the trained ML models</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-0.5 text-emerald-400">•</span>
                <span>Execute simulated trades with realistic slippage and commissions</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-0.5 text-emerald-400">•</span>
                <span>Log all activity to <code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">logs/paper_trading.log</code></span>
              </li>
            </ul>
          </div>
          <div className="rounded-xl border border-yellow-500/20 bg-yellow-500/5 p-4">
            <p className="text-sm text-yellow-300">
              <strong>⚠️ Recommendation:</strong> Run paper trading for at least 2–4 weeks
              before going live. Monitor drawdown, fill rates, and strategy behavior across
              different market conditions.
            </p>
          </div>
        </div>
      ),
    },
    {
      title: "Connect Broker & Go Live",
      icon: "🚀",
      content: (
        <div className="space-y-4 text-gray-300">
          <p>
            When you're confident in the strategy, connect your live broker account and
            switch to live mode. The AI executes trades autonomously during daytime hours.
          </p>
          <div className="rounded-xl border border-white/10 bg-gray-900/60 p-6">
            <h4 className="mb-3 text-sm font-semibold text-white">Live Deployment</h4>
            <CodeBlock
              label="Go live with your broker"
              code="python trade.py --mode live --strategy ensemble --markets ES,NQ \\
  --risk-per-trade 1.0 --max-drawdown 5.0"
            />
            <p className="mt-3 text-sm text-gray-400">
              Critical live trading flags:
            </p>
            <ul className="mt-2 space-y-1 text-sm">
              <li><code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">--risk-per-trade</code> — percentage of account risked per trade (default: 1.0%)</li>
              <li><code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">--max-drawdown</code> — auto-stop if drawdown exceeds this percentage</li>
              <li><code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">--trading-hours</code> — restrict to specific hours (e.g., <code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">09:30-16:00</code>)</li>
              <li><code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">--broker</code> — <code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">ninjatrader</code> or <code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">quantconnect</code></li>
            </ul>
          </div>
          <div className="rounded-xl border border-white/10 bg-gray-900/60 p-6">
            <h4 className="mb-3 text-sm font-semibold text-white">Supported Brokers</h4>
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="rounded-lg border border-white/5 bg-white/5 p-4">
                <h5 className="font-semibold text-white">NinjaTrader</h5>
                <p className="mt-1 text-xs text-gray-400">
                  Direct FIX API connection. Futures & forex supported. Set
                  NINJATRADER_CLIENT_ID and NINJATRADER_CLIENT_SECRET in .env.
                </p>
              </div>
              <div className="rounded-lg border border-white/5 bg-white/5 p-4">
                <h5 className="font-semibold text-white">QuantConnect</h5>
                <p className="mt-1 text-xs text-gray-400">
                  Cloud-based execution via LEAN engine. Ideal for multi-asset
                  strategies. Set QUANTCONNECT_USER_ID and QUANTCONNECT_API_TOKEN.
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
            <a href="/#features" className="transition hover:text-white">
              Features
            </a>
            <a href="/#how-it-works" className="transition hover:text-white">
              How It Works
            </a>
            <a href="/#pricing" className="transition hover:text-white">
              Pricing
            </a>
            <a href="/getting-started" className="text-emerald-400 transition hover:text-emerald-300">
              Getting Started
            </a>
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
            Getting Started with{" "}
            <span className="text-gradient">Apex Algo</span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-gray-400">
            Follow this step-by-step guide to install, configure, and deploy the Apex Algo
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
              Choose a plan below to get access to the trading engine. You'll be redirected to
              our secure Stripe checkout, then come right back here to follow the setup guide.
            </p>
            <div className="mt-8 grid gap-4 sm:grid-cols-3">
              <a
                href={stripeLinks.starter}
                target="_blank"
                rel="noopener noreferrer"
                className="rounded-xl border border-white/10 bg-gray-900/60 px-6 py-4 text-center transition hover:border-emerald-500/30 hover:bg-gray-900/80"
              >
                <div className="text-lg font-bold text-white">Starter</div>
                <div className="mt-1 text-2xl font-bold text-emerald-400">$49<span className="text-sm text-gray-500">/mo</span></div>
                <div className="mt-2 text-xs text-gray-500">Up to 2 markets</div>
              </a>
              <a
                href={stripeLinks.pro}
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
                href={stripeLinks.enterprise}
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
              Setup Guide
            </h2>
            <p className="mt-3 text-gray-400">
              Already subscribed? Jump straight into the installation steps below.
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

      {/* Troubleshooting */}
      <section className="border-t border-white/5 py-16">
        <div className="mx-auto max-w-4xl px-6">
          <div className="mb-10 text-center">
            <h2 className="text-2xl font-bold text-white sm:text-3xl">
              Troubleshooting
            </h2>
            <p className="mt-3 text-gray-400">
              Common issues and how to resolve them quickly.
            </p>
          </div>
          <div className="space-y-4">
            <details className="group rounded-xl border border-white/10 bg-gray-900/50">
              <summary className="cursor-pointer px-6 py-4 text-sm font-medium text-white transition hover:text-emerald-400">
                "Module not found" errors during pip install
              </summary>
              <div className="border-t border-white/5 px-6 py-4 text-sm text-gray-400">
                <p>
                  Make sure you've activated your virtual environment before running pip. If issues
                  persist, try:
                </p>
                <CodeBlock
                  code="pip install --upgrade pip setuptools wheel
pip install -r requirements.txt --no-cache-dir"
                />
              </div>
            </details>
            <details className="group rounded-xl border border-white/10 bg-gray-900/50">
              <summary className="cursor-pointer px-6 py-4 text-sm font-medium text-white transition hover:text-emerald-400">
                API rate limit errors during backtesting
              </summary>
              <div className="border-t border-white/5 px-6 py-4 text-sm text-gray-400">
                <p>
                  Free API tiers have rate limits. Either upgrade your API plan or reduce
                  concurrent requests:
                </p>
                <CodeBlock
                  code="python backtest.py --years 5 --rate-limit 5  # Max 5 requests per minute"
                />
              </div>
            </details>
            <details className="group rounded-xl border border-white/10 bg-gray-900/50">
              <summary className="cursor-pointer px-6 py-4 text-sm font-medium text-white transition hover:text-emerald-400">
                Broker connection fails in live mode
              </summary>
              <div className="border-t border-white/5 px-6 py-4 text-sm text-gray-400">
                <p>
                  Verify your broker credentials in <code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">.env</code> and
                  that your broker account has API trading enabled. Test the connection:
                </p>
                <CodeBlock
                  code="python trade.py --mode test-connection --broker ninjatrader"
                />
              </div>
            </details>
            <details className="group rounded-xl border border-white/10 bg-gray-900/50">
              <summary className="cursor-pointer px-6 py-4 text-sm font-medium text-white transition hover:text-emerald-400">
                High memory usage during backtests
              </summary>
              <div className="border-t border-white/5 px-6 py-4 text-sm text-gray-400">
                <p>
                  Large backtests can consume significant RAM. Reduce the scope or use
                  incremental backtesting:
                </p>
                <CodeBlock
                  code="python backtest.py --years 5 --batch-size 250  # Process 250 days at a time"
                />
              </div>
            </details>
          </div>
        </div>
      </section>

      {/* Need help */}
      <section className="border-t border-white/5 py-16">
        <div className="mx-auto max-w-3xl px-6 text-center">
          <div className="mx-auto mb-6 inline-flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-4 py-1.5 text-sm font-medium text-emerald-400">
            Support
          </div>
          <h2 className="text-2xl font-bold text-white sm:text-3xl">
            Need Help?
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-gray-400">
            Our team is here to help you get set up. Priority support is included with
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
              href="/#features"
              className="rounded-xl border border-white/10 bg-white/5 px-8 py-4 text-base font-semibold text-gray-300 transition hover:bg-white/10 hover:text-white"
            >
              Explore Features
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

/* ── Reusable code block ── */

function CodeBlock({ code, label }: { code: string; label?: string }) {
  return (
    <div className="rounded-lg border border-white/10 bg-gray-950 overflow-hidden">
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
