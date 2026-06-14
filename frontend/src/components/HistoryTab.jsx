/**
 * HistoryTab.jsx — The "Saved Recipes" tab component.
 *
 * This component:
 * 1. Fetches all saved recipes from the backend when it mounts
 * 2. Displays them in a clean HTML table
 * 3. Lets the user click "View Details" to see full recipe data in a modal
 *
 * State:
 *   - recipes: array of saved recipes from the API
 *   - loading: true while fetching the recipe list
 *   - error: error message if fetching fails
 *   - selectedRecipe: the full recipe data to show in the modal
 *   - modalLoading: true while fetching a single recipe's details
 */

import { useState, useEffect } from 'react';
import { getRecipes, getRecipe } from '../api';
import RecipeModal from './RecipeModal';

function HistoryTab() {
  // State variables
  const [recipes, setRecipes] = useState([]);           // List of all saved recipes
  const [loading, setLoading] = useState(true);          // Loading the list
  const [error, setError] = useState(null);              // Error message
  const [selectedRecipe, setSelectedRecipe] = useState(null); // Recipe shown in modal
  const [modalLoading, setModalLoading] = useState(false);    // Loading recipe details

  /**
   * Fetch all saved recipes when the component first mounts.
   * useEffect with empty dependency array [] runs only once.
   */
  useEffect(() => {
    fetchRecipes();
  }, []);

  /**
   * Fetch the list of saved recipes from the API.
   */
  const fetchRecipes = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getRecipes();
      setRecipes(data);
    } catch (err) {
      setError(err.message || 'Failed to load saved recipes');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle clicking "View Details" on a recipe row.
   * Fetches the full recipe data and opens the modal.
   */
  const handleViewDetails = async (id) => {
    try {
      setModalLoading(true);
      const data = await getRecipe(id);
      setSelectedRecipe(data);
    } catch (err) {
      alert('Failed to load recipe details: ' + err.message);
    } finally {
      setModalLoading(false);
    }
  };

  /**
   * Close the recipe detail modal.
   */
  const handleCloseModal = () => {
    setSelectedRecipe(null);
  };

  // ===== LOADING STATE =====
  if (loading) {
    return (
      <div className="loading">
        <span className="loading-spinner">📚 Loading saved recipes...</span>
      </div>
    );
  }

  // ===== ERROR STATE =====
  if (error) {
    return (
      <div className="error-message">
        ❌ {error}
      </div>
    );
  }

  // ===== EMPTY STATE =====
  if (recipes.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon">📭</div>
        <p>No recipes saved yet.</p>
        <p>Extract a recipe to see it here!</p>
      </div>
    );
  }

  return (
    <div>
      {/* ===== RECIPES TABLE ===== */}
      <table className="history-table">
        <thead>
          <tr>
            <th>Title</th>
            <th>Cuisine</th>
            <th>Difficulty</th>
            <th>Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {recipes.map((recipe) => (
            <tr key={recipe.id}>
              <td>{recipe.title || 'Untitled'}</td>
              <td>{recipe.cuisine || '—'}</td>
              <td>{recipe.difficulty || '—'}</td>
              <td>
                {/* Format the date nicely, or show a dash if no date */}
                {recipe.created_at
                  ? new Date(recipe.created_at).toLocaleDateString()
                  : '—'
                }
              </td>
              <td>
                <button
                  className="view-btn"
                  onClick={() => handleViewDetails(recipe.id)}
                  disabled={modalLoading}
                >
                  👁️ View Details
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* ===== LOADING INDICATOR FOR MODAL ===== */}
      {modalLoading && (
        <div className="loading">
          <span className="loading-spinner">Loading recipe details...</span>
        </div>
      )}

      {/* ===== RECIPE DETAIL MODAL ===== */}
      {selectedRecipe && (
        <RecipeModal
          data={selectedRecipe}
          onClose={handleCloseModal}
        />
      )}
    </div>
  );
}

export default HistoryTab;
