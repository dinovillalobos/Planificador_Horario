# src/rules.py
"""
REGLAS Y CONDICIONES DEL PLANIFICADOR DE HORARIOS

Este módulo define:
- Las reglas duras (hard constraints)
- Las reglas blandas / heurísticas (soft constraints)
- La validación de asignaciones y la puntuación de calidad del horario.

Requiere importar las clases de hechos desde models.py
"""

from typing import List, Dict, Any, TYPE_CHECKING
from collections import defaultdict

# Usamos TYPE_CHECKING para importar los modelos sin causar dependencias circulares
# en tiempo de ejecución si rules.py se importa en models.py
if TYPE_CHECKING:
    from .models import KnowledgeBase, Materia, Aula, Profesor, Grupo, SlotTiempo
    
# Alias de tipos
Asignacion = Dict[str, Any]
Horario = List[Asignacion]


# ============================================================
# 1. REGLAS DURAS (Hard Constraints)
# (Estas funciones deben devolver False si la asignación es INVÁLIDA)
# ============================================================

def es_salon_valido(kb: 'KnowledgeBase', asignacion: Asignacion) -> bool:
    """Regla dura: el salón debe existir en la base de conocimiento."""
    return asignacion.get('salon') in kb.salones_disponibles


def es_profesor_valido_para_materia(kb: 'KnowledgeBase', asignacion: Asignacion) -> bool:
    """Regla dura: el profesor debe estar autorizado para impartir la materia."""
    materia_nombre = asignacion.get('materia')
    profesor_nombre = asignacion.get('profesor')

    if materia_nombre not in kb.profes_por_materia:
        return False

    return profesor_nombre in kb.profes_por_materia[materia_nombre]


def respeta_patron_y_turno(kb: 'KnowledgeBase', asignacion: Asignacion) -> bool:
    """Regla dura: la asignación debe cumplir con los bloques según turno y patrón."""
    turno = asignacion.get('turno')
    patron = asignacion.get('patron')
    bloque = asignacion.get('bloque')

    # Usamos la función auxiliar de la KB
    bloques_validos = kb.get_bloques_disponibles(turno, patron)
    
    return bloque in bloques_validos


def no_choque_salon(horario: Horario, nueva: Asignacion) -> bool:
    """Regla dura: un salón no puede tener dos clases al mismo tiempo."""
    for a in horario:
        if (
            a['salon'] == nueva['salon'] and
            a['dia'] == nueva['dia'] and
            a['bloque'] == nueva['bloque']
        ):
            return False
    return True


def no_choque_profesor(horario: Horario, nueva: Asignacion) -> bool:
    """Regla dura: un profesor no puede estar en dos clases al mismo tiempo."""
    for a in horario:
        if (
            a['profesor'] == nueva['profesor'] and
            a['dia'] == nueva['dia'] and
            a['bloque'] == nueva['bloque']
        ):
            return False
    return True


def no_choque_grupo(horario: Horario, nueva: Asignacion) -> bool:
    """Regla dura: un grupo no puede tener dos materias al mismo tiempo."""
    for a in horario:
        if (
            a['grupo'] == nueva['grupo'] and
            a['dia'] == nueva['dia'] and
            a['bloque'] == nueva['bloque']
        ):
            return False
    return True


def mismo_profesor_para_materia_y_grupo(horario: Horario, nueva: Asignacion) -> bool:
    """
    Regla dura: Si ya existe una clase con la misma materia y grupo, debe ser el mismo profesor.
    """
    for a in horario:
        if (
            a['materia'] == nueva['materia'] and
            a['grupo'] == nueva['grupo']
        ):
            if a['profesor'] != nueva['profesor']:
                return False
    return True

# --- REGLAS DURAS ADICIONALES CRUCIALES ---

def respeta_capacidad_aula(kb: 'KnowledgeBase', asignacion: Asignacion) -> bool:
    """Regla dura: la capacidad del aula debe ser mayor o igual al número de alumnos del grupo."""
    
    # Nota: Asume que las IDs se usan en la asignación para buscar en la KB
    id_grupo = asignacion.get('id_grupo') # Se necesita esta ID en el diccionario de asignacion
    id_aula = asignacion.get('id_aula')   # Se necesita esta ID en el diccionario de asignacion
    
    grupo = kb.grupos.get(id_grupo)
    aula = kb.aulas.get(id_aula)
    
    if not grupo or not aula:
        # Si no se encuentra el objeto, asumimos que no es válida o faltan datos
        return False
        
    return aula.capacidad >= grupo.alumnos


