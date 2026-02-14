# HoopCast

HoopCast is an NBA player analytics app that combines traditional stats, advanced metrics, percentile rankings, and on/off impact data in a searchable UI.

## Live Deployments

- Frontend: deployed on Vercel
- Backend API: deployed on Render at `https://hoopcast.onrender.com`
- Database: Supabase (PostgreSQL)

## Features

- Player search with autocomplete suggestions
- Current player profile pages with:
  - Traditional stats
  - Per-36 stats (PTS/REB/AST/STL/BLK)
  - Advanced metrics (TS%, USG%, eFG%)
  - On/off impact metrics (on-court, off-court, and on-off differentials)
- Percentile bars for key metrics
- On/Off deep-dive panel with detailed ratings and percentiles

## Tech Stack

- Frontend: Next.js (App Router), React, Tailwind CSS
- Backend: FastAPI, `nba_api`, `psycopg2`
- Database: Supabase PostgreSQL
- Hosting: Vercel (frontend), Render (backend)

## Repository Structure

- `frontend/` Next.js app
- `backend/` FastAPI API + data ingestion scripts
- `backend/sql/` SQL migration scripts

## Local Development Setup

## 1) Backend Setup

1. Go to backend:
   ```bash
   cd backend
   ```

2. Create and activate virtual env:
   ```bash
   python -m venv venv
   # Windows (PowerShell)
   .\venv\Scripts\Activate.ps1
   # macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `backend/.env`:
   ```env
   DATABASE_URL=postgresql://postgres.<project_ref>:<db_password>@<pooler_host>:6543/postgres
   DB_SSLMODE=require
   ```

   Optional CORS overrides (recommended for deployed frontend):
   ```env
   CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,https://<your-vercel-domain>.vercel.app
   CORS_ORIGIN_REGEX=https://.*\.vercel\.app
   ```

5. Run backend API:
   ```bash
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

6. API docs:
   - `http://127.0.0.1:8000/docs`

## 2) Frontend Setup

1. Go to frontend:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create `frontend/.env.local`:
   ```env
   NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
   NEXT_PUBLIC_DEFAULT_SEASON=2025-26
   ```

4. Run frontend:
   ```bash
   npm run dev
   ```

5. Open:
   - `http://localhost:3000`

## Database (Supabase)

This project uses Supabase PostgreSQL.

Current schema includes:
- `players`
- `traditional_stats`
- `advanced_stats`
- `player_season_stats` (view)
- `current_season_stats` (view)

Additional on/off columns are added via:
- `backend/sql/add_on_off_columns.sql`

Run SQL migrations in Supabase SQL Editor.

## Data Ingestion Scripts

From `backend/`:

1. Sync players:
   ```bash
   python fetch_all_players.py
   ```

2. Sync stats:
   ```bash
   python fetch_all_stats.py
   ```

Defaults currently focus on current players and recent seasons configured in script defaults.

## Deployment

## Backend (Render)

- Root/workdir: `backend`
- Build command:
  ```bash
  pip install -r requirements.txt
  ```
- Start command:
  ```bash
  uvicorn main:app --host 0.0.0.0 --port $PORT
  ```
- Required env vars:
  - `DATABASE_URL`
  - `DB_SSLMODE=require`
  - `CORS_ORIGINS` (include localhost + Vercel domain)
  - `CORS_ORIGIN_REGEX=https://.*\.vercel\.app`

Live API URL:
- `https://hoopcast.onrender.com`

## Frontend (Vercel)

- Project root: `frontend`
- Required env vars:
  ```env
  NEXT_PUBLIC_API_BASE_URL=https://hoopcast.onrender.com
  NEXT_PUBLIC_DEFAULT_SEASON=2025-26
  ```

## Troubleshooting

- If API works in browser/Postman but fails from Vercel frontend, check CORS settings in backend env/config.
- If Render deploy fails on `psycopg2` import, clear build cache and redeploy.
- If frontend changes to env vars do not apply, redeploy/restart so Next.js picks up new env values.

## License

MIT
