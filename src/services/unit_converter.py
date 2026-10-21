"""
Módulo de conversión de unidades coherentes para NutriApp.
Soporta masa (g, kg, mg), volumen (ml, l, cc) y unidades discretas (unidad/u).
Prohíbe terminantemente conversiones incompatibles (masa <-> volumen) sin densidad.
"""

from typing import Optional

# Factores respecto a la unidad base del grupo
# Masa -> Base: 'g'
MASS_FACTORS = {
    "g": 1.0,
    "gramo": 1.0,
    "gramos": 1.0,
    "kg": 1000.0,
    "kilogramo": 1000.0,
    "kilogramos": 1000.0,
    "mg": 0.001,
    "miligramo": 0.001,
    "miligramos": 0.001,
}

# Volumen -> Base: 'ml'
VOLUME_FACTORS = {
    "ml": 1.0,
    "mililitro": 1.0,
    "mililitros": 1.0,
    "cc": 1.0,
    "l": 1000.0,
    "lt": 1000.0,
    "litro": 1000.0,
    "litros": 1000.0,
}

# Discreta -> Base: 'unidad'
DISCRETE_FACTORS = {
    "unidad": 1.0,
    "unidades": 1.0,
    "u": 1.0,
    "ud": 1.0,
    "und": 1.0,
    "pz": 1.0,
    "pieza": 1.0,
    "piezas": 1.0,
}


def normalize_unit_name(unit: str) -> str:
    """Normaliza el nombre de la unidad a minúsculas y sin espacios."""
    if not unit:
        return ""
    u = unit.strip().lower()
    # Normalizaciones comunes
    if u in MASS_FACTORS:
        if u in ("kilogramo", "kilogramos"):
            return "kg"
        if u in ("gramo", "gramos"):
            return "g"
        if u in ("miligramo", "miligramos"):
            return "mg"
        return u
    if u in VOLUME_FACTORS:
        if u in ("litro", "litros", "lt"):
            return "l"
        if u in ("mililitro", "mililitros", "cc"):
            return "ml"
        return u
    if u in DISCRETE_FACTORS:
        return "unidad"
    return u


def get_unit_family(unit: str) -> str:
    """Retorna la familia de la unidad: 'mass', 'volume', 'discrete' o 'unknown'."""
    norm = normalize_unit_name(unit)
    if norm in MASS_FACTORS:
        return "mass"
    if norm in VOLUME_FACTORS:
        return "volume"
    if norm in DISCRETE_FACTORS:
        return "discrete"
    return "unknown"


def are_units_compatible(unit_a: str, unit_b: str) -> bool:
    """Verifica si dos unidades pertenecen a la misma familia compatible."""
    norm_a = normalize_unit_name(unit_a)
    norm_b = normalize_unit_name(unit_b)
    if norm_a == norm_b:
        return True
    fam_a = get_unit_family(norm_a)
    fam_b = get_unit_family(norm_b)
    if fam_a == "unknown" or fam_b == "unknown":
        return False
    return fam_a == fam_b


def convert_quantity(amount: float, from_unit: str, to_unit: str) -> float:
    """
    Convierte una cantidad numérica entre unidades compatibles.
    Lanza ValueError si las unidades no son compatibles o desconocidas.
    """
    if amount < 0:
        raise ValueError("La cantidad no puede ser negativa.")

    norm_from = normalize_unit_name(from_unit)
    norm_to = normalize_unit_name(to_unit)

    if norm_from == norm_to:
        return float(amount)

    fam_from = get_unit_family(norm_from)
    fam_to = get_unit_family(norm_to)

    if fam_from == "unknown":
        raise ValueError(f"Unidad de origen desconocida: '{from_unit}'.")
    if fam_to == "unknown":
        raise ValueError(f"Unidad de destino desconocida: '{to_unit}'.")

    if fam_from != fam_to:
        raise ValueError(
            f"No es posible convertir de '{from_unit}' ({fam_from}) a '{to_unit}' ({fam_to}) "
            "sin una densidad o equivalencia válida."
        )

    if fam_from == "mass":
        base_amount = amount * MASS_FACTORS[norm_from]
        return base_amount / MASS_FACTORS[norm_to]

    if fam_from == "volume":
        base_amount = amount * VOLUME_FACTORS[norm_from]
        return base_amount / VOLUME_FACTORS[norm_to]

    if fam_from == "discrete":
        base_amount = amount * DISCRETE_FACTORS[norm_from]
        return base_amount / DISCRETE_FACTORS[norm_to]

    raise ValueError(f"No se pudo procesar la conversión entre '{from_unit}' y '{to_unit}'.")
