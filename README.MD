Verificación de clientes dentro de una zona geográfica (GeoPandas + KML)

Este proyecto utiliza GeoPandas y Shapely para validar si clientes con coordenadas GPS se encuentran dentro de una zona geográfica definida en un archivo KML.

El script toma un archivo con polígonos (zona) y un archivo CSV con clientes, y genera como salida un nuevo CSV indicando si cada cliente está o no dentro de la zona.

¿Que hace el script?

Lee un archivo ZonaMendi.kml que contiene uno o varios polígonos de una zona geográfica.

Lee un archivo direccion_f_clientes.csv con clientes y sus coordenadas GPS.

Convierte las coordenadas de texto en puntos geográficos (Point).

Unifica todos los polígonos del KML en una sola geometría.

Verifica si cada cliente se encuentra dentro de la zona.

Agrega una columna booleana llamada "chequeo gps".

Exporta el resultado final a un archivo CSV.

Archivos requeridos

ZonaMendi.kml
Archivo KML que define la zona geográfica.

direccion_f_clientes.csv
Archivo CSV con los datos de los clientes y una columna con coordenadas GPS.

Formato esperado del CSV de entrada

El archivo direccion_f_clientes.csv debe contener una columna llamada:

Punto gps

El formato de las coordenadas debe ser:

latitud,longitud

Ejemplo:
-34.6037,-58.3816

Archivo de salida

El script genera un archivo CSV con el nombre:

ClientesGpsConfirmado.csv

Este archivo contiene todos los datos originales del cliente y una nueva columna:

chequeo gps

Valores posibles:

True -> El cliente está dentro de la zona

False -> El cliente está fuera de la zona o tiene coordenadas inválidas

Librerías utilizadas

geopandas

shapely

pandas

fiona

Se habilita explícitamente el soporte para archivos KML mediante fiona.

Sistema de coordenadas

Se utiliza el sistema de referencia EPSG:4326.
Si el archivo KML tiene un CRS distinto, el script lo reproyecta automáticamente.

Cómo ejecutar el script

Ejecutar el archivo Python desde la terminal:

python nombre_del_script.py

Asegurarse de que los archivos KML y CSV se encuentren en el mismo directorio que el script o ajustar las rutas según corresponda.

Notas adicionales

El script maneja coordenadas vacías o inválidas sin interrumpir la ejecución.

Los polígonos del KML se combinan en una única zona para simplificar la validación.

El resultado final es un archivo CSV listo para análisis o uso operativo.