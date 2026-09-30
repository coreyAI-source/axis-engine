import axios from "axios";
import { api } from "./api";

export type AssessmentStatus = "unassessed" | "conforming" | "observation" | "minor" | "major" | "not_applicable";
export interface Member { id: string; organisation_id?: string; name: string; email: string; role_code: string }
export interface AuditSummary { id: string; title: string; site_name: string; status: string; version: number; updated_at: string }
export interface Actor { name: string; userId?: string; authenticated: boolean }
export interface Source { documentId: string; documentTitle: string; revision: string; section?: string; clause?: string; page?: string }
export interface Requirement { id: string; version: number; text: string; title?: string; indicators?: string[]; guidance?: string[]; category?: string; auditPrompt?: string; source: Source; reviewStatus: string; reviewNote?: string; critical?: boolean; weight?: number }
export interface Template { id: string; version: string; title: string; fictional: boolean; disclaimer: string }
export interface Assessment { id: string; requirementId: string; status: AssessmentStatus; rationale: string; evidenceIds: string[]; assessedAt?: string; assessedBy?: Actor }
export interface Evidence { id: string; kind: string; description: string; reference?: string; collectedAt: string; collectedBy: Actor; attachment?: { fileName: string; sizeBytes: number; contentType: string } }
export interface Finding { id: string; requirementId: string; severity: string; statement: string; status: string; raisedAt: string; reviewRequired?: { reason: string }; withdrawal?: { rationale: string }; snapshot: { text: string } }
export interface CorrectiveAction { id: string; findingId: string; description: string; owner: Actor; dueDate: string; status: string; deadlineBasis: { kind: string; days?: number; reason?: string; reference?: string }; updates: { at: string; by: Actor; note: string }[]; implementation?: { note: string; evidenceIds: string[]; submittedBy: Actor }; verifications: { at: string; verifier: Actor; outcome: string; note: string; separation: string }[] }
export interface Violation { code: string; message: string }
export interface AuditReport {
  generatedAt: string; draft: boolean;
  audit: { title: string; siteName: string; scopeStatement?: string; status: string; leadAuditor: string; startDate: string; endDate?: string };
  counts: Record<AssessmentStatus, number>;
  hospitality?: { score: number | null; coverage: number; rating: string; favourable: boolean; methodNote: string; blockers: string[]; categories: { category: string; score: number | null; assessed: number; applicable: number }[] };
  readiness: { ready: boolean; blockers: Violation[]; warnings: Violation[] };
  disclaimers: string[];
  items: { requirementId: string; requirementText: string; source: Source; status: AssessmentStatus; rationale: string; evidence: { id: string; description: string; reference?: string; fileName?: string }[]; findings: { id: string; severity: string; status: string; statement: string; actions: { id: string; description: string; owner: string; dueDate: string; deadlineNote: string; status: string; flags: string[]; verification?: string }[] }[] }[];
}
export interface AuditDetail {
  id: string; version: number; updated_at?: string; warnings?: Violation[];
  bundle: {
    audit: { id: string; title: string; siteName: string; status: string; scopeStatement?: string; requirementIds: string[]; leadAuditor: Actor; history: { at: string; event: string; actor: Actor }[] };
    requirements: Requirement[]; assessments: Assessment[]; evidence: Evidence[]; findings: Finding[]; actions: CorrectiveAction[];
    config?: { minRationaleLength?: number; deadlineDays?: { minor: number; major: number } };
    template?: Template;
  };
  report: AuditReport;
}

