import json
import heapq
import time #Libreria para medir el tiempo de ejecucion
import random 
import math

def cargar_mapa(ruta_archivo):
    
    # Objetivo: cargar las coordenadas del mapa, obstaculos y metas.
    # Evita valores fijos (hardcoding) y permite cambiar de escenario facilmente  
   
    try:
        #se abre el archivo json en modo lectura ('r')
        with open(ruta_archivo, 'r') as f:
            datos = json.load(f)
            #mensajes y despliegue de la estructura cargada
            print(f"Dimensiones de la cuadricula: {datos['dimensiones'][0]}x{datos['dimensiones'][1]}")
            print(f"Coordenada de inicio: {datos['inicio']}")
            print(f"Puntos de entrega: {datos['entregas']}")
            print(f"Destino final: {datos['destino_final']}")
            print(f"Semilla de aleatoriedad configurada: {datos['semilla']}")

            return datos
    except Exception as e:
        #control de errores por si el archivo no existe o esta mal escrito
        print(f"Error al leer el archivo de configuracion: {e}")
        return None
def heuristica(a, b):
    #Funcion heuristica distancia Manhattan
    #Objetivo: estima la distancia restante desde la posicion actual hasta la meta
    return abs(a[0] - b[0]) + abs(a[1] - b[1])
def a_estrella(config):
    #algoritmo de busqueda heuristica A* A star
    #objetivo: encontrar la ruta optima minimizando el costo y esquivando obstaculos
    inicio = tuple(config['inicio'])
    meta = tuple(config['destino_final'])
    obstaculos = set(tuple(obs) for obs in config['obstaculos'])
    dimensiones = config['dimensiones']

    #cola de prioridad, almacena tuplas de f_score, costo_g, nodo_actual, ruta_recorrida
    pq = [(0, 0, inicio, [inicio])]
    visitados = set()
    nodos_expandidos = 0 #iniciar contador de casillas analizadas
    while pq:
        f, g, actual, camino = heapq.heappop(pq)
        #si llegamos al destino final retornamos la ruta completa
        if actual == meta:
            return camino, nodos_expandidos #regresa 2 cosas, ruta y nodos
        if actual in visitados:
            continue
        visitados.add(actual)
        nodos_expandidos += 1 #sumar 1 cada vez que pisamos una celda 

        #movimientos permitidos en la cuadricula, arriba, abajo, izquierda, derecha
        x, y = actual 
        vecinos = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]

        for vecino in vecinos:
            vx, vy = vecino

            #validar que el vecino este dentro de los limites del mapa 12x12
            if 0 <= vx < dimensiones[0] and 0 <= vy < dimensiones[1]:
                #validar que no sea un obstaculo ni haya sido visitado
                if vecino not in obstaculos and vecino not in visitados:
                    g_nuevo = g + 1 #costo por cada paso en la cuadricula
                    h_nuevo = heuristica(vecino, meta)
                    f_nuevo = g_nuevo + h_nuevo

                    heapq.heappush(pq, (f_nuevo, g_nuevo, vecino, camino + [vecino]))
    return None, nodos_expandidos #si no hay ruta posible
def greedy_best_first(config):
    #algoritmo greedy best-first search
    inicio = tuple(config['inicio'])
    meta = tuple(config['destino_final'])
    obstaculos = set(tuple(obs) for obs in config['obstaculos'])
    dimensiones = config['dimensiones']

    #solo usa heuristica, no suma el costo de los pasos
    pq = [(heuristica(inicio, meta), inicio, [inicio])]
    visitados = set()
    nodos_expandidos = 0

    while pq:
        h, actual, camino = heapq.heappop(pq)

        if actual == meta:
            return camino, nodos_expandidos

        if actual in visitados:
            continue
        visitados.add(actual)
        nodos_expandidos += 1

        x, y = actual
        vecinos = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y -1)]

        for vecino in vecinos:
            vx, vy = vecino
            if 0 <= vx < dimensiones[0] and 0 <= vy < dimensiones[1]:
                if vecino not in obstaculos and vecino not in visitados:
                    h_nuevo = heuristica(vecino, meta)
                    heapq.heappush(pq, (h_nuevo, vecino, camino + [vecino]))
    return None, nodos_expandidos

def evaluar_orden_entregas(orden, inicio, meta):
    #Calcula la distancia de una ruta completa pasando por todas las entregas
    distancia = 0
    actual = inicio
    for entrega in orden:
        distancia += heuristica(actual, entrega)
        actual = entrega
    distancia += heuristica(actual, meta)
    return distancia

