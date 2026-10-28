from django.db import models

class Food(models.Model):
    name = models.CharField(max_length=255, unique=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    unit = models.CharField(max_length=50)
    reference_base_amount = models.FloatField(default=100.0)
    reference_base_unit = models.CharField(max_length=20, default='g')
    unit_price = models.FloatField()
    price_unit = models.CharField(max_length=50)
    
    # Macros
    calories = models.FloatField(null=True, blank=True)
    protein = models.FloatField(null=True, blank=True)
    carbohydrates = models.FloatField(null=True, blank=True)
    fats = models.FloatField(null=True, blank=True)
    fiber = models.FloatField(null=True, blank=True)
    sodium = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'foods'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    base_portions = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'recipes'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    food = models.ForeignKey(Food, on_delete=models.RESTRICT)
    quantity = models.FloatField()
    unit = models.CharField(max_length=50)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'recipe_ingredients'


class WeeklyPlan(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'weekly_plans'

    def __str__(self):
        return self.name


class PlanItem(models.Model):
    plan = models.ForeignKey(WeeklyPlan, on_delete=models.CASCADE, related_name='items')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=20)  # Ej: 'Lunes', 'Martes'
    meal_type = models.CharField(max_length=50)    # Ej: 'Desayuno', 'Almuerzo'

    class Meta:
        db_table = 'plan_items'