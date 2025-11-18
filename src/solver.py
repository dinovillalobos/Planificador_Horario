# src/solver.py
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import random

# Importar las clases de Hechos (Estado Inicial) y Reglas (Condiciones)
from .models import KnowledgeBase, ClasePendiente, Materia, Aula, Profesor, Grupo
from .rules import es_asignacion_valida, calcular_puntaje_horario 

# Alias de tipos
AsignacionFinal = Dict[str, any] 


class SchedulerSolver:
    def __init__(self, kb: KnowledgeBase, clases_pendientes_inicial: List[ClasePendiente]):
        self.kb = kb  
        # Usamos una copia de la lista inicial
        self.clases_pendientes = clases_pendientes_inicial 
        
        self.horario_actual: List[AsignacionFinal] = [] 
        
        # Estructuras de apoyo para verificar choques rápidamente (no es la única verificación)
        self.slots_ocupados_salon = defaultdict(lambda: defaultdict(str)) 
        self.slots_ocupados_profesor = defaultdict(lambda: defaultdict(str))
        self.slots_ocupados_grupo = defaultdict(lambda: defaultdict(str))
        
        # Mejor solución encontrada (para optimización)
        self.mejor_horario = None
        self.mejor_puntaje = float('inf')

    # --- Funciones Auxiliares de Tiempo ---
    
    def _hora_a_minutos(self, hora_str: str) -> int:
        """Convierte 'HH:MM' a minutos totales desde medianoche."""
        try:
            h, m = map(int, hora_str.split(':'))
            return h * 60 + m
        except ValueError:
            return 0 

    def _calcular_duracion_bloque(self, bloque: str) -> float:
        """Calcula la duración en horas a partir del formato 'HH:MM-HH:MM'."""
        try:
            inicio_str, fin_str = bloque.split('-')
            inicio_min = self._hora_a_minutos(inicio_str)
            fin_min = self._hora_a_minutos(fin_str)
            return (fin_min - inicio_min) / 60  # Duración en horas
        except:
            return 0.0 

    def _get_entidad(self, entidad_type: str, id_key: str) -> Optional[any]:
        """Función auxiliar para obtener entidades de la KB de forma segura."""
        if entidad_type == 'materia':
            return self.kb.materias.get(id_key)
        elif entidad_type == 'grupo':
            return self.kb.grupos.get(id_key)
        elif entidad_type == 'profesor':
            return self.kb.profesores.get(id_key)
        elif entidad_type == 'aula':
            return self.kb.aulas.get(id_key)
        return None


    # --- Lógica de Búsqueda y Backtracking ---
    
    def planificar_horario(self) -> Optional[List[AsignacionFinal]]:
        
        # 1. ESTADO FINAL (Condición de parada de la recursión: la lista está vacía)
        if not self.clases_pendientes:
            return self._guardar_mejor_solucion() 

        # Tomamos la primera tarea pendiente (Estrategia: Mínimo Restante/Más Restrictivo)
        clase_a_asignar = self.clases_pendientes[0] 
        
        # Generar opciones de asignación para UN solo bloque de tiempo
        posibles_opciones = self._generar_opciones(clase_a_asignar)
        
        # Ordenamos las opciones (Heurística: intentar primero las mejores)
        # Aquí puedes usar la función de puntaje si quieres ordenar por Soft Constraints
        random.shuffle(posibles_opciones) # Simplificación: Desordenar para evitar ciclos infinitos.
        
        # Iterar y Backtrack
        for opcion in posibles_opciones:
            
            # 2. VERIFICACIÓN (Antecedente / Precondición)
            if es_asignacion_valida(self.kb, self.horario_actual, opcion):
                
                # --- ACCIÓN Y AVANCE ---
                
                # 2a. Aplicar la asignación (guarda en horario_actual y marca slots como ocupados)
                self._aplicar_asignacion(opcion) 
                
                # 2b. Reducir las horas restantes (ESTADO ACTUALIZADO)
                duracion = opcion['duracion_bloque']
                clase_a_asignar.horas_restantes -= duracion
                
                # 2c. Reorganizar la lista (mover la clase si ya terminó, o dejarla al inicio)
                self._reorganizar_clases_pendientes(clase_a_asignar) 
                
                # Llamada recursiva 
                resultado = self.planificar_horario()
                
                # --- BACKTRACKING ---
                
                # 3a. Revertir la reorganización (mover la clase de vuelta si fue necesario)
                self._revertir_reorganizacion(clase_a_asignar)
                
                # 3b. Sumar las horas de vuelta (REVERTIR ESTADO)
                clase_a_asignar.horas_restantes += duracion
                
                # 3c. Deshacer la asignación (eliminar del horario y desmarcar slots)
                self._deshacer_asignacion(opcion)

                # Si buscas solo una solución, descomenta esto:
                # if resultado:
                #    return resultado 

        return None # Indica que falló en este nivel (backtracking implícito)


    # --- Optimización y Generación ---
    
    def _generar_opciones(self, clase_pendiente: ClasePendiente) -> List[AsignacionFinal]:
        """
        Genera opciones de asignación aplicando filtros heurísticos (Poda) para reducir
        el espacio de búsqueda drásticamente.
        """
        opciones = []
        
        materia: Materia = self._get_entidad('materia', clase_pendiente.id_materia)
        grupo: Grupo = self._get_entidad('grupo', clase_pendiente.id_grupo)

        if not materia or not grupo: return []

        materia_nombre = materia.nombre
        profes_posibles = self.kb.profes_por_materia.get(materia_nombre, [])
        
        # Heurística 1: Definir patrón de tiempo (Asumimos M-J para 2h/bloque y L-M-V para 1.5h/bloque)
        patron = 'M-J' if materia.horas_semana == 4 else 'L-M-V'
        
        for id_prof, profesor in self.kb.profesores.items():
            if profesor.nombre in profes_posibles:
                
                for id_aula, aula in self.kb.aulas.items():
                    # FILTRO 1: Tipo de Aula (PODA)
                    # Si requiere LAB/COMPUTO, descartar Aulas NORMALES
                    if materia.tipo in ['LAB', 'COMPUTO', 'MIXTA'] and aula.tipo not in ['LAB', 'COMPUTO']:
                        continue
                        
                    # FILTRO 2: Capacidad (PODA, aunque la regla dura lo hace, pre-filtrar ayuda)
                    if aula.capacidad < grupo.alumnos:
                        continue

                    for slot in self.kb.slots_tiempo:
                        
                        # FILTRO 3: Patrón y Día (PODA)
                        if slot.dia not in self.kb.patrones_info.get(patron, {}).get('dias', []):
                            continue
                            
                        # FILTRO 4: Disponibilidad del Profesor (PODA)
                        if slot.bloque_tiempo in profesor.bloques_no_disponibles:
                             continue

                        duracion_horas = self._calcular_duracion_bloque(slot.bloque_tiempo)

                        opcion = {
                            'id_materia': clase_pendiente.id_materia,
                            'materia': materia_nombre,
                            'id_grupo': clase_pendiente.id_grupo,
                            'grupo': grupo.nombre, 
                            'id_profesor': id_prof,
                            'profesor': profesor.nombre,
                            'id_aula': id_aula,
                            'salon': aula.nombre,
                            'dia': slot.dia,
                            'bloque': slot.bloque_tiempo,
                            'duracion_bloque': duracion_horas,
                            'turno': 'M' if slot.bloque_tiempo.startswith('0') else 'V',
                            'patron': patron 
                        }
                        opciones.append(opcion)

        return opciones

    # --- Gestión del Estado (Reorganización de Pendientes) ---
    
    def _reorganizar_clases_pendientes(self, clase_a_asignar: ClasePendiente):
        """Mueve la clase al final si quedan horas, o la elimina si las horas restantes son <= 0."""
        try:
            current_index = self.clases_pendientes.index(clase_a_asignar)
        except ValueError:
            return

        if clase_a_asignar.horas_restantes <= 0:
            # Tarea COMPLETADA: Eliminar permanentemente.
            self.clases_pendientes.pop(current_index)
            # Para la reversión, guardamos la clase eliminada temporalmente.
            setattr(clase_a_asignar, '_was_removed', True)
        else:
            # Tarea NO COMPLETADA: Moverla al final.
            if current_index < len(self.clases_pendientes) - 1:
                self.clases_pendientes.pop(current_index)
                self.clases_pendientes.append(clase_a_asignar)
                setattr(clase_a_asignar, '_was_removed', False)
    
    def _revertir_reorganizacion(self, clase_a_revertir: ClasePendiente):
        """Revierte el movimiento y la eliminación."""
        
        # 1. Si fue eliminada, reinsertarla al principio.
        if hasattr(clase_a_revertir, '_was_removed') and getattr(clase_a_revertir, '_was_removed'):
            self.clases_pendientes.insert(0, clase_a_revertir)
            delattr(clase_a_revertir, '_was_removed')
            
        # 2. Si fue movida al final, moverla de vuelta al inicio para ser la siguiente tarea.
        elif clase_a_revertir in self.clases_pendientes and self.clases_pendientes[-1] == clase_a_revertir:
            self.clases_pendientes.pop()
            self.clases_pendientes.insert(0, clase_a_revertir)


    # --- Aplicación y Reversión de Asignación ---

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
            self.horario_actual.pop() 
            
            # Deshacer la actualización de las estructuras de choque
            dia_bloque = (opcion['dia'], opcion['bloque'])
            self.slots_ocupados_salon.pop(dia_bloque, None)
            self.slots_ocupados_profesor.pop(dia_bloque, None)
            self.slots_ocupados_grupo.pop(dia_bloque, None)


    def _guardar_mejor_solucion(self) -> List[AsignacionFinal]:
        """Calcula el puntaje y guarda la mejor solución encontrada hasta ahora."""
        puntaje_actual = calcular_puntaje_horario(self.horario_actual, self.kb)
        
        if puntaje_actual < self.mejor_puntaje:
            self.mejor_puntaje = puntaje_actual
            self.mejor_horario = self.horario_actual.copy() 
            
        return self.mejor_horario 

    # --- Método de Lanzamiento ---
    
    def run(self) -> Optional[List[AsignacionFinal]]:
        """Lanza el proceso de planificación y retorna el mejor horario."""
        print(f"Iniciando búsqueda de horario para {len(self.clases_pendientes)} tareas...")
        
        # Intentamos ordenar las tareas pendientes antes de la búsqueda (heurística de variables)
        # Aquí puedes priorizar las materias con más restricciones (LAB, más horas)
        
        self.planificar_horario() 
        
        if self.mejor_horario:
            print(f"¡Solución encontrada! Mejor puntaje (calidad): {self.mejor_puntaje}")
        else:
            print("No se encontró una solución válida que cumpla todas las Reglas Duras.")
            
        return self.mejor_horario