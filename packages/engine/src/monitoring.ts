import type { CorrectiveAction, EngineConfig, Finding } from "./types.ts";
import { daysBetween, hoursBetween } from "./util.ts";

export type MonitorFlagCode = "overdue" | "inactive" | "unstarted_past_half_window" | "major_unstarted_48h";

export interface MonitorFlag {
  code: MonitorFlagCode;
  message: string;
}

/**
 * Computed on read. Scheduled notifications are a later milestone;
 * these flags are what a scheduler would eventually act on.
 */
export function actionFlags(a: CorrectiveAction, finding: Finding, now: string, config: EngineConfig): MonitorFlag[] {
  if (a.status === "closed" || a.status === "cancelled") return [];
  const flags: MonitorFlag[] = [];
  const nowMs = Date.parse(now);
  const due = Date.parse(a.dueDate);
  const created = Date.parse(a.createdAt);

  if (nowMs > due) {
    const days = Math.floor(daysBetween(a.dueDate, now));
    flags.push({ code: "overdue", message: `Overdue by ${days} day(s).` });
  }

  const idle = daysBetween(a.lastActivityAt, now);
  if (idle >= config.inactivityDays)
    flags.push({ code: "inactive", message: `No update for ${Math.floor(idle)} days.` });

  if (a.status === "not_started") {
    const halfway = created + (due - created) * config.unstartedWindowFraction;
    if (nowMs > halfway) flags.push({ code: "unstarted_past_half_window", message: "Not started and more than half the time allowed has passed." });
    if (finding.severity === "major" && hoursBetween(a.createdAt, now) >= config.majorUnstartedHours)
      flags.push({ code: "major_unstarted_48h", message: `Major finding action not started after ${config.majorUnstartedHours} hours.` });
  }
  return flags;
}

export interface MonitorSummary {
  open: number;
  closed: number;
  byFlag: Record<MonitorFlagCode, number>;
}

export function summarise(actions: CorrectiveAction[], findings: Finding[], now: string, config: EngineConfig): MonitorSummary {
  const fById = new Map(findings.map((f) => [f.id, f]));
  const byFlag: Record<MonitorFlagCode, number> = { overdue: 0, inactive: 0, unstarted_past_half_window: 0, major_unstarted_48h: 0 };
  let open = 0;
  let closed = 0;
  for (const a of actions) {
    if (a.status === "closed") closed++;
    else if (a.status !== "cancelled") open++;
    const f = fById.get(a.findingId);
    if (!f) continue;
    for (const flag of actionFlags(a, f, now, config)) byFlag[flag.code]++;
  }
  return { open, closed, byFlag };
}
