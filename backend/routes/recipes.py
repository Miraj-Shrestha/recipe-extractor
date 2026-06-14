"""
recipes.py — Routes for listing and viewing saved recipes.

Endpoints:
  GET /api/recipes       — List all saved recipes (summary view)
  GET /api/recipes/{id}  — Get full details of a single recipe
"""

from fastapi import APIRouter, HTTPException

from services.database import get_all_recipes, get_recipe_by_id


# Create the router
router = APIRouter()


@router.get("/recipes")
async def list_recipes():
    """
    Get all saved recipes in summary form.
    Returns a list with id, title, cuisine, difficulty, and created_at.
    Used by the HistoryTab component to populate the table.
    """
    try:
        recipes = get_all_recipes()
        return recipes
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch recipes: {str(e)}"
        )


@router.get("/recipes/{recipe_id}")
async def get_recipe(recipe_id: int):
    """
    Get the full details of a single recipe by ID.
    Returns the complete recipe object with ingredients, instructions, etc.
    Used by the RecipeModal component to show the detail view.
    """
    try:
        recipe = get_recipe_by_id(recipe_id)

        if recipe is None:
            raise HTTPException(status_code=404, detail="Recipe not found")

        return recipe
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch recipe: {str(e)}"
        )
