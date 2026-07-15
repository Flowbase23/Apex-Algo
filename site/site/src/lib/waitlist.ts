import { createServerFn } from "@tanstack/react-start";
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { join, resolve } from "node:path";

const DATA_DIR = resolve(process.cwd(), "data");
const WAITLIST_FILE = join(DATA_DIR, "waitlist.json");

interface WaitlistEntry {
  email: string;
  timestamp: string;
}

async function readWaitlist(): Promise<WaitlistEntry[]> {
  try {
    const raw = await readFile(WAITLIST_FILE, "utf-8");
    return JSON.parse(raw) as WaitlistEntry[];
  } catch {
    return [];
  }
}

async function appendWaitlist(entry: WaitlistEntry): Promise<void> {
  if (!existsSync(DATA_DIR)) {
    await mkdir(DATA_DIR, { recursive: true });
  }
  const entries = await readWaitlist();
  entries.push(entry);
  await writeFile(WAITLIST_FILE, JSON.stringify(entries, null, 2), "utf-8");
}

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

    // Check for duplicates
    const entries = await readWaitlist();
    if (entries.some((e) => e.email === email)) {
      return {
        success: true,
        message: "You're already on the waitlist! We'll be in touch.",
      };
    }

    await appendWaitlist({
      email,
      timestamp: new Date().toISOString(),
    });

    return {
      success: true,
      message: "Thanks for joining! We'll keep you posted on early access.",
    };
  });