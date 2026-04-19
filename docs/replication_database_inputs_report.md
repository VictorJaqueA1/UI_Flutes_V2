# Informe de la Base de Replicación

## 1. Propósito

La base de replicación tiene como función almacenar la información necesaria para reconstruir en el futuro una corrida de cálculo con la mayor fidelidad posible.

En esta etapa, la base ya cubre:

- inputs
- estructuras entregadas a OpenWind
- protocolo de cortes
- outputs base seleccionados

La base no se orienta a visualización rápida, sino a:

- trazabilidad
- auditoría técnica
- reproducibilidad
- reconstrucción de la forma exacta en que se llamó a OpenWind

## 2. Tecnología elegida

Se implementa en SQLite.

Archivo principal:

- `db/replication/replication_inputs.sqlite3`

## 3. Idea estructural

La información se agrupa en varios niveles:

1. `instrument`
2. `calculation_run`
3. `run_input_parameters`
4. `run_input_payloads`
5. `cut_runs`

### Razonamiento

No se usa una tabla única gigante porque:

- una flauta no es lo mismo que una corrida
- una corrida no es lo mismo que un corte
- los inputs escalares no son lo mismo que las estructuras complejas serializadas

## 4. Identidad principal

### `instrument_id`

Representa la identidad de la flauta.

Es la referencia principal de geometría.

Debe poder alinearse con la base operativa.

### `run_id`

Representa una corrida concreta de cálculo aplicada a una flauta.

Permite distinguir:

- misma flauta
- distintos métodos de cálculo
- distintas fechas
- distintas versiones del motor

### `cut_index`

Representa uno de los 10 cortes dentro de una corrida.

## 5. Tabla `instruments`

Propósito:

- representar la flauta geométrica base a la que pertenece una corrida

Columnas:

- `instrument_id`
  - identificador principal de la flauta
- `kind`
  - `base` o `inverse`
- `d_mm`
  - diámetro de embocadura
- `x_mm`
  - posición de embocadura
- `y_mm`
  - altura de chimenea
- `a_mm`
  - breakpoint
- `dt_mm`
  - diámetro extremo variable
- `l_mm`
  - longitud total
- `di_mm`
  - diámetro interno fijo
- `created_at`
  - fecha/hora del registro

## 6. Tabla `calculation_runs`

Propósito:

- registrar una corrida concreta ejecutada sobre una flauta

Columnas:

- `run_id`
  - identificador de corrida
- `instrument_id`
  - referencia a la flauta
- `created_at`
  - fecha/hora de ejecución/registro
- `engine_version`
  - versión del motor usada
- `openwind_version`
  - versión de OpenWind detectada
- `calculation_method`
  - método de cálculo, por ejemplo `FEM` o `modal`
- `loss_model`
  - modelo de pérdidas
- `resonance_method`
  - criterio usado para extraer resonancias
- `source_location`
  - ubicación de la fuente
- `notes`
  - comentarios opcionales

## 7. Tabla `run_input_parameters`

Propósito:

- guardar inputs escalares o configuraciones lógicas de la corrida

Columnas:

- `run_id`
  - referencia a la corrida
- `input_name`
  - nombre del input
- `input_value`
  - valor del input, serializado como texto
- `input_unit`
  - unidad si aplica
- `input_origin`
  - origen del valor:
    - `explicit`
    - `default`
    - `derived`
- `was_provided`
  - si fue entregado explícitamente por el pipeline
- `used_default`
  - si quedó en valor por defecto de OpenWind
- `description`
  - explicación del campo

### Comentario estratégico

Esta tabla permite registrar tanto:

- parámetros geométricos
- opciones de cálculo
- defaults
- inputs derivados

## 8. Tabla `run_input_payloads`

Propósito:

- guardar estructuras complejas entregadas a OpenWind

Columnas:

- `run_id`
  - referencia a la corrida
- `payload_name`
  - nombre del payload
- `payload_format`
  - formato del contenido, por ejemplo `json`
- `payload_value`
  - contenido serializado
- `description`
  - explicación del payload

### Payloads actualmente incluidos

- `frequencies`
- `holes_valves`
- `main_bore_by_cut`

### Comentario estratégico

Esta tabla responde a la necesidad de guardar no solo valores conceptuales, sino también la forma efectiva en que se entregaron a `ImpedanceComputation`.

## 9. Tabla `cut_runs`

Propósito:

- registrar el protocolo de cortes asociado a una corrida

Columnas:

- `run_id`
  - referencia a la corrida
- `cut_index`
  - índice del corte
- `cut_length_mm`
  - longitud efectiva del corte
