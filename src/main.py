# src/main.py
import sys
from typing import List
import pandas as pd
from pathlib import Path

# Asegurarse de que Python pueda encontrar los módulos en el directorio 'src'
# Esto es importante para las importaciones relativas (from .models import ...)
# Si ejecutas desde la raíz del proyecto, esto no debería ser necesario, 
# pero es una buena práctica para la portabilidad:
# sys.path.append(str(Path(__file__).parent.parent)) 

from src.models import KnowledgeBase, ClasePendiente
from src.solver import SchedulerSolver

RUTA_CSV_DATOS = "data/base_conocimiento.csv"

def generar_clases_pendientes(kb: KnowledgeBase) -> List[ClasePendiente]:
    """
    Crea la lista inicial de tareas a planificar (Estado Inicial).
    Cada ClasePendiente = Materia + Grupo con sus horas semanales.
    """
    pendientes: List[ClasePendiente] = []
    
    # Supongamos que la combinación Materia-Grupo se define en la KB
    # (Esto es una simulación, la lógica real debe ser más robusta)
    
    # EJEMPLO DE LÓGICA DE SIMULACIÓN:
    # Si tienes un listado de (ID_MATERIA, ID_GRUPO) que deben programarse, úsalo.
    
    # Iteramos sobre todos los grupos para asignarles todas las materias de su semestre
    for id_grupo, grupo in kb.grupos.items():
        for id_materia, materia in kb.materias.items():
            if materia.semestre == grupo.semestre:
                # Cada clase necesita ser programada por la cantidad de horas_semana
                if materia.horas_semana > 0:
                    pendientes.append(
                        ClasePendiente(
                            id_materia=id_materia,
                            id_grupo=id_grupo,
                            horas_restantes=materia.horas_semana
                        )
                    )
    
    # Opcional: ordenar la lista (heurística de ordenamiento de variables)
    # Por ejemplo, las materias con más horas o menos opciones de aula primero.
    
    return pendientes

def mostrar_horario(horario: List[dict]):
    """
    Función para formatear y mostrar el horario final como una tabla (opcionalmente con pandas).
    """
    if not horario:
        print("\n--- ¡NO SE ENCONTRÓ SOLUCIÓN VÁLIDA! ---")
        return

    print("\n=======================================================")
    print("🤖 HORARIO GENERADO CON ÉXITO (Plan Final)")
    print(f"Total de Asignaciones (Bloques): {len(horario)}")
    print("=======================================================")
    
    # Convertir a DataFrame para una visualización limpia
    df = pd.DataFrame(horario)
    
    # Seleccionar y renombrar columnas clave para la presentación
    df_presentacion = df[[
        'grupo', 'materia', 'profesor', 'salon', 'dia', 'bloque'
    ]].rename(columns={
        'grupo': 'Grupo',
        'materia': 'Materia',
        'profesor': 'Profesor',
        'salon': 'Aula',
        'dia': 'Día',
        'bloque': 'Hora'
    })

    # Mostrar la tabla, agrupada por Grupo para mayor claridad
    df_presentacion.sort_values(by=['Grupo', 'Día', 'Hora'], inplace=True)
    
    print(df_presentacion.to_markdown(index=False))


def main():
    """Punto de entrada principal para ejecutar el Planificador IA."""
    
    # 1. CARGA DE BASE DE CONOCIMIENTO (Hechos)
    print("--- 1. Carga de Base de Conocimiento (KB) ---")
    if not Path(RUTA_CSV_DATOS).exists():
        print(f"ERROR: Archivo de datos no encontrado en {RUTA_CSV_DATOS}.")
        print("Asegúrate de tener tu CSV en la carpeta 'data'.")
        return

    kb = KnowledgeBase(csv_path=RUTA_CSV_DATOS)
    
    # Verificación rápida de la KB
    print(f"KB cargada. Materias: {len(kb.materias)}, Grupos: {len(kb.grupos)}, Profesores: {len(kb.profesores)}, Aulas: {len(kb.aulas)}")
    
    if len(kb.materias) == 0 or len(kb.grupos) == 0:
        print("Advertencia: La KB parece vacía. Asegúrate de que tu CSV tenga las columnas 'tipo' (MATERIA, GRUPO, PROFESOR, AULA).")
        return

    # 2. CREACIÓN DE TAREAS PENDIENTES (Estado Inicial)
    print("\n--- 2. Generación de Tareas Pendientes ---")
    clases_pendientes = generar_clases_pendientes(kb)
    print(f"Tareas totales a asignar (ClasePendiente): {len(clases_pendientes)}")
    
    if not clases_pendientes:
        print("ERROR: No hay clases pendientes para asignar. Revisa la lógica de 'generar_clases_pendientes'.")
        return
    
    # 3. EJECUCIÓN DEL SOLVER (Motor de IA)
    print("\n--- 3. Ejecución del Scheduler Solver (Backtracking) ---")
    solver = SchedulerSolver(kb, clases_pendientes)
    
    # El método run lanza la recursión
    horario_final = solver.run() 
    
    # 4. VISUALIZACIÓN DE RESULTADOS
    mostrar_horario(horario_final)


if __name__ == "__main__":
    main()