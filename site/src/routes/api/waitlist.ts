import { createServerFn } from "@tanstack/react-start";
import { sql } from "~/db";

export const submitWaitlist = createServerFn({ method: "POST" })
  .validator((data: unknown) => {
    if (typeof data !== "object" || data === null) {
      throw new Error("Invalid request body");
    }
    const { email } = data as Record<string, unknown>;
    if (typeof email !== "string" || !email.trim()) {
      throw new Error("Email is required");
    }
    const trimmed = email.trim().toLowerCase();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed)) {
      throw new Error("Please enter a valid email address");
    }
    return { email: trimmed };
  })
  .handler(async ({ data }) => {
    const { email } = data;

    try {
      const result = await sql()`INSERT INTO waitlist (email, created_at) VALUES (${email}, NOW()) RETURNING id`;

      const id = result[0]?.id;

      return {
        success: true as const,
        id: id as number,
        message: "Thanks! You're on the list.",
      };
    } catch {
      return {
        success: false as const,
        error: "Service unavailable — try again later",
      };
    }
  });