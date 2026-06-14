"""
database.py — PostgreSQL database layer for storing and retrieving recipes.

Uses psycopg2 to connect to PostgreSQL.
Reads DATABASE_URL from environment variables (set by Render or .env locally).

Tables:
  - recipes: stores all extracted recipe data
    - id (SERIAL PRIMARY KEY)
    - title, cuisine, difficulty, servings (TEXT)
    - prep_time, cook_time, total_time (TEXT)
    - source_url (TEXT)
    - ingredients, instructions, nutrition, substitutions,
      shopping_list, related_recipes (TEXT — JSON-encoded)
    - created_at (TIMESTAMP)
"""

import os
import json
from datetime import datetime, timezone

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# PostgreSQL connection URL (e.g. postgres://user:pass@host:5432/dbname)
DATABASE_URL = os.getenv('DATABASE_URL')

# Render gives postgres:// but psycopg2 requires postgresql://
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)


def get_connection():
    """Create and return a database connection with RealDictCursor."""
    if not DATABASE_URL:
        raise ValueError(
            "DATABASE_URL is not set. "
            "Please set it in your .env file or environment variables."
        )
    conn = psycopg2.connect(DATABASE_URL)
    return conn


def init_db():
    """
    Initialize the database by creating the recipes table if it doesn't exist.
    Called once when the FastAPI app starts up.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id SERIAL PRIMARY KEY,
            title TEXT,
            cuisine TEXT,
            difficulty TEXT,
            servings TEXT,
            prep_time TEXT,
            cook_time TEXT,
            total_time TEXT,
            source_url TEXT,
            ingredients TEXT,
            instructions TEXT,
            nutrition TEXT,
            substitutions TEXT,
            shopping_list TEXT,
            related_recipes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    cursor.close()
    conn.close()


def save_recipe(recipe_data: dict, source_url: str = None) -> dict:
    """
    Save a recipe to the database.

    Args:
        recipe_data: The extracted recipe data (dict from AI)
        source_url: The original URL the recipe was scraped from

    Returns:
        The full recipe dict including the generated id and created_at
    """
    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now(timezone.utc).isoformat()

    cursor.execute('''
        INSERT INTO recipes (
            title, cuisine, difficulty, servings,
            prep_time, cook_time, total_time,
            source_url, ingredients, instructions,
            nutrition, substitutions, shopping_list,
            related_recipes, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    ''', (
        recipe_data.get('title', 'Untitled'),
        recipe_data.get('cuisine', 'Not specified'),
        recipe_data.get('difficulty', 'Not specified'),
        recipe_data.get('servings', 'Not specified'),
        recipe_data.get('prep_time', 'Not specified'),
        recipe_data.get('cook_time', 'Not specified'),
        recipe_data.get('total_time', 'Not specified'),
        source_url,
        json.dumps(recipe_data.get('ingredients', [])),
        json.dumps(recipe_data.get('instructions', [])),
        json.dumps(recipe_data.get('nutrition', {})),
        json.dumps(recipe_data.get('substitutions', [])),
        json.dumps(recipe_data.get('shopping_list', {})),
        json.dumps(recipe_data.get('related_recipes', [])),
        now,
    ))

    recipe_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()

    # Return the complete recipe object
    return _build_recipe_dict(recipe_data, recipe_id, source_url, now)


def get_all_recipes() -> list:
    """
    Get all saved recipes (summary view for the history table).

    Returns:
        List of recipe summary dicts with: id, title, cuisine, difficulty, created_at
    """
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute('''
        SELECT id, title, cuisine, difficulty, created_at
        FROM recipes
        ORDER BY created_at DESC
    ''')

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return [
        {
            'id': row['id'],
            'title': row['title'],
            'cuisine': row['cuisine'],
            'difficulty': row['difficulty'],
            'created_at': str(row['created_at']),
        }
        for row in rows
    ]


def get_recipe_by_id(recipe_id: int) -> dict | None:
    """
    Get a single recipe by its ID (full detail view).

    Args:
        recipe_id: The recipe's database ID

    Returns:
        Full recipe dict, or None if not found
    """
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute('SELECT * FROM recipes WHERE id = %s', (recipe_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row is None:
        return None

    return {
        'id': row['id'],
        'title': row['title'],
        'cuisine': row['cuisine'],
        'difficulty': row['difficulty'],
        'servings': row['servings'],
        'prep_time': row['prep_time'],
        'cook_time': row['cook_time'],
        'total_time': row['total_time'],
        'source_url': row['source_url'],
        'ingredients': json.loads(row['ingredients'] or '[]'),
        'instructions': json.loads(row['instructions'] or '[]'),
        'nutrition': json.loads(row['nutrition'] or '{}'),
        'substitutions': json.loads(row['substitutions'] or '[]'),
        'shopping_list': json.loads(row['shopping_list'] or '{}'),
        'related_recipes': json.loads(row['related_recipes'] or '[]'),
        'created_at': str(row['created_at']),
    }


def get_recipes_by_ids(recipe_ids: list) -> list:
    """
    Get multiple recipes by their IDs (for meal plan generation).

    Args:
        recipe_ids: List of recipe database IDs

    Returns:
        List of full recipe dicts
    """
    if not recipe_ids:
        return []

    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    placeholders = ','.join(['%s'] * len(recipe_ids))
    cursor.execute(f'SELECT * FROM recipes WHERE id IN ({placeholders})', recipe_ids)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return [
        {
            'id': row['id'],
            'title': row['title'],
            'cuisine': row['cuisine'],
            'difficulty': row['difficulty'],
            'servings': row['servings'],
            'prep_time': row['prep_time'],
            'cook_time': row['cook_time'],
            'total_time': row['total_time'],
            'source_url': row['source_url'],
            'ingredients': json.loads(row['ingredients'] or '[]'),
            'instructions': json.loads(row['instructions'] or '[]'),
            'nutrition': json.loads(row['nutrition'] or '{}'),
            'substitutions': json.loads(row['substitutions'] or '[]'),
            'shopping_list': json.loads(row['shopping_list'] or '{}'),
            'related_recipes': json.loads(row['related_recipes'] or '[]'),
            'created_at': str(row['created_at']),
        }
        for row in rows
    ]


def _build_recipe_dict(recipe_data: dict, recipe_id: int, source_url: str, created_at: str) -> dict:
    """
    Build a complete recipe dict from the extracted data plus DB metadata.
    Used after saving to return the full object to the frontend.
    """
    return {
        'id': recipe_id,
        'title': recipe_data.get('title', 'Untitled'),
        'cuisine': recipe_data.get('cuisine', 'Not specified'),
        'difficulty': recipe_data.get('difficulty', 'Not specified'),
        'servings': recipe_data.get('servings', 'Not specified'),
        'prep_time': recipe_data.get('prep_time', 'Not specified'),
        'cook_time': recipe_data.get('cook_time', 'Not specified'),
        'total_time': recipe_data.get('total_time', 'Not specified'),
        'source_url': source_url,
        'ingredients': recipe_data.get('ingredients', []),
        'instructions': recipe_data.get('instructions', []),
        'nutrition': recipe_data.get('nutrition', {}),
        'substitutions': recipe_data.get('substitutions', []),
        'shopping_list': recipe_data.get('shopping_list', {}),
        'related_recipes': recipe_data.get('related_recipes', []),
        'created_at': created_at,
    }
