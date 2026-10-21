"""
Pruebas de persistencia real en SQLite (Criterio de Aceptación 2 y 9).
Verifica que los datos persisten tras cerrar y volver a abrir conexiones y reiniciar la BD.
"""

from pathlib import Path
from src.database.connection import Database
from src.models.food import Food
from src.models.recipe import Recipe, RecipeIngredient
from src.services.food_service import FoodService
from src.services.recipe_service import RecipeService


def test_persistence_across_connection_restarts(tmp_path: Path):
    db_file = tmp_path / "persistent_test.db"

    # 1. Primera sesión: Crear BD y registrar alimentos y receta
    db_session1 = Database(db_file)
    food_service1 = FoodService(db_session1)
    recipe_service1 = RecipeService(db_session1, food_service1)

    f1 = food_service1.add_food(
        Food(
            name="Zanahoria",
            category="Verduras",
            unit="g",
            reference_base_amount=100.0,
            reference_base_unit="g",
            unit_price=2.50,
            price_unit="kg",
            calories=41.0,
            protein=0.9,
            carbohydrates=9.6,
            fats=0.2,
            fiber=2.8,
            sodium=69.0,
        )
    )

    r1 = recipe_service1.add_recipe(
        Recipe(
            name="Ensalada Fresca",
            base_portions=2,
            ingredients=[RecipeIngredient(food_id=f1.id, quantity=150.0, unit="g")],
        )
    )

    food_id = f1.id
    recipe_id = r1.id

    # Simular cierre total de sesión
    del db_session1
    del food_service1
    del recipe_service1

    # 2. Segunda sesión: Reabrir el archivo SQLite con una nueva instancia
    db_session2 = Database(db_file)
    food_service2 = FoodService(db_session2)
    recipe_service2 = RecipeService(db_session2, food_service2)

    # Verificar que el alimento existe y sus valores son idénticos
    f2 = food_service2.get_food_by_id(food_id)
    assert f2 is not None
    assert f2.name == "Zanahoria"
    assert f2.category == "Verduras"
    assert f2.unit_price == 2.50
    assert f2.fiber == 2.8

    # Verificar que la receta existe con sus ingredientes intactos
    r2 = recipe_service2.get_recipe_by_id(recipe_id)
    assert r2 is not None
    assert r2.name == "Ensalada Fresca"
    assert r2.base_portions == 2
    assert len(r2.ingredients) == 1
    assert r2.ingredients[0].food_id == food_id
    assert r2.ingredients[0].quantity == 150.0
    assert r2.ingredients[0].food_name == "Zanahoria"
