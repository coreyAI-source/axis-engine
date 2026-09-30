# Hotel audit pilot: run it and show your dad

The hospitality pilot connects the website to the shared audit engine through the Python API and saves its records in your configured PostgreSQL database. New audits start with the **40 criteria of the GSTC Hotel Standard v4.0** and their performance indicators. A new audit starts in progress, with no assessments, evidence, findings or actions already filled in. Criteria that don't apply to the property (e.g. A11/A12 when there is no construction) are marked Not applicable with a reason. The result is an internal assessment; only GSTC-accredited certification bodies certify hotels.

## Start the updated app

Keep the project's existing `services/api/.env`. Your working setup uses Neon, so you do not need a local Docker database for this pilot. The new hospitality evidence uploads are stored privately in the database, so they do not need MinIO either. The older evidence routes and background workers still have their own infrastructure requirements.

Node.js 22.6 or later must be available to the API process as well as to the web development server. The Python API invokes the engine using Node. Keep the full `packages/engine` directory with the API source.

In a terminal starting from `axis-engine`:

```powershell
cd services/api
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

The migration adds the new hospitality tables to the database selected in `.env`. It does not require resetting the existing database. If your login already works, there is no need to run the seed again. Keep this terminal running.

In a second terminal starting from `axis-engine`:

```powershell
cd apps/web
npm run dev
```

Open http://localhost:3000 and use your existing login. Choose **Hospitality**, or open http://localhost:3000/hospitality. Use the port printed by the web terminal if it differs from 3000. Restart both services after pulling changes if you ran them without automatic reload.

## A short demonstration

Use a fictional hotel, for example **Bali Practice Hotel**, and test files containing no real guest or employee information.

1. In **Hospitality**, choose **New hotel audit**. Enter a hotel name, title and scope, such as "Fictional training hotel; guest rooms and housekeeping; September 2026."
2. Open **Criteria**: all 40 GSTC Hotel Standard v4.0 criteria are listed by section (A–D). Expand one to show its performance indicators and the matching GSTC guidelines. Custom criteria (e.g. a local regulation) start as drafts and need a reviewer before they can be assessed. The [GSTC review notes](gstc-hotel-review.md) list the decisions your dad still needs to make.
3. Open **Evidence**. Add a small PDF, JPEG, PNG, text file or CSV with a useful description. Hospitality uploads are limited to 10 MB per file. Use factual observation/interview notes where appropriate; a file name alone does not establish that a requirement is met.
4. Open **Assessments**. Select a criterion, choose the evidence, enter the reasoning and save a result. Record one minor or major finding deliberately so that the corrective-action workflow can be shown. A not-applicable result needs a defensible explanation.
5. Refresh the page and reopen the audit from the list. The saved assessment and evidence should still be present. Download an attachment to confirm its contents are retained.
6. In **Findings & actions**, assign a corrective action to a team member. Record progress, attach implementation evidence, then **Submit for verification**.
7. Sign in as a different eligible user. Choose **Verify effective** with a meaningful note, or **Return for more work** to demonstrate failed verification. The owner and the person who submitted implementation cannot verify their own action. Close the finding after the action is properly closed.
8. In **Report**, inspect remaining blockers, choose **Move to reporting**, and **Complete audit** when the engine permits it. Assess every criterion in scope, including a reason for each exclusion, and assign actions to findings. Actions can remain open after an audit completes; completing the audit does not mean every problem has been corrected. Download the Markdown report or use **Print / save PDF** for the browser's print dialog.

Use **Team accounts** on the Hospitality list while signed in as an administrator to create a second account. A **Lead auditor** can review and verify; a **Process owner** can own corrective actions. Use distinct people for a real pilot. Merely creating two accounts for the same person does not create genuine independence. New account passwords must meet the displayed requirements (at least 12 characters).

Closing an action does not erase the original finding from the historical assessment. The report can continue to show a non-favourable result after the problem has been corrected because it describes the audit-time result and the later corrective work separately. Scoring and deadlines remain provisional AXIS rules, not GSTC certification rules. The 90% threshold for the provisional score is distinct from the completion checks, which require every scoped criterion to have a recorded assessment or justified exclusion. Each audit retains the engine configuration it started with.

## What to check together

- [ ] A hotel audit saves and can be reopened after logging out and back in.
- [ ] Evidence downloads match the uploaded files.
- [ ] A supported assessment includes clear reasoning and the right evidence.
- [ ] Missing required evidence or explanations produce useful validation messages.
- [ ] An action has a named owner, deadline, progress, implementation evidence and verification.
- [ ] The action owner cannot verify their own work.
- [ ] A failed verification returns work to the owner and is recorded in the history.
- [ ] Report blockers prevent premature completion.
- [ ] The exported report is understandable to your dad and clearly identifies the demonstration criteria and provisional score.
- [ ] A major finding remains visible even after its action closes.

## If something fails

| Symptom | Check |
| --- | --- |
| Browser says it cannot reach the API | Keep the uvicorn terminal open; check http://localhost:8000/health; inspect the API terminal error. The website and API are separate processes. |
| Login works but Hospitality reports missing tables | Run `alembic upgrade head` from `services/api` against the same `.env` used by uvicorn. |
| Hospitality engine is unavailable | Run `node --version` in the API terminal; Node 22.6+ and `packages/engine` must be accessible to that process. |
| Changes conflict with a newer version | Refresh/reopen the audit before retrying; another update may have saved first. |
| Verification is refused | Use a different eligible authenticated user from both the action owner and implementation submitter. |
| Completion is refused | Read the returned blockers and finish the required assessment/action stages. Do not change the rules just to hide the blocker. |
| An upload is refused | Use an allowed file type, check the 10 MB limit, and avoid empty files. |

The frontend API address is controlled by `NEXT_PUBLIC_API_URL` and defaults to `http://localhost:8000`. If you change a frontend environment setting, restart its development server. A shared/public deployment needs the browser-accessible API address, not `localhost`.

