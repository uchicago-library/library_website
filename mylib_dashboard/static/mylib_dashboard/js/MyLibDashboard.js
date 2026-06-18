import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query'
import React, { useCallback, useState } from 'react'
import ReactDOM from 'react-dom/client'

import createApi from './api'
import {
  AccountBlockWarning,
  AlertBanner,
  AppointmentItem,
  AutoRenewalNotice,
  CategoryCard,
  DownloadItem,
  ILLRequestItem,
  LoanItem,
  MyAccountSidebar,
  PagingRequestItem,
  PickupItem,
  ReservationItem,
  ScanDeliverItem,
  ScMaterialItem,
  TabNav,
  TABS,
} from './components'
import { useLoanAlerts, useTabCounts } from './hooks'

// Get the mount element and extract configuration from data attributes
const DOM_ELEMENT = document.getElementById('mylib-dashboard')

const CONFIG = {
  apiBaseUrl: DOM_ELEMENT.getAttribute('data-api-base-url') || '/api/mylib',
  catalogAccountUrl: DOM_ELEMENT.getAttribute('data-catalog-account-url') || '',
  accountsFaqUrl: DOM_ELEMENT.getAttribute('data-accounts-faq-url') || '',
  autoRenewalNotice: DOM_ELEMENT.getAttribute('data-auto-renewal-notice') || '',
  autoRenewalNoticeVersion: DOM_ELEMENT.getAttribute('data-auto-renewal-notice-version') || '',
  // Max items to show per card (0 or empty = show all)
  maxItemsPerCard: parseInt(DOM_ELEMENT.getAttribute('data-max-items-per-card'), 10) || 0,
  // LibCal web interface base URL
  libcalWebUrl: DOM_ELEMENT.getAttribute('data-libcal-web-url') || '',
  // Whether the user has an active Shibboleth session
  isAuthenticated: DOM_ELEMENT.getAttribute('data-is-authenticated') === 'true',
  // Per-card empty-state messages (rich-text HTML from Wagtail)
  emptyState: {
    nonRenewableLoans: DOM_ELEMENT.getAttribute('data-empty-state-non-renewable-loans') || '',
    standardLoans: DOM_ELEMENT.getAttribute('data-empty-state-standard-loans') || '',
    pickups: DOM_ELEMENT.getAttribute('data-empty-state-pickups') || '',
    downloads: DOM_ELEMENT.getAttribute('data-empty-state-downloads') || '',
    illInProcess: DOM_ELEMENT.getAttribute('data-empty-state-ill-in-process') || '',
    scanDeliver: DOM_ELEMENT.getAttribute('data-empty-state-scan-deliver') || '',
    pagingRequests: DOM_ELEMENT.getAttribute('data-empty-state-paging-requests') || '',
    roomReservations: DOM_ELEMENT.getAttribute('data-empty-state-room-reservations') || '',
    appointments: DOM_ELEMENT.getAttribute('data-empty-state-appointments') || '',
    materialRequests: DOM_ELEMENT.getAttribute('data-empty-state-material-requests') || '',
    readingRoomReservations: DOM_ELEMENT.getAttribute('data-empty-state-reading-room-reservations') || '',
  },
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
const STORAGE_KEY_TAB = 'mylib-active-tab'
const VALID_TABS = new Set(Object.values(TABS))

function Dashboard() {
  const [activeTab, setActiveTab] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY_TAB)
      return saved && VALID_TABS.has(saved) ? saved : TABS.CHECKED_OUT
    } catch {
      return TABS.CHECKED_OUT
    }
  })

  const handleTabChange = useCallback(tabId => {
    try { localStorage.setItem(STORAGE_KEY_TAB, tabId) } catch {}
    setActiveTab(tabId)
  }, [])

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
  const appointmentsQuery = useQuery({ queryKey: ['appointments'], queryFn: api.fetchAppointments })
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
    appointmentsQuery.data,
    pagingRequestsQuery.data,
    scSeatsQuery.data,
    scMaterialsQuery.data
  )
  const tabLoading = {
    checkedOut: loansQuery.isLoading,
    availableForPickup: holdsQuery.isLoading || downloadsQuery.isLoading,
    inProcess:
      illInProcessQuery.isLoading ||
      scanDeliverQuery.isLoading ||
      pagingRequestsQuery.isLoading,
    reservations: reservationsQuery.isLoading || appointmentsQuery.isLoading,
    specialCollections: scSeatsQuery.isLoading || scMaterialsQuery.isLoading,
  }

  // Note: We render the layout immediately - no blocking loading state.
  // Each section handles its own loading state for progressive rendering.

  return (
    <div className="mylib-dashboard">
      {/* Account Block Warning */}
      {blocksQuery.data?.hasBlocks && (
        <AccountBlockWarning blocks={blocksQuery.data.blocks} />
      )}

      {/* Auto-renewal Notice */}
      <AutoRenewalNotice
        content={CONFIG.autoRenewalNotice}
        versionToken={CONFIG.autoRenewalNoticeVersion}
      />

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
            onTabChange={handleTabChange}
            counts={tabCounts}
            loading={tabLoading}
          />

          {/* Tab Panels */}
          <div className="mylib-dashboard__panels" aria-live="polite">
            {activeTab === TABS.CHECKED_OUT && (
              <div
                id="panel-checked-out"
                role="tabpanel"
                aria-labelledby="tab-checked-out"
                className="mylib-panel"
              >
                <h2 className="sr-only">Checked Out</h2>
                <div className="mylib-card-grid">
                  <CategoryCard
                    title="Non-Renewable Loans"
                    count={loansQuery.data?.nonRenewableLoans?.length || 0}
                    manageUrl={CONFIG.catalogAccountUrl}
                    manageLabel="View all and sort"
                    maxItems={CONFIG.maxItemsPerCard}
                    isLoading={loansQuery.isLoading}
                    error={loansQuery.error?.message}
                    onRetry={() => loansQuery.refetch()}
                    emptyMessage={CONFIG.emptyState.nonRenewableLoans}
                  >
                    {loansQuery.data?.nonRenewableLoans?.map(loan => (
                      <LoanItem key={loan.id} loan={loan} />
                    ))}
                  </CategoryCard>
                  <CategoryCard
                    title="Standard Loans"
                    count={loansQuery.data?.standardLoans?.length || 0}
                    manageUrl={CONFIG.catalogAccountUrl}
                    manageLabel="View all and sort"
                    maxItems={CONFIG.maxItemsPerCard}
                    isLoading={loansQuery.isLoading}
                    error={loansQuery.error?.message}
                    onRetry={() => loansQuery.refetch()}
                    emptyMessage={CONFIG.emptyState.standardLoans}
                  >
                    {loansQuery.data?.standardLoans?.map(loan => (
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
                <h2 className="sr-only">Available for Pickup</h2>
                <div className="mylib-card-grid">
                  <CategoryCard
                    title="Pickups"
                    count={holdsQuery.data?.holds?.length || 0}
                    manageUrl={CONFIG.catalogAccountUrl}
                    maxItems={CONFIG.maxItemsPerCard}
                    isLoading={holdsQuery.isLoading}
                    error={holdsQuery.error?.message}
                    onRetry={() => holdsQuery.refetch()}
                    emptyMessage={CONFIG.emptyState.pickups}
                  >
                    {holdsQuery.data?.holds?.map(hold => (
                      <PickupItem key={hold.id} hold={hold} />
                    ))}
                  </CategoryCard>
                  <CategoryCard
                    title="Downloads"
                    count={downloadsQuery.data?.copies?.length || 0}
                    manageUrl="https://requests.lib.uchicago.edu/illiad/illiad.dll?Action=10&Form=64"
                    maxItems={CONFIG.maxItemsPerCard}
                    isLoading={downloadsQuery.isLoading}
                    error={downloadsQuery.error?.message}
                    onRetry={() => downloadsQuery.refetch()}
                    emptyMessage={CONFIG.emptyState.downloads}
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
                <h2 className="sr-only">In Process</h2>
                <div className="mylib-card-grid">
                  <CategoryCard
                    title="Interlibrary Loan (ILL)"
                    count={illInProcessQuery.data?.requests?.length || 0}
                    manageUrl="https://requests.lib.uchicago.edu/illiad/illiad.dll?Action=10&Form=62"
                    maxItems={CONFIG.maxItemsPerCard}
                    isLoading={illInProcessQuery.isLoading}
                    error={illInProcessQuery.error?.message}
                    onRetry={() => illInProcessQuery.refetch()}
                    emptyMessage={CONFIG.emptyState.illInProcess}
                  >
                    {illInProcessQuery.data?.requests?.map(request => (
                      <ILLRequestItem key={request.id} request={request} />
                    ))}
                  </CategoryCard>
                  <CategoryCard
                    title="Scan & Deliver"
                    count={scanDeliverQuery.data?.requests?.length || 0}
                    manageUrl="https://requests.lib.uchicago.edu/illiad/illiad.dll?Action=10&Form=62"
                    maxItems={CONFIG.maxItemsPerCard}
                    isLoading={scanDeliverQuery.isLoading}
                    error={scanDeliverQuery.error?.message}
                    onRetry={() => scanDeliverQuery.refetch()}
                    emptyMessage={CONFIG.emptyState.scanDeliver}
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
                    emptyMessage={CONFIG.emptyState.pagingRequests}
                  >
                    {pagingRequestsQuery.data?.requests?.map(request => (
                      <PagingRequestItem key={request.id} request={request} />
                    ))}
                  </CategoryCard>
                </div>
              </div>
            )}

            {activeTab === TABS.RESERVATIONS && (
              <div
                id="panel-reservations"
                role="tabpanel"
                aria-labelledby="tab-reservations"
                className="mylib-panel"
              >
                <h2 className="sr-only">Reservations</h2>
                <div className="mylib-card-grid">
                  <CategoryCard
                    title="Room Reservations"
                    count={reservationsQuery.data?.reservations?.length || 0}
                    manageUrl="/spaces/"
                    manageLabel="Make a new reservation"
                    isLoading={reservationsQuery.isLoading}
                    error={reservationsQuery.error?.message}
                    onRetry={() => reservationsQuery.refetch()}
                    emptyMessage={CONFIG.emptyState.roomReservations}
                  >
                    {reservationsQuery.data?.reservations?.map(reservation => (
                      <ReservationItem key={reservation.id} reservation={reservation} />
                    ))}
                  </CategoryCard>
                  <CategoryCard
                    title="Appointments"
                    count={appointmentsQuery.data?.appointments?.length || 0}
                    manageUrl="/about/directory/?view=staff&subject=All+Subject+Specialists"
                    manageLabel="Schedule appointment"
                    isLoading={appointmentsQuery.isLoading}
                    error={appointmentsQuery.error?.message}
                    onRetry={() => appointmentsQuery.refetch()}
                    emptyMessage={CONFIG.emptyState.appointments}
                  >
                    {appointmentsQuery.data?.appointments?.map(appointment => (
                      <AppointmentItem key={appointment.id} appointment={appointment} />
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
                <h2 className="sr-only">Special Collections</h2>
                <div className="mylib-card-grid">
                  <CategoryCard
                    title="Material Requests"
                    count={scMaterialsQuery.data?.requests?.length || 0}
                    manageUrl="https://scrcrequests.lib.uchicago.edu/"
                    maxItems={CONFIG.maxItemsPerCard}
                    isLoading={scMaterialsQuery.isLoading}
                    error={scMaterialsQuery.error?.message}
                    onRetry={() => scMaterialsQuery.refetch()}
                    emptyMessage={CONFIG.emptyState.materialRequests}
                  >
                    {scMaterialsQuery.data?.requests?.map(request => (
                      <ScMaterialItem key={request.id} request={request} />
                    ))}
                  </CategoryCard>
                  <CategoryCard
                    title="Reading Room Reservations"
                    count={scSeatsQuery.data?.reservations?.length || 0}
                    manageUrl={CONFIG.libcalWebUrl ? `${CONFIG.libcalWebUrl}/reserve/scrc` : ''}
                    manageLabel="Make a new reservation"
                    maxItems={CONFIG.maxItemsPerCard}
                    isLoading={scSeatsQuery.isLoading}
                    error={scSeatsQuery.error?.message}
                    onRetry={() => scSeatsQuery.refetch()}
                    emptyMessage={CONFIG.emptyState.readingRoomReservations}
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
          isAuthenticated={CONFIG.isAuthenticated}
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
