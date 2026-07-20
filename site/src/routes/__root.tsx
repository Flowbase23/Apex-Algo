import {
  HeadContent,
  Outlet,
  Scripts,
  createRootRoute,
} from "@tanstack/react-router";
import type { ReactNode } from "react";

import appCss from "~/styles/app.css?url";

export const Route = createRootRoute({
  head: () => ({
    meta: [
      { charSet: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      {
        title: "Apex Algo Trading — AI-Powered Automated Trading",
      },
      {
        name: "description",
        content:
          "AI-powered automated trading for futures and forex. Combining Random Forest & Neural Networks for disciplined, emotion-free trades. Backtested on NinjaTrader & QuantConnect.",
      },
      {
        name: "keywords",
        content:
          "algo trading, automated trading, AI trading, futures trading, forex trading, trading bot, quantitative trading",
      },
      { name: "theme-color", content: "#030712" },
      { property: "og:title", content: "Apex Algo Trading — AI-Powered Automated Trading" },
      {
        property: "og:description",
        content:
          "AI-powered automated trading for futures and forex. Combining Random Forest & Neural Networks for disciplined, emotion-free trades.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
      { name: "twitter:title", content: "Apex Algo Trading — AI-Powered Automated Trading" },
      {
        name: "twitter:description",
        content:
          "AI-powered automated trading for futures and forex. Combining Random Forest & Neural Networks for disciplined, emotion-free trades.",
      },
    ],
    links: [
      { rel: "stylesheet", href: appCss },
      {
        rel: "preconnect",
        href: "https://fonts.googleapis.com",
      },
      {
        rel: "preconnect",
        href: "https://fonts.gstatic.com",
        crossOrigin: "anonymous",
      },
      {
        rel: "stylesheet",
        href: "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap",
      },
      { rel: "icon", href: "data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>📈</text></svg>" },
    ],
  }),
  notFoundComponent: () => (
    <div className="flex min-h-dvh items-center justify-center bg-gray-950">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-100">Page not found</h1>
        <p className="mt-2 text-gray-400">The page you're looking for doesn't exist.</p>
        <a
          href="/"
          className="mt-6 inline-block rounded-lg bg-emerald-600 px-6 py-3 text-sm font-semibold text-white transition hover:bg-emerald-500"
        >
          Go home
        </a>
      </div>
    </div>
  ),
  component: RootComponent,
});

function RootComponent() {
  return (
    <RootDocument>
      <Outlet />
    </RootDocument>
  );
}

function RootDocument({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className="dark">
      <head>
        <HeadContent />
      </head>
      <body style={{ fontFamily: "'Inter', system-ui, sans-serif" }}>
        {children}
        <Scripts />
      </body>
    </html>
  );
}