def hill_climbing(config, iteraciones=10):
    #Modulo B algoritmo hill climbing
    #Genera ritas al azar e intenta mejorarlas intercambiando entregas
    inicio = tuple(config['inicio'])
    meta = tuple(config['destino_final'])
    entregas = [tuple(e) for e in config['entregas']]
    random.seed(config['semilla']) #usamos la semilla del JSON para que sea reproducible

    mejores_rutas = []

    for i in range(iteraciones):
        #Crear una solucion inicial al azar
        ruta_actual = entregas.copy()
        random.shuffle(ruta_actual)
        costo_actual = evaluar_orden_entregas(ruta_actual, inicio, meta)

        #buscar mejoras intercambiando dos entregas
        mejor_local = False
        while not mejor_local:
            mejor_local = True
            for j in range(len(ruta_actual)):
                for k in range(j + 1, len(ruta_actual)):
                    #intercambiar posiciones
                    vecino = ruta_actual.copy()
                    vecino[j], vecino[k] = vecino[k], vecino[j]
                    costo_vecino = evaluar_orden_entregas(vecino, inicio, meta)

                    if costo_vecino < costo_actual:
                        ruta_actual = vecino
                        costo_actual = costo_vecino
                        mejor_local = False #encontramos una mejora, seguimos buscando
        mejores_rutas.append((costo_actual, ruta_actual))
    return mejores_rutas

def recocido_simulado(config):
    #Modulo C
    #A veces acepta rutas peores solo para saltar y no quedarse atrapado en un optimo local
    inicio = tuple(config['inicio'])
    meta = tuple(config['destino_final'])
    entregas = [tuple(e) for e in config['entregas']]
    random.seed(config['semilla'])

    #ruta al azar
    ruta_actual = entregas.copy()
    random.shuffle(ruta_actual)
    costo_actual = evaluar_orden_entregas(ruta_actual, inicio, meta)

    #variables de control del efriamiento
    temperatura = 100.0 #aceptamos muchos errores, esta caliente
    tasa_enfriamiento = 0.95
    temperatura_minima = 0.1

    mejor_ruta = ruta_actual.copy()
    mejor_costo = costo_actual

    while temperatura > temperatura_minima:
        #elegir dos entregas al azar e intercambiarlas
        j, k = random.sample(range(len(ruta_actual)), 2)
        vecino = ruta_actual.copy()
        vecino[j], vecino[k] = vecino[k], vecino[j]
        costo_vecino = evaluar_orden_entregas(vecino, inicio, meta)

        #calcular si la ruta nueva es mejor o peor
        diferencia = costo_vecino - costo_actual
         
         #si es mejor, diferencia negaiva, la aceptamos siempre
         #si es peor, la aceptamos a veces dependiendo la temperatuea
        if diferencia < 0 or random.random() < math.exp(-diferencia / temperatura):
            ruta_actual = vecino
            costo_actual = costo_vecino

            #guardamos la mejor historica
            if costo_actual < mejor_costo:
                mejor_costo = costo_actual
                mejor_ruta = ruta_actual.copy()

        #enfriar el sistema un poco para la sigueinte vuelta
        temperatura *= tasa_enfriamiento
    return mejor_costo, mejor_ruta

