# Inventario de outputs de ImpedanceComputation

## Propósito

Este inventario resume qué outputs y métodos públicos de `ImpedanceComputation` resultaron relevantes en las pruebas del proyecto, qué tipo devuelven y si conviene guardarlos en la base de replicación.

## 1. Outputs base directos

### `result.frequencies`

- Tipo observado: `ndarray`
- Naturaleza: output base del cálculo
- Serialización: fácil
- Costo adicional: bajo o nulo
- Recomendación: guardar

### `result.impedance`

- Tipo observado: `ndarray` complejo
- Naturaleza: output base del cálculo
- Serialización: posible, pero requiere separar parte real e imaginaria o usar otra codificación
- Costo adicional: bajo o nulo
- Recomendación: guardar al menos en replicación, quizá por corte o por corrida

### `result.Zc`

- Tipo observado: `float64`
- Naturaleza: output base del cálculo
- Serialización: trivial
- Costo adicional: bajo o nulo
- Recomendación: guardar

## 2. Resonancias y antiresonancias

### `resonance_frequencies(k=5)`

- Tipo observado: `ndarray`
- Contenido: lista de frecuencias resonantes
- Serialización: fácil
- Costo adicional: parece moderado, pero razonable
- Recomendación: guardar

### `resonance_peaks(k=5)`

- Tipo observado: `tuple(ndarray, ndarray, ndarray)`
- Contenido: frecuencias, factores y amplitudes/picos
- Serialización: fácil si se separan los arrays
- Costo adicional: moderado
- Recomendación: guardar opcionalmente

### `antiresonance_frequencies(k=5)`

- Tipo observado: `ndarray`
- Serialización: fácil
- Costo adicional: moderado
- Recomendación: opcional

### `antiresonance_peaks(k=5)`

- Tipo observado: `tuple(ndarray, ndarray, list)`
- Serialización: factible
- Costo adicional: moderado
- Recomendación: opcional

## 3. Información técnica del solver

### `technical_infos()`

- Tipo observado: `None`
- Comportamiento: imprime información a consola
- Serialización directa: no
- Valor: útil para inspección humana, malo para persistencia automática
- Recomendación: no guardar directamente; si interesa, extraer manualmente después

### `discretization_infos()`

- Tipo observado: `None`
- Comportamiento: imprime información a consola
- Serialización directa: no
- Valor: útil para auditoría técnica, pero no como salida automática persistible
- Recomendación: no guardar directamente; si interesa, reconstruir o capturar aparte

### `get_nb_dof()`

- Tipo observado: `int64`
- Serialización: trivial
- Valor: útil para auditoría del solver
- Recomendación: guardar opcionalmente

### `get_entry_coefs(*labels)`

- Tipo observado: `tuple`
- En la prueba: tupla vacía
- Valor: incierto para el flujo actual
- Recomendación: no priorizar por ahora

## 4. Geometría y etiquetas

### `get_instrument_geometry()`

- Tipo observado: `InstrumentGeometry`
- Serialización directa: no recomendable
- Valor: alto como objeto, bajo como output persistible directo
- Recomendación: no guardar el objeto; ya guardamos `main_bore`, `holes_valves` y payloads

### `get_all_notes()`

- Tipo observado: `list`
- En la prueba: lista vacía
- Valor: bajo en el flujo actual sin digitación real
- Recomendación: no priorizar

### `get_pipes_label()`

- Tipo observado: `list`
- Serialización: fácil
- Valor: útil para auditoría/interfaz técnica
- Recomendación: opcional

### `get_connectors_label()`

- Tipo observado: `list`
- Serialización: fácil
- Valor: útil para diagnóstico técnico
- Recomendación: opcional

### `get_components_label()`

- Tipo observado: `list`
- Serialización: fácil
- Valor: útil para diagnóstico técnico
- Recomendación: opcional

## 5. Campos acústicos

### `get_pressure_flow()`

- En FEM con `interp=True`: devuelve `tuple(ndarray, ndarray, ndarray)`
  - ubicación espacial
  - presión compleja
  - flujo complejo
- En modal: no disponible en la práctica actual porque la interpolación no está implementada
- Costo: alto y volumen alto
- Recomendación: no guardar por defecto; usar solo en corridas especiales

### `get_energy_field()`

- En FEM con `interp=True`: devuelve `tuple(ndarray, ndarray)`
- En modal: no disponible en la práctica actual
- Costo: alto y volumen alto
- Recomendación: no guardar por defecto

## 6. Evaluación adicional

### `evaluate_impedance_at(freqs)`

- En modal: devuelve `ndarray` complejo
- En FEM: no disponible por esta vía, la clase recomienda `recompute_impedance_at()`
- Valor: útil para consultas puntuales o refinamiento local
- Recomendación: no guardar como output principal; usar como herramienta de análisis

## 7. Métodos de visualización / escritura

### `plot_impedance()`, `plot_admittance()`, `plot_ac_field()`, `plot_ac_field_at_freq()`, `plot_instrument_geometry()`

- Naturaleza: visualización
- Recomendación: no guardar en la base

### `write_impedance(...)`

- Naturaleza: exportación a archivo
- Recomendación: no como base principal de replicación

## 8. Recomendación práctica de persistencia

### Guardar siempre

- `frequencies`
- `impedance`
- `Zc`
- `resonance_frequencies`
- `f1`, `f2`
- `delta_cents`

### Guardar opcionalmente

- `resonance_peaks`
- `antiresonance_frequencies`
- `antiresonance_peaks`
- `get_nb_dof`
- etiquetas de componentes/pipes/connectors

### No guardar por defecto

- `technical_infos()` como salida directa
- `discretization_infos()` como salida directa
- `InstrumentGeometry` como objeto
- campos `pressure/flow/energy`
- resultados de plotting

## 9. Conclusión

La estrategia razonable es:

1. guardar outputs base y resonancias
2. guardar algunos outputs técnicos livianos si aportan valor
3. dejar campos espaciales y salidas pesadas para corridas especiales o de diagnóstico

Eso permite mantener una base de replicación rica, pero sin disparar el costo de almacenamiento y cálculo innecesariamente.
