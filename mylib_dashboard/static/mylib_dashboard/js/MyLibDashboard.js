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
  DownloadItem,
  ILLRequestItem,
  ScanDeliverItem,
  ReservationItem,
  PagingRequestItem,
  ScMaterialItem,
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
  // ILLiad web interface URL for "Manage requests" links
  illiadWebUrl: DOM_ELEMENT.getAttribute('data-illiad-web-url') || '',
  // LibCal web interface URL for "Manage reservations" links
  libcalWebUrl: DOM_ELEMENT.getAttribute('data-libcal-web-url') || '',
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

  // Fetch all data - FOLIO
  const profileQuery = useQuery({ queryKey: ['profile'], queryFn: api.fetchProfile })
  const loansQuery = useQuery({ queryKey: ['loans'], queryFn: api.fetchLoans })
  const holdsQuery = useQuery({ queryKey: ['holds'], queryFn: api.fetchHolds })
  const finesQuery = useQuery({ queryKey: ['fines'], queryFn: api.fetchFines })
  const blocksQuery = useQuery({ queryKey: ['blocks'], queryFn: api.fetchBlocks })

  // Fetch all data - ILLiad
  const downloadsQuery = useQuery({ queryKey: ['downloads'], queryFn: api.fetchDownloads })
  const illInProcessQuery = useQuery({ queryKey: ['illInProcess'], queryFn: api.fetchIllInProcess })
  const scanDeliverQuery = useQuery({ queryKey: ['scanDeliverInProcess'], queryFn: api.fetchScanDeliverInProcess })

  // Fetch all data - LibCal
  const reservationsQuery = useQuery({ queryKey: ['reservations'], queryFn: api.fetchReservations })
  const scSeatsQuery = useQuery({ queryKey: ['scSeats'], queryFn: api.fetchScSeats })

  // Fetch all data - FOLIO paging requests
  const pagingRequestsQuery = useQuery({ queryKey: ['pagingRequests'], queryFn: api.fetchPagingRequests })

  // Fetch all data - Aeon (Special Collections materials)
  const scMaterialsQuery = useQuery({ queryKey: ['scMaterials'], queryFn: api.fetchScMaterials })

  // Compute derived data (returns zeros/empty when data not yet loaded)
  const alerts = useLoanAlerts(loansQuery.data)
  const tabCounts = useTabCounts(
    loansQuery.data,
    holdsQuery.data,
    downloadsQuery.data,
    illInProcessQuery.data,
    scanDeliverQuery.data,
    reservationsQuery.data,
    pagingRequestsQuery.data,
    scSeatsQuery.data,
    scMaterialsQuery.data
  )

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
                  <CategoryCard
                    title="Downloads"
                    count={downloadsQuery.data?.copies?.length || 0}
                    manageUrl={CONFIG.illiadWebUrl}
                    manageLabel="View all in ILLiad"
                    maxItems={CONFIG.maxItemsPerCard}
                    isLoading={downloadsQuery.isLoading}
                    error={downloadsQuery.error?.message}
                    onRetry={() => downloadsQuery.refetch()}
                    emptyMessage="No downloads available"
                  >
                    {downloadsQuery.data?.copies?.map(copy => (
                      <DownloadItem key={copy.id} copy={copy} />
                    ))}
                  </CategoryCard>
                </div>
              </div>
            )}

            {activeTab === TABS.IN_PROCESS && (
              <div
                id="panel-in-process"
                role="tabpanel"
                aria-labelledby="tab-in-process"
                className="mylib-panel"
              >
                <div className="mylib-card-grid">
                  <CategoryCard
                    title="Interlibrary Loan (ILL)"
                    count={illInProcessQuery.data?.requests?.length || 0}
                    manageUrl={CONFIG.illiadWebUrl}
                    manageLabel="View all in ILLiad"
                    maxItems={CONFIG.maxItemsPerCard}
                    isLoading={illInProcessQuery.isLoading}
                    error={illInProcessQuery.error?.message}
                    onRetry={() => illInProcessQuery.refetch()}
                    emptyMessage="No ILL requests in process"
                  >
                    {illInProcessQuery.data?.requests?.map(request => (
                      <ILLRequestItem key={request.id} request={request} />
                    ))}
                  </CategoryCard>
                  <CategoryCard
                    title="Scan & Deliver"
                    count={scanDeliverQuery.data?.requests?.length || 0}
                    manageUrl={CONFIG.illiadWebUrl}
                    manageLabel="View all in ILLiad"
                    maxItems={CONFIG.maxItemsPerCard}
                    isLoading={scanDeliverQuery.isLoading}
                    error={scanDeliverQuery.error?.message}
                    onRetry={() => scanDeliverQuery.refetch()}
                    emptyMessage="No scan requests in process"
                  >
                    {scanDeliverQuery.data?.requests?.map(request => (
                      <ScanDeliverItem key={request.id} request={request} />
                    ))}
                  </CategoryCard>
                  <CategoryCard
                    title="Paging Requests"
                    count={pagingRequestsQuery.data?.requests?.length || 0}
                    manageUrl={CONFIG.catalogAccountUrl}
                    maxItems={CONFIG.maxItemsPerCard}
                    isLoading={pagingRequestsQuery.isLoading}
                    error={pagingRequestsQuery.error?.message}
                    onRetry={() => pagingRequestsQuery.refetch()}
                    emptyMessage="No paging requests in process"
                  >
                    {pagingRequestsQuery.data?.requests?.map(request => (
                      <PagingRequestItem key={request.id} request={request} />
                    ))}
                  </CategoryCard>
                </div>
              </div>
            )}

            {activeTab === TABS.ROOM_RESERVATIONS && (
              <div
                id="panel-room-reservations"
                role="tabpanel"
                aria-labelledby="tab-room-reservations"
                className="mylib-panel"
              >
                <div className="mylib-card-grid">
                  <CategoryCard
                    title="Room Reservations"
                    count={reservationsQuery.data?.reservations?.length || 0}
                    manageUrl={CONFIG.libcalWebUrl}
                    manageLabel="Manage in LibCal"
                    maxItems={CONFIG.maxItemsPerCard}
                    isLoading={reservationsQuery.isLoading}
                    error={reservationsQuery.error?.message}
                    onRetry={() => reservationsQuery.refetch()}
                    emptyMessage="No upcoming room reservations"
                  >
                    {reservationsQuery.data?.reservations?.map(reservation => (
                      <ReservationItem key={reservation.id} reservation={reservation} />
                    ))}
                  </CategoryCard>
                </div>
              </div>
            )}

            {activeTab === TABS.SPECIAL_COLLECTIONS && (
              <div
                id="panel-special-collections"
                role="tabpanel"
                aria-labelledby="tab-special-collections"
                className="mylib-panel"
              >
                <div className="mylib-card-grid">
                  <CategoryCard
                    title="Material Requests"
                    count={scMaterialsQuery.data?.requests?.length || 0}
                    maxItems={CONFIG.maxItemsPerCard}
                    isLoading={scMaterialsQuery.isLoading}
                    error={scMaterialsQuery.error?.message}
                    onRetry={() => scMaterialsQuery.refetch()}
                    emptyMessage="No material requests"
                  >
                    {scMaterialsQuery.data?.requests?.map(request => (
                      <ScMaterialItem key={request.id} request={request} />
                    ))}
                  </CategoryCard>
                  <CategoryCard
                    title="Reading Room Reservations"
                    count={scSeatsQuery.data?.reservations?.length || 0}
                    manageUrl={CONFIG.libcalWebUrl}
                    manageLabel="Manage in LibCal"
                    maxItems={CONFIG.maxItemsPerCard}
                    isLoading={scSeatsQuery.isLoading}
                    error={scSeatsQuery.error?.message}
                    onRetry={() => scSeatsQuery.refetch()}
                    emptyMessage="No upcoming reading room reservations"
                  >
                    {scSeatsQuery.data?.reservations?.map(reservation => (
                      <ReservationItem key={reservation.id} reservation={reservation} />
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
