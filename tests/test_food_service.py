"""
Pruebas del servicio de alimentos (HU-01, T01-T04).
"""

import pytest
from src.models.food import Food
from src.models.recipe import Recipe, RecipeIngredient
from src.services.food_service import (
    FoodService,
    FoodValidationError,
    DuplicateFoodError,
    FoodInUseError,
)
from src.services.recipe_service import RecipeService


def test_add_and_get_food(food_service: FoodService):
    food = Food(
        name="Lentejas",
        category="Legumbres",
        unit="g",
        reference_base_amount=100.0,
        reference_base_unit="g",
        unit_price=5.50,
        price_unit="kg",
        calories=353.0,
        protein=25.8,
        carbohydrates=60.1,
        fats=1.1,
        fiber=30.5,
        sodium=6.0,
    )
    saved = food_service.add_food(food)
    assert saved.id is not None
    assert saved.name == "Lentejas"
    assert saved.calories == 353.0

    retrieved = food_service.get_food_by_id(saved.id)
    assert retrieved is not None
    assert retrieved.name == "Lentejas"
    assert retrieved.unit_price == 5.50
    assert retrieved.fiber == 30.5


def test_reject_empty_name(food_service: FoodService):
    food = Food(name="   ", unit="g", unit_price=1.0, price_unit="kg")
    with pytest.raises(FoodValidationError, match="El nombre del alimento es obligatorio"):
        food_service.add_food(food)


def test_reject_negative_price(food_service: FoodService):
    food = Food(name="Manzana", unit="g", unit_price=-2.5, price_unit="kg")
    with pytest.raises(FoodValidationError, match="precio unitario no puede ser negativo"):
        food_service.add_food(food)


def test_reject_negative_nutrients(food_service: FoodService):
    food = Food(
        name="Plátano",
        unit="g",
        unit_price=3.0,
        price_unit="kg",
        calories=-10.0,
    )
    with pytest.raises(FoodValidationError, match="energía.*no puede ser negativo"):
        food_service.add_food(food)

    food2 = Food(
        name="Plátano 2",
        unit="g",
        unit_price=3.0,
        price_unit="kg",
        protein=-1.0,
    )
    with pytest.raises(FoodValidationError, match="proteínas.*no puede ser negativo"):
        food_service.add_food(food2)


def test_reject_duplicate_food_name(food_service: FoodService):
    f1 = Food(name="Avena en hojuelas", unit="g", unit_price=4.0, price_unit="kg")
    food_service.add_food(f1)

    f2 = Food(name="  avena en hojuelas  ", unit="g", unit_price=4.5, price_unit="kg")
    with pytest.raises(DuplicateFoodError, match="Ya existe un alimento registrado"):
        food_service.add_food(f2)


def test_update_food(food_service: FoodService):
    food = food_service.add_food(
        Food(name="Papa blanca", unit="g", unit_price=2.00, price_unit="kg", calories=87.0)
    )
    food.unit_price = 2.40
    food.calories = 89.0
    updated = food_service.update_food(food)

    assert updated.unit_price == 2.40
    assert updated.calories == 89.0

    # Verificar que persiste recuperándolo por ID
    fetched = food_service.get_food_by_id(food.id)
    assert fetched.unit_price == 2.40


def test_search_and_filter_foods(food_service: FoodService):
    food_service.add_food(Food(name="Leche entera", category="Lácteos", unit="ml", unit_price=4.0, price_unit="l"))
    food_service.add_food(Food(name="Yogurt natural", category="Lácteos", unit="ml", unit_price=6.0, price_unit="l"))
    food_service.add_food(Food(name="Queso fresco", category="Lácteos", unit="g", unit_price=22.0, price_unit="kg"))
    food_service.add_food(Food(name="Manzana verde", category="Frutas", unit="g", unit_price=5.0, price_unit="kg"))

    # Búsqueda por texto
    results = food_service.list_foods(search="queso")
    assert len(results) == 1
    assert results[0].name == "Queso fresco"

    # Filtro por categoría
    lacteos = food_service.list_foods(category="Lácteos")
    assert len(lacteos) == 3

    # Búsqueda y categoría combinadas
    res_comb = food_service.list_foods(search="leche", category="Lácteos")
    assert len(res_comb) == 1
    assert res_comb[0].name == "Leche entera"


def test_prevent_deletion_when_used_in_recipe(
    food_service: FoodService, recipe_service: RecipeService, sample_foods
):
    pollo = sample_foods["pollo"]
    # Crear una receta que usa pollo
    recipe_service.add_recipe(
        Recipe(
            name="Pollo a la plancha",
            base_portions=2,
            ingredients=[
                RecipeIngredient(food_id=pollo.id, quantity=300, unit="g")
            ],
        )
    )

    with pytest.raises(FoodInUseError, match="siendo utilizado en las siguientes recetas"):
        food_service.delete_food(pollo.id)

    # Verificar que el alimento sigue intacto
    assert food_service.get_food_by_id(pollo.id) is not None
