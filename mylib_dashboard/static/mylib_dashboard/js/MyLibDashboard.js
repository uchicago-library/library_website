import React, { useState } from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query'

import createApi from './api'
import { useLoanAlerts, useTabCounts } from './hooks'
import {
  TabNav,
  TABS,
  AlertBanner,
  AutoRenewalNotice,
  AccountBlockWarning,
  MyAccountSidebar,
} from './components'

// Get the mount element and extract configuration from data attributes
const DOM_ELEMENT = document.getElementById('mylib-dashboard')

const CONFIG = {
  apiBaseUrl: DOM_ELEMENT.getAttribute('data-api-base-url') || '/api/mylib',
  vufindAccountUrl: DOM_ELEMENT.getAttribute('data-vufind-account-url') || '',
  illiadUrl: DOM_ELEMENT.getAttribute('data-illiad-url') || '',
  libcalUrl: DOM_ELEMENT.getAttribute('data-libcal-url') || '',
  autoRenewalNotice: DOM_ELEMENT.getAttribute('data-auto-renewal-notice') || '',
}

// Create API instance
const api = createApi(CONFIG.apiBaseUrl)

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
})

/**
 * MyLib Dashboard - Main Application Component
 *
 * Displays patron account information from FOLIO, ILLiad, and LibCal.
 */
function Dashboard() {
  const [activeTab, setActiveTab] = useState(TABS.CHECKED_OUT)

  // Fetch all data
  const profileQuery = useQuery({ queryKey: ['profile'], queryFn: api.fetchProfile })
  const loansQuery = useQuery({ queryKey: ['loans'], queryFn: api.fetchLoans })
  const holdsQuery = useQuery({ queryKey: ['holds'], queryFn: api.fetchHolds })
  const finesQuery = useQuery({ queryKey: ['fines'], queryFn: api.fetchFines })
  const blocksQuery = useQuery({ queryKey: ['blocks'], queryFn: api.fetchBlocks })

  // Compute derived data
  const alerts = useLoanAlerts(loansQuery.data)
  const tabCounts = useTabCounts(loansQuery.data, holdsQuery.data)

  // Loading state
  const isLoading = profileQuery.isLoading || loansQuery.isLoading

  // Error state - show if profile fails (critical)
  if (profileQuery.error) {
    return (
      <div className="mylib-dashboard mylib-dashboard--error">
        <div className="mylib-error">
          <h2>Unable to load your account</h2>
          <p>{profileQuery.error.message}</p>
          <button type="button" onClick={() => profileQuery.refetch()}>Try Again</button>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="mylib-dashboard mylib-dashboard--loading">
        <div className="mylib-loading">
          <div className="mylib-loading__spinner" aria-hidden="true" />
          <p>Loading your library account...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="mylib-dashboard">
      {/* Account Block Warning */}
      {blocksQuery.data?.hasBlocks && (
        <AccountBlockWarning blocks={blocksQuery.data.blocks} />
      )}

      {/* Auto-renewal Notice */}
      <AutoRenewalNotice content={CONFIG.autoRenewalNotice} />

      {/* Alert Banner */}
      {alerts.hasAlerts && (
        <AlertBanner
          recalledCount={alerts.recalledCount}
          overdueCount={alerts.overdueCount}
          dueSoonCount={alerts.dueSoonCount}
        />
      )}

      <div className="mylib-dashboard__layout">
        {/* Main Content */}
        <main className="mylib-dashboard__main">
          {/* Tab Navigation */}
          <TabNav
            activeTab={activeTab}
            onTabChange={setActiveTab}
            counts={tabCounts}
          />

          {/* Tab Panels */}
          <div className="mylib-dashboard__panels">
            {activeTab === TABS.CHECKED_OUT && (
              <div
                id="panel-checked-out"
                role="tabpanel"
                aria-labelledby="tab-checked-out"
                className="mylib-panel"
              >
                {/* Checked Out Items */}
                <p className="mylib-panel__placeholder">
                  {loansQuery.data?.totalLoans || 0} items checked out
                </p>
              </div>
            )}

            {activeTab === TABS.AVAILABLE_PICKUP && (
              <div
                id="panel-available-pickup"
                role="tabpanel"
                aria-labelledby="tab-available-pickup"
                className="mylib-panel"
              >
                {/* Available for Pickup */}
                <p className="mylib-panel__placeholder">
                  {holdsQuery.data?.totalHolds || 0} items available for pickup
                </p>
              </div>
            )}
          </div>
        </main>

        {/* Sidebar */}
        <MyAccountSidebar
          profile={profileQuery.data}
          finesTotal={finesQuery.data?.totalAmount || 0}
          recalledCount={alerts.recalledCount}
          externalLinks={{
            vufindAccountUrl: CONFIG.vufindAccountUrl,
            illiadUrl: CONFIG.illiadUrl,
            libcalUrl: CONFIG.libcalUrl,
          }}
        />
      </div>
    </div>
  )
}

/**
 * App wrapper with React Query provider.
 */
function MyLibDashboard() {
  return (
    <QueryClientProvider client={queryClient}>
      <Dashboard />
    </QueryClientProvider>
  )
}

// Mount the React application
const root = ReactDOM.createRoot(DOM_ELEMENT)
root.render(<MyLibDashboard />)
