# Estrategia de bases de datos

## Decisión general

Se recomienda trabajar con dos lógicas de persistencia distintas:

- base operativa de plataforma
- base de replicación completa

## 1. Base operativa de plataforma

Objetivo:

- alimentar la UI
- mostrar curvas
- guardar emparejamientos
- responder rápido a consultas

Debe almacenar solo lo necesario para uso interactivo.

Ejemplos:

- geometrías resumidas
- curvas resumidas
- puntos de inarmonicidad
- emparejamientos
- RMSE
- identificadores y metadatos básicos

## 2. Base de replicación

Objetivo:

- trazabilidad
- reproducibilidad científica
- persistencia completa de inputs y outputs

Ejemplos:

- geometría completa
- protocolo de cortes
- condiciones físicas y parámetros del cálculo
- parámetros entregados al motor / OpenWind
- outputs completos
- resultados intermedios
- metadata técnica y versiones

## Recomendación arquitectónica

No pensar solo en dos archivos de base de datos, sino en dos capas de persistencia con fines distintos.

Pueden ser:

- dos bases completamente separadas
- o dos esquemas/lógicas claramente separados

La decisión concreta de implementación puede tomarse más adelante, pero la separación conceptual debe mantenerse desde el principio.

