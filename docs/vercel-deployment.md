# Deploying the web app to Vercel

The deployable app is `apps/web` (Next.js 15, App Router). The Python API in `services/api` is a separate service and is not deployed to Vercel.

## Verified

- `npm run build` in `apps/web` passes: compile, lint, type check, and all 11 routes generate.
- No API keys or `.env*.local` files are tracked in git.

## Vercel project settings

| Setting | Value |
| --- | --- |
| Framework preset | Next.js (auto-detected) |
| Root directory | `apps/web` |
| Node.js version | 22.x (matches the root `engines` field, `>=22.6.0`) |
| Install command | `npm ci` (default) |
| Build command | `npm run build` (default) |
| Output directory | Next.js default (leave blank) |

## Environment variables

Set these in the Vercel project (Settings → Environment Variables). Never commit them.

| Name | Used by | Notes |
| --- | --- | --- |
| `NEXT_PUBLIC_API_URL` | Browser and server calls to the API (`src/lib/api.ts`) | Must be the public HTTPS URL of the hosted API. Defaults to `http://localhost:8000` if unset, which will not work on Vercel. |
| `OPENROUTER_API_KEY` | `src/app/api/audit-questions/route.ts` (server only) | Secret. Do not prefix with `NEXT_PUBLIC_`. |
| `OPENROUTER_MODEL` | Same route | Model identifier. |

## Blocker: the API is not public yet

`NEXT_PUBLIC_API_URL` points at `localhost:8000`, which is the developer laptop. The deployed site will load, but every page that calls the API will fail until `services/api` is hosted somewhere public (for example Render, Railway, or Fly.io) and its HTTPS URL is set above. The API's CORS list must also include the Vercel domain. It currently allows only localhost origins (`cors_origins` in `services/api/app/config.py`).

## Deploy steps

1. Commit and push to `origin/main` (see the git notes below before pushing).
2. In Vercel, import the GitHub repo and set Root Directory to `apps/web`.
3. Add the environment variables above, then deploy.
4. Check that the deployed pages render. Check the API-backed pages only after the API is hosted.

## Before pushing

- The business plan PDF (`AXIS_Environmental_Business_Plan_Hospitality_Launch.pdf`) exists only in unpushed local commits (74bd2eb to 2ee1fe9) and is deleted in the working tree. The repo is public, so it must be removed from those commits before pushing.
- Review the other deleted tracked files (`WHO_DOES_WHAT.md`, `IMPLEMENTATION_SUMMARY.md`) and the untracked `brand_kit/` and `apps/web/public/` before committing.
