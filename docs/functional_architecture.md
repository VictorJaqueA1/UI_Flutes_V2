# Arquitectura funcional

## Principio central

No mezclar en una misma capa:

- UI
- geometría
- validación
- cálculo acústico
- emparejamiento
- persistencia

## Capas del sistema

### 1. Frontend

Responsable de:

- sliders
- dibujo de flautas
- gráfico
- modos de interacción
- formularios de cálculo
- visualización de resultados

No debe ser la fuente final de verdad para las restricciones geométricas.

### 2. Dominio geométrico

Responsable de:

- definir qué es una flauta
- sus parámetros
- defaults
- constantes
- cortes
- restricciones geométricas

Esta es la capa más importante del sistema.

### 3. Motor de cálculo

Responsable de:

- preparar los casos de cálculo
- integrar OpenWind
- producir curvas y resultados técnicos

### 4. Matching

Responsable de:

- comparar curvas
- calcular RMSE
- emparejar flautas base e inversas

### 5. Persistencia

Responsable de:

- base de datos operativa de plataforma
- base de datos completa de replicación

### 6. Backend

Responsable de:

- exponer API
- validar requests
- coordinar motor, matching y persistencia
- devolver respuestas correctas a la UI

## Modos funcionales de la UI

### Modo visualización

- interacción rápida
- cambios locales de geometría
- curva y comparación visibles

### Modo cálculo

- cálculo explícito por botón
- envío de geometría al backend
- persistencia de resultados

### Modo cálculo por rangos

- cálculo masivo
- barridos de parámetros
- llenado intensivo de bases de datos

