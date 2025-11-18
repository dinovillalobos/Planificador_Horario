# src/solver.py
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import random

# Importar las clases de Hechos (Estado Inicial) y Reglas (Condiciones)
from .models import KnowledgeBase, ClasePendiente
from .rules import es_asignacion_valida, calcular_puntaje_horario 

# Define la estructura de la asignación final que maneja el solver
# Usaremos un diccionario con las IDs de los objetos para facilitar la búsqueda en la KB
AsignacionFinal = Dict[str, str] # { 'id_materia': 'M101', 'id_profesor': 'P001', ...}


class SchedulerSolver:
    def __init__(self, kb: KnowledgeBase, clases_pendientes_inicial: List[ClasePendiente]):
        self.kb = kb  # La Base de Conocimiento
        self.clases_pendientes = clases_pendientes_inicial # La lista de tareas a realizar (Estado Inicial)
        
        # El horario actual, que se construye recursivamente (El 'Plan' parcial)
        self.horario_actual: List[AsignacionFinal] = [] 
        
        # Estructuras de apoyo para verificar choques rápidamente (Postcondición)
        self.slots_ocupados_salon = defaultdict(lambda: defaultdict(str)) # [dia][bloque] = salon_id
        self.slots_ocupados_profesor = defaultdict(lambda: defaultdict(str))
        self.slots_ocupados_grupo = defaultdict(lambda: defaultdict(str))
        
        # Mejor solución encontrada (para optimización)
        self.mejor_horario = None
        self.mejor_puntaje = float('inf')

    # --- Lógica de Búsqueda y Backtracking ---
        
    def planificar_horario(self) -> Optional[List[AsignacionFinal]]:
        
        # 1. ESTADO FINAL (Condición de parada de la recursión: la lista está vacía)
        if not self.clases_pendientes:
            # Lógica de optimización: calcular el puntaje y guardar self.mejor_horario
            return self._guardar_mejor_solucion() 

        # Tomamos la primera tarea pendiente (Estrategia de Búsqueda: Mínimo Restante)
        clase_a_asignar = self.clases_pendientes[0] 
        
        # Generar opciones de asignación para UN solo bloque de tiempo
        posibles_opciones = self._generar_opciones(clase_a_asignar)
        
        # 2. Iterar y Backtrack
        for opcion in posibles_opciones:
            
            # VERIFICACIÓN (Precondición: Reglas Duras)
            if self._intentar_asignacion(opcion):
                
                # --- ACCIÓN Y AVANCE ---
                
                # 2a. Aplicar la asignación (guarda en horario_actual y marca slots como ocupados)
                self._aplicar_asignacion(opcion) 
                
                # 2b. Reducir las horas restantes (ESTADO ACTUALIZADO)
                clase_a_asignar.horas_restantes -= opcion['duracion_bloque'] # Asume que la opción tiene la duración
                
                # 2c. Reorganizar la lista (mover la clase si ya terminó, o dejarla al inicio)
                self._reorganizar_clases_pendientes(clase_a_asignar) 
                
                # Llamada recursiva (avanzar a la siguiente tarea o seguir con la misma si quedan horas)
                resultado = self.planificar_horario()
                
                # --- BACKTRACKING ---
                
                # 3a. Deshacer la asignación (eliminar del horario y desmarcar slots)
                self._deshacer_asignacion(opcion) 
                
                # 3b. Sumar las horas de vuelta (REVERTIR ESTADO)
                clase_a_asignar.horas_restantes += opcion['duracion_bloque'] 
                
                # 3c. Revertir la reorganización
                self._revertir_reorganizacion(clase_a_asignar)

        return None # No se encontró solución en este camino
    # --- Funciones Auxiliares ---
    
    def _generar_opciones(self, clase_pendiente: ClasePendiente) -> List[AsignacionFinal]:
        """Genera una lista de todas las combinaciones (Profesor, Aula, Slot) válidas para la clase."""
        opciones = []
        
        # Lógica simplificada: Iterar sobre profesores, aulas y slots de tiempo
        
        # 1. Definir los profesores posibles (usando PROFES_POR_MATERIA)
        materia_nombre = self.kb.materias.get(clase_pendiente.id_materia).nombre
        profes_posibles = self.kb.profes_por_materia.get(materia_nombre, [])
        
        # Aquí se necesita una lógica más avanzada para el tipo de slot (M-J, L-M-V, etc.)
        # Simplificación: Usar todos los slots para generar opciones
        
        for id_prof, profesor in self.kb.profesores.items():
            if profesor.nombre in profes_posibles:
                for id_aula, aula in self.kb.aulas.items():
                    for slot in self.kb.slots_tiempo:
                        # Se debe construir el diccionario de asignación con la información de ID y nombre
                        opcion = {
                            'id_materia': clase_pendiente.id_materia,
                            'materia': materia_nombre,
                            'id_grupo': clase_pendiente.id_grupo,
                            'grupo': clase_pendiente.id_grupo, 
                            'id_profesor': id_prof,
                            'profesor': profesor.nombre,
                            'id_aula': id_aula,
                            'salon': aula.nombre,
                            'dia': slot.dia,
                            'bloque': slot.bloque_tiempo,
                            # Se necesitan el turno y el patrón, que deben estar disponibles en el modelo de Grupo o Materia
                            'turno': 'M', # <--- Asumir o obtener de la KB
                            'patron': 'M-J' # <--- Asumir o obtener de la KB
                        }
                        opciones.append(opcion)

        # Opcional: Ordenar las opciones para mejorar la velocidad de búsqueda
        # random.shuffle(opciones) 
        
        return opciones

    def _intentar_asignacion(self, opcion: AsignacionFinal) -> bool:
        """Verifica todas las reglas duras."""
        # Nota: La función 'es_asignacion_valida' en rules.py requiere el 'horario_actual' y la KB
        return es_asignacion_valida(self.kb, self.horario_actual, opcion)

    def _aplicar_asignacion(self, opcion: AsignacionFinal):
        """Añade la asignación al horario y actualiza las estructuras de choque."""
        self.horario_actual.append(opcion)
        
        # Actualizar estructuras de choque rápido (Postcondición)
        dia_bloque = (opcion['dia'], opcion['bloque'])
        self.slots_ocupados_salon[dia_bloque] = opcion['id_aula']
        self.slots_ocupados_profesor[dia_bloque] = opcion['id_profesor']
        self.slots_ocupados_grupo[dia_bloque] = opcion['id_grupo']


    def _deshacer_asignacion(self, opcion: AsignacionFinal):
        """Revierte la asignación (Backtracking)."""
        if self.horario_actual and self.horario_actual[-1] == opcion:
            self.horario_actual.pop() # Elimina la última asignación
            
            # Deshacer la actualización de las estructuras de choque
            dia_bloque = (opcion['dia'], opcion['bloque'])
            if self.slots_ocupados_salon.get(dia_bloque) == opcion['id_aula']:
                del self.slots_ocupados_salon[dia_bloque]
            # Repetir para profesor y grupo

    # --- Método de Lanzamiento ---
    
    def run(self) -> Optional[List[AsignacionFinal]]:
        """Lanza el proceso de planificación y retorna el mejor horario."""
        print(f"Iniciando búsqueda de horario para {len(self.clases_pendientes)} tareas...")
        
        # Llama a la función recursiva desde el inicio (índice 0)
        self.planificar_horario(0) 
        
        if self.mejor_horario:
            print(f"¡Solución encontrada! Mejor puntaje (calidad): {self.mejor_puntaje}")
        else:
            print("No se encontró una solución válida que cumpla todas las Reglas Duras.")
            
        return self.mejor_horario

