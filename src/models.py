# src/models.py
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import pandas as pd
from pathlib import Path

# ===============================================
# 1. CONSTANTES Y DOMINIOS DEL HORARIO (De base_conocimiento.py)
# ===============================================

SALONES_DISPONIBLES = [
    'A214', 'A215', 'A216', 'A8118', 'A8120', 'A8117', 'A8119', 'A11201', 'A8121',
    'A504', 'A205', 'A213', 'A211', 'A505', 'A506', 'A507', 'A212', 'A11202',
    'A203', 'CCSAL5', 'CCSAL7', 'CCSAL1', 'A11203', 'CLOUD', 'CCSAL9', 'A11204',
    'A325', 'A1023'
]


PROFES_POR_MATERIA = {
    'ALGEBRA': ['ORTIZ CORDERO GABRIEL', 'HERNANDEZ LOPEZ SERGIO', 'VIEYRA REBOYO LUIS ARMANDO', 'RAMIREZ LAZOS ESTEBAN'],
    'CALCULO DIFERENCIAL E INTEGRAL': ['VERDE CRUZ ABEL', 'GONZALEZ HERNANDEZ GERARDO', 'RAMIREZ LAZOS ESTEBAN', 'PELCASTRE RAMIREZ GLORIA SAMANTHA', 'HERNANDEZ GALICIA SALOMON', 'RODRIGUEZ GARCIA ARTURO'],
    'COMPUTADORAS Y PROGRAMACION': ['PEÑALOZA ROMERO ERNESTO', 'GASTALDI PEREZ JUAN', 'HERNANDEZ CABRERA JESUS', 'SANCHEZ SANCHEZ VICTOR MANUEL', 'CANDELARIO ALAVEZ JORGE LUIS', 'RAMOS MARQUEZ JUAN CARLOS'],
    'GEOMETRIA ANALITICA': ['MARTINEZ ROMERO JONATHAN', 'VIEYRA REBOYO LUIS ARMANDO', 'PATIÑO RODRIGUEZ RAMON', 'GONZALEZ BETANCOURT RAFAEL', 'RODRIGUEZ GARCIA ARTURO', 'SOLIS ALCANTAR EVERARDO'],
    'INTRODUCCION A LA INGENIERIA EN COMPUTACION': ['VELASCO AGUSTIN AARON', 'CANDELARIO ALAVEZ JORGE LUIS', 'ARELLANO OROZCO JUAN MANUEL', 'PARRALES CASTAÑEDA CARLOS ALBERTO', 'GRADA HUERTA IVAN'],
    'ALGEBRA LINEAL': ['PEREZ GUZMAN ALEJANDRO', 'FALCON ARELLANO BERENICE ITZEL', 'SOLIS ALCANTAR EVERARDO'],
    'CALCULO VECTORIAL': ['GONZALEZ HERNANDEZ GERARDO', 'RODRIGUEZ GARCIA ARTURO', 'RAMIREZ LAZOS ESTEBAN', 'SANCHEZ MORALES VICTOR MANUEL'],
    'COMUNICACION': ['MONDRAGON ESCOBAR ALFREDO', 'GUTIERREZ CASTILLO ALMA ROSA', 'ISLAS HERNANDEZ CLARA YAHAIRA', 'ALMANZAR VAZQUEZ MARIA GUADALUPE'],
    'EMPRENDIMIENTO 1': ['FERIA VICTORIA MARIA ANGELICA', 'ROMERO ANDALON JESUS ANGEL', 'COLUNGA VAZQUEZ MATILDE'],
    'PROGRAMACION ORIENTADA A OBJETOS': ['CANDELARIO ALAVEZ JORGE LUIS', 'CRUZ LUEVANO BLANCA ESTELA'],
    'TALLER DE CREATIVIDAD E INNOVACION': ['PEREZ VALDES JOEL ALFREDO', 'CHIAPA MONROY CUAUHTEMOC', 'ABURTO CAMACHO BLANCA PAMELA'],
    'ECUACIONES DIFERENCIALES': ['GONZALEZ HERNANDEZ GERARDO', 'BLANCO BAUTISTA ROBERTO', 'MARTINEZ ROMERO JONATHAN', 'VERDE CRUZ ABEL', 'JUAREZ PALMA JOSE GIL', 'GONZALEZ BETANCOURT RAFAEL', 'RODRIGUEZ GARCIA ARTURO'],
    'ELECTRICIDAD Y MAGNETISMO': ['HERNANDEZ LOPEZ SERGIO', 'SUAREZ HERRERA ALEJANDRO', 'PICCINELLI BOCCHI GABRIELLA', 'VERDE CRUZ ABEL', 'SEGURA RAUDA MINERVA', 'ALVAREZ SORIANO MANUEL ALEJANDRO', 'PEREZ GUZMAN ALEJANDRO'],
    'EMPRENDIMIENTO 2': ['GARCIA VILLANUEVA MA. DEL PILAR', 'MONDRAGON ESCOBAR ALFREDO', 'GUTIERREZ CASTILLO ALMA ROSA', 'COLUNGA VAZQUEZ MATILDE', 'REYES TECONTERO NORMA'],
    'ESTRUCTURA DE DATOS': ['SANCHEZ HERNANDEZ MIGUEL ANGEL', 'BLANCO BAUTISTA ROBERTO', 'PEÑALOZA ROMERO ERNESTO', 'CRUZ LUEVANO BLANCA ESTELA', 'HERNANDEZ CABRERA JESUS', 'SANCHEZ SANCHEZ VICTOR MANUEL'],
    'METODOS NUMERICOS': ['MARTINEZ ROMERO JONATHAN', 'PEREZ GUZMAN ALEJANDRO', 'BLANCO BAUTISTA ROBERTO', 'VIEYRA REBOYO LUIS ARMANDO', 'GONZALEZ BETANCOURT RAFAEL', 'MORALES GONZALEZ JORGE CARLOS', 'RAMIREZ LAZOS ESTEBAN'],
    'PROBABILIDAD Y ESTADISTICA': ['HERNANDEZ LOPEZ SERGIO', 'TORRES TORRES FAUSTO', 'PELCASTRE RAMIREZ GLORIA SAMANTHA'],
    'BASE DE DATOS 1': ['ORDOÑEZ ROSALES MARTIN', 'SOBERANES JAIME ROBERTO MISAEL'],
    'DISPOSITIVOS ELECTRONICOS': ['ORTEGA NAVA CARLOS FERNANDO', 'ALVAREZ SORIANO MANUEL ALEJANDRO', 'LOPEZ CARRETO JUAN MANUEL'],
    'EMPRENDIMIENTO 3': ['GARCIA VILLANUEVA MA. DEL PILAR', 'CERVANTES PATIÑO MOISES'],
    'MATEMATICAS DISCRETAS': ['ORTIZ CORDERO GABRIEL', 'RODRIGUEZ GARCIA ARTURO'],
    'ADMINISTRACION DE PROYECTOS': ['REYES CRUZ ANA CLAUDIA', 'MONDRAGON ESCOBAR ALFREDO', 'GONZALEZ AYALA LUIS ENRIQUE', 'ROMERO ANDALON JESUS ANGEL', 'ALBA VILLA BELEN ANAID', 'VIDAL CASTRO RICARDO ADOLFO', 'GUERRERO SANTAMARIA EFREN'],
    'DISEÑO LOGICO': ['BERNAL DIAZ ARCELIA', 'LOZANO MENDEZ EFREN', 'GONZALEZ MAXINEZ DAVID JAIME', 'RAMIREZ CRUZ JOSE LUIS', 'LOPEZ CARRETO JUAN MANUEL', 'ARELLANO RIVERA ESTEBAN', 'PATIÑO RODRIGUEZ RAMON'],
    'DISEÑO Y ANALISIS DE ALGORITMOS': ['PEREZ MEDEL MARCELO', 'OLIVER MORALES CARLOS', 'SANCHEZ HERNANDEZ MIGUEL ANGEL', 'SANCHEZ SANCHEZ VICTOR MANUEL', 'HERNANDEZ CABRERA JESUS', 'CAMACHO ALVAREZ JUAN CARLOS', 'QUIROZ ALMARAZ SERGIO'],
    'LENGUAJES FORMALES-AUTOMATAS': ['SANCHEZ SANCHEZ VICTOR MANUEL', 'OLIVER MORALES CARLOS', 'JUAREZ ROBLES ELIZABETH', 'ORTIZ CORDERO GABRIEL', 'CAMPOS BRAVO JORGE IVAN'],
    'PROGRAMACION WEB 1': ['CANDELARIO ALAVEZ JORGE LUIS', 'VELASCO AGUSTIN AARON', 'ORTIZ JIMENEZ MARIA ELENA', 'CAMACHO ALVAREZ JUAN CARLOS', 'PEREZ PAZ EDUARDO'],
    'COMPILADORES': ['ORDOÑEZ ROSALES MARTIN', 'CORDERO ORTIZ GABRIEL', 'PEREZ MEDEL MARCELO', 'GUTIERREZ OROZCO RICARDO ARTURO'],
    'DISEÑO DE SISTEMAS DIGITALES (L)': ['HERNANDEZ HERNANDEZ MARTIN', 'GONZALEZ MAXINEZ DAVID JAIME', 'LOZANO MENDEZ EFREN'],
    'INGENIERIA DE SOFTWARE': ['GONZALEZ HERNANDEZ MARIA GABRIELA', 'CAMACHO ALVAREZ JUAN CARLOS', 'CRUZ LUEVANO BLANCA ESTELA'],
    'SISTEMAS OPERATIVOS': ['VAZQUEZ MORALES RODOLFO', 'GONZALEZ HERNANDEZ MARIA GABRIELA', 'AYALA PEÑA ESTEBAN'],
    'MICROPROCESADOR.Y MICROCONTROLAD.(L)': ['BERNAL DIAZ ARCELIA', 'GONZALEZ MAXINEZ DAVID JAIME', 'CANDELARIO ALAVEZ JORGE LUIS', 'HERNANDEZ CONTRERAS JUAN MANUEL', 'LOZANO MENDEZ EFREN', 'OCAMPO ALVAREZ ARTURO', 'MARTINEZ ROMERO JONATHAN'],
    'PROGRAMACION WEB 2': ['SANCHEZ SANCHEZ VICTOR MANUEL', 'SANCHEZ HERNANDEZ MIGUEL ANGEL', 'VERDUZCO RODRIGUEZ MARIANA', 'VELASCO AGUSTIN AARON', 'RAMOS MARQUEZ JUAN CARLOS'],
    'REDES DE COMPUTADORAS 1 (L)': ['HERNANDEZ CABRERA JESUS', 'GALICIA RANGEL GILDA', 'GARCIA MONROY JOSE ANTONIO', 'QUINTERO CERVANTES JOSE MANUEL', 'PEREZ MUÑOZ ANTONIO GERARDO', 'GARCIA GUZMAN ENRIQUE', 'ANAYA MANILA DZOARA IVETTE', 'TORRES RODRIGUEZ GERARDO'],
    'SISTEMAS DE INFORMACION': ['GUTIERREZ OROZCO RICARDO ARTURO', 'MENDOZA GONZALEZ OMAR', 'CANDELARIO ALAVEZ JORGE LUIS', 'VERDUZCO RODRIGUEZ MARIANA', 'VELASCO AGUSTIN AARON', 'CRUZ LUEVANO BLANCA ESTELA'],
    'BASES DE DATOS 2': ['GERMAN ROSAS CESAR FRANCISCO', 'MENDOZA GONZALEZ OMAR', 'SOBERANES JAIME ROBERTO MISAEL'],
    'HABILIDADES DIRECTIVAS': ['FERIA VICTORIA MARIA ANGELICA', 'GARIBAY PEDRAZA ALMA LILIA', 'UGALDE LOPEZ JUDITH', 'GUERRERO SANTAMARIA EFREN', 'REYES TECONTERO NORMA'],
    'PROGRAMACION MOVIL 1': ['CAMACHO ALVAREZ JUAN CARLOS', 'GUTIERREZ LOPEZ FELIPE DE JESUS'],
    'REDES DE COMPUTADORAS 2': ['GARCIA GUZMAN ENRIQUE', 'GARCIA MONROY JOSE ANTONIO', 'TORRES RODRIGUEZ GERARDO', 'QUIROZ ALMARAZ SERGIO'],
    'INTELIGENCIA ARTIFICIAL': ['ROMERO UGALDE MARTIN MANUEL', 'OLIVER MORALES CARLOS', 'JUAREZ ROBLES ELIZABETH', 'MONTERROSA ESCOBAR AMILCAR AMADO', 'MORALES PALAFOX EDGAR'],
    'MINERIA DE DATOS': ['SANCHEZ HERNANDEZ MIGUEL ANGEL', 'MENDOZA GONZALEZ OMAR', 'CANTO GALLO RAFAEL', 'JUAREZ ROBLES ELIZABETH', 'GOYTIA HERRERA MARCO INTI'],
    'SEGURIDAD INFORMATICA': ['VAZQUEZ MORALES RODOLFO', 'NERIA OROZCO ERIK DE JESUS', 'HERNANDEZ AUDELO LEOBARDO', 'VERDUZCO RODRIGUEZ MARIANA', 'NAVARRO DIAZ RAMON', 'PALMA LOPEZ DANIEL FERNANDO', 'AGUILAR HERNANDEZ JOSE FRANCISCO', 'SOBERANES JAIME ROBERTO MISAEL'],
    'GRAFICACION POR COMPUTADORA': ['GONZALEZ AYALA LUIS ENRIQUE', 'SALGADO RODRIGUEZ JOSE FRANCISCO', 'HERNANDEZ CERVANTES LILIANA'],
    'INSTRUMENTACION Y CONTROL': ['ZUÑIGA VILLEGAS BENITO', 'GARCIA GUZMAN ENRIQUE'],
    'INTERNET DE LAS COSAS': ['LOZANO MENDEZ EFREN'],
    'PROYECTO ESCUELA-INDUSTRIA': ['FLORES DIAZ IMELDA DE LA LUZ', 'MONDRAGON ESCOBAR ALFREDO', 'HERNANDEZ AGUILAR CESAR ALBERTO', 'COLUNGA VAZQUEZ MATILDE', 'COVARRUBIAS RODRIGUEZ FERNANDO ROBERTO', 'CRUZ ROSALES ERNESTO'],
    'TEMAS ESPECIALES DE BASES DE DATOS': ['ORDOÑEZ ROSALES MARTIN', 'GERMAN ROSAS CESAR FRANCISCO'],
    'TEMAS ESPECIALES DE COMPUTACION 2': ['AVILA GARCIA JOSE ANTONIO', 'VALENZUELA RAMOS JUAN GERMAN'],
    'TEMAS ESPECIALES DE COMPUTACION 6': ['VEGA MUNGUIA ELIO', 'SALGADO RODRIGUEZ JOSE FRANCISCO'],
    'TEMAS ESPECIALES DE PROGRAMACION 2': ['PEREZ SANCHEZ HIRAM EMMANUEL', 'SALDAÑA ALDANA HECTOR'],
    'VINCULACION EMPRESARIAL': ['PEREZ VALDES JOEL ALFREDO', 'RIVERO PICAZO MARIELA VIANEY'],
    'TEMAS ESPECIALES DE COMPUTACION 1': ['FLORES DIAZ IMELDA DE LA LUZ', 'ALMANZAR VAZQUEZ MARIA GUADALUPE', 'VALENZUELA LOPEZ RODOLFO'],
    'TEMAS ESPECIALES DE COMPUTACION 3': ['VILLANUEVA ORTEGA JUAN ANTONIO', 'SALGADO RODRIGUEZ JOSE FRANCISCO'],
    'PROGRAMACION DE VIDEOJUEGOS 2': ['SALGADO RODRIGUEZ JOSE FRANCISCO'],
    'ROBOTICA': ['GONZALEZ MAXINEZ DAVID JAIME', 'CASTRO DIAZ JOSE DANIEL'],
    'SEMINARIO INGENIERIA EN COMPUTACION': ['PEREZ VALDES JOEL ALFREDO', 'CANO SANTOS BERENICE'],
    'PROGRAMACION DE VIDEOJUEGOS 1': ['SALGADO RODRIGUEZ JOSE FRANCISCO'],
    'TEMAS ESPECIALES DE REDES': ['QUINTERO CERVANTES JOSE MANUEL', 'TORRES RODRIGUEZ GERARDO'],
    'PROCESAMIENTO DIGIT.IMAGENES': ['GONZALEZ PONCE ALEJANDRO RENE'],
    'TEMAS ESPECIALES DE COMPUTACION 4': ['ESCONDRILLAS MAYA CARLOS'],
    'TEMAS ESPECIALES DE SEGURIDAD INFORM': ['HERNANDEZ AUDELO LEOBARDO'],
    'ADMINISTRACION SISTEMAS MULTIUSUAR': ['LOPEZ HERNANDEZ JORGE ARTURO'],
    'SISTEMAS EXPERTOS': ['ROMERO UGALDE MARTIN MANUEL.']
}

