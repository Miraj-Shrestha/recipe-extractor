"""
gemini.py — AI integration for recipe extraction and meal planning.

Uses the Groq SDK (Llama 3.3 70B) for fast, free AI inference.
Reads the API key from the GROQ_API_KEY environment variable.
"""

import os
import json
import re
from groq import Groq
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Initialize the Groq client
API_KEY = os.getenv('GROQ_API_KEY')


def _get_client():
    """Get a Groq client instance. Raises an error if no API key is set."""
    if not API_KEY:
        raise ValueError(
            "GROQ_API_KEY is not set. "
            "Please set it in your .env file or environment variables."
        )
    return Groq(api_key=API_KEY)


# The model to use — Llama 3.3 70B is fast and great at structured output
MODEL = "llama-3.3-70b-versatile"


def _extract_json_from_response(text: str) -> dict:
    """
    Extract a JSON object from the AI response text.
    Handles cases where the AI wraps JSON in markdown code blocks.

    Args:
        text: Raw response text from the AI

    Returns:
        Parsed JSON dict
    """
    # Try to find JSON in a code block first (```json ... ```)
    code_block_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?\s*```', text, re.DOTALL)
    if code_block_match:
        json_str = code_block_match.group(1).strip()
    else:
        # Try to find a raw JSON object
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0).strip()
        else:
            raise ValueError("Could not find valid JSON in AI response")

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON from AI response: {e}")


# ─── The enriched prompt template for recipe extraction ───
EXTRACTION_PROMPT = """You are a recipe extraction assistant. Given the text content scraped from a recipe blog page, extract the following structured data and return it as a valid JSON object.

IMPORTANT: Return ONLY the JSON object, no extra text.

Extract and return this JSON structure:

{
  "title": "Recipe title",
  "cuisine": "Type of cuisine (e.g., Italian, Mexican, American)",
  "prep_time": "Preparation time (e.g., 10 mins)",
  "cook_time": "Cooking time (e.g., 20 mins)",
  "total_time": "Total time (e.g., 30 mins)",
  "servings": "Number of servings (e.g., 4)",
  "difficulty": "easy / medium / hard",
  "ingredients": [
    {"quantity": "1", "unit": "cup", "item": "flour"},
    {"quantity": "2", "unit": "tbsp", "item": "butter"}
  ],
  "instructions": [
    "Step 1 description",
    "Step 2 description"
  ],
  "nutrition": {
    "calories": "Estimated total calories per serving (e.g., 350)",
    "protein": "Estimated protein per serving (e.g., 25g)",
    "carbs": "Estimated carbs per serving (e.g., 40g)",
    "fat": "Estimated fat per serving (e.g., 12g)"
  },
  "substitutions": [
    {
      "original": "Original ingredient",
      "substitute": "Suggested substitute",
      "note": "Brief note about the substitution"
    }
  ],
  "shopping_list": {
    "Produce": ["item1", "item2"],
    "Dairy": ["item1"],
    "Pantry": ["item1", "item2"],
    "Meat & Seafood": ["item1"],
    "Spices": ["item1"]
  },
  "related_recipes": [
    {
      "title": "Related recipe name",
      "description": "Brief description of why it's related"
    }
  ]
}

Rules:
- If a field is not found in the text, make a reasonable estimate or use "Not specified"
- Ingredients MUST be split into quantity, unit, and item
- Instructions should be clear, ordered steps
- Difficulty should be based on number of steps and complexity
- Nutrition values should be estimated per serving if not explicitly stated
- Provide 2-4 ingredient substitutions (focus on common allergens and dietary needs)
- Shopping list should group ingredients by grocery store category
- Suggest 2-3 related recipes that pair well or are similar

Here is the scraped recipe text:
{scraped_text}"""


# ─── The prompt template for meal plan generation ───
MEAL_PLAN_PROMPT = """You are a meal planning assistant. Given the following recipes, create a simple 7-day meal plan.

IMPORTANT: Return ONLY the JSON object, no extra text.

Return this JSON structure:
{{
  "meal_plan": [
    {{
      "day": "Monday",
      "meals": {{
        "breakfast": "Suggested breakfast",
        "lunch": "Recipe title or suggestion",
        "dinner": "Recipe title or suggestion"
      }}
    }}
  ],
  "tips": ["Meal prep tip 1", "Meal prep tip 2"],
  "grocery_summary": "Brief summary of what to buy for the week"
}}

Rules:
- Distribute the provided recipes across the week
- Fill in non-recipe meals with simple suggestions that complement the recipes
- Include 2-3 practical meal prep tips
- Keep the grocery summary concise

Here are the recipes to work with:
{recipes_text}"""


async def extract_recipe_data(scraped_text: str) -> dict:
    """
    Send scraped recipe text to Groq (Llama 3.3) and get structured recipe data back.

    Args:
        scraped_text: Cleaned text content from a recipe page

    Returns:
        Structured recipe data dict

    Raises:
        ValueError: If the API key is missing or the AI response can't be parsed
    """
    client = _get_client()

    # Build the prompt with the scraped text inserted
    prompt = EXTRACTION_PROMPT.replace('{scraped_text}', scraped_text)

    # Call Groq
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a recipe extraction assistant. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=4096,
    )

    # Extract and return the JSON from the response
    return _extract_json_from_response(response.choices[0].message.content)


async def generate_meal_plan(recipes: list) -> dict:
    """
    Send a list of recipes to Groq (Llama 3.3) and get a meal plan back.

    Args:
        recipes: List of recipe dicts (from the database)

    Returns:
        Meal plan dict with days, meals, tips, and grocery summary

    Raises:
        ValueError: If the API key is missing or the AI response can't be parsed
    """
    client = _get_client()

    # Build a text summary of the recipes for the prompt
    recipes_text = ""
    for recipe in recipes:
        recipes_text += f"\n- {recipe['title']} ({recipe.get('cuisine', 'Unknown')} cuisine, "
        recipes_text += f"serves {recipe.get('servings', 'unknown')}, "
        recipes_text += f"{recipe.get('total_time', 'unknown time')})"

    # Build the prompt
    prompt = MEAL_PLAN_PROMPT.replace('{recipes_text}', recipes_text)

    # Call Groq
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a meal planning assistant. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=4096,
    )

    # Extract and return the JSON
    return _extract_json_from_response(response.choices[0].message.content)
