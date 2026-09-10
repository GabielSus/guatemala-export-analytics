# Scrum Plan — Guatemala Export Analytics

## Working style

Mini-sprints of 1–3 focused work sessions. Every ticket must leave a verifiable result.

## Definition of Done

- Code works locally.
- Relevant validation/test passes.
- No known blocking error.
- Files remain inside the agreed Clean Architecture boundaries.
- Commit is created with the ticket ID.
- README/docs updated when behavior changes.

## Sprint 0 — Functional foundation

**Sprint Goal:** understand the real source dataset and leave FastAPI + PostgreSQL + ETL ready to run.

| Ticket | Task | Target |
|---|---|---:|
| EA-001 | Inspect real CSV and document findings | 30 min |
| EA-002 | Create compact Clean Architecture | 30 min |
| EA-003 | Create FastAPI health endpoint | 20 min |
| EA-004 | Configure PostgreSQL + Alembic | 35 min |
| EA-005 | Build first ETL transform/validation | 45 min |
| EA-006 | Add automated tests | 20 min |
| EA-007 | Load data and verify analytics summary | 30–45 min |

Expected total: about 3–3.5 hours.

## Sprint 1 — Analytics API

Planned tickets:

- EA-101: yearly export totals
- EA-102: year-over-year growth
- EA-103: exports by tariff chapter
- EA-104: top tariff items
- EA-105: filters and pagination
- EA-106: API tests

Target: 5–7 hours.

## Sprint 2 — React dashboard

Target: 8–10 hours.

## Sprint 3 — Forecasting

Target: 5–8 hours, after validating whether the available yearly series supports the chosen model.

## Sprint 4 — Deploy and portfolio

Target: 4–6 hours.
