/**
 * RecipeDisplay.jsx — Displays full recipe data in a clean layout.
 *
 * This is a REUSABLE component used in both ExtractTab and RecipeModal.
 * It receives the recipe data as a prop and renders all sections.
 *
 * Sections:
 * 1. Recipe Summary (title, cuisine, time, servings, difficulty)
 * 2. Ingredients (list with quantity, unit, item)
 * 3. Instructions (numbered steps)
 * 4. Nutrition Estimate (calories, protein, carbs, fat)
 * 5. Ingredient Substitutions (original → substitute)
 * 6. Shopping List (grouped by category)
 * 7. Related Recipes (similar recipe suggestions)
 *
 * Props:
 *   - data: the recipe JSON object from the API
 */

function RecipeDisplay({ data }) {
  // If no data is provided, don't render anything
  if (!data) return null;

  /**
   * Helper function to get the difficulty badge color class.
   * Returns a CSS class name based on the difficulty level.
   */
  const getDifficultyClass = (difficulty) => {
    if (!difficulty) return 'difficulty-easy';
    const level = difficulty.toLowerCase();
    if (level === 'hard') return 'difficulty-hard';
    if (level === 'medium' || level === 'intermediate') return 'difficulty-medium';
    return 'difficulty-easy';
  };

  return (
    <div className="recipe-display">

      {/* ============================== */}
      {/* SECTION 1: Recipe Summary       */}
      {/* ============================== */}
      <div className="recipe-card">
        <h2 className="section-title">📋 Recipe Summary</h2>

        {/* Recipe title */}
        {data.title && (
          <h3 className="recipe-title">{data.title}</h3>
        )}

        {/* Meta info badges (cuisine, times, servings, difficulty) */}
        <div className="recipe-meta">
          {data.cuisine && (
            <span className="meta-badge">🌍 {data.cuisine}</span>
          )}
          {data.prep_time && (
            <span className="meta-badge">⏱️ Prep: {data.prep_time}</span>
          )}
          {data.cook_time && (
            <span className="meta-badge">🔥 Cook: {data.cook_time}</span>
          )}
          {data.total_time && (
            <span className="meta-badge">⏰ Total: {data.total_time}</span>
          )}
          {data.servings && (
            <span className="meta-badge">🍽️ Servings: {data.servings}</span>
          )}
          {data.difficulty && (
            <span className={`difficulty-badge ${getDifficultyClass(data.difficulty)}`}>
              {data.difficulty}
            </span>
          )}
        </div>
      </div>

      {/* ============================== */}
      {/* SECTION 2: Ingredients          */}
      {/* ============================== */}
      {data.ingredients && data.ingredients.length > 0 && (
        <div className="recipe-card">
          <h2 className="section-title">🥕 Ingredients</h2>
          <ul className="ingredients-list">
            {data.ingredients.map((ingredient, index) => (
              <li key={index}>
                {/* Show quantity and unit together, then the item name */}
                <span className="ingredient-qty">
                  {ingredient.quantity || ''} {ingredient.unit || ''}
                </span>
                <span className="ingredient-item">
                  {ingredient.item || ingredient.name || ingredient}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* ============================== */}
      {/* SECTION 3: Instructions         */}
      {/* ============================== */}
      {data.instructions && data.instructions.length > 0 && (
        <div className="recipe-card">
          <h2 className="section-title">📝 Instructions</h2>
          <ol className="instructions-list">
            {data.instructions.map((step, index) => (
              <li key={index}>
                {/* Step number circle */}
                <span className="step-number">{index + 1}</span>
                {/* Step text — handle both string and object formats */}
                <span>{typeof step === 'string' ? step : step.text || step.description || ''}</span>
              </li>
            ))}
          </ol>
        </div>
      )}

      {/* ============================== */}
      {/* SECTION 4: Nutrition Estimate   */}
      {/* ============================== */}
      {data.nutrition && (
        <div className="recipe-card">
          <h2 className="section-title">📊 Nutrition Estimate</h2>
          <div className="nutrition-grid">
            {/* Calories card */}
            {data.nutrition.calories !== undefined && (
              <div className="nutrition-item">
                <div className="nutrition-value">{data.nutrition.calories}</div>
                <div className="nutrition-label">🔥 Calories</div>
              </div>
            )}
            {/* Protein card */}
            {data.nutrition.protein !== undefined && (
              <div className="nutrition-item">
                <div className="nutrition-value">{data.nutrition.protein}</div>
                <div className="nutrition-label">💪 Protein</div>
              </div>
            )}
            {/* Carbs card */}
            {data.nutrition.carbs !== undefined && (
              <div className="nutrition-item">
                <div className="nutrition-value">{data.nutrition.carbs}</div>
                <div className="nutrition-label">🌾 Carbs</div>
              </div>
            )}
            {/* Fat card */}
            {data.nutrition.fat !== undefined && (
              <div className="nutrition-item">
                <div className="nutrition-value">{data.nutrition.fat}</div>
                <div className="nutrition-label">🧈 Fat</div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ============================== */}
      {/* SECTION 5: Substitutions        */}
      {/* ============================== */}
      {data.substitutions && data.substitutions.length > 0 && (
        <div className="recipe-card">
          <h2 className="section-title">🔄 Ingredient Substitutions</h2>
          <div className="substitutions-list">
            {data.substitutions.map((sub, index) => (
              <div className="substitution-card" key={index}>
                <div className="substitution-header">
                  {sub.original}
                  <span className="substitution-arrow">→</span>
                  {sub.substitute}
                </div>
                {sub.note && (
                  <div className="substitution-note">{sub.note}</div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ============================== */}
      {/* SECTION 6: Shopping List        */}
      {/* ============================== */}
      {data.shopping_list && Object.keys(data.shopping_list).length > 0 && (
        <div className="recipe-card">
          <h2 className="section-title">🛒 Shopping List</h2>
          <div className="shopping-categories">
            {/* Loop through each category (Dairy, Produce, Pantry, etc.) */}
            {Object.entries(data.shopping_list).map(([category, items]) => (
              <div className="category-group" key={category}>
                <h4>{category}</h4>
                <ul>
                  {/* Handle both array of strings and array of objects */}
                  {Array.isArray(items) && items.map((item, index) => (
                    <li key={index}>
                      {typeof item === 'string' ? item : item.name || item.item || ''}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ============================== */}
      {/* SECTION 7: Related Recipes      */}
      {/* ============================== */}
      {data.related_recipes && data.related_recipes.length > 0 && (
        <div className="recipe-card">
          <h2 className="section-title">🍽️ Related Recipes</h2>
          <div className="related-recipes">
            {data.related_recipes.map((recipe, index) => (
              <div className="related-card" key={index}>
                <h4>{recipe.title || recipe.name || 'Recipe'}</h4>
                <p>{recipe.description || ''}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default RecipeDisplay;
