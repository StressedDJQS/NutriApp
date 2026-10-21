"""
Modelos de datos para recetas (Recipe) e ingredientes (RecipeIngredient).
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Any
import sqlite3

from src.models.food import Food


@dataclass
class RecipeIngredient:
    id: Optional[int] = None
    recipe_id: Optional[int] = None
    food_id: int = 0
    food_name: Optional[str] = None
    food_category: Optional[str] = None
    quantity: float = 0.0
    unit: str = "g"
    notes: Optional[str] = None
    # Objeto food asociado si está disponible
    food: Optional[Food] = None

    @classmethod
    def from_row(cls, row: sqlite3.Row | dict[str, Any]) -> "RecipeIngredient":
        data = dict(row)
        return cls(
            id=data.get("id"),
            recipe_id=data.get("recipe_id"),
            food_id=int(data.get("food_id") or 0),
            food_name=data.get("food_name"),
            food_category=data.get("food_category"),
            quantity=float(data.get("quantity") or 0.0),
            unit=data.get("unit", "g"),
            notes=data.get("notes"),
        )

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        if self.food is not None:
            d["food"] = self.food.to_dict()
        return d


@dataclass
class Recipe:
    id: Optional[int] = None
    name: str = ""
    description: Optional[str] = None
    base_portions: int = 1
    ingredients: list[RecipeIngredient] = field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_row(cls, row: sqlite3.Row | dict[str, Any], ingredients: Optional[list[RecipeIngredient]] = None) -> "Recipe":
        data = dict(row)
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            description=data.get("description"),
            base_portions=int(data.get("base_portions") or 1),
            ingredients=ingredients if ingredients is not None else [],
            created_at=str(data["created_at"]) if data.get("created_at") is not None else None,
            updated_at=str(data["updated_at"]) if data.get("updated_at") is not None else None,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "base_portions": self.base_portions,
            "ingredients": [i.to_dict() for i in self.ingredients],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
