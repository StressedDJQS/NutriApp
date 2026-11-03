from ninja import ModelSchema, Schema
from typing import List, Optional
from .models import Food, Menu, MenuRecipe, Recipe, RecipeIngredient

class FoodSchemaIn(ModelSchema):
    class Meta:
        model = Food
        exclude = ['id']

class FoodSchemaOut(ModelSchema):
    class Meta:
        model = Food
        fields = '__all__'

# Esquemas de entrada para relaciones anidadas
class IngredientSchemaIn(Schema):
    food_id: int
    quantity: float

class IngredientSchemaOut(ModelSchema):
    food: FoodSchemaOut
    
    class Meta:
        model = RecipeIngredient
        fields = ['id', 'quantity']

class RecipeSchemaIn(Schema):
    name: str
    description: Optional[str] = None
    base_portions: int = 1
    ingredients: List[IngredientSchemaIn]

class RecipeSchemaOut(ModelSchema):
    ingredients: List[IngredientSchemaOut]
    
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'description', 'base_portions']

# Esquemas para cálculo de escalado y costeo
class ScaledIngredientOut(Schema):
    food_name: str
    required_quantity: float
    unit: str
    cost: float

class ScaledRecipeOut(Schema):
    target_portions: int
    total_cost: float
    cost_per_portion: float
    total_calories: float
    required_ingredients: List[ScaledIngredientOut]

class MenuRecipeSchemaIn(Schema):
    recipe_id: int
    day_of_week: str
    meal_time: str
    portions: int

class MenuSchemaIn(Schema):
    name: str
    target_calories: float
    schedule: List[MenuRecipeSchemaIn]

class MenuRecipeSchemaOut(ModelSchema):
    recipe: RecipeSchemaOut
    class Meta:
        model = MenuRecipe
        fields = ['id', 'day_of_week', 'meal_time', 'portions']

class MenuSchemaOut(ModelSchema):
    schedule: List[MenuRecipeSchemaOut]
    class Meta:
        model = Menu
        fields = ['id', 'name', 'target_calories']

class AdequacyReportOut(Schema):
    target_calories: float
    total_calories: float
    adequacy_percentage: float
    status: str

class GroceryItemOut(Schema):
    food_name: str
    category: Optional[str]
    total_quantity: float
    unit: str
    estimated_cost: float

class GroceryListOut(Schema):
    menu_name: str
    total_menu_cost: float
    items: List[GroceryItemOut]