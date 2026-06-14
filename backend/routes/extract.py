"""
extract.py — Route for extracting recipes from URLs.

Endpoint:
  POST /api/extract
  Body: { "url": "https://example.com/recipe/..." }
  Returns: Full extracted recipe JSON (saved to DB)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.scraper import scrape_url
from services.gemini import extract_recipe_data
from services.database import save_recipe


# Create the router
router = APIRouter()


class ExtractRequest(BaseModel):
    """Request body for the extract endpoint."""
    url: str


@router.post("/extract")
async def extract(request: ExtractRequest):
    """
    Extract a recipe from a given URL.

    Steps:
    1. Scrape the URL to get the page text
    2. Send the text to Groq AI to extract structured recipe data
    3. Save the recipe to the database
    4. Return the full recipe object
    """
    # Validate the URL
    url = request.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    if not url.startswith(('http://', 'https://')):
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")

    try:
        # Step 1: Scrape the recipe page
        scraped_text = scrape_url(url)

        if not scraped_text or len(scraped_text) < 50:
            raise HTTPException(
                status_code=400,
                detail="Could not extract enough content from this URL. Please try a different recipe page."
            )

        # Step 2: Use Groq AI to extract structured recipe data
        recipe_data = await extract_recipe_data(scraped_text)

        # Step 3: Save to database
        saved_recipe = save_recipe(recipe_data, source_url=url)

        # Step 4: Return the full recipe
        return saved_recipe

    except ValueError as e:
        # Scraping or AI parsing errors
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while extracting the recipe: {str(e)}"
        )
