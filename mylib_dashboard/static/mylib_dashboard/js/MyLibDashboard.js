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
  CategoryCard,
  LoanItem,
  PickupItem,
} from './components'

// Get the mount element and extract configuration from data attributes
const DOM_ELEMENT = document.getElementById('mylib-dashboard')

const CONFIG = {
  apiBaseUrl: DOM_ELEMENT.getAttribute('data-api-base-url') || '/api/mylib',
  catalogAccountUrl: DOM_ELEMENT.getAttribute('data-catalog-account-url') || '',
  accountsFaqUrl: DOM_ELEMENT.getAttribute('data-accounts-faq-url') || '',
  autoRenewalNotice: DOM_ELEMENT.getAttribute('data-auto-renewal-notice') || '',
  // Max items to show per card (0 or empty = show all)
  maxItemsPerCard: parseInt(DOM_ELEMENT.getAttribute('data-max-items-per-card'), 10) || 0,
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

  // Compute derived data (returns zeros/empty when data not yet loaded)
  const alerts = useLoanAlerts(loansQuery.data)
  const tabCounts = useTabCounts(loansQuery.data, holdsQuery.data)

  // Note: We render the layout immediately - no blocking loading state.
  // Each section handles its own loading state for progressive rendering.

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
                <div className="mylib-card-grid">
                  <CategoryCard
                    title="Standard Loans"
                    count={loansQuery.data?.standardLoans?.length || 0}
                    manageUrl={CONFIG.catalogAccountUrl}
                    maxItems={CONFIG.maxItemsPerCard}
                    isLoading={loansQuery.isLoading}
                    error={loansQuery.error?.message}
                    onRetry={() => loansQuery.refetch()}
                    emptyMessage="No standard loans"
                  >
                    {loansQuery.data?.standardLoans?.map(loan => (
                      <LoanItem key={loan.id} loan={loan} />
                    ))}
                  </CategoryCard>
                  <CategoryCard
                    title="Short Term Loans"
                    count={loansQuery.data?.shortTermLoans?.length || 0}
                    manageUrl={CONFIG.catalogAccountUrl}
                    maxItems={CONFIG.maxItemsPerCard}
                    isLoading={loansQuery.isLoading}
                    error={loansQuery.error?.message}
                    onRetry={() => loansQuery.refetch()}
                    emptyMessage="No short term loans"
                  >
                    {loansQuery.data?.shortTermLoans?.map(loan => (
                      <LoanItem key={loan.id} loan={loan} />
                    ))}
                  </CategoryCard>
                </div>
              </div>
            )}

            {activeTab === TABS.AVAILABLE_PICKUP && (
              <div
                id="panel-available-pickup"
                role="tabpanel"
                aria-labelledby="tab-available-pickup"
                className="mylib-panel"
              >
                <div className="mylib-card-grid">
                  <CategoryCard
                    title="Pickups"
                    count={holdsQuery.data?.holds?.length || 0}
                    manageUrl={CONFIG.catalogAccountUrl}
                    maxItems={CONFIG.maxItemsPerCard}
                    isLoading={holdsQuery.isLoading}
                    error={holdsQuery.error?.message}
                    onRetry={() => holdsQuery.refetch()}
                    emptyMessage="No items available for pickup"
                  >
                    {holdsQuery.data?.holds?.map(hold => (
                      <PickupItem key={hold.id} hold={hold} />
                    ))}
                  </CategoryCard>
                </div>
              </div>
            )}
          </div>
        </main>

        {/* Sidebar */}
        <MyAccountSidebar
          profile={profileQuery.data}
          profileLoading={profileQuery.isLoading}
          finesTotal={finesQuery.data?.totalAmount || 0}
          finesLoading={finesQuery.isLoading}
          recalledCount={alerts.recalledCount}
          accountsFaqUrl={CONFIG.accountsFaqUrl}
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
