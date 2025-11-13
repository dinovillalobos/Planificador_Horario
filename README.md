# 🤖 Planificador de Horarios con Inteligencia Artificial (Ingeniería en Computación)

## 📅 Resumen del Proyecto

Este proyecto consiste en el desarrollo de un **Programa Planificador de Horarios** para la carrera de Ingeniería en Computación.

Utilizando principios de **Inteligencia Artificial** (específicamente, **Programación por Restricciones** y un algoritmo de **Búsqueda con Backtracking**), el sistema genera horarios óptimos que satisfacen un conjunto de reglas (restricciones) académicas y logísticas definidas en nuestra base de conocimiento.

El objetivo principal es generar la **Solución (Plan)** que asigne todas las materias, grupos, profesores y aulas en el tiempo disponible, minimizando conflictos y maximizando la calidad del horario.

---

## ⚙️ Componentes de la Solución (Estructura IA)

El planificador se basa en la estructura formal requerida para sistemas de planificación:

### 1. Base de Conocimiento (Punto 1)
* **Hechos:** Modelado de las entidades (`Materia`, `Profesor`, `Aula`, `SlotTiempo`) a partir de los datos iniciales.
* **Reglas/Heurísticas:**
    * **Reglas Duras (Hard Constraints):** Restricciones que **no deben romperse** (ej. No hay choques de profesor/aula).
    * **Heurísticas (Reglas Blandas):** Criterios de optimización para un horario de alta calidad (ej. Agrupar clases, evitar horarios nocturnos).

### 2. Estados, Acciones y Condiciones (Puntos 2, 3, 4, 5)
* **Estado Inicial (Punto 2):** La lista de todas las asignaturas y grupos pendientes de planificación.
* **Acciones (Punto 3):** La función principal: `AsignarClase(materia, dia, hora, aula, profesor)`.
* **Condiciones (Punto 4):**
    * **Antecedente (Precondición):** Verificación de las Reglas Duras antes de ejecutar una Acción.
    * **Subsecuente (Postcondición):** Actualización del estado (tiempo y aula ocupados) tras una asignación exitosa.
* **Estado Final (Punto 5):** Horario completo generado donde todas las Reglas Duras se cumplen.

### 3. Solución (Punto 6)
* **Planes o Soluciones:** El *output* final, que es la representación tabular del horario generado.

---

## 🛠️ Tecnologías Utilizadas

| Herramienta | Función en el Proyecto |
| :--- | :--- |
| **Python 3.x** | Lenguaje de programación principal. |
| **`pandas`** | Manejo, limpieza y modelado de la Base de Conocimiento (`CSV`/`XLSX`). |
| **POO (Clases)** | Implementación de la estructura de la Base de Conocimiento (Hechos). |
| **Algoritmo de Búsqueda** | **Búsqueda con Backtracking** para resolver el problema con restricciones. |

---

## 📁 Estructura del Repositorio

| Directorio/Archivo | Descripción |
| :--- | :--- |
| `data/` | Archivos de entrada (`base_conocimiento.csv`). |
| `src/models.py` | Definición de las Clases POO (`Materia`, `Profesor`, `Aula`, etc.). |
| `src/rules.py` | Funciones de Reglas (Duras y Blandas). |
| `src/solver.py` | Motor de **Backtracking** / Algoritmo de Búsqueda. |
| `src/main.py` | Punto de entrada. Inicializa y ejecuta el planificador. |
| `tests/` | Archivos para pruebas unitarias y casos de prueba. |
| `docs/informe_final.pdf` | Documento de entrega formal (Punto 7). |
| `requirements.txt` | Lista de dependencias de Python. |

---

## 🚀 Instalación y Ejecución

Sigue estos pasos para configurar tu entorno de desarrollo y ejecutar el planificador:

### 1. Clonar el Repositorio

```bash
git clone [https://github.com/dinovillalobos/Planificador_Horario.git](https://github.com/dinovillalobos/Planificador_Horario.git)
cd Planificador-Horarios-IA

# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate   # En Linux/macOS
.\venv\Scripts\activate    # En Windows

pip install -r requirements.txt

python src/main.py
```

## 🤝 Integrantes del Equipo

Integrante,Rol en el Proyecto
1. [Ricardo Dominguez Villalobos](https://github.com/dinovillalobos), Responsable del Proyecto y Gestión
2. [Hernández Larios Omar Emilio](https://github.com/OmarLarios) ,Diseñador de Hechos y Base de Conocimiento
3. [Apellido, Nombre Completo]() ,Diseñador de Reglas y Condiciones
4. [Apellido, Nombre Completo]() ,Programador del Solver (Algoritmo IA)
5. [Apellido, Nombre Completo]() ,"Tester, Verificador y Documentación de Problemas"
6. [Apellido, Nombre Completo]() ,Redactor de Soporte y Visualización de Soluciones

## ⚖️ Licencia

Este proyecto está distribuido bajo la Licencia MIT.
