from ninja import NinjaAPI
from django.shortcuts import get_object_or_404
from typing import List
from .models import Food, Recipe, RecipeIngredient, Menu, MenuRecipe
from .schemas import (
    FoodSchemaIn, FoodSchemaOut,
    RecipeSchemaIn, RecipeSchemaOut,
    ScaledRecipeOut, MenuSchemaIn, MenuSchemaOut,
    AdequacyReportOut, GroceryListOut
)
from .services import calculate_recipe_totals, calculate_menu_adequacy, consolidate_menu_groceries

api = NinjaAPI(title="NutriApp API Backend")

# --- ALIMENTOS ---
@api.post("/foods/", response=FoodSchemaOut)
def create_food(request, payload: FoodSchemaIn):
    return Food.objects.create(**payload.dict())

@api.get("/foods/", response=List[FoodSchemaOut])
def list_foods(request):
    return Food.objects.all()

# --- RECETAS ---
@api.post("/recipes/", response=RecipeSchemaOut)
def create_recipe(request, payload: RecipeSchemaIn):
    data = payload.dict()
    ingredients_data = data.pop('ingredients')
    
    recipe = Recipe.objects.create(**data)
    
    for ing in ingredients_data:
        food = get_object_or_404(Food, id=ing['food_id'])
        RecipeIngredient.objects.create(
            recipe=recipe,
            food=food,
            quantity=ing['quantity']
        )
        
    return recipe

@api.get("/recipes/", response=List[RecipeSchemaOut])
def list_recipes(request):
    return Recipe.objects.all()

# --- ESCALADO Y COSTEO ---
@api.get("/recipes/{recipe_id}/scale", response=ScaledRecipeOut)
def scale_recipe(request, recipe_id: int, target_portions: int):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    
    ratio = target_portions / recipe.base_portions
    total_cost = 0.0
    total_cal = 0.0
    scaled_ingredients = []

    for ing in recipe.ingredients.all():
        req_quantity = float(ing.quantity) * ratio
        
        # Costo = Cantidad_requerida * Precio_Unitario
        ing_cost = req_quantity * float(ing.food.unit_price)
        
        # Asumiendo perfil nutricional basado en porción/100
        cal = float(ing.food.calories or 0) * (req_quantity / 100)

        total_cost += ing_cost
        total_cal += cal

        scaled_ingredients.append({
            "food_name": ing.food.name,
            "required_quantity": round(req_quantity, 3),
            "unit": ing.food.unit,
            "cost": round(ing_cost, 2)
        })

    return {
        "target_portions": target_portions,
        "total_cost": round(total_cost, 2),
        "cost_per_portion": round(total_cost / target_portions, 2),
        "total_calories": round(total_cal, 2),
        "required_ingredients": scaled_ingredients
    }

# --- MENÚS Y CRONOGRAMAS ---
@api.post("/menus/", response=MenuSchemaOut)
def create_menu(request, payload: MenuSchemaIn):
    data = payload.dict()
    schedule_data = data.pop('schedule')
    
    menu = Menu.objects.create(**data)
    
    for item in schedule_data:
        recipe = get_object_or_404(Recipe, id=item['recipe_id'])
        MenuRecipe.objects.create(
            menu=menu,
            recipe=recipe,
            day_of_week=item['day_of_week'],
            meal_time=item['meal_time'],
            portions=item['portions']
        )
        
    return menu

@api.get("/menus/", response=List[MenuSchemaOut])
def list_menus(request):
    return Menu.objects.all()

@api.get("/menus/{menu_id}/adequacy", response=AdequacyReportOut)
def get_menu_adequacy(request, menu_id: int):
    menu = get_object_or_404(Menu, id=menu_id)
    return calculate_menu_adequacy(menu)

@api.get("/menus/{menu_id}/groceries", response=GroceryListOut)
def get_menu_groceries(request, menu_id: int):
    menu = get_object_or_404(Menu, id=menu_id)
    return consolidate_menu_groceries(menu)

@api.put("/foods/{food_id}", response=FoodSchemaOut)
def update_food(request, food_id: int, payload: FoodSchemaIn):
    food = get_object_or_404(Food, id=food_id)
    for attr, value in payload.dict().items():
        setattr(food, attr, value)
    food.save()
    return food

@api.delete("/foods/{food_id}")
def delete_food(request, food_id: int):
    food = get_object_or_404(Food, id=food_id)
    food.delete()
    return {"success": True}

@api.put("/recipes/{recipe_id}", response=RecipeSchemaOut)
def update_recipe(request, recipe_id: int, payload: RecipeSchemaIn):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    data = payload.dict()
    ingredients_data = data.pop('ingredients')
    
    # Actualizar campos base
    for attr, value in data.items():
        setattr(recipe, attr, value)
    recipe.save()
    
    # Recrear ingredientes
    recipe.ingredients.all().delete()
    for ing in ingredients_data:
        food = get_object_or_404(Food, id=ing['food_id'])
        RecipeIngredient.objects.create(
            recipe=recipe,
            food=food,
            quantity=ing['quantity']
        )
    return recipe

@api.delete("/recipes/{recipe_id}")
def delete_recipe(request, recipe_id: int):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    recipe.delete()
    return {"success": True}

@api.put("/menus/{menu_id}", response=MenuSchemaOut)
def update_menu(request, menu_id: int, payload: MenuSchemaIn):
    menu = get_object_or_404(Menu, id=menu_id)
    data = payload.dict()
    schedule_data = data.pop('schedule')
    
    # Actualizar campos base
    for attr, value in data.items():
        setattr(menu, attr, value)
    menu.save()
    
    # Recrear cronograma
    menu.schedule.all().delete()
    for item in schedule_data:
        recipe = get_object_or_404(Recipe, id=item['recipe_id'])
        MenuRecipe.objects.create(
            menu=menu,
            recipe=recipe,
            day_of_week=item['day_of_week'],
            meal_time=item['meal_time'],
            portions=item['portions']
        )
    return menu

@api.delete("/menus/{menu_id}")
def delete_menu(request, menu_id: int):
    menu = get_object_or_404(Menu, id=menu_id)
    menu.delete()
    return {"success": True}