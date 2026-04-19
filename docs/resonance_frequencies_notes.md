# resonance_frequencies

`resonance_frequencies()` es un método público de `ImpedanceComputation`.

En esta etapa lo usamos como una referencia más limpia que el método manual con mínimos en ventanas.

## Qué hace

Dado un cálculo ya resuelto de impedancia, OpenWind estima frecuencias de resonancia y las devuelve ordenadas de menor a mayor.

Uso típico:

- `result.resonance_frequencies(k=5)`

Eso pide hasta 5 frecuencias resonantes.

## Diferencia respecto del método manual actual

Método manual actual:

- usa `|Z|`
- calcula `f1_hint = c / (2 * Li)`
- busca un mínimo dentro de una ventana alrededor de `f1_hint`
- busca otro mínimo dentro de una ventana alrededor de `2 * f1`

Método público de OpenWind:

- no usa nuestras ventanas manuales
- estima resonancias desde la solución interna del problema
- puede servir como contraste para detectar cuándo nuestro criterio casero empieza a elegir otra familia resonante

## Nota importante

OpenWind advierte que, con el método de cálculo actual, estas resonancias pueden ser una estimación a posteriori. Más adelante conviene evaluar `compute_method='modal'` para una referencia más rigurosa.
