/**
 * TabNav - Tab navigation with count badges.
 */
import React from 'react'
import PropTypes from 'prop-types'

export const TABS = {
  CHECKED_OUT: 'checked-out',
  AVAILABLE_PICKUP: 'available-pickup',
  IN_PROCESS: 'in-process',
  ROOM_RESERVATIONS: 'room-reservations',
  SPECIAL_COLLECTIONS: 'special-collections',
}

function TabNav({ activeTab, onTabChange, counts }) {
  const tabs = [
    {
      id: TABS.CHECKED_OUT,
      label: 'Checked Out',
      count: counts.checkedOut,
    },
    {
      id: TABS.AVAILABLE_PICKUP,
      label: 'Available for Pickup',
      count: counts.availableForPickup,
    },
    {
      id: TABS.IN_PROCESS,
      label: 'In Process',
      count: counts.inProcess,
    },
    {
      id: TABS.SPECIAL_COLLECTIONS,
      label: 'Special Collections',
      count: counts.specialCollections,
    },
    {
      id: TABS.ROOM_RESERVATIONS,
      label: 'Room Reservations',
      count: counts.roomReservations,
    },
  ]

  return (
    <nav className="mylib-tabs">
      {tabs.map(tab => (
        <button
          type="button"
          key={tab.id}
          aria-current={activeTab === tab.id ? 'page' : undefined}
          className={`mylib-tabs__tab ${activeTab === tab.id ? 'mylib-tabs__tab--active' : ''}`}
          onClick={() => onTabChange(tab.id)}
        >
          {tab.label}
          {tab.count > 0 && (
            <span className="mylib-tabs__badge">{tab.count}</span>
          )}
        </button>
      ))}
    </nav>
  )
}

TabNav.propTypes = {
  activeTab: PropTypes.string.isRequired,
  onTabChange: PropTypes.func.isRequired,
  counts: PropTypes.shape({
    checkedOut: PropTypes.number,
    availableForPickup: PropTypes.number,
    inProcess: PropTypes.number,
    roomReservations: PropTypes.number,
    specialCollections: PropTypes.number,
  }).isRequired,
}

export default TabNav
