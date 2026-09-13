# Guatemala Export Analytics

Proyecto de portafolio enfocado en Data Analytics + Data Engineering + Backend.
Analiza exportaciones históricas de Guatemala por inciso arancelario utilizando un dataset oficial de Banco de Guatemala.

## Estado

**MVP funcional:** ETL + PostgreSQL + FastAPI + Dashboard React.

La arquitectura se mantiene deliberadamente compacta:

```text
API Route -> Application Use Cases -> Repository Contract -> SQLAlchemy/PostgreSQL
CSV -> Pandas ETL -> Validation -> PostgreSQL
React Dashboard -> FastAPI Analytics API
```

## Stack

- Python 3.12
- FastAPI
- Pandas
- PostgreSQL 17
- SQLAlchemy 2
- Alembic
- Pytest
- React + Vite
- Recharts
- Docker Compose

## Dataset validado

- 13,046 incisos arancelarios
- 313,104 observaciones
- 24 años: 2002–2025
- 0 nulos en la transformación final
- 0 pares inciso/año duplicados
- 2025 marcado como provisional
- Total 2025 validado: USD 15,592,574,551

El CSV original permanece en `data/raw/` y está ignorado por Git.

## Endpoints

```text
GET /health
GET /health/database
GET /analytics/summary
GET /analytics/yearly
GET /analytics/growth
GET /analytics/top-items?year=2025&limit=10
GET /analytics/chapters?year=2025&limit=10
GET /analytics/items/{code}
GET /analytics/years
```

## Primera validación después de aplicar esta versión

```powershell
.\scripts\bootstrap.ps1
```

El bootstrap conserva la base existente; solo ejecuta el ETL si `export_values` está vacío.

## Arranque normal

Desde la raíz:

```powershell
docker compose up -d --build
```

O:

```powershell
.\scripts\start.ps1
```

Dashboard:

```text
http://127.0.0.1:5173
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

## Verificación

```powershell
.\scripts\verify.ps1
```

## Tests

```powershell
.\scripts\test.ps1
```

## Recargar dataset

```powershell
.\scripts\reload_data.ps1
```

El ETL usa `ON CONFLICT` para actualizar observaciones existentes sin duplicarlas.

## Próximas fases

1. Validación visual y funcional completa del dashboard.
2. Catálogo oficial de descripciones de incisos/productos.
3. Forecasting con evaluación del modelo antes de publicarlo.
4. Deploy del backend, frontend y PostgreSQL.
5. README final con screenshots y demo para portafolio.
