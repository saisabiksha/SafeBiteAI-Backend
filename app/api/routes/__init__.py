"""API route handlers."""
from app.api.routes.allergies import router as allergies_router
from app.api.routes.exposures import router as exposures_router
from app.api.routes.food_check import router as food_check_router
from app.api.routes.hydration import router as hydration_router
from app.api.routes.reminders import router as reminders_router
from app.api.routes.users import router as users_router

__all__ = [
    "users_router",
    "allergies_router",
    "food_check_router",
    "exposures_router",
    "hydration_router",
    "reminders_router",
]
