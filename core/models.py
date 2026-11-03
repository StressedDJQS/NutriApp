from django.db import models

class Food(models.Model):
    name = models.CharField(max_length=255, unique=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    unit = models.CharField(max_length=20)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    price_unit = models.CharField(max_length=20)
    
    # Perfil nutricional
    calories = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    protein = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    carbohydrates = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    fats = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    fiber = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    sodium = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name

class Recipe(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    base_portions = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.name

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    food = models.ForeignKey(Food, on_delete=models.RESTRICT, related_name='recipe_ingredients')
    quantity = models.DecimalField(max_digits=10, decimal_places=3)

    def __str__(self):
        return f"{self.quantity} {self.food.unit} de {self.food.name}"

class Menu(models.Model):
    name = models.CharField(max_length=255, unique=True)
    target_calories = models.DecimalField(max_digits=8, decimal_places=2, help_text="Requerimiento calórico objetivo")
    
    def __str__(self):
        return self.name

class MenuRecipe(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='schedule')
    recipe = models.ForeignKey(Recipe, on_delete=models.RESTRICT)
    day_of_week = models.CharField(max_length=20)  # ej. "Lunes", "Martes"
    meal_time = models.CharField(max_length=50)    # ej. "Desayuno", "Almuerzo"
    portions = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.recipe.name} - {self.day_of_week} ({self.meal_time})"