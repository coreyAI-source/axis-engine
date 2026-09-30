import type { Assessment, Finding, HospitalityConfig, Requirement } from "./types.ts";

export interface HospitalityCategoryScore {
  category: string;
  score: number | null; // percentage, null if nothing assessable
  assessed: number;
  applicable: number;
}

export interface HospitalityResult {
  provisional: true;
  methodNote: string;
  score: number | null;
  coverage: number; // assessed / applicable, 0..1
  rating: string;
  favourable: boolean;
  categories: HospitalityCategoryScore[];
  blockers: string[];
  criticalGaps: { requirementId: string; status: string }[];
}

const METHOD_NOTE =
  "Provisional internal scoring method. Not a certification or recognised rating scheme. " +
  "Critical gaps, major findings or incomplete coverage prevent a favourable rating regardless of score.";

/**
 * Weighted score over applicable, assessed criteria. Not applicable is excluded; unassessed counts against coverage.
 * Any major finding, open major finding, or critical gap caps the result at a non-favourable rating.
 */
export function scoreHospitality(
  requirements: Pick<Requirement, "id" | "category" | "critical" | "weight">[],
  assessments: Assessment[],
  findings: Finding[],
  config: HospitalityConfig,
): HospitalityResult {
  const aByReq = new Map(assessments.map((a) => [a.requirementId, a]));
  const cats = new Map<string, { earned: number; possible: number; assessed: number; applicable: number }>();
  let earned = 0;
  let possible = 0;
  let assessed = 0;
  let applicable = 0;
  const criticalGaps: HospitalityResult["criticalGaps"] = [];
  const blockers: string[] = [];
  let majors = 0;
  let unassessedCritical = 0;

  for (const r of requirements) {
    const a = aByReq.get(r.id);
    const status = a?.status ?? "unassessed";
    if (status === "not_applicable") continue;
    const key = a?.snapshot?.category ?? r.category ?? "Uncategorised";
    const critical = a?.snapshot?.critical ?? r.critical ?? false;
    const c = cats.get(key) ?? { earned: 0, possible: 0, assessed: 0, applicable: 0 };
    c.applicable++;
    applicable++;
    if (critical && config.criticalGapStatuses.includes(status)) criticalGaps.push({ requirementId: r.id, status });
    if (status === "unassessed") {
      if (critical) {
        unassessedCritical++;
        blockers.push(`Critical requirement ${r.id} has not been assessed.`);
      }
      cats.set(key, c);
      continue;
    }
    if (status === "major") majors++;
    const w = a?.snapshot?.weight ?? r.weight ?? 1;
    const pts = config.points[status] * w;
    c.earned += pts;
    c.possible += w;
    c.assessed++;
    earned += pts;
    possible += w;
    assessed++;
    cats.set(key, c);
  }

  const openMajors = findings.filter((f) => f.status === "open" && f.severity === "major").length;
  const coverage = applicable === 0 ? 0 : assessed / applicable;
  const score = possible === 0 ? null : Math.round((earned / possible) * 1000) / 10;

  if (applicable === 0) blockers.push("No applicable criteria.");
  if (coverage < config.minCoverage)
    blockers.push(`Only ${Math.round(coverage * 100)}% of applicable criteria assessed (minimum ${Math.round(config.minCoverage * 100)}%).`);
  if (majors > 0) blockers.push(`${majors} major finding(s) assessed.`);
  if (openMajors > majors) blockers.push(`${openMajors} open major finding(s).`);
  if (criticalGaps.length) blockers.push(`${criticalGaps.length} critical gap(s).`);

  let rating: string;
  let favourable: boolean;
  const incomplete = applicable === 0 || coverage < config.minCoverage || score === null || unassessedCritical > 0;
  if (incomplete) {
    rating = "Incomplete: not rated";
    favourable = false;
  } else {
    const band = config.bands.find((b) => score >= b.minScore) ?? config.bands[config.bands.length - 1]!;
    const capped = majors > 0 || openMajors > 0 || criticalGaps.length > 0;
    const lowest = config.bands.find((b) => !b.favourable) ?? band;
    rating = capped && band.favourable ? `${lowest.label} (capped: critical issues)` : band.label;
    favourable = capped ? false : band.favourable;
  }

  return {
    provisional: true,
    methodNote: METHOD_NOTE,
    score,
    coverage,
    rating,
    favourable,
    categories: [...cats.entries()].map(([category, c]) => ({
      category,
      score: c.possible === 0 ? null : Math.round((c.earned / c.possible) * 1000) / 10,
      assessed: c.assessed,
      applicable: c.applicable,
    })),
    blockers,
    criticalGaps,
  };
}
