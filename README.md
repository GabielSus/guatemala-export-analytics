# Guatemala Export Analytics — fixed Sprint 0

This revision fixes the Windows PostgreSQL authentication issue by avoiding port 5432 entirely.

## Root cause addressed

The backend was connecting to `localhost:5432`, where another PostgreSQL instance can already exist on Windows. A password failure there does not prove it reached the Docker container.

The fixed setup uses:

```text
Host: 127.0.0.1
Host port: 55432
Container port: 5432
Database: export_analytics
User: export_user
Password: export_dev_password
```

It also uses a new Docker volume so old credentials cannot leak into the new database.

## Recommended repair

Keep your current Python 3.12 `.venv`.

From the project root:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\reset_local_db.ps1
```

That script recreates only this project's DB, writes the matching `.env`, verifies the exact database connection, runs Alembic, and runs Pytest.

After success:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m app.infrastructure.etl.inspect_dataset
python -m app.infrastructure.etl.load_exports
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.
