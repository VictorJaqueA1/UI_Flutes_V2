# Dominio geométrico

## Tipos de flauta

- flauta base
- flauta inversa

La diferencia principal es la interpretación geométrica del parámetro `Dt`.

## Parámetros ajustables

- `d`: diámetro de embocadura
  - rango: `0.3 – 18 mm`
  - default: `9.0 mm`

- `x`: posición de embocadura
  - distancia desde el inicio de la flauta al centro de la embocadura
  - default: `160 mm`
  - restricción física: `d/2 ≤ x ≤ 285 - d/2`

- `y`: altura de la chimenea
  - rango: `0.3 – 15 mm`
  - default: `6 mm`

- `a`: breakpoint
  - rango: `0 – 570 mm`
  - default: `150 mm`

- `Dt`: diámetro extremo variable
  - rango: `0.3 – 18 mm`
  - default: `12 mm`

## Parámetros fijos

- `L = 570 mm`
- `Di = 18 mm`

## Interpretación de Dt

- en la flauta base: diámetro en la punta abierta
- en la flauta inversa: diámetro en el inicio de la flauta

## Protocolo de cortes

Se generan 10 cortes equiespaciados desde:

- `570 mm`
- hasta `285 mm`

Eso define el protocolo de cálculo de inarmonicidad para cada flauta.

## Restricciones geométricas

1. `d ≤ D_at_x`
2. `Df > 0`
3. `x ≥ d/2` y `x ≤ 285 − d/2`
4. `0 ≤ a ≤ 570`
5. `0.3 ≤ d ≤ 18`
6. `0.3 ≤ Dt ≤ 18`
7. `0.3 ≤ y ≤ 15`
8. proteger divisiones usando `max(..., 1e-9)`
9. la distancia perpendicular desde el centro de la embocadura a la pared del cono debe ser `≥ d/2`

## Decisión de arquitectura

Estas restricciones no deben vivir solo en la UI.

La fuente de verdad debe vivir en la capa de dominio/motor, mientras que la UI usa una versión derivada para:

- guiar al usuario
- limitar sliders
- mostrar rangos válidos

