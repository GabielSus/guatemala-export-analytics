# Scrum Roadmap

## Definition of Done

- Código funciona dentro de Docker.
- Tests relevantes pasan.
- Endpoint o pantalla puede verificarse manualmente.
- No se introducen capas innecesarias.
- Commit asociado al ticket.

## Sprint 0 — Foundation — COMPLETADO

- Dataset inspection
- ETL
- PostgreSQL
- Alembic
- Docker
- FastAPI health
- Base tests

## Sprint 1 — Analytics API — IMPLEMENTADO EN MVP

- EA-101 yearly totals
- EA-102 year-over-year growth
- EA-103 top tariff items
- EA-104 chapter analytics
- EA-105 item history and filters
- EA-106 metadata years
- EA-107 use-case tests

Tiempo estimado original: 4–6 h.
Estado: código implementado; falta validación completa en la PC del proyecto.

## Sprint 2 — Dashboard React — IMPLEMENTADO EN MVP

- KPI cards
- Historical exports chart
- YoY growth chart
- Top tariff items table
- Chapter participation visualization
- Year selector
- Loading/error states
- Responsive layout

Tiempo estimado original: 7–9 h.
Estado: código implementado; falta validación visual y ajustes.

## Sprint 3 — Data enrichment + Forecasting — PENDIENTE

- Conseguir catálogo oficial de descripciones
- Enriquecer códigos con nombres
- Analizar la serie temporal
- Baseline
- Evaluar MAE/RMSE o métrica apropiada
- Forecast endpoint
- Forecast visualization

Estimación: 6–9 h.

## Sprint 4 — Deploy + Portfolio — PENDIENTE

- Production Docker settings
- Hosted PostgreSQL
- Backend deploy
- Frontend deploy
- README final
- Screenshots
- Demo video

Estimación: 4–6 h.
