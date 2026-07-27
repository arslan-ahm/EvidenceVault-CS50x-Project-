🛡️ EvidenceVault AI — Community Vulnerability Disclosure Platform
==================================================================

**Report it. Prove it. Track it.**
A full-stack platform for submitting, verifying, and tracking security vulnerability reports — with OCR-powered evidence processing, auto-generated timelines, and a public disclosure feed. Built as a CS50x final project. 🎓🔐

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![SvelteKit](https://img.shields.io/badge/SvelteKit-FF3E00?style=for-the-badge&logo=svelte&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Bun](https://img.shields.io/badge/Bun-000000?style=for-the-badge&logo=bun&logoColor=white)
![Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)
![License](https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge)

---

## ✨ What's the Vibe?

EvidenceVault AI is what happens when a bug-bounty disclosure feed meets a digital-evidence locker. Security researchers submit vulnerability reports with real evidence (screenshots, PDFs, logs) — the backend OCRs the files, auto-builds a timeline from whatever dates it finds in the text, and the whole thing becomes a searchable, upvotable, publicly browsable report. Admins get a moderation dashboard. Everyone else gets a clean, dark-mode-friendly feed of what's happening. 🕵️‍♂️📄

| 🎯 You Get This | 📦 Without the Bloat |
|---|---|
| ✅ Public disclosure feed — browse, search & filter reports | ❌ No login wall for read-only access |
| ✅ OCR-powered evidence — text pulled straight out of screenshots & PDFs | ❌ No manual transcription |
| ✅ Auto-generated timelines — dates detected in evidence become a case timeline | ❌ No manual timeline building |
| ✅ Organizations, categories, upvotes & threaded comments | ❌ No flat, context-free report list |
| ✅ Cookie + JWT auth, with optional Supabase auth | ❌ No sketchy homegrown session handling |
| ✅ Admin dashboard — stats, user/case/comment moderation | ❌ No digging through a database by hand |
| ✅ Cloudflare Turnstile on auth routes | ❌ No bot-flooded signups |
| ✅ PDF case export via ReportLab | ❌ No screenshotting your dashboard |
| ✅ Dark mode, done right 🌙 | ❌ No eye strain |

## 🎨 Features at a Glance

| 🔥 Feature | 💬 What It Does |
|---|---|
| 🧠 Modern stack | FastAPI + SQLModel on the backend, SvelteKit 5 + TypeScript on the frontend |
| 🔍 OCR pipeline | `pytesseract` for images, `pdfplumber` for PDFs — extracted text is stored alongside each evidence item |
| 🗓️ Auto timelines | Dates found inside extracted evidence text are turned into ordered case timeline events |
| 🌍 Public explore feed | Anonymous browsing, search, filtering, sorting over public reports and organizations |
| 🔐 Full auth flow | Register, login, forgot/reset password (emailed), change password, session cookies |
| 🏢 Organizations | Reports can be linked to affected organizations with their own public profile |
| 💬 Community layer | Threaded comments and upvotes on every report |
| 🛠️ Admin surface | Platform-wide stats, user bans, case & comment moderation, cascading deletes |
| ☁️ Flexible storage | Evidence uploads go to MEGA when configured, falling back to local disk otherwise |
| 📤 PDF export | Generate a shareable PDF report for any case with ReportLab |
| 🚦 Rate limiting | In-memory rate limiter on top of `slowapi` guards the API from abuse |

## 🧰 Tech Stack

| 🏗️ Layer | 🔧 Technology |
|---|---|
| 🖥️ Frontend | SvelteKit 5, TypeScript, Vite 6 |
| 🎨 Styling | Tailwind CSS 3 + custom theme tokens, dark mode via `data-theme` |
| ✨ UX polish | GSAP for animation, `marked` + `DOMPurify` for safe markdown rendering |
| ⚙️ Backend | FastAPI, SQLModel (SQLAlchemy) |
| 🗄️ Database | PostgreSQL (Supabase-hosted) |
| 🔑 Auth | JWT (`python-jose`) + HTTP-only cookies, optional Supabase Auth passthrough |
| 🔍 OCR / parsing | Tesseract (`pytesseract`), `pdfplumber` |
| 📄 PDF export | ReportLab |
| ☁️ File storage | MEGA (`mega.py`), local disk fallback |
| 🤖 Anti-abuse | Cloudflare Turnstile, `slowapi` + custom in-memory rate limiter |
| 📧 Email | SMTP (welcome / reset / change-password emails) |
| 📦 Package management | `uv` (backend), `bun` (frontend) |
| 🚀 Deployment | Vercel (frontend + backend on one domain) · Docker Compose (self-hosted) |

## 📁 Project Layout

```
EvidenceVault/
├── 📂 api/
│   └── 📄 index.py                  # 🚀 Vercel serverless entrypoint (wraps backend/app)
├── 📂 backend/
│   ├── 📂 app/
│   │   ├── 📂 api/
│   │   │   ├── 📂 routes/           #   admin, auth, cases, categories, comments,
│   │   │   │                        #   evidence, health, organizations, public, search, votes
│   │   │   └── 📄 deps.py           #   Shared FastAPI dependencies (auth, etc.)
│   │   ├── 📂 core/                 #   Settings, security, rate limiting
│   │   ├── 📂 db/                   #   Engine/session + schema init & seeding
│   │   ├── 📂 models/               #   SQLModel tables (case, evidence, user, org, ...)
│   │   ├── 📂 schemas/               #   Pydantic request/response schemas
│   │   ├── 📂 services/             #   OCR, storage, email, timeline, MEGA, Turnstile
│   │   ├── 📂 utils/                 #   File validation helpers
│   │   └── 📄 main.py               #   FastAPI app + middleware
│   ├── 📂 tests/                    #   Pytest suite
│   ├── 📄 Dockerfile
│   └── 📄 pyproject.toml
├── 📂 frontend/
│   ├── 📂 src/
│   │   ├── 📂 routes/
│   │   │   ├── 📂 (public)/         #   🌍 Landing, explore, login, register, password reset
│   │   │   └── 📂 (app)/            #   🔒 Dashboard, case detail, profile, admin
│   │   └── 📂 lib/
│   │       ├── 📂 components/       #   Navbar, Sidebar, EvidenceUpload, Lightbox, ...
│   │       ├── 📂 stores/           #   Auth & theme stores
│   │       └── 📄 api.ts            #   Typed fetch wrapper for the backend API
│   ├── 📄 Dockerfile
│   ├── 📄 svelte.config.js
│   └── 📄 package.json
├── 📂 infra/
│   └── 📄 docker-compose.yml        # 🐳 Full local stack (Postgres + backend + frontend)
├── 📂 docs/
│   └── 📄 architecture.md
├── 📄 requirements.txt              # 🚀 Vercel Python function dependencies
├── 📄 vercel.json                   # 🚀 Vercel build + routing config
└── 📄 README.md
```

## 🚀 Getting Started Locally

### 📋 What You'll Need

| ✅ Prerequisite | ℹ️ Why? |
|---|---|
| Python ≥ 3.11 | Runs the FastAPI backend |
| [uv](https://github.com/astral-sh/uv) | Fast Python package manager |
| [Bun](https://bun.sh) ≥ 1.1 | Frontend package manager & dev server |
| PostgreSQL | Primary database (or point `DATABASE_URL` at a hosted instance, e.g. Supabase) |
| Tesseract OCR | Only needed if you want image OCR working locally |

### 🏃 Backend

```bash
cd backend
uv pip install -e ".[dev]"          # or: python -m pip install -e ".[dev]"
cp ../.env.example ../.env          # fill in DATABASE_URL, JWT_SECRET_KEY, etc.
uvicorn app.main:app --reload
```

The API comes up on `http://localhost:8000`, mounted under `/api`.

### 🎨 Frontend

```bash
cd frontend
bun install
bun run dev
```

Open `http://localhost:5173` — set `PUBLIC_API_BASE_URL=http://localhost:8000/api` in `.env` first.

### 🐳 Or just Docker Compose

```bash
docker compose -f infra/docker-compose.yml up --build
```

Spins up Postgres, the FastAPI backend, and the SvelteKit frontend together.

## 🌍 Environment Variables

Copy `.env.example` to `.env` at the repo root and fill in what you need — every variable has a safe local default except the database.

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ Yes | PostgreSQL connection string |
| `JWT_SECRET_KEY` | ✅ Yes (prod) | Secret used to sign auth tokens |
| `FRONTEND_ORIGIN` | ✅ Yes | Allowed CORS origin for the frontend |
| `PUBLIC_API_BASE_URL` | ✅ Yes | Base URL the frontend calls for the API |
| `COOKIE_SECURE` / `COOKIE_SAMESITE` | ❌ Optional | Cookie flags — `true` + `lax` in production |
| `UPLOADS_DIR` | ❌ Optional | Local evidence storage path (`/tmp/uploads` on Vercel) |
| `MEGA_UPLOADS_EMAIL` / `MEGA_UPLOADS_PASSWORD` | ❌ Optional | Enables remote evidence storage via MEGA |
| `SMTP_HOST` / `SMTP_PORT` / `SMTP_USERNAME` / `SMTP_PASSWORD` | ❌ Optional | Enables outgoing email (reset/welcome) |
| `SUPABASE_URL` / `SUPABASE_*` | ❌ Optional | Alternative auth provider |
| `CLOUDFLARE_TURNSTILE_SECRET` / `PUBLIC_TURNSTILE_SITE_KEY` | ❌ Optional | Enables CAPTCHA on register/login |

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         🌐 One Vercel domain                       │
│  ┌────────────────────────┐        ┌───────────────────────────┐ │
│  │   🎨 SvelteKit (SPA)     │  fetch │   ⚙️ FastAPI (serverless)   │ │
│  │  static build, served   │──────▶│   /api/* → api/index.py     │ │
│  │  from the CDN edge      │  /api  │                             │ │
│  └────────────────────────┘        └──────────────┬──────────────┘ │
│                                                     │                │
└─────────────────────────────────────────────────────┼────────────────┘
                                                        ▼
                                   ┌────────────────────────────────┐
                                   │  🗄️ PostgreSQL (Supabase, pooled) │
                                   └────────────────────────────────┘
                                                        │
                                   ┌────────────────────▼───────────┐
                                   │  ☁️ MEGA — evidence file storage  │
                                   └────────────────────────────────┘
```

## ☁️ Deploying to Vercel

This repo is set up to deploy **frontend and backend to the same Vercel domain** with zero extra services — just import the GitHub repo into Vercel.

1. **Import the repo** on [vercel.com/new](https://vercel.com/new) — Framework Preset: `Other`. `vercel.json` at the repo root handles the rest (it builds `frontend/` into static assets and exposes `backend/app` as a Python serverless function at `/api`).
2. **Add environment variables** in Project Settings → Environment Variables:

   | Variable | Value |
   |---|---|
   | `DATABASE_URL` | Your hosted Postgres URL (Supabase pooler recommended) |
   | `JWT_SECRET_KEY` | A long random secret |
   | `FRONTEND_ORIGIN` | `https://<your-project>.vercel.app` |
   | `PUBLIC_API_BASE_URL` | `/api` *(relative — works on every preview URL too)* |
   | `UPLOADS_DIR` | `/tmp/uploads` *(**required** — Vercel's filesystem is read-only outside `/tmp`)* |
   | `COOKIE_SECURE` | `true` |
   | `MEGA_UPLOADS_EMAIL` / `MEGA_UPLOADS_PASSWORD` | Your MEGA credentials, so evidence survives across serverless invocations |

3. **Deploy.** Every push to `main` redeploys both sides together, same domain, no CORS gymnastics.

> ⚠️ **Two known limitations of the serverless build**, worth knowing about before you rely on them in production:
> - **Image OCR** needs the `tesseract` binary, which isn't available in Vercel's Python runtime. PDF text extraction (`pdfplumber`) is pure-Python and works fine; OCR on `.png`/`.jpg` evidence will silently return empty text on Vercel (it works locally and in the Docker image, which installs `tesseract-ocr`).
> - **Profile avatars** are always written to local disk (never MEGA), so they won't persist between serverless cold starts on Vercel. Evidence files are unaffected as long as MEGA is configured.
>
> Neither is a hard blocker for a class project demo — just don't be surprised if an uploaded avatar or a screenshot's OCR text disappears after a redeploy.

## 🗺️ Roadmap

| Phase | 🎯 Focus | Status |
|---|---|---|
| 1 🏗️ | Platform foundation — orgs, reports, categories, comments, votes, admin data model | ✅ Done |
| 2 🌍 | Public discovery — landing page, explore/search, report detail pages | ✅ Done |
| 3 📝 | Submission & account flows — case creation, profile, password reset | ✅ Done |
| 4 💬 | Community & trust — comments, upvotes | ✅ Done |
| 5 🛠️ | Admin area — moderation dashboard, stats | ✅ Done |
| 6 🔒 | Hardening — rate limiting, Turnstile CAPTCHA, audit trails, migrations | 🚧 Ongoing |

## 👤 About the Developer

Built by **Arslan Ahmad** as a CS50x final project.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/arslan-ahmad-dev/)

## ⚖️ License

**Proprietary — All Rights Reserved.**
This is a closed-source academic project. The source is public for portfolio and evaluation purposes only — no permission is granted to copy, modify, or redistribute it without the author's consent.

---

Built with ☕, FastAPI & Svelte · CS50x Final Project 🎓
