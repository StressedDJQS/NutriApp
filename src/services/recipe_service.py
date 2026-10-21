"""
Servicio de negocio para la gestión de recetas y preparaciones (HU-02, T05-T09).
Incluye selector/integración con el catálogo de alimentos, validación de porciones e ingredientes,
cálculos de costos y nutrientes, persistencia y reutilización de recetas.
"""

from typing import List, Optional, Dict
import sqlite3

from src.database.connection import Database, get_database
from src.models.food import Food
from src.models.recipe import Recipe, RecipeIngredient
from src.services.food_service import FoodService
from src.services.unit_converter import are_units_compatible, normalize_unit_name, get_unit_family
from src.services.nutrition_calc import calculate_recipe_totals, RecipeTotals


class RecipeValidationError(ValueError):
    """Excepción para errores de validación en la estructura de recetas."""
    pass


class DuplicateRecipeError(RecipeValidationError):
    """Excepción cuando se intenta registrar una receta con un nombre ya existente."""
    pass


class RecipeService:
    def __init__(self, db: Optional[Database] = None, food_service: Optional[FoodService] = None):
        self.db = db or get_database()
        self.food_service = food_service or FoodService(self.db)

    def validate_recipe(self, recipe: Recipe, is_update: bool = False) -> None:
        """
        Valida que la receta cumpla con todos los requerimientos de integridad:
        - Nombre obligatorio.
        - Porciones base > 0.
        - Al menos 1 ingrediente.
        - Cada ingrediente con food_id existente, cantidad > 0 y unidad compatible.
        - Prevención de nombres duplicados.
        """
        if not recipe.name or not recipe.name.strip():
            raise RecipeValidationError("El nombre de la receta es obligatorio.")

        if len(recipe.name.strip()) < 2:
            raise RecipeValidationError("El nombre de la receta debe tener al menos 2 caracteres.")

        if recipe.base_portions is None or recipe.base_portions <= 0:
            raise RecipeValidationError("El número de porciones base debe ser un entero mayor a 0.")

        if not recipe.ingredients:
            raise RecipeValidationError("La receta debe contener al menos un ingrediente.")

        # Validar duplicados de nombre
        trimmed_name = recipe.name.strip()
        with self.db.connection() as conn:
            query = "SELECT id, name FROM recipes WHERE TRIM(name) = ? COLLATE NOCASE"
            params = [trimmed_name]
            if is_update and recipe.id is not None:
                query += " AND id != ?"
                params.append(recipe.id)

            cur = conn.cursor()
            cur.execute(query, params)
            row = cur.fetchone()
            if row is not None:
                raise DuplicateRecipeError(
                    f"Ya existe una receta registrada con el nombre '{row['name']}'."
                )

        # Validar ingredientes
        seen_foods = set()
        for i, ing in enumerate(recipe.ingredients, start=1):
            if ing.food_id <= 0:
                raise RecipeValidationError(f"El ingrediente #{i} no tiene un alimento válido asignado.")

            if ing.food_id in seen_foods:
                raise RecipeValidationError(
                    f"El alimento #{ing.food_id} está repetido en la receta. Agrupe sus cantidades en una sola línea."
                )
            seen_foods.add(ing.food_id)

            if ing.quantity is None or ing.quantity <= 0:
                raise RecipeValidationError(f"La cantidad del ingrediente #{i} debe ser mayor a 0.")

            if not ing.unit or not ing.unit.strip():
                raise RecipeValidationError(f"La unidad del ingrediente #{i} es obligatoria.")

            # Comprobar que el alimento existe y su unidad es compatible
            food = self.food_service.get_food_by_id(ing.food_id)
            if food is None:
                raise RecipeValidationError(f"El alimento seleccionado en el ingrediente #{i} no existe en el catálogo.")

            ing.food = food
            ing.food_name = food.name
            ing.food_category = food.category

            norm_ing_unit = normalize_unit_name(ing.unit)
            norm_food_unit = normalize_unit_name(food.unit)

            if not are_units_compatible(norm_ing_unit, norm_food_unit):
                raise RecipeValidationError(
                    f"Unidad incompatible en '{food.name}': el ingrediente usa '{ing.unit}' "
                    f"pero el alimento está definido en '{food.unit}'."
                )

    def add_recipe(self, recipe: Recipe) -> Recipe:
        """Crea una nueva receta e inserta sus ingredientes en una sola transacción."""
        self.validate_recipe(recipe, is_update=False)

        with self.db.connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO recipes (name, description, base_portions)
                VALUES (?, ?, ?)
                """,
                (
                    recipe.name.strip(),
                    recipe.description.strip() if recipe.description else None,
                    recipe.base_portions,
                ),
            )
            recipe_id = cur.lastrowid
            recipe.id = recipe_id

            for ing in recipe.ingredients:
                cur.execute(
                    """
                    INSERT INTO recipe_ingredients (recipe_id, food_id, quantity, unit, notes)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        recipe_id,
                        ing.food_id,
                        round(ing.quantity, 4),
                        normalize_unit_name(ing.unit),
                        ing.notes.strip() if ing.notes else None,
                    ),
                )
                ing.id = cur.lastrowid
                ing.recipe_id = recipe_id

        return self.get_recipe_by_id(recipe_id)  # type: ignore

    def update_recipe(self, recipe: Recipe) -> Recipe:
        """Actualiza la receta y sincroniza sus ingredientes en una transacción."""
        if recipe.id is None:
            raise RecipeValidationError("El ID de la receta es obligatorio para actualizarla.")

        self.validate_recipe(recipe, is_update=True)

        with self.db.connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE recipes SET
                    name = ?,
                    description = ?,
                    base_portions = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    recipe.name.strip(),
                    recipe.description.strip() if recipe.description else None,
                    recipe.base_portions,
                    recipe.id,
                ),
            )
            if cur.rowcount == 0:
                raise RecipeValidationError(f"No se encontró la receta con ID {recipe.id}.")

            # Reemplazar ingredientes existentes
            cur.execute("DELETE FROM recipe_ingredients WHERE recipe_id = ?", (recipe.id,))

            for ing in recipe.ingredients:
                cur.execute(
                    """
                    INSERT INTO recipe_ingredients (recipe_id, food_id, quantity, unit, notes)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        recipe.id,
                        ing.food_id,
                        round(ing.quantity, 4),
                        normalize_unit_name(ing.unit),
                        ing.notes.strip() if ing.notes else None,
                    ),
                )
                ing.id = cur.lastrowid
                ing.recipe_id = recipe.id

        return self.get_recipe_by_id(recipe.id)  # type: ignore

    def get_recipe_by_id(self, recipe_id: int) -> Optional[Recipe]:
        """Recupera una receta completa con sus ingredientes e información de alimentos."""
        with self.db.connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,))
            row = cur.fetchone()
            if row is None:
                return None

            # Obtener ingredientes uniéndolos con foods
            cur.execute(
                """
                SELECT
                    ri.id, ri.recipe_id, ri.food_id, ri.quantity, ri.unit, ri.notes,
                    f.name AS food_name, f.category AS food_category,
                    f.unit AS food_unit, f.reference_base_amount, f.reference_base_unit,
                    f.unit_price, f.price_unit, f.calories, f.protein,
                    f.carbohydrates, f.fats, f.fiber, f.sodium
                FROM recipe_ingredients ri
                JOIN foods f ON f.id = ri.food_id
                WHERE ri.recipe_id = ?
                ORDER BY ri.id ASC
                """,
                (recipe_id,),
            )
            ing_rows = cur.fetchall()

            ingredients: List[RecipeIngredient] = []
            for r in ing_rows:
                ing = RecipeIngredient(
                    id=r["id"],
                    recipe_id=r["recipe_id"],
                    food_id=r["food_id"],
                    food_name=r["food_name"],
                    food_category=r["food_category"],
                    quantity=float(r["quantity"]),
                    unit=r["unit"],
                    notes=r["notes"],
                    food=Food(
                        id=r["food_id"],
                        name=r["food_name"],
                        category=r["food_category"],
                        unit=r["food_unit"],
                        reference_base_amount=float(r["reference_base_amount"]),
                        reference_base_unit=r["reference_base_unit"],
                        unit_price=float(r["unit_price"]),
                        price_unit=r["price_unit"],
                        calories=float(r["calories"]) if r["calories"] is not None else None,
                        protein=float(r["protein"]) if r["protein"] is not None else None,
                        carbohydrates=float(r["carbohydrates"]) if r["carbohydrates"] is not None else None,
                        fats=float(r["fats"]) if r["fats"] is not None else None,
                        fiber=float(r["fiber"]) if r["fiber"] is not None else None,
                        sodium=float(r["sodium"]) if r["sodium"] is not None else None,
                    ),
                )
                ingredients.append(ing)

            return Recipe.from_row(row, ingredients=ingredients)

    def list_recipes(self, search: Optional[str] = None) -> List[Recipe]:
        """Lista recetas con opción de búsqueda por nombre."""
        with self.db.connection() as conn:
            cur = conn.cursor()
            query = "SELECT * FROM recipes WHERE 1=1"
            params = []

            if search and search.strip():
                query += " AND name LIKE ?"
                params.append(f"%{search.strip()}%")

            query += " ORDER BY name COLLATE NOCASE ASC"
            cur.execute(query, params)
            rows = cur.fetchall()

            recipes = []
            for r in rows:
                # Cargar ingredientes para cada receta
                full_rec = self.get_recipe_by_id(r["id"])
                if full_rec:
                    recipes.append(full_rec)
            return recipes

    def delete_recipe(self, recipe_id: int) -> bool:
        """Elimina una receta y sus ingredientes en cascada."""
        with self.db.connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
            return cur.rowcount > 0

    def duplicate_recipe(self, recipe_id: int, new_name: Optional[str] = None) -> Recipe:
        """
        Reutiliza una receta existente creando una copia idéntica lista para ser editada.
        """
        original = self.get_recipe_by_id(recipe_id)
        if original is None:
            raise RecipeValidationError(f"No se encontró la receta con ID {recipe_id}.")

        base_name = new_name or f"{original.name} (Copia)"
        counter = 1
        candidate_name = base_name
        while True:
            with self.db.connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT 1 FROM recipes WHERE TRIM(name) = ? COLLATE NOCASE",
                    (candidate_name.strip(),),
                )
                if cur.fetchone() is None:
                    break
                counter += 1
                candidate_name = f"{base_name} {counter}"

        new_ingredients = [
            RecipeIngredient(
                food_id=ing.food_id,
                food_name=ing.food_name,
                food_category=ing.food_category,
                quantity=ing.quantity,
                unit=ing.unit,
                notes=ing.notes,
                food=ing.food,
            )
            for ing in original.ingredients
        ]

        cloned_recipe = Recipe(
            name=candidate_name,
            description=original.description,
            base_portions=original.base_portions,
            ingredients=new_ingredients,
        )
        return self.add_recipe(cloned_recipe)

    def calculate_recipe(
        self, recipe_id: int, target_portions: Optional[int] = None
    ) -> RecipeTotals:
        """
        Calcula el aporte nutricional y económico total y por porción,
        escalando si se solicita un número de porciones distinto al base.
        """
        recipe = self.get_recipe_by_id(recipe_id)
        if recipe is None:
            raise RecipeValidationError(f"No se encontró la receta con ID {recipe_id}.")

        return calculate_recipe_totals(recipe, target_portions=target_portions)
