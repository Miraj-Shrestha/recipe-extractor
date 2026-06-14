/**
 * RecipeModal.jsx — A modal overlay that shows full recipe details.
 *
 * This component:
 * 1. Shows a dark semi-transparent overlay behind the modal
 * 2. Centers a white modal card on the screen
 * 3. Has a close (X) button in the top right
 * 4. Clicking the overlay background also closes the modal
 * 5. Renders RecipeDisplay inside the modal to show all recipe data
 *
 * Props:
 *   - data: the full recipe data object
 *   - onClose: function to call when the modal should close
 */

import RecipeDisplay from './RecipeDisplay';

function RecipeModal({ data, onClose }) {
  /**
   * Handle clicking the overlay background.
   * We only close if the user clicked the overlay itself, not the modal card.
   * This is done by checking if the click target is the overlay element.
   */
  const handleOverlayClick = (e) => {
    // e.target is what was clicked, e.currentTarget is the overlay div
    // Only close if the user clicked the overlay, not the modal content
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    /* Dark overlay behind the modal */
    <div className="modal-overlay" onClick={handleOverlayClick}>
      {/* White modal card */}
      <div className="modal-content">
        {/* Close (X) button */}
        <button className="modal-close" onClick={onClose}>
          ✕
        </button>

        {/* Render the full recipe data inside the modal */}
        <RecipeDisplay data={data} />
      </div>
    </div>
  );
}

export default RecipeModal;
