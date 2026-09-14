# EA-400 Deployment v2

Important fix: Render Free web services do not support pre-deploy commands.
Migrations and idempotent data seeding now run from Docker startup before
Uvicorn.

Stack:
- Neon: PostgreSQL
- Render Free: FastAPI
- Vercel: React/Vite

Neon:
Create a project named `guatemala-export-analytics`.
Copy its PostgreSQL connection string and keep it private.

Render:
Use New -> Blueprint, connect the GitHub repo, keep Blueprint path
`render.yaml`, and enter the Neon connection string when Render requests
`DATABASE_URL`.

Vercel:
Import the same GitHub repo, set Root Directory to `frontend`, and add:
`VITE_API_URL=https://YOUR-RENDER-SERVICE.onrender.com`
