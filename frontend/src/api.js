/**
 * api.js — Simple fetch wrapper for our Recipe Extractor API
 *
 * This file contains all the functions that talk to our backend server.
 * Each function makes an HTTP request and returns the JSON response.
 *
 * BASE_URL points to our FastAPI backend running on port 8000.
 */

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

/**
 * Extract a recipe from a given URL.
 * Sends a POST request with the URL, and the backend uses AI to extract recipe data.
 *
 * @param {string} url - The recipe page URL to extract from
 * @returns {object} - The extracted recipe data
 */
export async function extractRecipe(url) {
  try {
    const response = await fetch(`${BASE_URL}/extract`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url }),
    });

    // If the server returns an error status, throw an error
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to extract recipe');
    }

    // Return the parsed JSON data
    return await response.json();
  } catch (error) {
    // Re-throw the error so the component can handle it
    throw error;
  }
}

/**
 * Get all saved recipes from the database.
 * Sends a GET request and returns a list of recipe summaries.
 *
 * @returns {Array} - List of saved recipes
 */
export async function getRecipes() {
  try {
    const response = await fetch(`${BASE_URL}/recipes`);

    if (!response.ok) {
      throw new Error('Failed to fetch recipes');
    }

    return await response.json();
  } catch (error) {
    throw error;
  }
}

/**
 * Get a single recipe by its ID.
 * Sends a GET request and returns the full recipe details.
 *
 * @param {string|number} id - The recipe ID
 * @returns {object} - Full recipe data
 */
export async function getRecipe(id) {
  try {
    const response = await fetch(`${BASE_URL}/recipes/${id}`);

    if (!response.ok) {
      throw new Error('Failed to fetch recipe details');
    }

    return await response.json();
  } catch (error) {
    throw error;
  }
}

/**
 * Generate a meal plan from selected recipe IDs.
 * Sends a POST request with an array of recipe IDs.
 *
 * @param {Array} recipeIds - Array of recipe IDs to include in the meal plan
 * @returns {object} - The generated meal plan
 */
export async function generateMealPlan(recipeIds) {
  try {
    const response = await fetch(`${BASE_URL}/meal-plan`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ recipe_ids: recipeIds }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to generate meal plan');
    }

    return await response.json();
  } catch (error) {
    throw error;
  }
}
