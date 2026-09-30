/**
 * AXIS audit engine: domain types.
 *
 * The engine is pure: no database, network, clock or randomness.
 * Every mutation takes an EngineContext (who, when, id generator, config)
 * and returns a Result. Persistence (D1/R2) and UI live outside the engine.
 */

export type ModuleKind = "iso" | "offshore" | "hospitality";
export type IsoDiscipline = "environment" | "quality" | "ohs";

/** Who performed an action. `authenticated` is true only when the platform verified the identity. */
export interface Actor {
  name: string;
  userId?: string;
  authenticated: boolean;
}

export interface HistoryEntry {
  at: string; // ISO timestamp
  actor: Actor;
  event: string;
  detail?: Record<string, unknown>;
}

/** Every mutable record carries an optimistic-concurrency version and an append-only history. */
export interface Versioned {
  id: string;
  version: number;
  history: HistoryEntry[];
}

// ---------------------------------------------------------------- sources

export type SourceKind =
  | "standard"
  | "environment_plan"
  | "regulation"
  | "permit"
  | "client_requirement"
  | "internal"
  | "other";

export interface SourceDocument {
  id: string;
  title: string;
  revision: string;
  kind: SourceKind;
  issuedDate?: string;
}

/** Where a requirement comes from. Section, clause or page "where available". */
export interface SourceReference {
  documentId: string;
  documentTitle: string;
  revision: string;
  section?: string;
  clause?: string;
  page?: string;
}

// ---------------------------------------------------------------- requirements

export type ReviewStatus = "draft" | "approved" | "rejected";
export type RequirementOrigin = "manual" | "ai_extraction" | "imported";

export interface Requirement extends Versioned {
  module: ModuleKind;
  disciplines?: IsoDiscipline[]; // ISO module only
  category?: string; // e.g. hospitality "water", offshore "discharges"
  text: string;
  title?: string;
  /** Published performance indicators, in source order. */
  indicators?: string[];
  /** Published guidance notes for the indicators, in source order. */
  guidance?: string[];
  auditPrompt?: string;
  controls?: string[];
  performanceStandard?: string; // offshore
  measurementCriteria?: string; // offshore
  source: SourceReference;
  origin: RequirementOrigin;
  createdBy: Actor;
  reviewStatus: ReviewStatus;
  reviewedBy?: Actor;
  reviewedAt?: string;
  reviewNote?: string;
  /** Hospitality: a gap here blocks a favourable rating. Definition pending Tarren. */
  critical?: boolean;
  /** Hospitality scoring weight; defaults to 1. Provisional. */
  weight?: number;
}

// ---------------------------------------------------------------- audits

export type AuditStatus = "planned" | "in_progress" | "reporting" | "complete";

export interface Audit extends Versioned {
  module: ModuleKind;
  title: string;
  siteName: string;
  disciplines?: IsoDiscipline[]; // one = single-discipline, several = integrated
  status: AuditStatus;
  leadAuditor: Actor;
  requirementIds: string[]; // criteria in scope
  scopeStatement?: string;
  startDate: string;
  endDate?: string;
}

// ---------------------------------------------------------------- evidence

export type EvidenceKind = "document" | "photo" | "record" | "interview" | "observation";

export interface AttachmentRef {
  key: string; // R2 object key
  fileName: string;
  contentType: string;
  sizeBytes: number;
  sha256?: string;
}

export interface Evidence {
  id: string;
  auditId: string;
  kind: EvidenceKind;
  description: string;
  reference?: string; // e.g. "Waste manifest 2026-03, p. 4"
  attachment?: AttachmentRef;
  collectedBy: Actor;
  collectedAt: string;
}

// ---------------------------------------------------------------- assessments

export type AssessmentStatus =
  | "unassessed"
  | "conforming"
  | "observation"
  | "minor"
  | "major"
  | "not_applicable";

/** Frozen copy of the requirement at assessment time, so later revisions never rewrite history. */
export interface RequirementSnapshot {
  requirementId: string;
  requirementVersion: number;
  text: string;
  source: SourceReference;
  auditPrompt?: string;
  category?: string;
  critical?: boolean;
  weight?: number;
}

export interface Assessment extends Versioned {
  auditId: string;
  requirementId: string;
  status: AssessmentStatus;
  rationale: string;
  evidenceIds: string[];
  snapshot?: RequirementSnapshot;
  assessedBy?: Actor;
  assessedAt?: string;
}

// ---------------------------------------------------------------- findings

export type FindingSeverity = "minor" | "major";
export type FindingStatus = "open" | "closed" | "withdrawn";

export interface Finding extends Versioned {
  auditId: string;
  assessmentId: string;
  requirementId: string;
  snapshot: RequirementSnapshot;
  severity: FindingSeverity;
  statement: string;
  evidenceIds: string[];
  status: FindingStatus;
  raisedAt: string;
  raisedBy: Actor;
  /** Set when the linked assessment changed away from this finding. The finding is kept, never deleted. */
  reviewRequired?: { reason: string; since: string };
  withdrawal?: { rationale: string; by: Actor; at: string };
  closedAt?: string;
}

// ---------------------------------------------------------------- corrective actions

export type ActionStatus =
  | "not_started"
  | "in_progress"
  | "awaiting_verification"
  | "closed"
  | "cancelled";

export type DeadlineBasis =
  | { kind: "internal_default"; days: number }
  | { kind: "custom"; reason: string }
  | { kind: "external"; reference: string }; // must cite a real source; the engine never invents one

export interface ProgressUpdate {
  at: string;
  by: Actor;
  note: string;
}

export type SeparationOfDuties =
  | "enforced" // both people authenticated with distinct user IDs
  | "declared_only"; // based on typed names only; NOT authenticated separation

export interface Verification {
  verifier: Actor;
  at: string;
  outcome: "effective" | "not_effective";
  note: string;
  separation: SeparationOfDuties;
}

export interface CorrectiveAction extends Versioned {
  auditId: string;
  findingId: string;
  description: string;
  owner: Actor;
  createdAt: string;
  dueDate: string;
  deadlineBasis: DeadlineBasis;
  status: ActionStatus;
  startedAt?: string;
  updates: ProgressUpdate[];
  lastActivityAt: string;
  implementation?: { note: string; evidenceIds: string[]; submittedBy: Actor; at: string };
  verifications: Verification[];
  closedAt?: string;
  cancellation?: { reason: string; by: Actor; at: string };
}

// ---------------------------------------------------------------- engine plumbing

export interface Violation {
  code: string;
  message: string;
  field?: string;
}

export type Result<T> =
  | { ok: true; value: T; warnings: Violation[] }
  | { ok: false; violations: Violation[] };

export interface EngineConfig {
  /** Internal default deadlines in days. NOT statutory. Pending Tarren's confirmation. */
  deadlineDays: Record<FindingSeverity, number>;
  inactivityDays: number;
  majorUnstartedHours: number;
  unstartedWindowFraction: number;
  minRationaleLength: number;
  hospitality: HospitalityConfig;
}

export interface HospitalityConfig {
  /** Points per status, 0..1. Provisional internal method. */
  points: Record<"conforming" | "observation" | "minor" | "major", number>;
  /** Minimum share of applicable criteria that must be assessed before any rating is given. */
  minCoverage: number;
  /** Score bands, highest first. Provisional. */
  bands: { minScore: number; label: string; favourable: boolean }[];
  /** Assessment statuses on a critical requirement that count as a critical gap. Pending Tarren. */
  criticalGapStatuses: AssessmentStatus[];
}

export interface EngineContext {
  now: string;
  actor: Actor;
  newId: () => string;
  config: EngineConfig;
}
