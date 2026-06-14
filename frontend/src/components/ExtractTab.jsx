/**
 * ExtractTab.jsx — The "Extract Recipe" tab component.
 *
 * This component lets the user:
 * 1. Paste a recipe URL into an input field
 * 2. Click "Extract Recipe" to send it to the backend
 * 3. See a loading state while the AI processes the recipe
 * 4. View the extracted recipe data using RecipeDisplay
 *
 * State:
 *   - url: the URL typed by the user
 *   - loading: true while waiting for the API response
 *   - error: error message if something goes wrong
 *   - recipeData: the extracted recipe data from the API
 */

import { useState } from 'react';
import { extractRecipe } from '../api';
import RecipeDisplay from './RecipeDisplay';

function ExtractTab() {
  // State variables for this component
  const [url, setUrl] = useState('');           // The URL the user types
  const [loading, setLoading] = useState(false); // Are we waiting for the API?
  const [error, setError] = useState(null);      // Any error message
  const [recipeData, setRecipeData] = useState(null); // The extracted recipe

  /**
   * Handle the "Extract Recipe" button click.
   * Sends the URL to the backend and updates state based on the response.
   */
  const handleExtract = async () => {
    // Don't do anything if the URL is empty
    if (!url.trim()) {
      setError('Please enter a recipe URL');
      return;
    }

    // Reset state before making the API call
    setLoading(true);
    setError(null);
    setRecipeData(null);

    try {
      // Call the API to extract the recipe
      const data = await extractRecipe(url.trim());

      // Save the extracted recipe data
      setRecipeData(data);
    } catch (err) {
      // If something went wrong, show the error message
      setError(err.message || 'Something went wrong. Please try again.');
    } finally {
      // Always stop the loading spinner when done
      setLoading(false);
    }
  };

  /**
   * Handle pressing Enter in the input field.
   * This lets users press Enter instead of clicking the button.
   */
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleExtract();
    }
  };

  return (
    <div>
      {/* ===== URL INPUT SECTION ===== */}
      <div className="extract-section">
        <h2>🔗 Paste a Recipe URL</h2>
        <p>Enter the URL of any recipe page and we'll extract all the details for you.</p>

        {/* Input row with URL field and Extract button */}
        <div className="input-row">
          <input
            type="text"
            className="url-input"
            placeholder="https://www.example.com/recipe/..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onKeyDown={handleKeyPress}
            disabled={loading}
          />
          <button
            className="extract-btn"
            onClick={handleExtract}
            disabled={loading}
          >
            {loading ? 'Extracting...' : '🍳 Extract Recipe'}
          </button>
        </div>

        {/* Show error message if there's an error */}
        {error && (
          <div className="error-message">
            ❌ {error}
          </div>
        )}
      </div>

      {/* ===== LOADING STATE ===== */}
      {loading && (
        <div className="loading">
          <span className="loading-spinner">
            ⏳ Extracting recipe... This may take a moment
          </span>
        </div>
      )}

      {/* ===== RECIPE DISPLAY ===== */}
      {/* Show the extracted recipe data when available */}
      {recipeData && !loading && (
        <RecipeDisplay data={recipeData} />
      )}
    </div>
  );
}

export default ExtractTab;
