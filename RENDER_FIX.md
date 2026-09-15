# Render deploy fix v3

The previous Render container seeded the full database before starting Uvicorn.
That can make Render fail to detect an open HTTP port in time.

New flow:

1. Seed Neon once from the local Docker API.
2. Render only starts Uvicorn and connects to the already-seeded Neon database.

Apply the patch, run:

```powershell
.\scripts\seed_neon.ps1
```

After `NEON SEED OK`:

```powershell
git add .
git commit -m "fix(EA-400): seed Neon separately and start Render API immediately"
git push
```

Keep the same Neon `DATABASE_URL` in Render and redeploy.
