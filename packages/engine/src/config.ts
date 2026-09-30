import type { EngineConfig } from "./types.ts";

/**
 * Internal defaults. None of these values is a statutory or standard-mandated figure.
 * Items marked PENDING need Tarren's confirmation before production use.
 */
export const DEFAULT_CONFIG: EngineConfig = {
  deadlineDays: { major: 14, minor: 30 }, // PENDING: severity mapping to confirm
  inactivityDays: 7,
  majorUnstartedHours: 48,
  unstartedWindowFraction: 0.5,
  minRationaleLength: 10,
  hospitality: {
    points: { conforming: 1, observation: 0.75, minor: 0.4, major: 0 }, // PENDING
    minCoverage: 0.9, // PENDING
    bands: [
      // PENDING: labels and thresholds are placeholders
      { minScore: 85, label: "Strong", favourable: true },
      { minScore: 70, label: "Developing", favourable: true },
      { minScore: 0, label: "Needs improvement", favourable: false },
    ],
    criticalGapStatuses: ["minor", "major"], // PENDING: definition of "critical gap"
  },
};
