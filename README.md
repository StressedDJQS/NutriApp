# NutriApp — Sistema Web de Planificación Nutricional y Requerimiento de Víveres

NutriApp es una aplicación web moderna diseñada para instituciones que planifican, preparan y gestionan raciones alimentarias para múltiples comensales. El sistema permite administrar inventarios de alimentos, escalar recetas dinámicamente y planificar menús semanales evaluando su adecuación calórica y consolidando la lista de compras.

---

## 🚀 Alcance y Funcionalidades

1. **Catálogo y Registro de Alimentos**:
   - Mantenimiento completo (CRUD) de alimentos con categoría, unidad física y precio unitario.
   - Registro del perfil nutricional base (energía, proteínas, carbohidratos, grasas, fibra, sodio).
   - Cálculos estandarizados manejados desde el backend para compatibilidad entre sistemas de unidades (Masa, Volumen y Unidades discretas).

2. **Gestión de Recetas y Preparaciones**:
   - Creación de recetas interconectadas al catálogo de alimentos.
   - **Herencia/Clonación**: Capacidad de duplicar una receta existente para crear variaciones sin afectar la original.
   - **Calculadora de Escalado**: Motor dinámico que permite proyectar recetas a diferentes cantidades de porciones, recalculando insumos, costos y nutrientes en tiempo real.

3. **Planificador de Menús y Cronogramas**:
   - Asignación de recetas por días de la semana y tiempos de comida (Desayuno, Almuerzo, Cena, etc.).
   - **Reporte de Adecuación Nutricional**: Validación inteligente que compara el menú contra una meta calórica y determina si cumple con la "Regla de Oro" institucional (90% - 110%).
   - **Consolidado de Víveres**: Generación automática de listas de compras agrupadas por alimento, con unidades estandarizadas (ej. gramos a kilogramos) y proyección de costos totales.

---

## 🛠️ Arquitectura y Tecnologías

El proyecto ha migrado a una arquitectura web cliente-servidor, separando la lógica de negocio de la interfaz de usuario:

### Backend (API REST)
- **Framework**: Python / Django
- **API Toolkit**: Django Ninja (Tipado estático y validación con Pydantic)
- **Base de Datos**: SQLite (Preparado para migrar a PostgreSQL)
- **Capa de Servicios**: Aislamiento de la lógica compleja (`services.py` para conversión de unidades, matemáticas de escalado y consolidación de víveres).

### Frontend (SPA)
- **Librería Core**: React 18
- **Build Tool**: Vite
- **Estilos**: Tailwind CSS v4
- **Iconografía**: Lucide React
- **Peticiones HTTP**: Axios (Centralizado en `client.js`)

---

## 📁 Estructura del Proyecto

```text
NutriApp/
│
├── backend/                    # Servidor API Django
│   ├── core/
│   │   ├── models.py           # Modelos de base de datos relacional
│   │   ├── schemas.py          # Esquemas de validación de entrada/salida (Ninja)
│   │   ├── api.py              # Definición de rutas RESTful
│   │   └── services.py         # Lógica de negocio, cálculos y reportes
│   └── manage.py
│
├── frontend/                   # Aplicación Web React
│   ├── src/
│   │   ├── api/
│   │   │   └── client.js       # Configuración de Axios
│   │   ├── components/
│   │   │   ├── CreateFoodModal.jsx
│   │   │   └── CreateRecipeModal.jsx
│   │   ├── pages/
│   │   │   ├── Foods.jsx       # Interfaz del Catálogo
│   │   │   ├── Recipes.jsx     # Gestión y escalado de recetas
│   │   │   └── Menus.jsx       # Planificador y reportes visuales
│   │   ├── Layout.jsx          # Estructura de navegación base
│   │   └── main.jsx            # Punto de entrada de React
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

---

## ⚙️ Instalación y Configuración Local

### 1. Configurar el Backend (Django)
Abre una terminal en la carpeta del backend:
```bash
# 1. Crear y activar entorno virtual
python -m venv venv
# En Windows: venv\Scripts\activate
# En Mac/Linux: source venv/bin/activate

# 2. Instalar dependencias
pip install django django-ninja django-cors-headers

# 3. Aplicar migraciones a la base de datos
python manage.py makemigrations
python manage.py migrate

# 4. Iniciar el servidor (por defecto en http://localhost:8000)
python manage.py runserver
```

### 2. Configurar el Frontend (React/Vite)
Abre otra terminal en la carpeta del frontend:
```bash
# 1. Instalar dependencias de Node
npm install

# 2. Iniciar el servidor de desarrollo (por defecto en http://localhost:5173)
npm run dev
```

---

## 📖 Uso

1. Inicia ambos servidores (Backend y Frontend).
2. Abre tu navegador en la URL indicada por Vite (usualmente `http://localhost:5173`).
3. Empieza poblando el **Catálogo de Alimentos**.
4. Crea **Recetas**, prueba la calculadora de porciones o hereda preparaciones.
5. Finalmente, arma tu **Menú Semanal** y genera los reportes de adecuación y víveres para la semana.