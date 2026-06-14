"""
meal_plan.py — Route for generating meal plans from saved recipes.

Endpoint:
  POST /api/meal-plan
  Body: { "recipe_ids": [1, 2, 3] }
  Returns: Generated meal plan JSON
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.database import get_recipes_by_ids
from services.gemini import generate_meal_plan


# Create the router
router = APIRouter()


class MealPlanRequest(BaseModel):
    """Request body for the meal plan endpoint."""
    recipe_ids: list[int]


@router.post("/meal-plan")
async def create_meal_plan(request: MealPlanRequest):
    """
    Generate a weekly meal plan from selected recipes.

    Steps:
    1. Fetch the selected recipes from the database
    2. Send them to Groq AI to generate a meal plan
    3. Return the generated plan
    """
    if not request.recipe_ids:
        raise HTTPException(status_code=400, detail="At least one recipe ID is required")

    try:
        # Step 1: Fetch recipes from DB
        recipes = get_recipes_by_ids(request.recipe_ids)

        if not recipes:
            raise HTTPException(status_code=404, detail="No recipes found for the given IDs")

        # Step 2: Generate the meal plan with Groq AI
        meal_plan = await generate_meal_plan(recipes)

        # Step 3: Return it
        return meal_plan

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate meal plan: {str(e)}"
        )
