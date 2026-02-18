/**
 * PickupItem - A single item available for pickup.
 */
import React from 'react'
import PropTypes from 'prop-types'

/**
 * Format a date string for display.
 */
function formatPickupDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

function PickupItem({ hold }) {
  const { title, pickupLocation, holdShelfExpirationDate } = hold

  return (
    <div className="mylib-item">
      <div className="mylib-item__title">{title}</div>
      {pickupLocation && (
        <div className="mylib-item__location">{pickupLocation}</div>
      )}
      {holdShelfExpirationDate && (
        <div className="mylib-item__pickup-by">
          Pick up by {formatPickupDate(holdShelfExpirationDate)}
        </div>
      )}
    </div>
  )
}

PickupItem.propTypes = {
  hold: PropTypes.shape({
    id: PropTypes.string,
    title: PropTypes.string.isRequired,
    pickupLocation: PropTypes.string,
    holdShelfExpirationDate: PropTypes.string,
  }).isRequired,
}

export default PickupItem
