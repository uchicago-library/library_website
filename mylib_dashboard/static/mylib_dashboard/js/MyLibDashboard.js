import React from 'react'
import ReactDOM from 'react-dom/client'

// Get the mount element and extract configuration from data attributes
const DOM_ELEMENT = document.getElementById('mylib-dashboard')

const CONFIG = {
  apiBaseUrl: DOM_ELEMENT.getAttribute('data-api-base-url') || '/api/mylib',
  vufindAccountUrl: DOM_ELEMENT.getAttribute('data-vufind-account-url') || '',
  illiadUrl: DOM_ELEMENT.getAttribute('data-illiad-url') || '',
  libcalUrl: DOM_ELEMENT.getAttribute('data-libcal-url') || '',
}

/**
 * MyLib Dashboard - Main Application Component
 *
 * Displays patron account information from FOLIO, ILLiad, and LibCal.
 * Uses React Query for data fetching (to be added in Step 1).
 */
function MyLibDashboard() {
  return (
    <div className="mylib-dashboard">
      <div className="mylib-dashboard__loading">
        <h2>MyLib Dashboard</h2>
        <p>Loading your library account information...</p>
        <p>
          <small>
            API Base URL: {CONFIG.apiBaseUrl}
          </small>
        </p>
      </div>
    </div>
  )
}

// Mount the React application
const root = ReactDOM.createRoot(DOM_ELEMENT)
root.render(<MyLibDashboard />)
