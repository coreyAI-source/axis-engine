# AXIS Audit Engine

The shared rules core for all three AXIS modules (ISO, offshore, hospitality). The core is pure TypeScript with no database, network, clock or framework. Imported into `axis-engine/packages/engine` from the supplied ZIP. The new `server.ts` adapter now powers the FastAPI/Next.js hospitality pilot; see [integration notes](../../docs/engine-integration.md). The D1 example below is an illustrative adapter sketch, not this project's current backend.

```
npm test          # business rules, regressions and one full demo cycle per module
npm ci            # install locked type-checking dependencies
npm run typecheck
npm run demo      # regenerate the three fictional Markdown reports
```

Requires Node 22.6 or later (runs TypeScript directly) and TypeScript 5.8 or later for type-checking.

## Why a separate engine

- **One place for the rules.** Evidence requirements, rationale checks, finding and action lifecycles, deadlines, monitoring flags, closure and scoring are all enforced here, not scattered across UI and API handlers.
- **Testable without a browser.** Every rule has a fast unit test. Time and identity are passed in, so tests can say "48 hours later" without waiting.
- **Reusable later.** The offline field app can run the same rules on-device.

## How it works

Every change is a function call of the form `operation(record, input, expectedVersion, ctx)`. It returns either `{ ok: true, value, warnings }` or `{ ok: false, violations }`. It never throws for business-rule failures, and it never mutates its input.

`ctx` carries `now`, `actor`, `newId` and `config`. Each violation has a stable `code` for the UI to act on and a plain-English `message`.

| File | Covers |
|---|---|
| `requirements.ts` | Draft → competent-person review; revisions return to draft |
| `audits.ts` | Creation, ISO single/integrated disciplines, scope (approved only), status flow |
| `evidence.ts` | Immutable evidence records and R2 attachment references |
| `assessment.ts` | Six statuses, rationale and evidence rules, requirement snapshot, finding reconciliation |
| `findings.ts` | Withdraw (with rationale) and close (only after verified actions) |
| `actions.ts` | Internal default deadlines, progress, implementation evidence, independent verification |
| `monitoring.ts` | Overdue, 7-day inactivity, unstarted past half window, major unstarted 48 h |
| `hospitality.ts` | Provisional score with coverage gate and critical/major caps |
| `report.ts` | Readiness checks, completion, report model, Markdown export |

## Improvements over the earlier plan

1. **Concurrent edits are detected, not silently overwritten.** Mutable records have a `version`, and a stale write returns `VERSION_CONFLICT`. Enforce the same check in SQL as well (see below).
2. **History cannot be rewritten.** Assessments store a snapshot of the requirement text and source revision. Revising a requirement later doesn't change past audits.
3. **Findings are never deleted.** If an assessment changes, the finding stays open with `reviewRequired` until someone withdraws it with a rationale or closes it through verification.
4. **Separation of duties is recorded honestly.** Verification is labelled `enforced` only when the owner, submitter and verifier are all authenticated and the verifier has a different user ID from both the owner and submitter. The owner may submit their own implementation. Otherwise it is `declared_only`, and the report says so. The name check ignores case and extra spaces, so "sam owner" can't verify "Sam  Owner".
5. **Deadlines can't pose as statutory.** A deadline basis is either an internal default, custom (reason required) or external (source citation required).
6. **Hospitality rating gates.** Any major finding or critical gap caps the rating as non-favourable. Low coverage or an unassessed critical criterion gives "Incomplete: not rated"; a diagnostic score may still be shown. Every hospitality report carries the provisional-method note.
7. **Completion is gated.** An audit can't be completed with unassessed criteria, findings without actions, or findings awaiting review. A completed audit is locked.
8. **No content is invented.** The engine ships no standards content. Demo data is all labelled DEMO, with fictional clause numbers.

## Wiring it into a D1 route (sketch)

```ts
const row = await db.prepare("SELECT data FROM assessments WHERE id = ?").bind(id).first();
const res = assess(JSON.parse(row.data), audit, requirement, evidence, input, body.expectedVersion, ctx);
if (!res.ok) return Response.json({ violations: res.violations }, { status: 422 });

// Enforce the version in the database too; two requests can pass the engine check at the same moment.
const upd = await db.prepare("UPDATE assessments SET data = ?, version = ? WHERE id = ? AND version = ?")
  .bind(JSON.stringify(res.value), res.value.version, id, body.expectedVersion).run();
if (upd.meta.changes === 0) return Response.json({ violations: [{ code: "VERSION_CONFLICT" }] }, { status: 409 });

// Save findings from reconcileFindings(...) in the same D1 batch.
```

Build `ctx.actor` from the platform session on the server, never from the request body. Access control (which user or organisation may see which audit) stays in the route layer. Filter by it on every query.

## Decisions still needed (placeholders in `config.ts`)

- **Tarren:** major/minor default days (14/30 for now), what counts as a "critical gap", hospitality points, bands and minimum coverage.
- **Corey:** whether an audit may be completed while actions remain open (currently allowed, with a warning).
- **Design question:** the hospitality rating reflects conditions *at audit time*, so a major finding caps the rating even after its action is closed. Confirm that this is what you want.

## Not yet verified

The hospitality adapter is connected to new tenant-owned PostgreSQL aggregates through the Python API. Older ISO and mobile workflows still need their own integration. The initial hotel criteria are fictional, and business policy and real standard content need review before client use. See the [project testing guide](../../docs/testing.md) for scope and setup.
