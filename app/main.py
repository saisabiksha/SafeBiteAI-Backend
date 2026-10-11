from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.allergies import router as allergies_router
from app.api.routes.exposures import router as exposures_router
from app.api.routes.food_check import router as food_check_router
from app.api.routes.hydration import router as hydration_router
from app.api.routes.reminders import router as reminders_router
from app.api.routes.users import router as users_router
from app.core.config import (
    ALLOWED_ORIGINS,
    PROJECT_DESCRIPTION,
    PROJECT_NAME,
    PROJECT_VERSION,
)
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Initializes database tables on application startup.
    """
    init_db()
    yield


# Initialize the FastAPI application
app = FastAPI(
    title=PROJECT_NAME,
    description=PROJECT_DESCRIPTION,
    version=PROJECT_VERSION,
    lifespan=lifespan,
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(users_router)
app.include_router(allergies_router)
app.include_router(food_check_router)
app.include_router(exposures_router)
app.include_router(hydration_router)
app.include_router(reminders_router)


@app.get("/")
def get_root():
    """
    Root endpoint returning a welcome message for SafeBiteAI.
    """
    return {
        "message": "Welcome to SafeBiteAI Backend API",
        "service": "SafeBiteAI",
    }


@app.get("/health")
def get_health():
    """
    Health check endpoint returning the service status.
    """
    return {
        "status": "ok",
        "service": "SafeBiteAI-Backend",
    }
