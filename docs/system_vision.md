# Vision del sistema

## Objetivo

Construir una plataforma para estudiar, calcular, comparar y almacenar geometrías y curvas de inarmonicidad de dos familias de flautas:

- flauta base
- flauta inversa

## Capacidades principales

### 1. Visualización interactiva

La UI debe permitir:

- mover sliders para construir geometrías
- dibujar ambas flautas en tiempo real
- mostrar curvas de inarmonicidad en el gráfico
- comparar una flauta con su contraparte óptima

### 2. Cálculo puntual

La UI debe permitir:

- fijar una geometría
- solicitar cálculo explícito al motor
- obtener una curva de 10 puntos de inarmonicidad
- guardar resultados y compararlos con otras curvas

### 3. Cálculo por rangos

La parte inferior de la plataforma debe permitir:

- definir inicio, fin y paso para parámetros
- fijar otros parámetros
- ejecutar barridos masivos
- generar y almacenar grandes cantidades de geometrías y resultados

### 4. Emparejamiento entre curvas

El sistema debe:

- comparar curvas de flautas base e inversas
- calcular RMSE entre curvas
- encontrar pares de curvas con menor distancia
- mostrar esos emparejamientos en la UI

## Idea científica del proyecto

Cada flauta genera una curva de inarmonicidad a partir de 10 cortes equiespaciados entre:

- `L = 570 mm`
- `L/2 = 285 mm`

Cada curva resultante puede compararse con otras curvas usando una métrica tipo RMSE para encontrar correspondencias geométricas o acústicas relevantes.