def algoritmo_genetico(config, pob_size=10, generaciones=20):
    #Modulo C algoritmo genetico
    #se insipira en la evolucion, crea una poblacion de rutas
    #cruza a las mejores, a los papas, y a veces muta un gen, cambia una entrega
     inicio = tuple(config['inicio'])                 
     meta = tuple(config['destino_final'])            
     entregas = [tuple(e) for e in config['entregas']]
     random.seed(config['semilla']) 

     #crear la poblacion inicial, varias rutas al azar
     poblacion = []
     for _ in range(pob_size):
         ruta = entregas.copy()
         random.shuffle(ruta)
         poblacion.append(ruta)

     for _ in range(generaciones):
         #evaluar que tan buenas son las rutas, fitness
         #entre menor sea el costo mejor es la ruta
         poblacion.sort(key=lambda ruta: evaluar_orden_entregas(ruta, inicio, meta))

         #nos quedamos con la mejor mitad de la poblacion, los mas fuertes
         mejores = poblacion[:pob_size // 2]
         nueva_poblacion = mejores.copy()

         #cruza y mutacion, rellenar la poblacio con hijos de os menores
         while len(nueva_poblacion) < pob_size:
             #tomamos una ruta ganadora y la mutamos, cambiamos dos entregas
             padre = random.choice(mejores).copy()
             j, k = random.sample(range(len(padre)), 2)
             padre[j], padre[k] = padre[k], padre[j] #mutacion
             nueva_poblacion.append(padre)

         poblacion = nueva_poblacion

     #al terminar las generaciones, devolvemos a la mejor ruta de todas 
     mejor_ruta_final = poblacion[0]
     mejor_costo_final = evaluar_orden_entregas(mejor_ruta_final, inicio, meta)

     return mejor_costo_final, mejor_ruta_final

def minimax(recursos, turno_maximizador, alpha=float('inf'), beta=float('inf'), usar_poda=False):
    #Modulo d teoria de juegos
    #simula una competencia por recursos, juego Nim, gana quien no se lleve el ultimo
    #condicion de victoria/derrota
    if recursos <= 0:
        return(-1 if turno_maximizador else 1), 1 #retorna utilidad, q nodo evaluado
    mejor_valor = -float('inf') if turno_maximizador else float('inf')
    nodos_totales = 1

    #cada turno se pueden tomar 1, 2 o 3 recursos
    for tomar in [1, 2, 3]:
        if recursos - tomar < 0:
            continue
        valor, nodos = minimax(recursos - tomar, not turno_maximizador, alpha, beta, usar_poda)
        nodos_totales += nodos

        if turno_maximizador:
            mejor_valor = max(mejor_valor, valor)
            if usar_poda:
                alpha = max(alpha, mejor_valor)
                if beta <= alpha:
                    break #corta ramas inutiles
        else:
            mejor_valor = min(mejor_valor, valor)
            if usar_poda:
                beta = min(beta, mejor_valor)
                if beta <= alpha:
                    break 
    return mejor_valor, nodos_totales
    
if __name__ == "__main__":
     #punto de ejecucion del script
     print("Iniciando el sistema de logistica, modulo A")
     mapa_actual = cargar_mapa("config_mapa.json")

     if mapa_actual:
         print("Prueba de A")
         inicio_tiempo_a = time.time()
         ruta_a, nodos_a = a_estrella(mapa_actual)
         fin_tiempo_a = time.time()
         tiempo_a_ms = (fin_tiempo_a - inicio_tiempo_a) * 1000

         if ruta_a:
             print(f"Costo (Total de pasos): {len(ruta_a) - 1}")
             print(f"Nodos expandidos: {nodos_a}")
             print(f"Tiempo de ejecucion: {tiempo_a_ms:.4f} ms")

         print("Prueba de Greedy Best-First")
         inicio_tiempo_g = time.time()
         ruta_g, nodos_g = greedy_best_first(mapa_actual)
         fin_tiempo_g = time.time()
         tiempo_g_ms = (fin_tiempo_g - inicio_tiempo_g) * 1000

         if ruta_g:
             print(f"Costo (Total de pasos): {len(ruta_g) - 1}")
             print(f"Nodos expandidos: {nodos_g}")
             print(f"Tiempo de ejecucion: {tiempo_g_ms:.4f} ms")

             print("Modulo b hill climbing")
             rutas_hill = hill_climbing(mapa_actual)
             mejor_costo, mejor_orden = min(rutas_hill, key=lambda x: x[0])
             print(f"Mejor orden de entregas encontrado: {mejor_orden}")
             print(f"Distancia total de esta ruta: {mejor_costo} pasos")

             print("Modulo c metaheuristicas")
             costo_rs, ruta_rs = recocido_simulado(mapa_actual)
             print("Prueba de recocido simulado (simulated annealing):")
             print(f"Mayor orden encontrado: {ruta_rs}")
             print(f"Distancia total: {costo_rs} pasos")

             costo_ag, ruta_ag = algoritmo_genetico(mapa_actual)
             print("Prueba de algoritmo genetico")
             print(f"Mejor orden encontrado: {ruta_ag}")
             print(f"Distancia total: {costo_ag} pasos")

             print("Modulo D teoria de juegos, juego de recursos")
             recursos_iniciales= 15
             #Prueba 1, minimax estandar, revisa todo
             inicio_mm = time.time()
             utilidad_mm, nodos_mm = minimax(recursos_iniciales, True, usar_poda=False)
             tiempo_mm = (time.time() - inicio_mm) * 1000

             print(f"Minimax Estandar - Resultado del Agente: {'GANA (+1)' if utilidad_mm == 1 else 'PIERDE (-1)'}")
             print(f"Minimax Estandar - Nodos evaluados: {nodos_mm:,}")
             print(f"Minimax Estandar - Tiempo {tiempo_mm:.4f} ms")

             #prueba 2 poda alfa-beta, atajos matematicos
             inicio_ab = time.time()
             utilidad_ab, nodos_ab = minimax(recursos_iniciales, True, usar_poda=True)
             tiempo_ab = (time.time() - inicio_ab) * 1000

             print(f"Poda Alfa-Beta - Resultado del Agente: {'GANA (+1)' if utilidad_ab == 1 else 'PIERDE (-1)'}")
             print(f"Poda Alfa-Beta - Nodos evaluados: {nodos_ab:,}")
             print(f"Poda Alfa-Beta - Tiempo: {tiempo_ab:.4f} ms")


            