import { createRequirement, reviewRequirement } from "./requirements.ts";
import type { EngineContext, Requirement } from "./types.ts";
import { GSTC_HOTEL_V4_CRITERIA } from "./gstc-hotel-v4-data.ts";

export interface GstcCriterion {
  id: string;
  section: "A" | "B" | "C" | "D";
  group?: string;
  page: number;
  title: string;
  statement: string;
  indicators: string[];
  guidance: string[];
}

export interface HotelTemplate {
  id: string;
  version: string;
  title: string;
  fictional: boolean;
  disclaimer: string;
}

const CATEGORY: Record<GstcCriterion["section"], string> = {
  A: "A · Sustainable management",
  B: "B · Social & economic",
  C: "C · Cultural heritage",
  D: "D · Environmental",
};

export const GSTC_HOTEL_TEMPLATE: HotelTemplate = {
  id: "gstc-hotel-v4",
  version: "v4.0 (December 30, 2025)",
  title: "GSTC Hotel Standard",
  fictional: false,
  disclaimer: "Criteria, performance indicators and guidelines are reproduced from the GSTC Hotel Standard v4.0 (December 30, 2025), © Global Sustainable Tourism Council. This report is an internal assessment, not GSTC certification; only GSTC-accredited certification bodies can certify a hotel. Scores, severity categories and corrective-action deadlines are AXIS settings, not GSTC rules.",
};

/** Audits created before the GSTC library shipped keep loading with their original fictional criteria. */
export const LEGACY_PILOT_TEMPLATE: HotelTemplate = {
  id: "axis-hotel-pilot",
  version: "2026-09-29",
  title: "AXIS fictional hotel pilot criteria",
  fictional: true,
  disclaimer: "FICTIONAL internal demonstration criteria. This pilot is not a GSTC assessment, certification, or an approved interpretation of any standard. Criteria, scoring and deadlines require competent-person review before real use.",
};

export const HOTEL_TEMPLATES: readonly HotelTemplate[] = [GSTC_HOTEL_TEMPLATE, LEGACY_PILOT_TEMPLATE];

export function createGstcHotelRequirements(ctx: EngineContext): Requirement[] {
  const author = { ...ctx, actor: { name: "AXIS standards library", authenticated: false } };
  const checker = { ...ctx, actor: { name: "AXIS standards library (source check)", authenticated: false } };
  return GSTC_HOTEL_V4_CRITERIA.map((c) => {
    const created = createRequirement({
      module: "hospitality",
      text: `${c.id} ${c.title} — ${c.statement}`,
      title: c.title,
      indicators: [...c.indicators],
      guidance: [...c.guidance],
      category: CATEGORY[c.section],
      weight: 1,
      source: {
        documentId: GSTC_HOTEL_TEMPLATE.id,
        documentTitle: GSTC_HOTEL_TEMPLATE.title,
        revision: GSTC_HOTEL_TEMPLATE.version,
        section: c.group ? `Section ${c.section} · ${c.group}` : `Section ${c.section}`,
        clause: c.id,
        page: String(c.page),
      },
    }, author);
    if (!created.ok) throw new Error(`Invalid GSTC criterion ${c.id}.`);
    const reviewed = reviewRequirement(created.value, "approved", "Text matches the published GSTC Hotel Standard v4.0. Applicability, evidence sufficiency and severity remain the auditor's judgement.", created.value.version, checker);
    if (!reviewed.ok) throw new Error(`Invalid GSTC criterion review ${c.id}.`);
    return reviewed.value;
  });
}
