# Flujo de datos

## Flujo de visualización

1. La UI construye o modifica una geometría.
2. La UI dibuja la flauta.
3. La UI solicita o consulta curvas resumidas.
4. La UI muestra curvas y comparaciones.

## Flujo de cálculo puntual

1. La UI arma una geometría.
2. La UI envía una request al backend.
3. El backend valida la geometría.
4. El backend delega el cálculo al motor.
5. El motor genera cortes y ejecuta el cálculo.
6. El backend guarda resultados.
7. El backend devuelve la curva a la UI.

## Flujo de cálculo por rangos

1. La UI define rangos, pasos y parámetros fijos.
2. El backend transforma eso en múltiples geometrías.
3. El motor calcula cada caso.
4. Los resultados se guardan en persistencia.
5. El sistema puede generar emparejamientos RMSE sobre ese conjunto.

## Flujo de matching

1. Se toman curvas base e inversas.
2. Se calcula RMSE entre pares.
3. Se minimiza la distancia.
4. Se produce un conjunto de emparejamientos.
5. La UI consume esos emparejamientos y los muestra.

