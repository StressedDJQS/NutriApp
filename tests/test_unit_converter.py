"""
Pruebas del conversor de unidades y compatibilidad de familias.
"""

import pytest
from src.services.unit_converter import (
    convert_quantity,
    are_units_compatible,
    normalize_unit_name,
    get_unit_family,
)


def test_normalize_unit_name():
    assert normalize_unit_name("  Kilogramos  ") == "kg"
    assert normalize_unit_name("Gramo") == "g"
    assert normalize_unit_name("Litros") == "l"
    assert normalize_unit_name("Mililitros") == "ml"
    assert normalize_unit_name("Unidades") == "unidad"
    assert normalize_unit_name("ud") == "unidad"


def test_get_unit_family():
    assert get_unit_family("g") == "mass"
    assert get_unit_family("kg") == "mass"
    assert get_unit_family("mg") == "mass"
    assert get_unit_family("ml") == "volume"
    assert get_unit_family("l") == "volume"
    assert get_unit_family("unidad") == "discrete"
    assert get_unit_family("desconocido") == "unknown"


def test_units_compatibility():
    assert are_units_compatible("g", "kg") is True
    assert are_units_compatible("ml", "l") is True
    assert are_units_compatible("unidad", "u") is True
    # Incompatibles (masa vs volumen o discreto)
    assert are_units_compatible("g", "ml") is False
    assert are_units_compatible("kg", "l") is False
    assert are_units_compatible("g", "unidad") is False


def test_mass_conversions():
    assert convert_quantity(1.0, "kg", "g") == 1000.0
    assert convert_quantity(500.0, "g", "kg") == 0.5
    assert convert_quantity(2000.0, "mg", "g") == 2.0
    assert convert_quantity(0.001, "kg", "mg") == 1000.0


def test_volume_conversions():
    assert convert_quantity(1.0, "l", "ml") == 1000.0
    assert convert_quantity(250.0, "ml", "l") == 0.25
    assert convert_quantity(150.0, "cc", "ml") == 150.0


def test_discrete_conversions():
    assert convert_quantity(3.0, "unidad", "unidades") == 3.0
    assert convert_quantity(5.0, "u", "unidad") == 5.0


def test_incompatible_unit_conversion_raises():
    with pytest.raises(ValueError, match="No es posible convertir"):
        convert_quantity(500, "g", "ml")

    with pytest.raises(ValueError, match="No es posible convertir"):
        convert_quantity(1, "unidad", "kg")


def test_negative_quantity_raises():
    with pytest.raises(ValueError, match="negativa"):
        convert_quantity(-5, "g", "kg")


def test_unknown_unit_raises():
    with pytest.raises(ValueError, match="desconocida"):
        convert_quantity(10, "cucharada", "g")
