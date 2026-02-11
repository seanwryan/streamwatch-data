# StreamWatch App

Next.js app for StreamWatch (Watershed Institute): dashboards and digital forms backed by the StreamWatch PostgreSQL database.

## Prerequisites

- Node.js 18+
- Access to the StreamWatch database (Neon PostgreSQL). Get credentials from the team or from this repo’s root (e.g. `SECURE_CREDENTIALS` / `.env` there; not committed).

## Setup

1. **Install dependencies**

   ```bash
   npm install
   ```

2. **Configure database**

   Copy the env template and add your credentials:

   ```bash
   cp .env.example .env.local
   ```

   Edit `.env.local` and set:

   - `DB_HOST` — PostgreSQL host (e.g. Neon host)
   - `DB_NAME` — Database name (e.g. `neondb`)
   - `DB_USER` — Use `streamwatch_readonly` for read-only
   - `DB_PASSWORD` — Password for that user
   - `DB_SSLMODE` — `require` for Neon

   Do not commit `.env.local`.

## Run locally

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). You should see the StreamWatch home page with database stats (sites, samples, volunteers) and a sites table when the database is connected.

## API routes (read-only)

- **GET /api/sites** — List sites (up to 200).
- **GET /api/stats** — Counts for sites, samples, and volunteers.

Used by the app and available for future client-side or external use.

## Deploy (e.g. Vercel)

1. Push this repo to GitHub. In [Vercel](https://vercel.com), import the repo and set **Root Directory** to `app`.
2. Add **Environment Variables** (same as `.env.local`): `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_SSLMODE` (and optionally `DB_PORT`).
3. Deploy. The app uses the Neon database via these env vars.

For other hosts (Railway, Render, etc.), set the same env vars and run `npm run build` then `npm run start`.

## Project context

- **Phase 2** of the StreamWatch Next.js execution plan. This app lives in the **streamwatch-data** repo (`app/`).
- **Database:** Same repo — ETL and schema in `scripts/`, `docs/`; use `streamwatch_readonly` and env vars (see `.env.example`; credentials in repo’s `.env` / `SECURE_CREDENTIALS`, not committed).
