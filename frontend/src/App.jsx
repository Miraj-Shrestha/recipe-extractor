/**
 * App.jsx — The root component of our Recipe Extractor app.
 *
 * This component handles:
 * 1. Displaying the header with app title
 * 2. Tab navigation (Extract Recipe / Saved Recipes)
 * 3. Rendering the correct tab content based on which tab is active
 */

import { useState } from 'react';
import './App.css';
import ExtractTab from './components/ExtractTab';
import HistoryTab from './components/HistoryTab';

function App() {
  // Track which tab is currently active: 'extract' or 'history'
  const [activeTab, setActiveTab] = useState('extract');

  return (
    <div className="app">
      {/* ===== APP HEADER ===== */}
      <header className="header">
        <h1>Recipe Extractor 🍳</h1>
        <p>Extract recipes from any URL and plan your meals</p>
      </header>

      {/* ===== TAB NAVIGATION ===== */}
      <nav className="tabs">
        {/* Extract Recipe tab button */}
        <button
          className={`tab-btn ${activeTab === 'extract' ? 'active' : ''}`}
          onClick={() => setActiveTab('extract')}
        >
          🔍 Extract Recipe
        </button>

        {/* Saved Recipes tab button */}
        <button
          className={`tab-btn ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          📚 Saved Recipes
        </button>
      </nav>

      {/* ===== TAB CONTENT ===== */}
      <main className="main-content">
        {/* Show ExtractTab or HistoryTab based on active tab */}
        {activeTab === 'extract' ? <ExtractTab /> : <HistoryTab />}
      </main>
    </div>
  );
}

export default App;
