from ninja import NinjaAPI
from typing import List
from .models import Food, WeeklyPlan
from .schemas import FoodSchema, WeeklyPlanSchema, WeeklyPlanCreateSchema

api = NinjaAPI(title="NutriApp API")

# --- Endpoints de Alimentos ---
@api.get("/foods", response=List[FoodSchema])
def list_foods(request):
    return Food.objects.all()

# --- Endpoints de Planificación Semanal ---
@api.get("/plans", response=List[WeeklyPlanSchema])
def list_plans(request):
    return WeeklyPlan.objects.all().order_by('-start_date')

@api.post("/plans", response=WeeklyPlanSchema)
def create_plan(request, payload: WeeklyPlanCreateSchema):
    plan = WeeklyPlan.objects.create(**payload.dict())
    return plan