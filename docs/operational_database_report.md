# Informe de la Base de Datos Operativa

## 1. Propósito

La base de datos operativa es la base usada por la plataforma y por la UI.

Su función es:

- guardar la identidad de cada flauta
- guardar su geometría básica
- guardar la curva de inarmonicidad útil para visualización
- guardar comparaciones RMSE entre flautas base e inversas
- guardar los mejores emparejamientos vigentes en ambos sentidos

No intenta almacenar todo el detalle físico del cálculo. Ese rol queda reservado para la base de replicación.

## 2. Tecnología elegida

Se implementa en SQLite.

Razones:

- gratuito
- simple de desplegar
- archivo único
- suficiente para una primera etapa operativa
- adecuado para persistencia local/controlada

Archivo principal:

- `db/platform/platform_operational.sqlite3`

## 3. Estructura general

La base operativa quedó organizada en cinco tablas:

1. `instruments`
2. `curve_points`
3. `rmse_pairs`
4. `best_inverse_for_base`
5. `best_base_for_inverse`

## 4. Tabla `instruments`

Propósito:

- representar una flauta única dentro del sistema operativo

Columnas:

- `instrument_id`
  - clave primaria global de la flauta
- `kind`
  - tipo de flauta: `base` o `inverse`
- `d_mm`
  - diámetro de embocadura
- `x_mm`
  - posición de embocadura
- `y_mm`
  - altura de chimenea
- `a_mm`
  - breakpoint o transición cono-cilindro
- `dt_mm`
  - diámetro variable extremo
- `l_mm`
  - longitud total
- `di_mm`
  - diámetro interno cilíndrico fijo
- `created_at`
  - fecha y hora de creación del registro
- `calculation_method`
  - método de cálculo de OpenWind usado para esa flauta
- `loss_model`
  - modelo de pérdidas usado
- `resonance_method`
  - criterio usado para extraer resonancias
- `frequency_axis_min_hz`
  - mínimo del barrido frecuencial
- `frequency_axis_max_hz`
  - máximo del barrido frecuencial
- `frequency_axis_step_hz`
  - paso del barrido frecuencial
- `calculation_signature`
  - huella/hash del perfil de cálculo

### Comentario estratégico

Esta tabla incluye parámetros geométricos y metadatos del método, no solo un ID.

Eso permite:

- respaldo mínimo operativo
- trazabilidad histórica
- distinguir lotes calculados con versiones diferentes del motor

## 5. Tabla `curve_points`

Propósito:

- guardar la curva de inarmonicidad punto por punto

Columnas:

- `instrument_id`
  - referencia a `instruments`
- `cut_index`
  - índice del corte, de 1 a 10
- `cut_length_mm`
  - longitud efectiva del corte
- `f1_hz`
  - primera resonancia usada
- `f2_hz`
  - segunda resonancia usada
- `delta_cents`
  - inarmonicidad de ese corte

### Comentario estratégico

Se eligió una fila por punto en vez de un JSON único para:

- facilitar consultas
- facilitar depuración
- poder filtrar por corte
- mantener un formato relacional claro

## 6. Tabla `rmse_pairs`

Propósito:

- guardar comparaciones efectivamente calculadas entre una flauta base y una inversa

Columnas:

- `base_instrument_id`
- `inverse_instrument_id`
- `rmse`
- `created_at`
- `updated_at`

### Comentario estratégico

Esta tabla no guarda solo los óptimos, sino todas las comparaciones que realmente se han calculado.

Esto es importante porque:

- una flauta nueva debe compararse con todas las del otro tipo
- esas nuevas comparaciones pueden cambiar óptimos existentes
- la tabla de pares es la fuente de verdad para recalcular óptimos

## 7. Tabla `best_inverse_for_base`

Propósito:

- guardar la mejor inversa actual para cada base

Columnas:

- `base_instrument_id`
- `inverse_instrument_id`
- `rmse`
- `selected_at`

