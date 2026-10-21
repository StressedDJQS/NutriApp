"""
Punto de entrada principal de NutriApp.
Sistema de Planificación Nutricional y Requerimiento de Víveres Institucionales.
"""

import sys
import os

# Asegurar que el directorio raíz del proyecto esté en el sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from PySide6.QtWidgets import QApplication
from src.database.connection import get_database
from src.ui.main_window import MainWindow


def main():
    # Inicializar la base de datos SQLite y su esquema persistente
    db = get_database()

    app = QApplication(sys.argv)
    app.setApplicationName("NutriApp")
    app.setOrganizationName("NutriApp")

    window = MainWindow(db=db)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
