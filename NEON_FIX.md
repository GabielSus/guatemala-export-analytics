# Neon psycopg hotfix

## Root cause

The application already normalized `postgresql://` to
`postgresql+psycopg://`, but Alembic still wrote the raw Neon URL directly
into its SQLAlchemy config.

For SQLAlchemy, a generic `postgresql://` URL defaults to the `psycopg2`
dialect. This project installs psycopg v3 (`psycopg[binary]`), not psycopg2,
so Alembic failed with:

`ModuleNotFoundError: No module named 'psycopg2'`

The fix makes Alembic use the same `sqlalchemy_database_url()` normalization
as the application.

## Also important

Use Neon's DIRECT connection string for migrations and the initial seed.
A pooled Neon host contains `-pooler` in the hostname.

Run:

```powershell
.\scripts\seed_neon.ps1
```
