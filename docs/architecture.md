# Architecture Overview

EvidenceVault uses a monorepo with a separate frontend and backend, joined by a Docker Compose deployment.

## Backend

- FastAPI for REST APIs
- SQLModel for ORM and schema modeling
- PostgreSQL as the primary database
- Local filesystem storage for MVP uploads
- Tesseract OCR for image and PDF text extraction
- ReportLab for PDF report generation

## Frontend

- SvelteKit + TypeScript
- Bun for package management and runtime
- TailwindCSS for dashboard styling
- Cookie-based auth through the FastAPI backend

## Data flow

1. User registers or logs in.
2. Case is created and persisted in PostgreSQL.
3. Evidence is uploaded to local disk.
4. OCR extracts text and stores it with the evidence row.
5. Timeline events are generated from extracted text.
6. Search and export operate over case-scoped data.
