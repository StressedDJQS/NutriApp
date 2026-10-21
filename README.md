# NutriApp — Sistema de Planificación Nutricional y Requerimiento de Víveres

NutriApp es una aplicación de escritorio desarrollada con **Python**, **PySide6** y **SQLite** diseñada para instituciones que preparan raciones alimentarias para múltiples comensales. Funciona de manera 100% local y autónoma, sin requerir conexión a internet ni servicios en la nube.

---

## 🚀 Alcance Implementado (Sprint 1: T01 – T10)

1. **Catálogo y Registro de Alimentos (HU-01)**:
   - Registro con nombre, categoría, unidad de medida, precio unitario y perfil nutricional (energía, proteínas, carbohidratos, grasas, fibra, sodio).
   - Validaciones de valores no negativos, unidades coherentes y campos requeridos.
   - Búsqueda por nombre en tiempo real, filtrado por categoría, edición y eliminación protegida (no permite eliminar alimentos en uso por recetas).
   - Prevención de duplicados con cotejo insensible a mayúsculas y espacios.

2. **Gestión de Recetas y Preparaciones (HU-02)**:
   - Creación y edición de recetas con selector de ingredientes conectado al catálogo real.
   - Validación de porciones base (> 0), cantidades (> 0) y presencia obligatoria de ingredientes.
   - Cálculo automático y determinista de costos totales y costo por porción.
   - Cálculo de aporte nutricional consolidado y por porción.
   - **Escalado interactivo de porciones**: selector en tiempo real para simular cualquier número de comensales (ej. 4 a 10 porciones), recalculando los víveres requeridos, costo total y nutrientes.
   - **Reutilización de recetas**: función para duplicar y adaptar preparaciones existentes.

3. **Almacenamiento Persistente en SQLite**:
   - Modelo relacional normalizado con claves foráneas activas (`PRAGMA foreign_keys = ON;`).
   - Ubicación persistente de la base de datos: `data/nutriapp.db`.
   - Transacciones protegidas y consultas parametrizadas contra inyección SQL.

---

## 📁 Estructura del Proyecto

```text
NutriApp/
│
├── data/
│   └── nutriapp.db             # Base de datos SQLite persistente
│
├── src/
│   ├── database/
│   │   ├── connection.py       # Gestor de conexiones y transacciones SQLite
│   │   └── schema.py           # DDL con tablas foods, recipes y recipe_ingredients
│   │
│   ├── models/
│   │   ├── food.py             # Modelo de datos para Alimentos
│   │   └── recipe.py           # Modelos para Recetas e Ingredientes
│   │
│   ├── services/
│   │   ├── unit_converter.py   # Conversión de unidades coherentes (masa, volumen, discretas)
│   │   ├── nutrition_calc.py   # Cálculos deterministas de nutrientes, costos y escalado
│   │   ├── food_service.py     # Lógica de negocio y validación de alimentos
│   │   └── recipe_service.py   # Lógica de recetas, selector y persistencia
│   │
│   └── ui/
│       ├── styles.py           # Hoja de estilos moderna QSS
│       ├── food_view.py        # Pestaña y diálogo de gestión de alimentos
│       ├── recipe_view.py      # Pestaña, diálogo de recetas y visor de escalado
│       └── main_window.py      # Ventana principal PySide6 con pestañas integradas
│
├── tests/
│   ├── conftest.py             # Fixtures de BD aislada temporal en memoria/tmp
│   ├── test_food_service.py    # Pruebas de alimentos (CRUD, validaciones, duplicados)
│   ├── test_recipe_service.py  # Pruebas de recetas (CRUD, validaciones, duplicados)
│   ├── test_nutrition_calc.py  # Pruebas de cálculos de costos, nutrientes y escalado 4->10
│   ├── test_unit_converter.py  # Pruebas de conversiones y compatibilidad de unidades
│   ├── test_persistence.py     # Pruebas de persistencia real tras reiniciar conexión
│   └── test_ui.py              # Pruebas automatizadas de la interfaz PySide6 (offscreen)
│
├── main.py                     # Punto de entrada de la aplicación
├── requirements.txt            # Dependencias del proyecto (PySide6, pytest)
└── README.md                   # Documentación técnica
```

---

## ⚙️ Requisitos e Instalación

1. **Python 3.10 o superior**.
2. Activar el entorno virtual existente o crear uno nuevo:
   ```bash
   # En Windows PowerShell:
   .\env\Scripts\Activate.ps1
   ```
3. Instalar las dependencias estrictamente necesarias:
   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Ejecución de la Aplicación

Para iniciar la interfaz de escritorio de NutriApp:

```bash
python main.py
```

---

## 🧪 Ejecución de Pruebas Automatizadas

La suite incluye 35 pruebas automatizadas con `pytest` que evalúan todos los casos de negocio, persistencia, cálculos y la interfaz:

```bash
pytest -v
```
