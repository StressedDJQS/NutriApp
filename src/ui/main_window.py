"""
Ventana principal de NutriApp (PySide6).
Integra las vistas de Alimentos y Recetas con navegación fluida y diseño moderno.
"""

from typing import Optional
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTabWidget,
    QFrame,
    QStatusBar,
    QMessageBox,
)

from src.database.connection import Database, get_database, get_default_db_path
from src.services.food_service import FoodService
from src.services.recipe_service import RecipeService
from src.ui.styles import APP_STYLE
from src.ui.food_view import FoodView
from src.ui.recipe_view import RecipeView


class MainWindow(QMainWindow):
    """Ventana principal de escritorio de NutriApp."""

    def __init__(self, db: Optional[Database] = None):
        super().__init__()
        self.db = db or get_database()
        self.food_service = FoodService(self.db)
        self.recipe_service = RecipeService(self.db, self.food_service)

        self.setWindowTitle("NutriApp — Sistema de Planificación Nutricional y Víveres Institucionales")
        self.resize(1120, 740)
        self.setMinimumSize(850, 600)

        # Aplicar estilos globales
        self.setStyleSheet(APP_STYLE)

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        central_widget.setAutoFillBackground(True)
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Encabezado institucional — forzar color de fondo también vía código
        # para garantizar visibilidad independiente de herencia del QSS.
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_frame.setAutoFillBackground(True)
        header_frame.setFixedHeight(60)
        header_frame.setStyleSheet(
            "QFrame#headerFrame { background-color: #1A365D; border-bottom: 2px solid #2B6CB0; }"
        )
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 8, 20, 8)

        header_text_layout = QVBoxLayout()
        header_text_layout.setSpacing(2)

        lbl_title = QLabel("NutriApp")
        lbl_title.setObjectName("appTitle")
        lbl_title.setStyleSheet("color: #FFFFFF; font-size: 20px; font-weight: 700; background: transparent;")

        lbl_sub = QLabel("Sistema de Planificación Nutricional y Requerimiento de Víveres")
        lbl_sub.setObjectName("appSubtitle")
        lbl_sub.setStyleSheet("color: #E2E8F0; font-size: 11px; background: transparent;")

        header_text_layout.addWidget(lbl_title)
        header_text_layout.addWidget(lbl_sub)
        header_layout.addLayout(header_text_layout)
        header_layout.addStretch()

        root_layout.addWidget(header_frame)

        # Contenedor con pestañas principales
        content_container = QWidget()
        content_container.setObjectName("contentContainer")
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(14, 14, 14, 14)

        self.tabs = QTabWidget()

        # Pestaña 1: Catálogo de Alimentos
        self.food_view = FoodView(self.food_service)
        self.tabs.addTab(self.food_view, "🥗  Catálogo de Alimentos")

        # Pestaña 2: Gestión de Recetas
        self.recipe_view = RecipeView(self.food_service, self.recipe_service)
        self.tabs.addTab(self.recipe_view, "📖  Gestión de Recetas y Preparaciones")

        # Sincronización: si cambian alimentos, actualizar recetas
        self.food_view.foods_changed.connect(self.recipe_view.refresh_recipes)

        content_layout.addWidget(self.tabs)
        root_layout.addWidget(content_container)

        # Barra de estado
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        db_path_str = str(self.db.db_path)
        status_bar.showMessage(f"Base de datos local activa: {db_path_str} | Modo sin conexión garantizado")
