/**
 * AppointmentItem - A single appointment booking.
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

function AppointmentItem({ appointment }) {
  const { librarianName, location, directions, startTime, endTime } =
    appointment

  return (
    <div className="mylib-item">
      <div className="mylib-item__title">
        {librarianName ? `Appointment with ${librarianName}` : 'Appointment'}
      </div>
      {location && <div className="mylib-item__location">{location}</div>}
      {directions && <div className="mylib-item__directions">{directions}</div>}
      <div className="mylib-item__request-date">
        {formatDateTime(startTime)} - {formatTime(endTime)}
      </div>
    </div>
  )
}

AppointmentItem.propTypes = {
  appointment: PropTypes.shape({
    id: PropTypes.string,
    librarianName: PropTypes.string,
    location: PropTypes.string,
    directions: PropTypes.string,
    startTime: PropTypes.string.isRequired,
    endTime: PropTypes.string.isRequired,
  }).isRequired,
}

export default AppointmentItem
