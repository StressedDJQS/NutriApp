from ninja import ModelSchema
from .models import Food, Recipe, WeeklyPlan, PlanItem

class FoodSchema(ModelSchema):
    class Meta:
        model = Food
        fields = "__all__"

class RecipeSchema(ModelSchema):
    class Meta:
        model = Recipe
        fields = "__all__"

class WeeklyPlanSchema(ModelSchema):
    class Meta:
        model = WeeklyPlan
        fields = "__all__"

class WeeklyPlanCreateSchema(ModelSchema):
    class Meta:
        model = WeeklyPlan
        fields = ['name', 'start_date']