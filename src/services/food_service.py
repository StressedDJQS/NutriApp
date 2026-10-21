"""
Servicio de negocio para el catálogo y registro de alimentos (HU-01, T01-T04).
Maneja validaciones rigurosas, persistencia en SQLite, búsquedas, filtros y prevención de duplicados.
"""

from typing import List, Optional
import sqlite3

from src.database.connection import Database, get_database
from src.models.food import Food
from src.services.unit_converter import get_unit_family, normalize_unit_name


class FoodValidationError(ValueError):
    """Excepción cuando los datos de un alimento no cumplen con las validaciones de negocio."""
    pass


class DuplicateFoodError(FoodValidationError):
    """Excepción cuando se intenta registrar un alimento duplicado."""
    pass


class FoodInUseError(Exception):
    """Excepción cuando se intenta eliminar un alimento que está siendo usado en recetas."""
    pass


class FoodService:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or get_database()

    def validate_food(self, food: Food, is_update: bool = False) -> None:
        """
        Valida rigurosamente los datos del alimento:
        - Campos obligatorios (nombre, unidad, unidad de precio).
        - Precios no negativos.
        - Nutrientes no negativos cuando están presentes.
        - Unidades válidas y coherentes.
        """
        if not food.name or not food.name.strip():
            raise FoodValidationError("El nombre del alimento es obligatorio.")

        if len(food.name.strip()) < 2:
            raise FoodValidationError("El nombre del alimento debe tener al menos 2 caracteres.")

        if food.unit_price is None or food.unit_price < 0:
            raise FoodValidationError("El precio unitario no puede ser negativo.")

        if not food.unit or not food.unit.strip():
            raise FoodValidationError("La unidad de medida es obligatoria.")

        unit_fam = get_unit_family(food.unit)
        if unit_fam == "unknown":
            raise FoodValidationError(
                f"La unidad '{food.unit}' no es reconocida. Utilice g, kg, ml, l o unidad."
            )

        if not food.price_unit or not food.price_unit.strip():
            raise FoodValidationError("La unidad de referencia del precio es obligatoria.")

        price_unit_fam = get_unit_family(food.price_unit)
        if price_unit_fam == "unknown":
            raise FoodValidationError(
                f"La unidad de precio '{food.price_unit}' no es reconocida."
            )

        if unit_fam != price_unit_fam:
            raise FoodValidationError(
                f"Incoherencia de unidades: La unidad física '{food.unit}' ({unit_fam}) "
                f"no coincide con la familia de la unidad del precio '{food.price_unit}' ({price_unit_fam})."
            )

        if food.reference_base_amount <= 0:
            raise FoodValidationError("La cantidad base de referencia nutricional debe ser mayor a 0.")

        # Validar nutrientes no negativos
        nutrient_checks = [
            ("calories", "energía (kcal)", food.calories),
            ("protein", "proteínas (g)", food.protein),
            ("carbohydrates", "carbohidratos (g)", food.carbohydrates),
            ("fats", "grasas (g)", food.fats),
            ("fiber", "fibra (g)", food.fiber),
            ("sodium", "sodio (mg)", food.sodium),
        ]

        for field_name, label, val in nutrient_checks:
            if val is not None:
                if not isinstance(val, (int, float)):
                    raise FoodValidationError(f"El valor de {label} debe ser un número válido.")
                if val < 0:
                    raise FoodValidationError(f"El valor de {label} no puede ser negativo.")

        # Comprobar duplicados por nombre ignorando mayúsculas y espacios
        trimmed_name = food.name.strip()
        with self.db.connection() as conn:
            query = "SELECT id, name FROM foods WHERE TRIM(name) = ? COLLATE NOCASE"
            params = [trimmed_name]
            if is_update and food.id is not None:
                query += " AND id != ?"
                params.append(food.id)

            cur = conn.cursor()
            cur.execute(query, params)
            row = cur.fetchone()
            if row is not None:
                raise DuplicateFoodError(
                    f"Ya existe un alimento registrado con el nombre '{row['name']}'."
                )

    def add_food(self, food: Food) -> Food:
        """Registra un nuevo alimento en la base de datos."""
        self.validate_food(food, is_update=False)

        with self.db.connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO foods (
                    name, category, unit, reference_base_amount, reference_base_unit,
                    unit_price, price_unit, calories, protein, carbohydrates,
                    fats, fiber, sodium
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    food.name.strip(),
                    food.category.strip() if food.category else None,
                    normalize_unit_name(food.unit),
                    food.reference_base_amount,
                    normalize_unit_name(food.reference_base_unit),
                    round(food.unit_price, 4),
                    normalize_unit_name(food.price_unit),
                    round(food.calories, 2) if food.calories is not None else None,
                    round(food.protein, 2) if food.protein is not None else None,
                    round(food.carbohydrates, 2) if food.carbohydrates is not None else None,
                    round(food.fats, 2) if food.fats is not None else None,
                    round(food.fiber, 2) if food.fiber is not None else None,
                    round(food.sodium, 2) if food.sodium is not None else None,
                ),
            )
            food_id = cur.lastrowid

        return self.get_food_by_id(food_id)  # type: ignore

    def update_food(self, food: Food) -> Food:
        """Actualiza un alimento existente."""
        if food.id is None:
            raise FoodValidationError("El ID del alimento es necesario para actualizarlo.")

        self.validate_food(food, is_update=True)

        with self.db.connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE foods SET
                    name = ?,
                    category = ?,
                    unit = ?,
                    reference_base_amount = ?,
                    reference_base_unit = ?,
                    unit_price = ?,
                    price_unit = ?,
                    calories = ?,
                    protein = ?,
                    carbohydrates = ?,
                    fats = ?,
                    fiber = ?,
                    sodium = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    food.name.strip(),
                    food.category.strip() if food.category else None,
                    normalize_unit_name(food.unit),
                    food.reference_base_amount,
                    normalize_unit_name(food.reference_base_unit),
                    round(food.unit_price, 4),
                    normalize_unit_name(food.price_unit),
                    round(food.calories, 2) if food.calories is not None else None,
                    round(food.protein, 2) if food.protein is not None else None,
                    round(food.carbohydrates, 2) if food.carbohydrates is not None else None,
                    round(food.fats, 2) if food.fats is not None else None,
                    round(food.fiber, 2) if food.fiber is not None else None,
                    round(food.sodium, 2) if food.sodium is not None else None,
                    food.id,
                ),
            )
            if cur.rowcount == 0:
                raise FoodValidationError(f"No se encontró el alimento con ID {food.id}.")

        return self.get_food_by_id(food.id)  # type: ignore

    def get_food_by_id(self, food_id: int) -> Optional[Food]:
        """Obtiene un alimento por su ID."""
        with self.db.connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM foods WHERE id = ?", (food_id,))
            row = cur.fetchone()
            if row is None:
                return None
            return Food.from_row(row)

    def get_food_by_name(self, name: str) -> Optional[Food]:
        """Obtiene un alimento por su nombre (exacto o ignorando mayúsculas)."""
        with self.db.connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM foods WHERE TRIM(name) = ? COLLATE NOCASE",
                (name.strip(),),
            )
            row = cur.fetchone()
            if row is None:
                return None
            return Food.from_row(row)

    def list_foods(
        self,
        search: Optional[str] = None,
        category: Optional[str] = None,
    ) -> List[Food]:
        """Lista alimentos con soporte para búsqueda por nombre y filtro por categoría."""
        with self.db.connection() as conn:
            cur = conn.cursor()
            query = "SELECT * FROM foods WHERE 1=1"
            params = []

            if search and search.strip():
                query += " AND name LIKE ?"
                params.append(f"%{search.strip()}%")

            if category and category.strip() and category.strip().lower() != "todas":
                query += " AND category = ?"
                params.append(category.strip())

            query += " ORDER BY name COLLATE NOCASE ASC"
            cur.execute(query, params)
            rows = cur.fetchall()
            return [Food.from_row(r) for r in rows]

    def delete_food(self, food_id: int) -> bool:
        """
        Elimina un alimento si no está siendo utilizado en ninguna receta.
        Lanza FoodInUseError si está referenciado.
        """
        with self.db.connection() as conn:
            cur = conn.cursor()
            # Comprobar recetas que lo usan
            cur.execute(
                """
                SELECT r.name FROM recipe_ingredients ri
                JOIN recipes r ON r.id = ri.recipe_id
                WHERE ri.food_id = ?
                """,
                (food_id,),
            )
            recipes = [row["name"] for row in cur.fetchall()]
            if recipes:
                recipe_names = ", ".join(f"'{r}'" for r in recipes[:3])
                if len(recipes) > 3:
                    recipe_names += f" y {len(recipes) - 3} más"
                raise FoodInUseError(
                    f"No se puede eliminar el alimento porque está siendo utilizado en las siguientes recetas: {recipe_names}."
                )

            cur.execute("DELETE FROM foods WHERE id = ?", (food_id,))
            return cur.rowcount > 0

    def get_categories(self) -> List[str]:
        """Obtiene la lista de categorías existentes registradas en la base de datos."""
        with self.db.connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT DISTINCT category FROM foods WHERE category IS NOT NULL AND category != '' ORDER BY category ASC"
            )
            rows = cur.fetchall()
            return [row["category"] for row in rows]
