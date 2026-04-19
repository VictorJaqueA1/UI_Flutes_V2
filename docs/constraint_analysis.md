# Análisis de restricciones

## Restricciones que sí deben quedar como reglas del dominio

### 1. Rangos físicos primarios

- `0.3 ≤ d ≤ 18`
- `0.3 ≤ Dt ≤ 18`
- `0.3 ≤ y ≤ 15`
- `0 ≤ a ≤ 570`

Estas son restricciones fundamentales y deben vivir en la capa de dominio.

### 2. Embocadura dentro de la zona válida

- `d/2 ≤ x ≤ 285 - d/2`

Esta regla sí tiene sentido y debe quedar explícita.

## Restricciones útiles pero no suficientes por sí solas

### 3. `d ≤ D_at_x`

Esta regla tiene sentido como chequeo simple del centro de la embocadura.

Pero por sí sola no garantiza que el círculo completo quepa bien en una zona cónica. Por eso no conviene usarla sola como condición definitiva.

## Restricciones más fuertes y más valiosas

### 4. Distancia perpendicular a la pared del cono `≥ d/2`

Esta es una restricción importante porque evita que la pared del cono corte lateralmente la embocadura. Es más robusta que usar solo el diámetro local en el centro.

Se recomienda conservar ambas:

- la regla simple del centro
- la regla fuerte de distancia perpendicular

## Restricciones derivadas o de otro nivel

### 5. `Df > 0`

Esta tiene sentido, pero no es una restricción primaria de slider. Es una validación derivada del perfil de la flauta y de los cortes.

Por eso conviene tratarla como:

- validación de dominio derivada
- o validación del motor/cálculo

No como simple rango de un slider.

## Restricciones que en realidad son salvaguardas numéricas

### 6. `max(..., 1e-9)` en denominadores

Esto no es una restricción de usuario. Es una protección de implementación.

Debe existir en el código, pero no debe presentarse como regla geométrica para el usuario.

## Punto a revisar más adelante

La relación exacta entre:

- el rango dinámico real de `x`
- la forma cónica de cada flauta
- y el comportamiento del círculo completo de la embocadura

puede requerir refinamiento adicional cuando conectemos sliders y dibujo en tiempo real.

La base actual queda lista para eso.
