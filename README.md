# EvidenceVault AI

EvidenceVault AI is a secure evidence management system for uploading, organizing, OCR processing, timeline generation, search, and PDF export.

## Product Direction

EvidenceVault is being evolved into a community-driven vulnerability disclosure and evidence management platform with:

- Public browsing and search for reports and organizations
- Authenticated submission, voting, commenting, and saved items
- Separate admin analytics and moderation surfaces
- Strong security, accessibility, and performance foundations

## Implementation Plan

### Phase 1: Platform foundation

- Refactor the backend data model to support organizations, reports, categories, comments, votes, sessions, profiles, badges, and audit logs.
- Introduce a public read-only API for landing pages, exploration, trending content, and organization profiles.
- Keep the existing evidence workflow working during the transition.

### Phase 2: Public discovery experience

- Rebuild the landing page with hero content, live stats, trending cases, latest reports, featured organizations, and category browsing.
- Add an Explore experience with search, filters, sorting, and pagination or infinite scroll.
- Redesign case detail pages as report pages with evidence galleries, timelines, related reports, and discussion.

Current frontend routes now reflect the split between public and private surfaces:

- `/` public landing page
- `/explore` public browsing and discovery
- `/dashboard` authenticated workspace
- `/cases/[id]` authenticated case detail

### Phase 3: Submission and account workflows

- Replace the current one-step case form with a multi-step vulnerability submission flow.
- Add organization selection and creation during submission.
- Add profile management, session management, password reset, and email verification flows.

### Phase 4: Community and trust systems

- Add nested comments, voting, reputation, badges, and researcher ranking.
- Add saved reports, followed organizations, notification preferences, and activity dashboards.

### Phase 5: Admin area

- Build a separate admin application surface for moderation, analytics, summaries, and content governance.
- Add executive dashboards with charts and operational views.

### Phase 6: Hardening

- Add rate limiting, CSRF protection, role-based access control, audit logging, and stronger validation.
- Improve loading states, accessibility, keyboard navigation, and performance.
- Add database migrations and update documentation as the schema evolves.

## Structure

- `backend/` FastAPI, SQLModel, PostgreSQL, OCR, PDF export
- `frontend/` SvelteKit, TypeScript, Bun, TailwindCSS
- `infra/` Docker Compose deployment
- `docs/` Architecture notes

## Run locally

Backend:

1. Create a PostgreSQL database.
2. Set environment variables from `.env.example`.
3. Install backend deps and dev extras with `uv` or `python -m pip install -e ".[dev]"`.
4. Run `uvicorn app.main:app --reload` from `backend/`.

Frontend:

1. Install dependencies with `bun install` from `frontend/`.
2. Set `PUBLIC_API_BASE_URL` to the backend API URL.
3. Run `bun run dev`.

## Current Status

The repository still includes the original evidence-case workflow. The next code changes will refactor the backend and frontend incrementally so the existing features remain available while the new public, community, and admin surfaces are introduced.

The first implementation slice now includes a public report discovery API on the backend and a public landing page plus explore page on the frontend.

## Docker

Run the full stack with:

```bash
docker compose -f infra/docker-compose.yml up --build
```
