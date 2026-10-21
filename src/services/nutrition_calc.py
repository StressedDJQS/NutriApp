"""
Cálculos deterministas nutricionales y de costos para NutriApp.
Separado por completo de la interfaz para facilitar pruebas unitarias exhaustivas.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

from src.models.food import Food
from src.models.recipe import Recipe, RecipeIngredient
from src.services.unit_converter import convert_quantity, are_units_compatible


NUTRIENT_FIELDS = [
    ("calories", "Energía", "kcal"),
    ("protein", "Proteínas", "g"),
    ("carbohydrates", "Carbohidratos", "g"),
    ("fats", "Grasas", "g"),
    ("fiber", "Fibra", "g"),
    ("sodium", "Sodio", "mg"),
]


@dataclass
class IngredientCalculation:
    ingredient_id: Optional[int]
    food_id: int
    food_name: str
    original_quantity: float
    scaled_quantity: float
    unit: str
    cost: float
    nutrients: Dict[str, Optional[float]]
    warnings: List[str] = field(default_factory=list)


@dataclass
class RecipeTotals:
    total_cost: float = 0.0
    cost_per_portion: float = 0.0
    # Nutrientes totales acumulados (None si ningún ingrediente lo aportó o si falta dato clave)
    nutrients_total: Dict[str, Optional[float]] = field(default_factory=dict)
    # Nutrientes por porción
    nutrients_per_portion: Dict[str, Optional[float]] = field(default_factory=dict)
    # Alimentos con información nutricional parcial o ausente
    incomplete_nutrients_warnings: List[str] = field(default_factory=list)
    # Ingredientes detallados calculados y escalados
    ingredients_detail: List[IngredientCalculation] = field(default_factory=list)
    # Porciones sobre las que se realizó el cálculo
    base_portions: int = 1
    target_portions: int = 1
    scale_factor: float = 1.0


def calculate_ingredient_cost(food: Food, quantity: float, unit: str) -> float:
    """
    Calcula el costo económico de una cantidad de ingrediente según el precio del alimento.
    """
    if quantity <= 0:
        return 0.0
    if food.unit_price <= 0:
        return 0.0

    # Convertir la cantidad a la unidad en la que está cotizado el precio (price_unit)
    # Ej: precio por kg, cantidad en g -> convert_quantity(500, 'g', 'kg') = 0.5 kg
    qty_in_price_unit = convert_quantity(quantity, unit, food.price_unit)
    return round(qty_in_price_unit * food.unit_price, 4)


def calculate_ingredient_nutrients(
    food: Food, quantity: float, unit: str
) -> tuple[Dict[str, Optional[float]], List[str]]:
    """
    Calcula el aporte de cada nutriente para la cantidad dada.
    No inventa datos: si un nutriente es None, permanece None y se genera una advertencia.
    """
    nutrients: Dict[str, Optional[float]] = {}
    warnings: List[str] = []

    # Determinar factor de escala respecto a la base nutricional de referencia
    # (ej. 100 g de base, ingrediente 250 g -> factor = 2.5)
    qty_in_ref_unit = convert_quantity(quantity, unit, food.reference_base_unit)
    factor = qty_in_ref_unit / food.reference_base_amount

    for key, label, u_label in NUTRIENT_FIELDS:
        val = getattr(food, key, None)
        if val is None:
            nutrients[key] = None
            warnings.append(f"El alimento '{food.name}' no tiene registrado el campo {label}.")
        else:
            nutrients[key] = round(val * factor, 4)

    return nutrients, warnings


def scale_recipe_ingredients(
    ingredients: List[RecipeIngredient], base_portions: int, target_portions: int
) -> List[RecipeIngredient]:
    """
    Escala proporcionalmente las cantidades de cada ingrediente según el número de porciones.
    Retorna una nueva lista de RecipeIngredient con cantidades ajustadas.
    """
    if base_portions <= 0:
        raise ValueError("Las porciones base deben ser mayores a 0.")
    if target_portions <= 0:
        raise ValueError("Las porciones objetivo deben ser mayores a 0.")

    ratio = target_portions / base_portions
    scaled: List[RecipeIngredient] = []

    for ing in ingredients:
        scaled.append(
            RecipeIngredient(
                id=ing.id,
                recipe_id=ing.recipe_id,
                food_id=ing.food_id,
                food_name=ing.food_name,
                food_category=ing.food_category,
                quantity=round(ing.quantity * ratio, 4),
                unit=ing.unit,
                notes=ing.notes,
                food=ing.food,
            )
        )
    return scaled


def calculate_recipe_totals(
    recipe: Recipe,
    target_portions: Optional[int] = None,
    food_catalog: Optional[Dict[int, Food]] = None,
) -> RecipeTotals:
    """
    Cálculo consolidado de costo total, costo por porción, nutrientes totales y nutrientes
    por porción. Escala proporcionalmente si target_portions difiere de base_portions.
    """
    if recipe.base_portions <= 0:
        raise ValueError("La receta debe tener porciones base mayores a 0.")

    target = target_portions if (target_portions is not None and target_portions > 0) else recipe.base_portions
    scale_factor = target / recipe.base_portions

    res = RecipeTotals(
        base_portions=recipe.base_portions,
        target_portions=target,
        scale_factor=scale_factor,
    )

    total_cost = 0.0
    nutrients_accumulator: Dict[str, float] = {key: 0.0 for key, _, _ in NUTRIENT_FIELDS}
    nutrients_has_any_data: Dict[str, bool] = {key: False for key, _, _ in NUTRIENT_FIELDS}
    nutrients_has_missing_data: Dict[str, bool] = {key: False for key, _, _ in NUTRIENT_FIELDS}
    global_warnings: List[str] = []

    for ing in recipe.ingredients:
        # Resolver el alimento asociado
        food = ing.food
        if food is None and food_catalog and ing.food_id in food_catalog:
            food = food_catalog[ing.food_id]

        if food is None:
            # Alimento no encontrado en catálogo
            warning_msg = f"No se encontró información del alimento ID {ing.food_id} ('{ing.food_name or 'desconocido'}')."
            global_warnings.append(warning_msg)
            res.ingredients_detail.append(
                IngredientCalculation(
                    ingredient_id=ing.id,
                    food_id=ing.food_id,
                    food_name=ing.food_name or "Desconocido",
                    original_quantity=ing.quantity,
                    scaled_quantity=round(ing.quantity * scale_factor, 4),
                    unit=ing.unit,
                    cost=0.0,
                    nutrients={key: None for key, _, _ in NUTRIENT_FIELDS},
                    warnings=[warning_msg],
                )
            )
            continue

        scaled_qty = round(ing.quantity * scale_factor, 4)

        # Cálculo de costo
        try:
            cost = calculate_ingredient_cost(food, scaled_qty, ing.unit)
        except ValueError as e:
            cost = 0.0
            global_warnings.append(f"Error de costo en '{food.name}': {str(e)}")

        total_cost += cost

        # Cálculo de nutrientes
        try:
            nutrients, ing_warnings = calculate_ingredient_nutrients(food, scaled_qty, ing.unit)
        except ValueError as e:
            nutrients = {key: None for key, _, _ in NUTRIENT_FIELDS}
            ing_warnings = [f"Error de unidades en '{food.name}': {str(e)}"]

        if ing_warnings:
            global_warnings.extend(ing_warnings)

        for key, _, _ in NUTRIENT_FIELDS:
            val = nutrients.get(key)
            if val is not None:
                nutrients_accumulator[key] += val
                nutrients_has_any_data[key] = True
            else:
                nutrients_has_missing_data[key] = True

        res.ingredients_detail.append(
            IngredientCalculation(
                ingredient_id=ing.id,
                food_id=food.id or ing.food_id,
                food_name=food.name,
                original_quantity=ing.quantity,
                scaled_quantity=scaled_qty,
                unit=ing.unit,
                cost=cost,
                nutrients=nutrients,
                warnings=ing_warnings,
            )
        )

    res.total_cost = round(total_cost, 2)
    res.cost_per_portion = round(total_cost / target, 2) if target > 0 else 0.0

    # Procesar totales de nutrientes
    for key, label, _ in NUTRIENT_FIELDS:
        if nutrients_has_any_data[key]:
            t_val = round(nutrients_accumulator[key], 2)
            res.nutrients_total[key] = t_val
            res.nutrients_per_portion[key] = round(t_val / target, 2) if target > 0 else 0.0
            if nutrients_has_missing_data[key]:
                res.incomplete_nutrients_warnings.append(
                    f"El total de {label} es parcial: algunos ingredientes no tenían este valor registrado."
                )
        else:
            # Ningún ingrediente aportó este dato o no había datos
            res.nutrients_total[key] = None
            res.nutrients_per_portion[key] = None

    if global_warnings:
        # Eliminar duplicados manteniendo orden
        seen = set()
        unique_warnings = []
        for w in global_warnings + res.incomplete_nutrients_warnings:
            if w not in seen:
                seen.add(w)
                unique_warnings.append(w)
        res.incomplete_nutrients_warnings = unique_warnings

    return res
