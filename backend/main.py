"""
main.py — FastAPI application entry point for the Recipe Extractor backend.

This file:
1. Creates the FastAPI app
2. Configures CORS to allow the React frontend to make requests
3. Registers all API route modules
4. Initializes the database on startup

Run with:
  uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from services.database import init_db
from routes import extract, recipes, meal_plan


# Create the FastAPI application
app = FastAPI(
    title="Recipe Extractor API",
    description="Extract structured recipe data from any URL using AI",
    version="1.0.0",
)

# ─── CORS Configuration ───
# Allow the React frontend to make requests from local dev and Vercel
allowed_origins = [
    "http://localhost:5173",   # Vite dev server
    "http://localhost:3000",   # Alternative dev port
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

# Add the production frontend URL if set
frontend_url = os.environ.get("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",  # Allow all Vercel preview URLs
    allow_credentials=True,
    allow_methods=["*"],       # Allow all HTTP methods
    allow_headers=["*"],       # Allow all headers
)

# ─── Register Routes ───
# All routes are prefixed with /api to match what the frontend expects
app.include_router(extract.router, prefix="/api")
app.include_router(recipes.router, prefix="/api")
app.include_router(meal_plan.router, prefix="/api")


# ─── Startup Event ───
@app.on_event("startup")
async def startup():
    """Initialize the database when the server starts."""
    init_db()
    print("[OK] Database initialized")
    print("[OK] Recipe Extractor API is running!")
    print("[OK] Docs available at: http://localhost:8000/docs")


# ─── Health Check ───
@app.get("/")
async def root():
    """Simple health check endpoint."""
    return {
        "status": "ok",
        "message": "Recipe Extractor API is running",
    }
