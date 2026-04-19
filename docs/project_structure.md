# Estructura del proyecto

## Principio

La estructura se organiza por responsabilidad técnica y no por conveniencia temporal.

## Carpetas principales

- `frontend/`
  Interfaz histórica de referencia.

- `frontend_2/`
  Interfaz activa del proyecto.

- `backend/`
  API y orquestación entre UI, motor, matching y persistencia.

- `engine/`
  Motor geométrico y acústico.

- `matching/`
  Comparación de curvas y emparejamiento por RMSE.

- `db/`
  Persistencia operativa y de replicación.

- `docs/`
  Documentación funcional, técnica y de arquitectura.

- `scripts/`
  Scripts de arranque, utilidades e inicialización.

- `backups/`
  Congelamientos de seguridad del estado del proyecto.

## Estructura interna de frontend_2

- `frontend_2/index.html`
- `frontend_2/css/`
- `frontend_2/src/app/`
- `frontend_2/src/domain/`
- `frontend_2/src/flutes/`
- `frontend_2/src/charts/`
- `frontend_2/src/modes/`
- `frontend_2/src/api/`
- `frontend_2/src/shared/`

## Estructura interna recomendada de backend

- `backend/api/`
- `backend/services/`
- `backend/schemas/`
- `backend/jobs/`

## Estructura interna recomendada de engine

- `engine/models/`
- `engine/geometry/`
- `engine/constraints/`
- `engine/cuts/`
- `engine/openwind/`
- `engine/results/`

## Estructura interna recomendada de db

- `db/platform/`
- `db/replication/`
- `db/shared/`

## Estructura interna recomendada de matching

La carpeta `matching/` debe contener más adelante:

- cálculo RMSE
- selección de pares óptimos
- lógica de emparejamiento

