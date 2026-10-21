"""
Pruebas exhaustivas de cálculos nutricionales, costos y escalado proporcional (T07, T10).
"""

import pytest
from src.models.food import Food
from src.models.recipe import Recipe, RecipeIngredient
from src.services.nutrition_calc import (
    calculate_ingredient_cost,
    calculate_ingredient_nutrients,
    scale_recipe_ingredients,
    calculate_recipe_totals,
)


def test_ingredient_cost_calculation():
    # Arroz: 4.00 soles el kg (1000g). Se usan 250g -> Costo = 1.00 sol
    arroz = Food(name="Arroz", unit="g", unit_price=4.00, price_unit="kg")
    cost = calculate_ingredient_cost(arroz, 250.0, "g")
    assert cost == 1.00

    # Aceite: 10.00 soles el litro. Se usan 50 ml -> Costo = 0.50 soles
    aceite = Food(name="Aceite", unit="ml", unit_price=10.00, price_unit="l")
    cost_aceite = calculate_ingredient_cost(aceite, 50.0, "ml")
    assert cost_aceite == 0.50

    # Huevos: 0.70 soles por unidad. Se usan 3 unidades -> Costo = 2.10 soles
    huevo = Food(name="Huevo", unit="unidad", unit_price=0.70, price_unit="unidad")
    cost_huevo = calculate_ingredient_cost(huevo, 3.0, "unidad")
    assert cost_huevo == 2.10


def test_ingredient_nutrients_calculation():
    # Pechuga: base 100g -> 165 kcal, 31g prot. Se usan 200g -> 330 kcal, 62g prot
    pollo = Food(
        name="Pollo",
        unit="g",
        reference_base_amount=100.0,
        reference_base_unit="g",
        unit_price=15.0,
        price_unit="kg",
        calories=165.0,
        protein=31.0,
        carbohydrates=0.0,
        fats=3.6,
        fiber=0.0,
        sodium=74.0,
    )
    nutrients, warnings = calculate_ingredient_nutrients(pollo, 200.0, "g")
    assert len(warnings) == 0
    assert nutrients["calories"] == 330.0
    assert nutrients["protein"] == 62.0
    assert nutrients["fats"] == 7.2
    assert nutrients["sodium"] == 148.0


def test_incomplete_nutritional_data_handling():
    # Alimento sin fibra ni sodio registrados (None)
    alimento_parcial = Food(
        name="Alimento Parcial",
        unit="g",
        reference_base_amount=100.0,
        reference_base_unit="g",
        unit_price=5.0,
        price_unit="kg",
        calories=100.0,
        protein=10.0,
        carbohydrates=15.0,
        fats=2.0,
        fiber=None,  # No registrado
        sodium=None, # No registrado
    )

    nutrients, warnings = calculate_ingredient_nutrients(alimento_parcial, 100.0, "g")
    assert nutrients["calories"] == 100.0
    assert nutrients["fiber"] is None
    assert nutrients["sodium"] is None
    # Debe haber advertencias explícitas para los campos ausentes
    assert any("Fibra" in w for w in warnings)
    assert any("Sodio" in w for w in warnings)


def test_recipe_scaling_from_4_to_10_portions(sample_foods):
    arroz = sample_foods["arroz"]   # 4.50 / kg
    pollo = sample_foods["pollo"]   # 16.00 / kg

    # Receta base para 4 porciones:
    # 400g arroz -> costo: 0.4kg * 4.50 = 1.80
    # 600g pollo -> costo: 0.6kg * 16.00 = 9.60
    # Costo total base = 1.80 + 9.60 = 11.40
    # Costo por porción base = 11.40 / 4 = 2.85
    recipe = Recipe(
        name="Arroz con Pollo Institucional",
        base_portions=4,
        ingredients=[
            RecipeIngredient(food_id=arroz.id, quantity=400.0, unit="g", food=arroz),
            RecipeIngredient(food_id=pollo.id, quantity=600.0, unit="g", food=pollo),
        ],
    )

    # 1. Totales base (4 porciones)
    totals_base = calculate_recipe_totals(recipe, target_portions=4)
    assert totals_base.total_cost == 11.40
    assert totals_base.cost_per_portion == 2.85
    # Calorías base:
    # Arroz: (400 / 100) * 130 = 520 kcal
    # Pollo: (600 / 100) * 165 = 990 kcal
    # Total = 1510 kcal -> Por porción = 1510 / 4 = 377.5 kcal
    assert totals_base.nutrients_total["calories"] == 1510.0
    assert totals_base.nutrients_per_portion["calories"] == 377.5

    # 2. Escalado a 10 porciones (ratio = 10 / 4 = 2.5)
    totals_scaled = calculate_recipe_totals(recipe, target_portions=10)
    assert totals_scaled.scale_factor == 2.5
    # Costo total escalado = 11.40 * 2.5 = 28.50
    assert totals_scaled.total_cost == 28.50
    # El costo por porción DEBE mantenerse constante (28.50 / 10 = 2.85)
    assert totals_scaled.cost_per_portion == 2.85

    # Nutrientes totales escalados = 1510 * 2.5 = 3775.0
    assert totals_scaled.nutrients_total["calories"] == 3775.0
    # Nutrientes por porción se mantienen iguales (3775 / 10 = 377.5)
    assert totals_scaled.nutrients_per_portion["calories"] == 377.5

    # Verificar escalado de cantidades individuales de ingredientes
    ing_arroz = next(i for i in totals_scaled.ingredients_detail if i.food_id == arroz.id)
    assert ing_arroz.scaled_quantity == 1000.0  # 400 * 2.5 = 1000 g

    ing_pollo = next(i for i in totals_scaled.ingredients_detail if i.food_id == pollo.id)
    assert ing_pollo.scaled_quantity == 1500.0  # 600 * 2.5 = 1500 g


def test_scale_recipe_ingredients_function():
    ings = [
        RecipeIngredient(food_id=1, quantity=100.0, unit="g"),
        RecipeIngredient(food_id=2, quantity=50.0, unit="ml"),
    ]
    scaled = scale_recipe_ingredients(ings, base_portions=2, target_portions=6)
    assert len(scaled) == 2
    assert scaled[0].quantity == 300.0
    assert scaled[1].quantity == 150.0