# Estructura de patrones de tiempo (M-J, L-M-V, etc.)
PATRONES_INFO = {
    'M-J': {
        'dias': ['Martes', 'Jueves'],
        'duracion_horas': 2.0
    },
    'L-M-V': {
        'dias': ['Lunes', 'Miercoles', 'Viernes'],
        'duracion_horas': 1.5
    },
    'Indefinido': {
        'dias': [],
        'duracion_horas': 0
    }
}

# Bloques de Horario
BLOQUES_MATUTINOS_MJ = ['07:00-09:00', '09:00-11:00', '11:00-13:00']
BLOQUES_MATUTINOS_LMV = ['07:00-08:30', '08:30-10:00', '10:00-11:30', '11:30-13:00']
BLOQUES_VESPERTINOS_MJ = ['13:00-15:00', '15:00-17:00', '17:00-19:00', '19:00-21:00']
BLOQUES_VESPERTINOS_LMV = ['13:00-14:30', '14:30-16:00', '16:00-17:30', '17:30-19:00', '19:00-20:30']

def obtener_bloques_para(turno, patron):
    """
    Función simple que retorna la lista correcta de bloques de
    horario según el turno y el patrón.
    """
    if turno == 'M':
        if patron == 'M-J':
            return BLOQUES_MATUTINOS_MJ
        elif patron == 'L-M-V':
            return BLOQUES_MATUTINOS_LMV
    elif turno == 'V':
        if patron == 'M-J':
            return BLOQUES_VESPERTINOS_MJ
        elif patron == 'L-M-V':
            return BLOQUES_VESPERTINOS_LMV
    return []


