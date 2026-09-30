import type { AttachmentRef, EngineContext, Evidence, EvidenceKind, Result, Violation } from "./types.ts";
import { blank, fail, ok, v } from "./util.ts";

export const MAX_ATTACHMENT_BYTES = 50 * 1024 * 1024; // internal limit; adjust to R2/Worker limits in use

export interface NewEvidence {
  auditId: string;
  kind: EvidenceKind;
  description: string;
  reference?: string;
  attachment?: AttachmentRef;
}

/** Evidence is immutable once recorded. Correct it by adding new evidence, not editing old. */
export function createEvidence(input: NewEvidence, ctx: EngineContext): Result<Evidence> {
  const errors: Violation[] = [];
  if (blank(input.description)) errors.push(v("DESCRIPTION_REQUIRED", "Describe what this evidence shows.", "description"));
  const a = input.attachment;
  if (a) {
    if (blank(a.key)) errors.push(v("ATTACHMENT_KEY_REQUIRED", "Attachment storage key is missing.", "attachment.key"));
    if (blank(a.fileName)) errors.push(v("ATTACHMENT_NAME_REQUIRED", "Attachment file name is missing.", "attachment.fileName"));
    if (!(a.sizeBytes > 0)) errors.push(v("ATTACHMENT_EMPTY", "Attachment is empty.", "attachment.sizeBytes"));
    if (a.sizeBytes > MAX_ATTACHMENT_BYTES) errors.push(v("ATTACHMENT_TOO_LARGE", "Attachment exceeds the size limit.", "attachment.sizeBytes"));
  }
  if (errors.length) return fail(...errors);
  const warnings = !a && blank(input.reference)
    ? [v("EVIDENCE_UNTRACEABLE", "No attachment or reference. Add a document reference so the evidence can be traced.")]
    : [];
  return ok({ ...input, id: ctx.newId(), collectedBy: ctx.actor, collectedAt: ctx.now }, warnings);
}
