# compute_method='modal'

`compute_method` controla el esquema de cálculo que usa OpenWind internamente.

## FEM

- Es el método que veníamos usando por defecto.
- Con `resonance_frequencies()` OpenWind advirtió que las resonancias se estiman a posteriori desde la fase.

## modal

- Es un modo de cálculo modal del solver.
- En nuestras pruebas, OpenWind indicó que este modo entrega una estimación más rigurosa para las características resonantes.
- Con la configuración por defecto de pérdidas no fue compatible.

Para que `modal` funcionara en nuestras pruebas, usamos:

- `compute_method='modal'`
- `losses='diffrepr+'`

OpenWind también activó automáticamente `use_rad1dof=True`.

## Diferencia práctica

- `resonance_frequencies()` sigue siendo el método público que consultamos.
- Lo que cambia con `modal` es la forma en que el solver calcula el problema antes de estimar esas resonancias.
