# Analytics API

## `/analytics/summary`
Resumen global del dataset.

## `/analytics/yearly`
Totales agregados por año. Acepta `start_year` y `end_year`.

## `/analytics/growth`
Variación interanual calculada sobre los totales anuales. Cuando se especifica `start_year`, el caso de uso consulta también el año anterior para conservar el cálculo correcto del primer punto solicitado.

## `/analytics/top-items`
Top de incisos arancelarios por valor exportado. Parámetros: `year`, `limit`, `chapter`.

## `/analytics/chapters`
Agregación de exportaciones por los primeros dos dígitos del inciso arancelario.

## `/analytics/items/{code}`
Serie histórica de un inciso de 8 o 10 dígitos.

## `/analytics/years`
Años disponibles en PostgreSQL.
