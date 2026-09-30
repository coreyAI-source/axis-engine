# Shared engine integration

## Hospitality pilot update (29 September 2026)

The new `/hospitality` screens call dedicated FastAPI routes backed by `hospitality_audits` and `hospitality_files`. Python validates request schemas, session identity, roles and organisation ownership, then invokes `packages/engine/src/server.ts` using Node. The server loads the saved bundle rather than trusting client-supplied records. Each update checks the aggregate version atomically in PostgreSQL; uploads commit metadata and bytes together. Each audit stores the scoring configuration it started with.

New hotel audits use the GSTC Hotel Standard v4.0 criteria from `gstc-hotel.ts` / `gstc-hotel-v4-data.ts`; audits saved with the earlier fictional pilot template still load. Custom criteria start as drafts and need an eligible reviewer. See [the review notes](gstc-hotel-review.md). Older ISO/mobile routes still use their existing Python business logic.

The import notes below describe the original ZIP baseline. For running and deploying the current pilot, use [the hotel walkthrough](hospitality-pilot.md).

## What was imported

Source: the user-supplied `axis-engine.zip`, reviewed on 28 September 2026. Its TypeScript source, tests, fictional report examples and README live in `packages/engine/`. Existing API, web, mobile, ISO reference documents and private environment files were preserved.

The ZIP is a standalone library, not an upgrade of the current web app. Its embedded setup/architecture notes were treated as reference material. In particular, no Cloudflare D1/R2/Vinext migration was performed: this project currently uses Python/FastAPI, PostgreSQL and MinIO.

## Available rules

- Draft requirements and reviewer approval before adding criteria to audits.
- Single/integrated ISO scope, offshore and hospitality modules.
- Evidence and rationale checks, version checks and historical requirement snapshots.
- Minor/major finding reconciliation, withdrawal reasons and corrective actions.
- Implementation evidence, verifier independence and closure checks.
- Deadline basis tracking, inactivity/overdue flags and report completion gates.
- Provisional hospitality coverage/rating rules and Markdown reports.

The library does not provide persistence, authentication, tenant access checks, uploads or a user interface. Caller-supplied identity must come from a verified server session. Database updates must enforce the expected version atomically and save related records in a transaction. A TypeScript type check is not runtime validation of an HTTP request.

## Improvements made during import

The package now declares its TypeScript/Node type dependencies and runtime version, and the project root provides test, demo, setup and type-check commands. Regression fixes address completed scope changes, duplicate criteria, cross-audit references, critical unassessed hospitality criteria and report-readiness integrity. The direct completion bypass was removed; snapshots preserve scoring metadata and prompts; missing criteria stay visible in reports; invalid weights and falsely labelled default deadlines are rejected. The tests are the executable record of these rules.

Local Compose infrastructure and API/mobile environment samples were also added because the previous README referenced missing setup files. Their credentials are local demo defaults; existing `.env` files were not changed.

## Decisions before connecting live workflows

1. Choose how the Python API will invoke or share the TypeScript rules (a service boundary or a carefully tested Python equivalent). Adding the package alone does not change backend behavior.
2. Map requirements, snapshots, evidence, findings, actions and record versions to the existing database, then add reviewed migrations and API integration tests. The current schemas do not match the ZIP one-for-one.
3. Confirm deadline policy: the imported engine defaults to **14 days major / 30 minor**; the Python API currently defaults to **90 days major / 30 minor / 60 observation**. These have deliberately not been silently unified.
4. Confirm hospitality weights, score bands, 90% minimum coverage and the definition of a critical gap. These are provisional internal settings, not certified or statutory ratings.
5. Confirm whether an audit can complete with open actions. The imported engine permits this with a warning when other readiness checks pass. Findings/actions continue to require their own closure steps.
6. Finish tenant/role authorization, action verification enforcement in the API, idempotent finding creation, web audit/report screens and mobile setup before a shared pilot.

Before production use, also make finding reconciliation idempotent after closure/withdrawal, validate loaded records at the persistence boundary, and retain the scoring configuration used for each audit so changing policy cannot change a historical rating.

The engine demos' criteria and evidence references are fictional. Apart from the GSTC Hotel Standard library, no real standards text, legal obligations, uploaded evidence files or customer records are added by the demos.
