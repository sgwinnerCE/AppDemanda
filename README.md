# AppDemanda
Software para proyeccion de demanda electrica basado en modelos econometricos para distintos subsectores economicos. 

Desarrollado por Centro de Energía para Coordinador Electrico Nacional.

Aplicacion desarrollada en Python 3.10

## Instrucciones
- Instalar librerias de requierements.txt en un ambiente virtual en python 3.10.
- Copiar datos de entrada en carpeta input (actualmente desde google drive).
- Cambiar algunos parametros en archivo configuracion.py, si se desea. Por ejemplo horizonte temporal.
- Ejecutar archivo run.py

## Caracteristicas

- Proyecciones para modelos con variables y efectos fijos unicos a nivel nacional.
- Asignacion de proyecciones en barras de retiro

## TO DOs

- Procesar variables y efectos fijos con distintos valores para cada elemento. Ej: Elasticidades diferenciadas por region.
- Asignacion en barras de retiro para modelos con resolucion distinta a nivel de barras.
- Compilacion de resultados en archivo unico.
- Graficos de resultados.
- Incluir datos de encuestas.
