"""
Configuración de fixtures de pytest para NutriApp.
Utiliza bases de datos SQLite temporales y aisladas para garantizar que las pruebas
no toquen los datos de producción.
"""

import os
import tempfile
from pathlib import Path
import pytest

from src.database.connection import Database
from src.services.food_service import FoodService
from src.services.recipe_service import RecipeService
from src.models.food import Food


@pytest.fixture
def temp_db(tmp_path: Path) -> Database:
    """Crea una base de datos SQLite nueva en un directorio temporal."""
    db_file = tmp_path / "test_nutriapp.db"
    return Database(db_file)


@pytest.fixture
def food_service(temp_db: Database) -> FoodService:
    """Servicio de alimentos conectado a la base temporal."""
    return FoodService(temp_db)


@pytest.fixture
def recipe_service(temp_db: Database, food_service: FoodService) -> RecipeService:
    """Servicio de recetas conectado a la base temporal."""
    return RecipeService(temp_db, food_service)


@pytest.fixture
def sample_foods(food_service: FoodService) -> dict[str, Food]:
    """Crea un conjunto de alimentos de prueba variados para los tests."""
    arroz = food_service.add_food(
        Food(
            name="Arroz blanco",
            category="Cereales",
            unit="g",
            reference_base_amount=100.0,
            reference_base_unit="g",
            unit_price=4.50,  # 4.50 por kg
            price_unit="kg",
            calories=130.0,
            protein=2.7,
            carbohydrates=28.2,
            fats=0.3,
            fiber=0.4,
            sodium=1.0,
        )
    )

    pollo = food_service.add_food(
        Food(
            name="Pechuga de pollo",
            category="Carnes",
            unit="g",
            reference_base_amount=100.0,
            reference_base_unit="g",
            unit_price=16.00,  # 16.00 por kg
            price_unit="kg",
            calories=165.0,
            protein=31.0,
            carbohydrates=0.0,
            fats=3.6,
            fiber=0.0,
            sodium=74.0,
        )
    )

    aceite = food_service.add_food(
        Food(
            name="Aceite vegetal",
            category="Grasas y aceites",
            unit="ml",
            reference_base_amount=100.0,
            reference_base_unit="ml",
            unit_price=8.00,  # 8.00 por litro
            price_unit="l",
            calories=884.0,
            protein=0.0,
            carbohydrates=0.0,
            fats=100.0,
            fiber=0.0,
            sodium=0.0,
        )
    )

    huevo = food_service.add_food(
        Food(
            name="Huevo fresco",
            category="Huevos",
            unit="unidad",
            reference_base_amount=1.0,
            reference_base_unit="unidad",
            unit_price=0.60,  # 0.60 por unidad
            price_unit="unidad",
            calories=74.0,
            protein=6.3,
            carbohydrates=0.4,
            fats=5.0,
            fiber=0.0,
            sodium=70.0,
        )
    )

    sal = food_service.add_food(
        Food(
            name="Sal de mesa",
            category="Condimentos",
            unit="g",
            reference_base_amount=100.0,
            reference_base_unit="g",
            unit_price=1.50,  # 1.50 por kg
            price_unit="kg",
            calories=0.0,
            protein=0.0,
            carbohydrates=0.0,
            fats=0.0,
            fiber=0.0,
            sodium=38758.0,
        )
    )

    return {
        "arroz": arroz,
        "pollo": pollo,
        "aceite": aceite,
        "huevo": huevo,
        "sal": sal,
    }
