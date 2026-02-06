/**
 * ReservationItem - A single room reservation.
 */
import React from 'react'
import PropTypes from 'prop-types'

/**
 * Format a date/time string for display (e.g., "Feb 6, 1:00 PM").
 */
function formatDateTime(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

/**
 * Format time only (e.g., "4:00 PM").
 */
function formatTime(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
  })
}

function ReservationItem({ reservation }) {
  const { roomName, locationName, startTime, endTime, status } = reservation

  return (
    <div className="mylib-item">
      <div className="mylib-item__title">{roomName}</div>
      {locationName && (
        <div className="mylib-item__location">{locationName}</div>
      )}
      <div className="mylib-item__time">
        {formatDateTime(startTime)} - {formatTime(endTime)}
      </div>
      {status && status !== 'Confirmed' && (
        <div className="mylib-item__status">{status}</div>
      )}
    </div>
  )
}

ReservationItem.propTypes = {
  reservation: PropTypes.shape({
    id: PropTypes.string,
    roomName: PropTypes.string.isRequired,
    locationName: PropTypes.string,
    startTime: PropTypes.string.isRequired,
    endTime: PropTypes.string.isRequired,
    status: PropTypes.string,
  }).isRequired,
}

export default ReservationItem