## Deployment preparation

This local pilot is not itself a live deployment. The current runtime layout is:

```text
Browser -> Next.js web app -> Python FastAPI -> PostgreSQL/Neon
                                  |
                                  +-> Node 22 shared audit engine
```

The API host needs both Python and Node, the engine files, database credentials and a strong signing secret. Its authenticated evidence downloads read the new hospitality attachment records from the database. The web host needs `NEXT_PUBLIC_API_URL` set to the HTTPS API URL; the API must allow the actual web origin through its CORS configuration.

A container host is a straightforward fit for this API layout. A frontend may be hosted separately, including on Vercel, but moving only the Next.js project does not deploy the database or the Python/Node backend. Do not assume an unchanged Python-only serverless deployment can invoke Node or locate the engine package.

An API container recipe is included at `infra/Dockerfile.api`, with `.dockerignore` excluding local credentials and development files. From `axis-engine`, build with `docker build -f infra/Dockerfile.api -t axis-api .`. Docker execution is not verified on this computer. The container includes both runtimes and runs as a non-root user. Configure the two database URLs, a private `SECRET_KEY` and `CORS_ORIGINS` (a JSON list of allowed HTTPS website origins) through your host. Run `python -m alembic upgrade head` as a release/migration step before starting the container. `AUTO_CREATE_TABLES=false` disables development schema creation in the container.

Before a shared pilot, choose the host and region, set secrets through the host's protected environment settings, migrate the intended database, replace public demonstration credentials, and verify login, organisation isolation, uploads and report export over HTTPS. The new hospitality access controls should be assessed in the context of the complete application; they do not prove every older route is production-ready.

### Backups and recovery

No backup schedule or paid provider plan has been configured by this implementation. Confirm the database provider's actual retention and restore settings for the selected project. Define a recovery-point target (how much recent work can be lost) and a recovery-time target (how quickly service must recover).

For this pilot the new hospitality audit bundles and attachment bytes live in PostgreSQL, so they must be included in a database backup. Keep encrypted backups in a separate controlled location, restrict access, and test a restore into a separate database before relying on the procedure. Application source and migration files also need versioned backups; private `.env` values belong in a secrets manager or an access-controlled recovery record, not Git.

If the older MinIO evidence routes are used, back up that object storage separately and test that restored records can retrieve the matching objects. Define retention/deletion rules before uploading real personal information.

## Still needed before real client use

- Your dad's approval of the audit scope, source interpretation, evidence rules, severity, scoring, deadlines and final report.
- A complete reviewed hotel-standard pack, with any required commercial-use permission confirmed. The demonstration pack is not a substitute for all GSTC criteria and indicators.
- A real pilot with two suitably competent people and feedback on the workflow.
- A selected hosting environment, production secrets, verified backup recovery, monitoring, account lifecycle and a wider security review.
- Production evidence controls such as malware scanning, retention policy and capacity planning before accepting arbitrary client files at scale.

Mobile/offline auditing, email notifications and external certification-body integrations remain separate work. Nothing in this pilot claims GSTC accreditation, formal certification or approval by Control Union.
