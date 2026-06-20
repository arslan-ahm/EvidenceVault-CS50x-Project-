# EvidenceVault AI

EvidenceVault AI is a secure evidence management system for uploading, organizing, OCR processing, timeline generation, search, and PDF export.

## Structure

- `backend/` FastAPI, SQLModel, PostgreSQL, OCR, PDF export
- `frontend/` SvelteKit, TypeScript, Bun, TailwindCSS
- `infra/` Docker Compose deployment
- `docs/` Architecture notes

## Run locally

Backend:

1. Create a PostgreSQL database.
2. Set environment variables from `.env.example`.
3. Install backend deps with `uv`.
4. Run `uvicorn app.main:app --reload` from `backend/`.

Frontend:

1. Install dependencies with `bun install` from `frontend/`.
2. Set `PUBLIC_API_BASE_URL` to the backend API URL.
3. Run `bun run dev`.

## Docker

Run the full stack with:

```bash
docker compose -f infra/docker-compose.yml up --build
```
