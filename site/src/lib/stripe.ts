// Stripe payment links for Apex Algo Trading pricing tiers.
// After payment, Stripe redirects users to the /getting-started page.

export const STRIPE_LINKS = {
  starter: "https://buy.stripe.com/9B65kCh2MgWEbXxdeB73G06",
  pro: "https://buy.stripe.com/dRmbJ0eUEdKs5z9a2p73G07",
  enterprise: "https://buy.stripe.com/fZufZg13O7m43r12zX73G08",
} as const;

export type PricingTier = keyof typeof STRIPE_LINKS;

export function getStripeLink(tier: PricingTier): string {
  return STRIPE_LINKS[tier];
}