## 8. Tabla `best_base_for_inverse`

Propósito:

- guardar la mejor base actual para cada inversa

Columnas:

- `inverse_instrument_id`
- `base_instrument_id`
- `rmse`
- `selected_at`

### Comentario estratégico

Los óptimos no se asumen simétricos.

Puede ocurrir que:

- la mejor inversa de una base sea una flauta X
- pero la mejor base de esa flauta X sea otra base distinta

Por eso se mantienen dos relaciones dirigidas.

## 9. Flujo cuando ingresa una flauta nueva base

Supongamos que entra una nueva flauta base.

### Paso 1

Se crea o identifica la flauta en `instruments`.

### Paso 2

Se calcula y guarda su curva de inarmonicidad en `curve_points`.

### Paso 3

Se compara esa nueva base con todas las inversas ya existentes.

Por cada comparación:

- se calcula un RMSE
- se guarda o actualiza una fila en `rmse_pairs`

### Paso 4

Se recalcula el mejor emparejamiento de esa nueva base:

- se busca el mínimo RMSE entre sus pares
- se actualiza `best_inverse_for_base`

### Paso 5

También se revisa el efecto inverso:

- la nueva base puede convertirse en la mejor base para algunas inversas existentes
- por eso se recalculan los mejores óptimos afectados en `best_base_for_inverse`

## 10. Flujo cuando ingresa una flauta nueva inversa

Es el mismo esquema, pero en el sentido opuesto:

- se registra en `instruments`
- se guardan sus puntos en `curve_points`
- se compara contra todas las bases existentes
- se actualiza `best_base_for_inverse` para ella
- y potencialmente `best_inverse_for_base` para bases ya existentes

## 11. Escalamiento y actualización incremental

La estrategia operativa no asume recalcular todo desde cero cada vez.

Si entra una sola flauta nueva:

- solo se calculan las comparaciones nuevas contra el conjunto opuesto
- no se recalculan todos los pares antiguos

Eso hace que el costo incremental crezca linealmente con el tamaño del otro conjunto, no cuadráticamente con todo el sistema histórico.

## 12. Relación con la base de replicación

La base operativa y la base de replicación no cumplen el mismo rol.

### Base operativa

Guarda:

- identidad de flauta
- geometría mínima útil
- curva resumida
- RMSE
- mejores emparejamientos

### Base de replicación

Guardará:

- inputs completos de cálculo
- configuración física completa
- protocolo de cortes completo
- barridos frecuenciales
- salida detallada de OpenWind
- resultados intermedios
- trazabilidad técnica total

## 13. Campos conceptualmente compartidos con replicación

Hasta el momento, los campos más claramente compartidos o alineables entre ambas bases serían:

- `instrument_id`
- `kind`
- parámetros geométricos:
  - `d`
  - `x`
  - `y`
  - `a`
  - `Dt`
  - `L`
  - `Di`
- metadata de cálculo:
  - `calculation_method`
  - `loss_model`
  - `resonance_method`
  - barrido frecuencial
- fechas de creación/cálculo

### Conexión conceptual

La operativa usa una representación resumida de la misma flauta cuya representación completa vivirá en replicación.

La recomendación de diseño es:

- usar el mismo `instrument_id` lógico o una relación 1 a 1 explícita entre ambas bases

## 14. Archivos implementados

Esquema:

- `db/platform/schema/schema.sql`

Repositorio SQLite:

- `db/platform/repositories/sqlite_platform.py`

Inicialización:

- `scripts/init_platform_db.py`

Demostración de persistencia:

- `scripts/demo_platform_persistence.py`

## 15. Estado actual

La base operativa ya quedó implementada y lista para:

- registrar instrumentos
- registrar curvas
- registrar RMSE
- actualizar mejores emparejamientos

El siguiente paso lógico es conectar el pipeline modal actual del engine con este repositorio de persistencia y luego diseñar con mayor detalle la base de replicación.
