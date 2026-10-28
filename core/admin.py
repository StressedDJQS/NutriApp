from django.contrib import admin
from .models import Food, Recipe, RecipeIngredient, WeeklyPlan, PlanItem

admin.site.register(Food)
admin.site.register(Recipe)
admin.site.register(RecipeIngredient)
admin.site.register(WeeklyPlan)
admin.site.register(PlanItem)