# NAGE_PROYECTO-SEGUNDO-PARCIAL
Este proyecto implementa algoritmos de Inteligencia Artificial para resolver un problema de logistica, optimizacion de rutas y toma de decisiones en un entorno de cuadricula (12x12).
Requisitos Previos
Python: Version 3.13 o superior.
Dependencias: No se requiere la instalacion de paquetes externos (no se necesita pip install). 
El proyecto utiliza unicamente bibliotecas estandar de Python (json, heapq, time, random, math).
Instrucciones de Ejecucion
Clona o descarga este repositorio en tu maquina local.
Abre una terminal o linea de comandos.
Navega hasta el directorio donde se encuentran los archivos del proyecto.
Ejecuta el script principal con el siguiente comando:
python main.py

Configuracion del Sistema
El entorno del agente logistico se configura de manera externa mediante el archivo config_mapa.json. 
No es necesario modificar el codigo fuente (main.py) para probar nuevos escenarios.
Dentro del archivo JSON puedes ajustar los siguientes parametros:
inicio: Coordenada donde arranca el vehiculo ([0, 0]).
destino_final: Coordenada de la meta final ([11, 11]).
entregas: Lista de coordenadas que el agente debe visitar obligatoriamente.
obstaculos: Arreglo de coordenadas que representan muros o zonas bloqueadas en el mapa.
semilla: Valor numerico (por defecto 42) utilizado para controlar la aleatoriedad y asegurar que las pruebas sean reproducibles.
Aclaraciones Adicionales
El sistema asume movimientos estrictamente ortogonales (arriba, abajo, izquierda, derecha) con un costo de 1 por paso.
Al ejecutar main.py, el programa procesara los 4 modulos y mostrara en la consola los resultados exactos de: costo total de pasos, nodos expandidos y tiempo de ejecucion en milisegundos (ms) para cada algoritmo 
