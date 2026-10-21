"""
Pruebas del servicio de recetas (HU-02, T05, T06, T08, T09).
"""

import pytest
from src.models.recipe import Recipe, RecipeIngredient
from src.services.recipe_service import (
    RecipeService,
    RecipeValidationError,
    DuplicateRecipeError,
)


def test_create_and_get_recipe(recipe_service: RecipeService, sample_foods):
    arroz = sample_foods["arroz"]
    pollo = sample_foods["pollo"]
    aceite = sample_foods["aceite"]

    recipe = Recipe(
        name="Arroz con Pollo Básico",
        description="Receta nutritiva institucional",
        base_portions=4,
        ingredients=[
            RecipeIngredient(food_id=arroz.id, quantity=400, unit="g"),
            RecipeIngredient(food_id=pollo.id, quantity=600, unit="g"),
            RecipeIngredient(food_id=aceite.id, quantity=20, unit="ml"),
        ],
    )

    saved = recipe_service.add_recipe(recipe)
    assert saved.id is not None
    assert saved.name == "Arroz con Pollo Básico"
    assert len(saved.ingredients) == 3

    # Recuperar
    fetched = recipe_service.get_recipe_by_id(saved.id)
    assert fetched is not None
    assert fetched.name == "Arroz con Pollo Básico"
    assert fetched.base_portions == 4
    assert len(fetched.ingredients) == 3
    # Verificar que los datos del alimento están unidos
    assert fetched.ingredients[0].food_name == "Arroz blanco"
    assert fetched.ingredients[1].food_name == "Pechuga de pollo"


def test_reject_recipe_without_name(recipe_service: RecipeService, sample_foods):
    arroz = sample_foods["arroz"]
    recipe = Recipe(
        name="",
        base_portions=2,
        ingredients=[RecipeIngredient(food_id=arroz.id, quantity=200, unit="g")],
    )
    with pytest.raises(RecipeValidationError, match="El nombre de la receta es obligatorio"):
        recipe_service.add_recipe(recipe)


def test_reject_recipe_without_ingredients(recipe_service: RecipeService):
    recipe = Recipe(name="Receta Vacía", base_portions=2, ingredients=[])
    with pytest.raises(RecipeValidationError, match="debe contener al menos un ingrediente"):
        recipe_service.add_recipe(recipe)


def test_reject_invalid_portions(recipe_service: RecipeService, sample_foods):
    arroz = sample_foods["arroz"]
    recipe = Recipe(
        name="Porciones Cero",
        base_portions=0,
        ingredients=[RecipeIngredient(food_id=arroz.id, quantity=100, unit="g")],
    )
    with pytest.raises(RecipeValidationError, match="mayor a 0"):
        recipe_service.add_recipe(recipe)


def test_reject_invalid_ingredient_quantity(recipe_service: RecipeService, sample_foods):
    arroz = sample_foods["arroz"]
    recipe = Recipe(
        name="Cantidad Negativa",
        base_portions=1,
        ingredients=[RecipeIngredient(food_id=arroz.id, quantity=-50, unit="g")],
    )
    with pytest.raises(RecipeValidationError, match="cantidad.*debe ser mayor a 0"):
        recipe_service.add_recipe(recipe)


def test_reject_duplicate_recipe_name(recipe_service: RecipeService, sample_foods):
    arroz = sample_foods["arroz"]
    r1 = Recipe(
        name="Tortilla Simple",
        base_portions=1,
        ingredients=[RecipeIngredient(food_id=arroz.id, quantity=100, unit="g")],
    )
    recipe_service.add_recipe(r1)

    r2 = Recipe(
        name="  tortilla simple  ",
        base_portions=2,
        ingredients=[RecipeIngredient(food_id=arroz.id, quantity=150, unit="g")],
    )
    with pytest.raises(DuplicateRecipeError, match="Ya existe una receta registrada"):
        recipe_service.add_recipe(r2)


def test_duplicate_and_reuse_recipe(recipe_service: RecipeService, sample_foods):
    pollo = sample_foods["pollo"]
    original = recipe_service.add_recipe(
        Recipe(
            name="Guiso de Pollo",
            description="Versión estándar",
            base_portions=4,
            ingredients=[RecipeIngredient(food_id=pollo.id, quantity=500, unit="g")],
        )
    )

    cloned = recipe_service.duplicate_recipe(original.id)
    assert cloned.id != original.id
    assert "Copia" in cloned.name
    assert len(cloned.ingredients) == 1
    assert cloned.ingredients[0].food_id == pollo.id
    assert cloned.ingredients[0].quantity == 500


def test_update_recipe(recipe_service: RecipeService, sample_foods):
    pollo = sample_foods["pollo"]
    arroz = sample_foods["arroz"]

    rec = recipe_service.add_recipe(
        Recipe(
            name="Plato Combinado",
            base_portions=2,
            ingredients=[RecipeIngredient(food_id=pollo.id, quantity=300, unit="g")],
        )
    )

    rec.base_portions = 3
    rec.name = "Plato Combinado Modificado"
    rec.ingredients.append(RecipeIngredient(food_id=arroz.id, quantity=200, unit="g"))

    updated = recipe_service.update_recipe(rec)
    assert updated.name == "Plato Combinado Modificado"
    assert updated.base_portions == 3
    assert len(updated.ingredients) == 2


def test_delete_recipe(recipe_service: RecipeService, sample_foods):
    arroz = sample_foods["arroz"]
    rec = recipe_service.add_recipe(
        Recipe(
            name="Receta a borrar",
            base_portions=1,
            ingredients=[RecipeIngredient(food_id=arroz.id, quantity=100, unit="g")],
        )
    )
    rec_id = rec.id

    assert recipe_service.delete_recipe(rec_id) is True
    assert recipe_service.get_recipe_by_id(rec_id) is None
    # El alimento original no debe haberse borrado
    assert sample_foods["arroz"].id is not None