# ============================================================
# 2. IMPLEMENTACIÓN DE PRUEBA (Debe moverse a src/main.py)
# ============================================================

if __name__ == "__main__":
    # NOTA: Este bloque debe moverse a src/main.py. Solo está aquí para prueba.
    
    # Se necesita importar la KB y los Hechos
    from .models import KnowledgeBase, Materia, Grupo, Aula, Profesor, ClasePendiente, SlotTiempo
    
    # --- SIMULACIÓN DE DATOS (Necesitas que tu CSV funcione para tener datos reales) ---
    
    # Creamos una KB con datos de prueba MÍNIMOS para que no falle al iniciar
    kb_simulada = KnowledgeBase(csv_path="ruta_invalida_solo_para_simulacion.csv")
    
    # Rellenar la KB simulada con un profesor, un aula, una materia y un grupo de prueba
    kb_simulada.profesores['P001'] = Profesor('P001', 'PROF_A', ['ALGEBRA'], [], 20)
    kb_simulada.aulas['A214'] = Aula('A214', 'A214', 50, 'NORMAL')
    kb_simulada.grupos['G101'] = Grupo('G101', 1, 40)
    kb_simulada.materias['M101'] = Materia('M101', 'ALGEBRA', 1, 4, 'TEORIA')
    kb_simulada.salones_disponibles.append('A214')
    kb_simulada.profes_por_materia['ALGEBRA'] = ['PROF_A']
    
    # Crear slots de tiempo MÍNIMOS para que la búsqueda no sea infinita
    kb_simulada.slots_tiempo = [
        SlotTiempo(dia='Martes', bloque_tiempo='09:00-11:00'),
        SlotTiempo(dia='Jueves', bloque_tiempo='09:00-11:00')
    ]

    # Estado Inicial: 1 sola clase pendiente (una tarea)
    clases_pendientes_test = [
        ClasePendiente(id_materia='M101', id_grupo='G101', horas_restantes=4)
    ]

    # --- Lanzar Solver ---
    # scheduler = SchedulerSolver(kb_simulada, clases_pendientes_test)
    # resultado_final = scheduler.run()

    # if resultado_final:
    #     print("\nResultado:")
    #     for asignacion in resultado_final:
    #         print(f"- {asignacion['materia']} con {asignacion['profesor']} en {asignacion['salon']} el {asignacion['dia']} a las {asignacion['bloque']}")
    # else:
    #     print("No se pudo generar el horario de prueba.")