def respeta_tipo_aula(kb: 'KnowledgeBase', asignacion: Asignacion) -> bool:
    """Regla dura: Materias de Laboratorio/Cómputo deben ir en aulas adecuadas."""
    
    id_materia = asignacion.get('id_materia')
    id_aula = asignacion.get('id_aula')
    
    materia = kb.materias.get(id_materia)
    aula = kb.aulas.get(id_aula)
    
    if not materia or not aula:
        return False
    
    # Lógica simplificada: LAB/COMPUTO vs. NORMAL
    materia_requiere_lab = materia.tipo in ['LAB', 'COMPUTO', 'MIXTA']
    aula_es_lab = aula.tipo in ['LAB', 'COMPUTO']

    if materia_requiere_lab and not aula_es_lab:
        return False
    
    # También se podría penalizar si una materia NORMAL usa un aula LAB (Soft), pero aquí es Hard:
    # if not materia_requiere_lab and aula_es_lab:
    #     return False 

    return True


def respeta_disponibilidad_profesor(kb: 'KnowledgeBase', asignacion: Asignacion) -> bool:
    """Regla dura: El profesor no debe estar asignado en un bloque que marcó como no disponible."""
    
    id_profesor = asignacion.get('id_profesor')
    bloque_a_verificar = asignacion.get('bloque') # Ej. '07:00-09:00'

    profesor = kb.profesores.get(id_profesor)
    
    if not profesor:
        return False
        
    # Asume que 'bloques_no_disponibles' en la clase Profesor se cargó con los strings de tiempo (ej. '07:00-09:00')
    return bloque_a_verificar not in profesor.bloques_no_disponibles


def es_asignacion_valida(kb: 'KnowledgeBase', horario: Horario, nueva: Asignacion) -> bool:
    """
    Función general que combina TODAS las reglas duras (Precondición).
    El solver la llama antes de agregar una asignación al horario.
    """
    return (
        # 1. Reglas estáticas (basadas solo en la nueva asignación y la KB)
        es_salon_valido(kb, nueva) and
        es_profesor_valido_para_materia(kb, nueva) and
        respeta_patron_y_turno(kb, nueva) and
        respeta_capacidad_aula(kb, nueva) and
        respeta_tipo_aula(kb, nueva) and
        respeta_disponibilidad_profesor(kb, nueva) and
        
        # 2. Reglas dinámicas (basadas en el horario ya construido)
        no_choque_salon(horario, nueva) and
        no_choque_profesor(horario, nueva) and
        no_choque_grupo(horario, nueva) and
        mismo_profesor_para_materia_y_grupo(horario, nueva)
    )


# ============================================================
# 2. REGLAS BLANDAS / HEURÍSTICAS (Soft Constraints)
# ============================================================

def _inicio_a_minutos(bloque: str) -> int:
    """Convierte HH:MM-HH:MM → minutos para calcular huecos."""
    try:
        inicio = bloque.split('-')[0]
        h, m = inicio.split(':')
        return int(h) * 60 + int(m)
    except:
        # En caso de formato incorrecto, retorna 0 (no penaliza)
        return 0


def _fin_a_minutos(bloque: str) -> int:
    """Convierte HH:MM-HH:MM → minutos para calcular huecos."""
    try:
        fin = bloque.split('-')[1]
        h, m = fin.split(':')
        return int(h) * 60 + int(m)
    except:
        # En caso de formato incorrecto, retorna 0
        return 0


def penalizacion_huecos_por_grupo(horario: Horario) -> int:
    penalizacion = 0
    por_grupo_dia = defaultdict(list)

    for a in horario:
        # Agrupar asignaciones por Grupo y Día
        por_grupo_dia[(a['grupo'], a['dia'])].append(a)

    for asignaciones in por_grupo_dia.values():
        # Ordenar por tiempo de inicio
        asignaciones.sort(key=lambda x: _inicio_a_minutos(x['bloque']))
        
        for i in range(len(asignaciones) - 1):
            tiempo_fin_clase_actual = _fin_a_minutos(asignaciones[i]['bloque'])
            tiempo_inicio_clase_siguiente = _inicio_a_minutos(asignaciones[i + 1]['bloque'])
            
            # Calcular la duración del hueco
            hueco_minutos = tiempo_inicio_clase_siguiente - tiempo_fin_clase_actual

            # Penaliza huecos mayores a 90 minutos (típicamente 1.5 horas)
            if hueco_minutos > 90:
                # Penalización más alta por huecos grandes
                penalizacion += 5 
            elif hueco_minutos > 0:
                 # Penalización baja por cualquier hueco (ej. 30 o 60 min)
                penalizacion += 1 

    return penalizacion


