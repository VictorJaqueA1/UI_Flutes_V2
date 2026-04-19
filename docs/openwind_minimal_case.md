# Caso mínimo de OpenWind

## Objetivo

Construir una corrida canónica y pequeña antes de implementar:

- 10 cortes
- inarmonicidad
- RMSE
- backend
- base de datos

El objetivo de este paso es entender y fijar:

- cómo se arma el `main_bore`
- cómo se arma la embocadura
- qué eje de frecuencias se entrega a `ImpedanceComputation`
- qué outputs públicos se reciben

## Qué implementa esta fase

Se dejó un caso mínimo en Python dentro de `engine/`:

- `engine/models/flute.py`
- `engine/geometry/truncated_bore.py`
- `engine/openwind/frequency_axis.py`
- `engine/openwind/runner.py`
- `engine/results/impedance.py`
- `scripts/run_openwind_minimal.py`

## Input canónico del caso mínimo

### 1. Geometría de una flauta

Se usa:

- `kind`
- `d`
- `x`
- `y`
- `a`
- `Dt`
- `L = 570 mm`
- `Di = 18 mm`

### 2. Un solo corte

Se usa:

- `Li = 570 mm`

Esto representa una sola flauta truncada. Más adelante se repetirá para los 10 cortes.

### 3. Opciones básicas de OpenWind

Se usan por ahora:

- `unit = "mm"`
- `diameter = True`
- `temperature = 25.0`
- `humidity = 0.50`
- `source_location = "embouchure"`
- `radiation_category = "unflanged"`
- `losses = True`

No se usan todavía:

- `set_frequencies()`
- `recompute_impedance_at()`
- atributos privados como `result._ImpedanceComputation__freq_model.impedance`

## Cómo se elige `frequencies`

`frequencies` no es la lista de resonancias finales ni las notas.

Es el eje de barrido donde OpenWind calcula la curva de impedancia `Z(f)`.

En esta fase mínima se usa una regla pragmática:

1. Se estima una fundamental aproximada del corte:

`f1 ~= c / (2 * L_cut)`

2. Se construye un barrido amplio alrededor de esa escala:

- mínimo: `max(20 Hz, 0.5 * f1_est)`
- máximo: `min(5000 Hz, 5.0 * f1_est)`
- paso: `2 Hz`

Esto no pretende ser todavía la regla científica final. Es solo un barrido inicial razonable para una primera corrida pública y limpia.

## Qué outputs se guardan en esta fase

Se usan solo outputs públicos:

- `result.frequencies`
- `result.impedance`
- `result.Zc`

La estructura resultante separa:

- eje de frecuencias
- parte real de la impedancia
- parte imaginaria
- `Zc`
- `main_bore` usado
- `holes_valves` usado

## Qué falta después de esta fase

Después de validar esta corrida mínima, el siguiente paso será decidir:

- cómo extraer resonancias (`f1`, `f2`) de manera robusta
- si usar resonancias, picos o mínimos
- cómo definir formalmente la inarmonicidad
- cómo repetir el proceso para los 10 cortes