# ===============================================
# 2. HECHOS (ENTIDADES - De base1.py)
# ===============================================

@dataclass
class Materia:
    id_materia: str
    nombre: str
    semestre: int
    horas_semana: int
    tipo: str  # TEORIA / LAB / MIXTA


@dataclass
class Grupo:
    id_grupo: str
    semestre: int
    alumnos: int


@dataclass
class Profesor:
    id_profesor: str
    nombre: str
    materias_impartibles: List[str] = field(default_factory=list)
    bloques_no_disponibles: List[str] = field(default_factory=list)
    carga_max_horas: int = 20 # Valor por defecto


@dataclass
class Aula:
    id_aula: str
    nombre: str
    capacidad: int
    tipo: str  # NORMAL / LAB / COMPUTO


@dataclass
class SlotTiempo:
    # Usaremos el formato de BLOQUES_MATUTINOS_MJ, etc. (ej. '09:00-11:00')
    dia: str       # LUNES, MARTES, ...
    bloque_tiempo: str # El string del bloque de tiempo (ej. '09:00-11:00')


@dataclass
class ClasePendiente:
    id_materia: str
    id_grupo: str
    horas_restantes: int


# ===============================================
# 3. BASE DE CONOCIMIENTO (CLASE DE GESTIÓN)
# ===============================================