export const hospitality = {
  me: () => api.get<Member>("/hospitality/me"),
  members: () => api.get<Member[]>("/hospitality/members"),
  addMember: (input: { first_name: string; last_name: string; email: string; password: string; role_code: string }) => api.post<Member>("/hospitality/members", input),
  list: () => api.get<AuditSummary[]>("/hospitality/audits"),
  create: (input: { title: string; site_name: string; scope_statement: string }) => api.post<AuditDetail>("/hospitality/audits", input),
  get: (id: string) => api.get<AuditDetail>(`/hospitality/audits/${encodeURIComponent(id)}`),
  command: (id: string, version: number, operation: string, input: object = {}) => api.post<AuditDetail>(`/hospitality/audits/${encodeURIComponent(id)}/commands`, { expected_version: version, operation, input }),
  upload: (id: string, version: number, file: File, description: string) => {
    // Windows may label CSV files as Excel data or leave text files untyped.
    const extension = file.name.split(".").pop()?.toLowerCase();
    const types: Record<string, string> = { csv: "text/csv", txt: "text/plain", pdf: "application/pdf", png: "image/png", jpg: "image/jpeg", jpeg: "image/jpeg" };
    const type = types[extension || ""] || file.type;
    const uploadFile = type === file.type ? file : new File([file], file.name, { type });
    const body = new FormData(); body.append("file", uploadFile); body.append("expected_version", String(version)); body.append("description", description);
    return api.post<AuditDetail>(`/hospitality/audits/${encodeURIComponent(id)}/files`, body, { headers: { "Content-Type": undefined } });
  },
  file: (id: string, evidenceId: string) => api.get<Blob>(`/hospitality/audits/${encodeURIComponent(id)}/files/${encodeURIComponent(evidenceId)}`, { responseType: "blob" }),
  report: (id: string) => api.get<Blob>(`/hospitality/audits/${encodeURIComponent(id)}/report`, { params: { format: "markdown" }, responseType: "blob" }),
};

export function apiError(error: unknown): string {
  if (!axios.isAxiosError(error)) return error instanceof Error ? error.message : "Something went wrong. Please try again.";
  if (!error.response) return "The API could not be reached. Check that the API is running, then retry. Your unsaved input is still here.";
  const detail = error.response.data?.detail;
  if (Array.isArray(detail)) return detail.map((item) => item.message || item.msg || "Invalid input").join(" ");
  if (typeof detail === "string") return detail;
  if (error.response.status === 403) return "Your account does not have permission for this action.";
  return `The request failed (${error.response.status}). Please retry.`;
}
export const httpStatus = (error: unknown) => axios.isAxiosError(error) ? error.response?.status : undefined;
export const canAudit = (member: Member | null) => !!member && ["admin", "compliance_manager", "lead_auditor", "auditor"].includes(member.role_code);
export const canReview = (member: Member | null) => !!member && ["admin", "compliance_manager", "lead_auditor"].includes(member.role_code);
export const label = (value: string) => value.replace(/_/g, " ").replace(/^\w/, (character) => character.toUpperCase());
export const dateTime = (value?: string) => value ? new Date(value).toLocaleString() : "—";
export const sourceLabel = (source: Source) => [source.documentTitle, `revision ${source.revision}`, source.section && `section ${source.section}`, source.clause && `clause ${source.clause}`, source.page && `page ${source.page}`].filter(Boolean).join(" · ");
export const statusLabels: Record<AssessmentStatus, string> = { unassessed: "Not assessed", conforming: "Conforming", observation: "Observation", minor: "Minor finding", major: "Major finding", not_applicable: "Not applicable" };
export const statusTone: Record<AssessmentStatus, string | undefined> = { unassessed: undefined, conforming: "green", observation: "blue", minor: "amber", major: "red", not_applicable: "slate" };

export const criterionHeading = (r: Requirement) => r.title ? [r.source.clause, r.title].filter(Boolean).join(" ") : r.text;
export function criterionStatement(r: Requirement) {
  const prefix = `${criterionHeading(r)} — `;
  return r.title && r.text.startsWith(prefix) ? r.text.slice(prefix.length) : r.text;
}
const GUIDELINE_MARK = /\s*\(See Guidelines\)\s*$/;
/** Pairs each published indicator with its numbered Annex guideline, if any. */
export function indicatorsWithGuidance(r: Requirement) {
  const numbered = new Map<number, string>();
  const notes: string[] = [];
  for (const entry of r.guidance || []) {
    const match = /^(\d+)\.\s+([\s\S]*)$/.exec(entry);
    if (match) numbered.set(Number(match[1]), match[2]); else notes.push(entry);
  }
  return { notes, indicators: (r.indicators || []).map((text, index) => ({ text: text.replace(GUIDELINE_MARK, ""), guidance: numbered.get(index + 1) })) };
}
export function saveBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob); const link = document.createElement("a"); link.href = url; link.download = filename; document.body.appendChild(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
}
