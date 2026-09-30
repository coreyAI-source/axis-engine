import type { Actor, EngineContext, HistoryEntry, Result, Versioned, Violation } from "./types.ts";

export const ok = <T>(value: T, warnings: Violation[] = []): Result<T> => ({ ok: true, value, warnings });
export const fail = <T = never>(...violations: Violation[]): Result<T> => ({ ok: false, violations });
export const v = (code: string, message: string, field?: string): Violation =>
  field === undefined ? { code, message } : { code, message, field };

const DAY_MS = 86_400_000;
export const addDays = (iso: string, days: number): string => new Date(Date.parse(iso) + days * DAY_MS).toISOString();
export const hoursBetween = (a: string, b: string): number => (Date.parse(b) - Date.parse(a)) / 3_600_000;
export const daysBetween = (a: string, b: string): number => (Date.parse(b) - Date.parse(a)) / DAY_MS;

export const blank = (s: string | undefined | null): boolean => !s || s.trim().length === 0;

/** Optimistic concurrency: reject writes based on a stale copy. */
export function checkVersion(record: Versioned, expectedVersion: number): Violation | null {
  return record.version === expectedVersion
    ? null
    : v(
        "VERSION_CONFLICT",
        `This record was changed by someone else (you had version ${expectedVersion}, current is ${record.version}). Reload and reapply your change.`,
      );
}

export function entry(ctx: EngineContext, event: string, detail?: Record<string, unknown>): HistoryEntry {
  return detail === undefined ? { at: ctx.now, actor: ctx.actor, event } : { at: ctx.now, actor: ctx.actor, event, detail };
}

/** Return a new record with version bumped and a history entry appended. Never mutates input. */
export function bump<T extends Versioned>(
  record: T,
  changes: Partial<T>,
  ctx: EngineContext,
  event: string,
  detail?: Record<string, unknown>,
): T {
  return { ...record, ...changes, version: record.version + 1, history: [...record.history, entry(ctx, event, detail)] };
}

/**
 * Same person? Uses user IDs when both are authenticated; otherwise falls back to
 * normalised names. Name comparison is a courtesy check, not a security control.
 */
export function samePerson(a: Actor, b: Actor): boolean {
  if (a.authenticated && b.authenticated && a.userId && b.userId) return a.userId === b.userId;
  return normName(a.name) === normName(b.name);
}
const normName = (s: string) => s.trim().toLowerCase().replace(/\s+/g, " ");