class KnowledgeBase:
    """
    Contiene y gestiona todos los hechos y constantes del problema:
    materias, grupos, profesores, aulas y reglas de tiempo.
    """
    def __init__(self, csv_path: str = "data/base_conocimiento.csv") -> None:
        self.materias: Dict[str, Materia] = {}
        self.grupos: Dict[str, Grupo] = {}
        self.profesores: Dict[str, Profesor] = {}
        self.aulas: Dict[str, Aula] = {}
        self.slots_tiempo: List[SlotTiempo] = []

        # Atributos de Constantes (Directamente accesibles)
        self.salones_disponibles = SALONES_DISPONIBLES
        self.profes_por_materia = PROFES_POR_MATERIA
        self.patrones_info = PATRONES_INFO

        self._load_data_from_sources(csv_path)
        self._init_slots_tiempo()

    def _load_data_from_sources(self, csv_path: str) -> None:
        """Carga datos de Materias, Grupos, Profesores y Aulas desde el CSV."""
        path = Path(csv_path)
        if not path.exists():
            print(f"Advertencia: Archivo CSV no encontrado en {csv_path}. La KB estará vacía.")
            return

        df = pd.read_csv(path)

        for _, row in df.iterrows():
            tipo = str(row["tipo"]).upper()

            if tipo == "MATERIA":
                materia = Materia(
                    id_materia=row.get("id", ""), # Usar .get para ser más robusto
                    nombre=row.get("nombre", ""),
                    semestre=int(row.get("semestre", 0)),
                    horas_semana=int(row.get("horas_semana", 0)),
                    tipo=row.get("tipo_materia", "TEORIA")
                )
                self.materias[materia.id_materia] = materia

            elif tipo == "GRUPO":
                grupo = Grupo(
                    id_grupo=row.get("id_grupo", ""),
                    semestre=int(row.get("semestre", 0)),
                    alumnos=int(row.get("alumnos", 0))
                )
                self.grupos[grupo.id_grupo] = grupo

            elif tipo == "PROFESOR":
                # Usamos los datos del CSV, pero si no están, se complementan con PROFES_POR_MATERIA si es necesario
                materias_imp = str(row.get("materias_impartibles", "")).split("|") if pd.notna(row.get("materias_impartibles")) else []
                bloques_no_disp = str(row.get("bloques_no_disponibles", "")).split("|") if pd.notna(row.get("bloques_no_disponibles")) else []

                profesor = Profesor(
                    id_profesor=row.get("id", ""),
                    nombre=row.get("nombre", ""),
                    materias_impartibles=[m for m in materias_imp if m],
                    bloques_no_disponibles=[b for b in bloques_no_disp if b],
                    carga_max_horas=int(row.get("carga_max_horas", 20))
                )
                self.profesores[profesor.id_profesor] = profesor

            elif tipo == "AULA":
                aula = Aula(
                    id_aula=row.get("id_aula", ""),
                    nombre=row.get("nombre", ""),
                    capacidad=int(row.get("capacidad", 0)),
                    tipo=row.get("tipo_aula", "NORMAL")
                )
                self.aulas[aula.id_aula] = aula

    def _init_slots_tiempo(self) -> None:
        """Genera todos los posibles SlotTiempo (Día + Bloque de tiempo)."""
        dias = ["LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES"]
        # Usamos todos los bloques posibles de ambos turnos y patrones para generar todos los slots
        bloques_totales = set(BLOQUES_MATUTINOS_MJ + BLOQUES_MATUTINOS_LMV + BLOQUES_VESPERTINOS_MJ + BLOQUES_VESPERTINOS_LMV)

        for d in dias:
            for b in bloques_totales:
                self.slots_tiempo.append(SlotTiempo(dia=d, bloque_tiempo=b))

    def get_bloques_disponibles(self, turno: str, patron: str) -> List[str]:
        """ Wrapper para la función auxiliar que define los bloques reales por patrón y turno. """
        return obtener_bloques_para(turno, patron)


if __name__ == "__main__":
    # Ejemplo simple de cómo cargar y usar la KB (asumiendo que existe un CSV)
    # Crea un archivo dummy_data.csv en la carpeta data/ para probar
    kb = KnowledgeBase(csv_path="dummy_data.csv") 
    
    print("--- Base de Conocimiento Consolidada (src/models.py) ---")
    
    print(f"\nTotal de Salones (Constante): {len(kb.salones_disponibles)}")
    print(f"Total de Slots de Tiempo generados: {len(kb.slots_tiempo)}")
    
    print("\nEjemplo de Bloques:")
    print(f"Matutino L-M-V: {kb.get_bloques_disponibles('M', 'L-M-V')}")