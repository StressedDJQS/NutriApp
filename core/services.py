# core/services.py

# --- CONVERSOR DE UNIDADES ---
MASS_FACTORS = {"g": 1.0, "kg": 1000.0, "mg": 0.001}
VOLUME_FACTORS = {"ml": 1.0, "l": 1000.0, "cc": 1.0}
DISCRETE_FACTORS = {"unidad": 1.0, "u": 1.0}

def normalize_unit(unit: str) -> str:
    if not unit: return ""
    u = unit.strip().lower()
    if u in ("kilogramo", "kilogramos"): return "kg"
    if u in ("gramo", "gramos"): return "g"
    if u in ("litro", "litros", "lt"): return "l"
    if u in ("mililitro", "mililitros"): return "ml"
    return u

def get_unit_family(unit: str) -> str:
    norm = normalize_unit(unit)
    if norm in MASS_FACTORS: return "mass"
    if norm in VOLUME_FACTORS: return "volume"
    if norm in DISCRETE_FACTORS: return "discrete"
    return "unknown"

def convert_quantity(amount: float, from_unit: str, to_unit: str) -> float:
    """Convierte cantidades. Lanza error si son incompatibles (ej. masa a volumen)."""
    norm_from = normalize_unit(from_unit)
    norm_to = normalize_unit(to_unit)
    
    if norm_from == norm_to:
        return float(amount)
        
    fam_from = get_unit_family(norm_from)
    fam_to = get_unit_family(norm_to)
    
    if fam_from != fam_to or fam_from == "unknown":
        raise ValueError(f"No se puede convertir de {from_unit} a {to_unit}.")
        
    if fam_from == "mass":
        return (amount * MASS_FACTORS[norm_from]) / MASS_FACTORS[norm_to]
    if fam_from == "volume":
        return (amount * VOLUME_FACTORS[norm_from]) / VOLUME_FACTORS[norm_to]
    if fam_from == "discrete":
        return (amount * DISCRETE_FACTORS[norm_from]) / DISCRETE_FACTORS[norm_to]


# --- CALCULADORA NUTRICIONAL Y DE COSTOS ---
def calculate_recipe_totals(recipe, target_portions: int):
    """Realiza el cálculo exacto escalado, validando unidades como el sistema original."""
    ratio = target_portions / recipe.base_portions
    total_cost = 0.0
    total_cal = 0.0
    scaled_ingredients = []

    for ing in recipe.ingredients.all():
        food = ing.food
        req_quantity = float(ing.quantity) * ratio
        
        # 1. Cálculo de Costo (convirtiendo unidad de la receta a la unidad de precio del alimento)
        try:
            qty_in_price_unit = convert_quantity(req_quantity, food.unit, food.price_unit)
            ing_cost = qty_in_price_unit * float(food.unit_price)
        except ValueError as e:
            # Si hay error de unidades, el costo asume 0 para no quebrar la API, pero lo reporta.
            ing_cost = 0.0

        # 2. Cálculo Nutricional (basado en 100g/ml o 1 unidad)
        # El sistema original asume base 100 para masa/volumen y 1 para discretos
        ref_base = 1.0 if get_unit_family(food.unit) == "discrete" else 100.0
        cal = float(food.calories or 0) * (req_quantity / ref_base)

        total_cost += ing_cost
        total_cal += cal

        scaled_ingredients.append({
            "food_name": food.name,
            "required_quantity": round(req_quantity, 3),
            "unit": food.unit,
            "cost": round(ing_cost, 2)
        })

    return {
        "target_portions": target_portions,
        "total_cost": round(total_cost, 2),
        "cost_per_portion": round(total_cost / target_portions, 2) if target_portions > 0 else 0,
        "total_calories": round(total_cal, 2),
        "required_ingredients": scaled_ingredients
    }

def calculate_menu_adequacy(menu) -> dict:
    total_cals = 0.0
    for mr in menu.schedule.all():
        # Reutilizamos el motor de cálculo exacto por receta
        totals = calculate_recipe_totals(mr.recipe, mr.portions)
        total_cals += totals["total_calories"]
    
    target = float(menu.target_calories) if menu.target_calories else 0.0
    adequacy = (total_cals / target * 100) if target > 0 else 0.0
    
    # Rango óptimo 90-110% según especificación
    if 90 <= adequacy <= 110:
        status = "Óptimo"
    elif adequacy < 90:
        status = "Déficit"
    else:
        status = "Exceso"

    return {
        "target_calories": round(target, 2),
        "total_calories": round(total_cals, 2),
        "adequacy_percentage": round(adequacy, 2),
        "status": status
    }

def consolidate_menu_groceries(menu) -> dict:
    consolidated = {}
    total_menu_cost = 0.0

    for mr in menu.schedule.all():
        ratio = mr.portions / mr.recipe.base_portions
        
        for ing in mr.recipe.ingredients.all():
            food = ing.food
            raw_qty = float(ing.quantity) * ratio
            
            # Determinar unidad estándar (g -> kg, ml -> l)
            fam = get_unit_family(food.unit)
            std_unit = "kg" if fam == "mass" else "l" if fam == "volume" else "u"
            
            try:
                qty_in_std = convert_quantity(raw_qty, food.unit, std_unit)
            except ValueError:
                qty_in_std = raw_qty
                std_unit = food.unit

            # Costo
            try:
                qty_in_price_unit = convert_quantity(raw_qty, food.unit, food.price_unit)
                ing_cost = qty_in_price_unit * float(food.unit_price)
            except ValueError:
                ing_cost = 0.0

            if food.id not in consolidated:
                consolidated[food.id] = {
                    "food_name": food.name,
                    "category": food.category,
                    "total_quantity": 0.0,
                    "unit": std_unit,
                    "estimated_cost": 0.0
                }
            
            consolidated[food.id]["total_quantity"] += qty_in_std
            consolidated[food.id]["estimated_cost"] += ing_cost
            total_menu_cost += ing_cost

    items = [
        {
            **data,
            "total_quantity": round(data["total_quantity"], 3),
            "estimated_cost": round(data["estimated_cost"], 2)
        }
        for data in consolidated.values()
    ]

    return {
        "menu_name": menu.name,
        "total_menu_cost": round(total_menu_cost, 2),
        "items": items
    }