- `created_at`
  - timestamp

### Comentario estratégico

Los 10 cortes no se modelan como flautas nuevas independientes.

Se modelan como subunidades de una corrida de una flauta.

## 10. Tabla `run_output_core`

Propósito:

- guardar outputs generales de la corrida

Columnas:

- `run_id`
  - referencia a la corrida
- `zc`
  - impedancia característica de entrada
- `frequencies_payload_name`
  - referencia lógica al payload de frecuencias usado
- `impedance_storage_mode`
  - modo de almacenamiento elegido para impedancia
- `created_at`
  - timestamp del registro

## 11. Tabla `cut_output_resonances`

Propósito:

- guardar resultados principales por corte para el pipeline actual

Columnas:

- `run_id`
- `cut_index`
- `f1_hz`
- `f2_hz`
- `delta_cents`
- `created_at`

### Comentario estratégico

Estos son los outputs derivados que hoy sí usamos en el motor:

- resonancia 1
- resonancia 2
- inarmonicidad

## 12. Tabla `cut_output_impedance`

Propósito:

- guardar la impedancia completa por corte

Columnas:

- `run_id`
- `cut_index`
- `frequencies_json`
- `impedance_real_json`
- `impedance_imag_json`
- `created_at`

### Comentario estratégico

Se eligió, por ahora, almacenamiento serializado por corte para evitar una explosión de filas.

En vez de una fila por frecuencia, se guarda:

- la lista de frecuencias
- la parte real de la impedancia
- la parte imaginaria de la impedancia

Todo esto por corte.

## 13. Cómo se guardan los defaults

La base contempla explícitamente esta diferencia.

Para cada input se puede registrar:

- si fue entregado por nosotros
- si fue derivado por el pipeline
- si quedó con el valor por defecto de OpenWind

Esto es importante para reproducibilidad, porque el valor final puede coincidir aunque el origen haya sido distinto.

## 14. Relación con la base operativa

### Base operativa

Guarda:

- identidad resumida
- curva útil para UI
- RMSE
- emparejamientos

### Base de replicación

Guarda:

- identidad de flauta
- corrida
- inputs
- payloads complejos
- cortes

## 15. Campos conceptualmente comunes con la operativa

Los más relevantes son:

- `instrument_id`
- `kind`
- `d`
- `x`
- `y`
- `a`
- `Dt`
- `L`
- `Di`
- `calculation_method`
- `loss_model`
- `resonance_method`
- datos del barrido frecuencial

### Relación recomendada

Mantener el mismo `instrument_id` lógico entre ambas bases.

Así, una flauta en la operativa y la misma flauta en replicación se pueden cruzar sin ambigüedad.

## 16. Ejemplo de flujo cuando se registra una flauta

### Paso 1

Se registra la flauta en `instruments`.

### Paso 2

Se crea una corrida en `calculation_runs`.

### Paso 3

Se guardan los inputs escalares y configuraciones en `run_input_parameters`.

### Paso 4

Se guardan los payloads complejos en `run_input_payloads`.

### Paso 5

Se guarda el protocolo de 10 cortes en `cut_runs`.

### Paso 6

Se guarda el output general de la corrida en `run_output_core`.

### Paso 7

Se guardan los resultados por corte en:

- `cut_output_resonances`
- `cut_output_impedance`

## 17. Qué outputs se eligieron en esta etapa

Se decidió guardar por defecto:

- `frequencies`
- `impedance`
- `Zc`
- `f1`
- `f2`
- `delta_cents`

No se añadieron todavía:

- `resonance_peaks`
- `antiresonance_*`
- `pressure_flow`
- `energy_field`
- `technical_infos()`
- `discretization_infos()`

### Nota metodológica

En esta etapa no se hacen llamadas adicionales pesadas para rescatar campos especiales.

Se guardan:

- los tres outputs base del cálculo (`frequencies`, `impedance`, `Zc`)
- y los outputs que el pipeline ya necesita para operar (`f1`, `f2`, `delta`)

## 18. Archivos implementados

Esquema:

- `db/replication/schema/schema.sql`

Repositorio:

- `db/replication/repositories/sqlite_replication.py`

Inicialización:

- `scripts/init_replication_db.py`

Demo de carga:

- `scripts/demo_replication_inputs.py`

## 19. Estado actual

La base de replicación ya quedó implementada para inputs.

En la demo se cargaron dos flautas:

- una inversa
- una base

con sus corridas, inputs, payloads y cortes.

El siguiente paso lógico será extender esta misma base con outputs opcionales adicionales solo si aportan valor real para la replicación.
