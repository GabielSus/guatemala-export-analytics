# Permanent Docker connectivity fix

This patch moves both PostgreSQL and FastAPI into Docker Compose.

The API connects to PostgreSQL through Docker's internal network:

api -> db:5432

It no longer depends on Windows localhost:5432 or localhost:55432.

Apply the patch over the root of the current project, replacing files.

Then run:

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\bootstrap_docker.ps1

After the first successful bootstrap, normal startup is:

docker compose up -d

Swagger:
http://127.0.0.1:8000/docs
