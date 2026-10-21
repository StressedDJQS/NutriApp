"""
Modelo de datos para alimentos (Food).
"""

from dataclasses import dataclass, asdict
from typing import Optional, Any
import sqlite3


@dataclass
class Food:
    id: Optional[int] = None
    name: str = ""
    category: Optional[str] = None
    unit: str = "g"  # Unidad física principal o habitual de despacho
    reference_base_amount: float = 100.0  # Base nutricional estándar: 100 g / 100 ml / 1 unidad
    reference_base_unit: str = "g"        # 'g', 'ml', 'unidad'
    unit_price: float = 0.0               # Precio unitario registrado
    price_unit: str = "kg"                # Unidad del precio ('kg', 'g', 'l', 'ml', 'unidad')
    calories: Optional[float] = None      # Energía (kcal)
    protein: Optional[float] = None       # Proteínas (g)
    carbohydrates: Optional[float] = None # Carbohidratos (g)
    fats: Optional[float] = None          # Grasas totales (g)
    fiber: Optional[float] = None         # Fibra (g)
    sodium: Optional[float] = None        # Sodio (mg)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_row(cls, row: sqlite3.Row | dict[str, Any]) -> "Food":
        data = dict(row)
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            category=data.get("category"),
            unit=data.get("unit", "g"),
            reference_base_amount=float(data.get("reference_base_amount") or 100.0),
            reference_base_unit=data.get("reference_base_unit", "g"),
            unit_price=float(data.get("unit_price") or 0.0),
            price_unit=data.get("price_unit", "kg"),
            calories=float(data["calories"]) if data.get("calories") is not None else None,
            protein=float(data["protein"]) if data.get("protein") is not None else None,
            carbohydrates=float(data["carbohydrates"]) if data.get("carbohydrates") is not None else None,
            fats=float(data["fats"]) if data.get("fats") is not None else None,
            fiber=float(data["fiber"]) if data.get("fiber") is not None else None,
            sodium=float(data["sodium"]) if data.get("sodium") is not None else None,
            created_at=str(data["created_at"]) if data.get("created_at") is not None else None,
            updated_at=str(data["updated_at"]) if data.get("updated_at") is not None else None,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
