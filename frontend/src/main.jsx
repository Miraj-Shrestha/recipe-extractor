/**
 * main.jsx — The entry point of our React application.
 *
 * This file renders the root App component into the DOM.
 * StrictMode helps catch common mistakes during development.
 */

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App.jsx';

// Find the root div in index.html and render our App inside it
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
