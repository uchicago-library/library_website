/**
 * TabNav - Tab navigation with count badges.
 *
 * Implements the WAI-ARIA Tabs pattern:
 * https://www.w3.org/WAI/ARIA/apg/patterns/tabpanel/
 */
import React, { useRef, useCallback } from 'react'
import PropTypes from 'prop-types'

export const TABS = {
  CHECKED_OUT: 'checked-out',
  AVAILABLE_PICKUP: 'available-pickup',
  IN_PROCESS: 'in-process',
  RESERVATIONS: 'reservations',
  SPECIAL_COLLECTIONS: 'special-collections',
}

function TabNav({ activeTab, onTabChange, counts, loading }) {
  const tabRefs = useRef([])

  const tabs = [
    {
      id: TABS.CHECKED_OUT,
      label: 'Checked Out',
      count: counts.checkedOut,
      loading: loading.checkedOut,
    },
    {
      id: TABS.AVAILABLE_PICKUP,
      label: 'Available for Pickup',
      count: counts.availableForPickup,
      loading: loading.availableForPickup,
    },
    {
      id: TABS.IN_PROCESS,
      label: 'In Process',
      count: counts.inProcess,
      loading: loading.inProcess,
    },
    {
      id: TABS.SPECIAL_COLLECTIONS,
      label: 'Special Collections',
      count: counts.specialCollections,
      loading: loading.specialCollections,
    },
    {
      id: TABS.RESERVATIONS,
      label: 'Reservations',
      count: counts.reservations,
      loading: loading.reservations,
    },
  ]

  const handleKeyDown = useCallback(
    e => {
      const currentIndex = tabs.findIndex(t => t.id === activeTab)
      let newIndex

      switch (e.key) {
        case 'ArrowRight':
          newIndex = (currentIndex + 1) % tabs.length
          break
        case 'ArrowLeft':
          newIndex = (currentIndex - 1 + tabs.length) % tabs.length
          break
        case 'Home':
          newIndex = 0
          break
        case 'End':
          newIndex = tabs.length - 1
          break
        default:
          return
      }

      e.preventDefault()
      onTabChange(tabs[newIndex].id)
      tabRefs.current[newIndex]?.focus()
    },
    [activeTab, onTabChange],
  )

  return (
    <div role="tablist" aria-label="Dashboard sections" className="mylib-tabs">
      {tabs.map((tab, index) => (
        <button
          type="button"
          role="tab"
          key={tab.id}
          id={`tab-${tab.id}`}
          ref={el => {
            tabRefs.current[index] = el
          }}
          aria-selected={activeTab === tab.id}
          aria-controls={`panel-${tab.id}`}
          tabIndex={activeTab === tab.id ? 0 : -1}
          className={`mylib-tabs__tab ${activeTab === tab.id ? 'mylib-tabs__tab--active' : ''}`}
          onClick={() => onTabChange(tab.id)}
          onKeyDown={handleKeyDown}
          data-ga-subcategory={tab.label}
          data-ga-label={tab.label}
        >
          {tab.label}
          {tab.loading && (
            <span
              className="mylib-tabs__badge mylib-tabs__badge--loading"
              aria-label="Loading count"
              role="status"
            />
          )}
          {!tab.loading && tab.count > 0 && (
            <span className="mylib-tabs__badge">{tab.count}</span>
          )}
        </button>
      ))}
    </div>
  )
}

TabNav.propTypes = {
  activeTab: PropTypes.string.isRequired,
  onTabChange: PropTypes.func.isRequired,
  counts: PropTypes.shape({
    checkedOut: PropTypes.number,
    availableForPickup: PropTypes.number,
    inProcess: PropTypes.number,
    reservations: PropTypes.number,
    specialCollections: PropTypes.number,
  }).isRequired,
  loading: PropTypes.shape({
    checkedOut: PropTypes.bool,
    availableForPickup: PropTypes.bool,
    inProcess: PropTypes.bool,
    reservations: PropTypes.bool,
    specialCollections: PropTypes.bool,
  }).isRequired,
}

export default TabNav
