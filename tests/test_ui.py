"""
Pruebas automatizadas de la interfaz gráfica PySide6 (offscreen).
Verifica que las ventanas y componentes principales se inicializan y comunican correctamente.
"""

import os
import pytest
from PySide6.QtWidgets import QApplication

# Configurar plataforma offscreen para entornos de pruebas automatizadas
os.environ["QT_QPA_PLATFORM"] = "offscreen"

@pytest.fixture(scope="session")
def qapp():
    """Fixture que provee la instancia única de QApplication."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_main_window_initialization(qapp, temp_db, sample_foods):
    from src.ui.main_window import MainWindow

    window = MainWindow(db=temp_db)
    assert window is not None
    assert "NutriApp" in window.windowTitle()
    assert window.tabs.count() == 2

    # Verificar que las pestañas están presentes
    assert window.food_view is not None
    assert window.recipe_view is not None

    # Verificar que los alimentos de muestra se muestran en la tabla
    assert window.food_view.table.rowCount() == len(sample_foods)
    window.close()


def test_food_view_filter_interaction(qapp, temp_db, sample_foods):
    from src.ui.food_view import FoodView
    from src.services.food_service import FoodService

    service = FoodService(temp_db)
    view = FoodView(service)

    # Filtrar por texto "pollo"
    view.input_search.setText("pollo")
    assert view.table.rowCount() == 1
    assert "pollo" in view.table.item(0, 1).text().lower()

    # Limpiar filtro
    view.clear_filters()
    assert view.table.rowCount() == len(sample_foods)
    view.close()


def test_recipe_view_interaction(qapp, temp_db, sample_foods):
    from src.ui.recipe_view import RecipeView
    from src.services.food_service import FoodService
    from src.services.recipe_service import RecipeService
    from src.models.recipe import Recipe, RecipeIngredient

    f_service = FoodService(temp_db)
    r_service = RecipeService(temp_db, f_service)

    pollo = sample_foods["pollo"]
    r_service.add_recipe(
        Recipe(
            name="Receta Test UI",
            base_portions=4,
            ingredients=[RecipeIngredient(food_id=pollo.id, quantity=400, unit="g")],
        )
    )

    view = RecipeView(f_service, r_service)
    assert view.table.rowCount() == 1
    assert view.table.item(0, 1).text() == "Receta Test UI"
    view.close()
