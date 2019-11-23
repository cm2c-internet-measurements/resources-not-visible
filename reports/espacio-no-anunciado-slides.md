% Espacio IPv4 de LACNIC no anunciado
% TI LACNIC
% 20191120


# ¿Que se incluye en este reporte? 

Este reporte incluye información acerca de espacio IPv4 asignado por LACNIC pero que no está visible en la tabla de enrutamiento global.


# Metodología

Los datos para la elaboración de este reporte se toman de las siguientes fuentes:

- "delegated-extended" de LACNIC
- RIPE RIS IPv4 Dump

El algoritmo de alto nivel es:

1. Recorrer el delegated extended
   1. Para cada organización, tomar todas sus asignaciones
   2. Producir un agregado de las mismas
2. Recorrer el producto de (1)
   1. Para cada ruta de RIS, identificar el agregado de asignaciones de donde proviene, y de allí la organización a la que pertenece
3. Recorrer el producto de (2)
   1. Para cada agregado, agregar todas las rutas que le corresponden y de allí calcular cuanto del total todas esas rutas cubren.

# Producto del algoritmo

El producto es un archivo separado por pipes con la siguiente estructura:

```
orgid|prefix|visible|dark|total
20118|24.232.0.0/16|65536|0|65536
272078|45.4.0.0/22|1024|0|1024
271038|45.4.4.0/22|1024|0|1024
261330|45.4.8.0/22|1024|0|1024

...
...
258668|45.4.60.0/22|1024|0|1024
258825|45.4.64.0/22|1024|0|1024
```

# Resultados

# Espacio no visible vs espacio asignado

## 8.06%