def penalizacion_horas_extremas(horario: Horario) -> int:
    """Penaliza clases al inicio (7:00) y al final (19:00 o 20:00)."""
    penalizacion = 0
    for a in horario:
        bloque = a['bloque']
        if bloque.startswith("07:00") or bloque.startswith("19:00") or bloque.startswith("20:"):
            penalizacion += 1
    return penalizacion


def penalizacion_clases_dispersas(horario: Horario) -> int:
    """
    Penaliza a los grupos si sus clases están demasiado dispersas durante la semana.
    Ej: Clase el Lunes a las 7:00 y otra el Viernes a las 19:00.
    """
    penalizacion = 0
    por_grupo_dias = defaultdict(set)

    for a in horario:
        por_grupo_dias[a['grupo']].add(a['dia'])

    # Penaliza grupos con clases en 5 días diferentes
    for dias in por_grupo_dias.values():
        if len(dias) == 5: 
            penalizacion += 3
        elif len(dias) == 4: 
            penalizacion += 1
            
    return penalizacion


def calcular_puntaje_horario(horario: Horario, kb: 'KnowledgeBase') -> int:
    """
    Suma de heurísticas:
    MENOR PUNTAJE = MEJOR HORARIO
    """
    # Nota: Las penalizaciones por carga desbalanceada/huecos de profesor
    # deben calcularse ÚNICAMENTE cuando el horario esté casi completo, 
    # o si no ralentizarán el Backtracking prematuramente.
    
    puntaje = (
        penalizacion_huecos_por_grupo(horario) * 3 + # Alto impacto en estudiantes
        penalizacion_horas_extremas(horario) * 2 +
        penalizacion_clases_dispersas(horario) * 1 
        # Falta penalizacion_huecos_por_profesor y penalizacion_carga_profesor_desbalanceada
        # Estas dos son mejores como revisión final o con pesos bajos.
    )
    return puntaje

# ============================================================
# 3. FUNCIÓN PRINCIPAL DE EJECUCIÓN (No es parte de las reglas, pero útil)
# ============================================================

def main():
    """Para probar la estructura de importación y reglas (necesitas un archivo dummy_data.csv)."""
    # IMPORTACIÓN DINÁMICA DE MODELS
    try:
        from .models import KnowledgeBase, Materia, Aula, Profesor, Grupo
    except ImportError:
        print("Error: No se puede importar KnowledgeBase. Asegúrate de que 'src/models.py' exista.")
        return

    print("--- Verificación de Reglas y Condiciones ---")
    
    # Asume que el archivo CSV existe o la KB estará vacía.
    kb = KnowledgeBase(csv_path="data/dummy_data.csv")
    ejemplo_horario: Horario = []

    # Ejemplo de una asignación VÁLIDA (con datos de ejemplo, necesitas tu CSV real)
    nueva_asignacion = {
        'id_materia': 'M1101', # ID de materia de models.py
        'materia': 'ALGEBRA', # Nombre de materia de PROFES_POR_MATERIA
        'id_grupo': 'G101',   # ID de grupo de models.py
        'grupo': 'G101',
        'id_profesor': 'P001', # ID de profesor de models.py
        'profesor': 'ORTIZ CORDERO GABRIEL',
        'id_aula': 'A214',     # ID de aula de models.py
        'salon': 'A214',
        'turno': 'M',
        'patron': 'M-J',
        'dia': 'Martes',
        'bloque': '09:00-11:00'
    }

    print(f"\nIntentando asignar: {nueva_asignacion['materia']} con {nueva_asignacion['profesor']}")
    
    # NOTA: Para que esto funcione, debes tener datos consistentes en tu CSV
    # (ej. crear el profesor P001, la materia M1101, el grupo G101 y el aula A214 en el CSV).
    
    # Simulación de la verificación
    valida = es_asignacion_valida(kb, ejemplo_horario, nueva_asignacion)
    print(f"Resultado de es_asignacion_valida (debe ser True si la KB está bien): {valida}")

if __name__ == "__main__":
    main()