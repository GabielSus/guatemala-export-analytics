# Production deployment

Recommended portfolio stack:

- Frontend: Vercel
- API: Render Web Service
- PostgreSQL: Neon

Why Neon instead of Render Free Postgres:
Render's free PostgreSQL database expires after 30 days. Neon has a persistent
free Postgres plan that is better suited to a portfolio demo.

## 1. Run local pre-deploy check

```powershell
.\scripts\predeploy_check.ps1
```

Then commit/push:

```powershell
git add .
git commit -m "chore(EA-400): prepare production deployment"
git push
```

## 2. Create Neon database

Create a Neon Postgres project. Copy its connection string, but DO NOT commit
or paste it into source code.

You will set it directly as `DATABASE_URL` in Render.

## 3. Deploy API on Render

Create a new Blueprint from the GitHub repository.

Render will detect `render.yaml`.

When prompted for `DATABASE_URL`, paste the Neon connection string.

The Render `preDeployCommand` automatically:

1. applies Alembic migrations;
2. loads the Banguat export dataset if the DB is empty;
3. loads the SAC catalog if missing;
4. skips those loads on later deploys.

The API must end up at a URL similar to:

`https://guatemala-export-analytics-api.onrender.com`

Verify:

- `/health`
- `/analytics/summary`
- `/forecast?horizon=3`
- `/docs`

## 4. Deploy frontend on Vercel

Import the same GitHub repository.

Set the Vercel project's **Root Directory** to:

`frontend`

Add this Production environment variable:

`VITE_API_URL=https://YOUR-RENDER-API.onrender.com`

Deploy.

## 5. Final production QA

Open the Vercel URL and verify:

- API connected indicator;
- year filter;
- historical chart;
- growth chart;
- SAC product names;
- chapter descriptions;
- forecasting section.

## Important

Never commit:

- Neon connection strings
- passwords
- `.env` files

The raw CSV and official SAC PDF are intentionally included because the
production bootstrap needs them to seed a fresh database.
