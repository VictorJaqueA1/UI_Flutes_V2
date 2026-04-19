# Resumen de metodos provisionales

## Metodo manual legado

1. Se calcula la impedancia en un barrido global.
2. Se estima `f1_hint = c / (2 * Li)`.
3. Se busca un minimo de `|Z|` en una ventana alrededor de `f1_hint`.
4. Se busca otro minimo de `|Z|` en una ventana alrededor de `2 * f1`.
5. Se calcula la inarmonicidad.

Formula:

`delta = 1200 * log2(f2 / (2 * f1))`

## Metodo publico actual

1. Se calcula la impedancia en el mismo barrido global.
2. Se llama a `resonance_frequencies()` sobre el resultado de OpenWind.
3. Se toma:
   - `f1 = primera resonancia`
   - `f2 = segunda resonancia`
4. Se calcula la inarmonicidad con la misma formula.

Formula:

`delta = 1200 * log2(f2 / (2 * f1))`

## RMSE entre curvas

Si una curva base tiene deltas `delta_base_i` y una curva inversa tiene deltas `delta_inv_i`, entonces:

`rmse = sqrt(mean((delta_base_i - delta_inv_i)^2))`

Ese valor resume cuan parecidas son ambas curvas.
