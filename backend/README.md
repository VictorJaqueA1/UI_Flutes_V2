# backend

Aqui vive la API del proyecto y la capa de orquestacion entre UI, motor y base de datos.

## Estado actual

El backend minimo ya quedo conectado al engine y a ambas bases de datos.

La API principal vive en:

- `backend/api/app.py`

## Como levantarlo

Con el Python del proyecto:

```powershell
& 'C:\Users\victo\AppData\Local\Programs\Python\Python312\python.exe' -m uvicorn backend.api.app:app --reload --port 8000
```

## Endpoints actuales

- `GET /api/health`
- `POST /api/flutes`
- `GET /api/flutes/{instrument_id}/curve`
- `GET /api/flutes/{instrument_id}/visualization`

## Flujo actual

1. La API recibe una flauta.
2. Construye `FluteGeometry`.
3. Llama a `compute_and_store_flute(...)`.
4. El engine calcula con el pipeline principal modal.
5. Se persiste en la base operativa y en la base de replicacion.
6. Se actualizan RMSE y pairings en la base operativa.
7. La API responde con:
   - `instrument_id`
   - `run_id`
   - curva de inarmonicidad
   - mejor pairing actual, si existe

## Endpoint de visualizacion

`GET /api/flutes/{instrument_id}/visualization` entrega en una sola respuesta:

- la flauta seleccionada
- su geometria resumida
- su curva de inarmonicidad
- la flauta emparejada, si existe
- la curva emparejada
- el pairing actual con su RMSE
