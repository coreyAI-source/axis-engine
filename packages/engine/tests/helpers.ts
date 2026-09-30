import { DEFAULT_CONFIG } from "../src/config.ts";
import type { Actor, EngineContext, Result } from "../src/types.ts";

let counter = 0;
export const resetIds = () => { counter = 0; };

export function ctx(actor: Actor, now: string): EngineContext {
  return { actor, now, newId: () => `id-${++counter}`, config: DEFAULT_CONFIG };
}

export function must<T>(r: Result<T>): T {
  if (!r.ok) throw new Error("Expected ok, got: " + r.violations.map((x) => x.code).join(", "));
  return r.value;
}

export function codes<T>(r: Result<T>): string[] {
  return r.ok ? [] : r.violations.map((x) => x.code);
}

// Fictional people. Unauthenticated = today's named-field behaviour.
export const TARREN: Actor = { name: "DEMO Tarren (auditor)", authenticated: false };
export const SAM: Actor = { name: "DEMO Sam Owner", authenticated: false };
export const ALEX: Actor = { name: "DEMO Alex Verifier", authenticated: false };

export const T0 = "2026-10-01T09:00:00.000Z";
