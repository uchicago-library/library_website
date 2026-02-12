/**
 * AlertBanner - Shows recalled, overdue, and due soon counts.
 */
import React from 'react'
import PropTypes from 'prop-types'

function AlertBanner({
  recalledCount = 0,
  overdueCount = 0,
  dueSoonCount = 0,
}) {
  const alerts = []

  if (recalledCount > 0) {
    alerts.push({
      type: 'recalled',
      className: 'mylib-alert--danger',
      message: `${recalledCount} item${recalledCount !== 1 ? 's' : ''} recalled`,
    })
  }

  if (overdueCount > 0) {
    alerts.push({
      type: 'overdue',
      className: 'mylib-alert--warning',
      message: `${overdueCount} item${overdueCount !== 1 ? 's' : ''} overdue`,
    })
  }

  if (dueSoonCount > 0) {
    alerts.push({
      type: 'due-soon',
      className: 'mylib-alert--info',
      message: `${dueSoonCount} item${dueSoonCount !== 1 ? 's' : ''} due soon`,
    })
  }

  if (alerts.length === 0) {
    return null
  }

  return (
    <div className="mylib-alerts" role="status" aria-live="polite">
      {alerts.map(alert => (
        <div
          key={alert.type}
          className={`mylib-alert ${alert.className}`}
          role="alert"
        >
          {alert.message}
        </div>
      ))}
    </div>
  )
}

AlertBanner.propTypes = {
  recalledCount: PropTypes.number,
  overdueCount: PropTypes.number,
  dueSoonCount: PropTypes.number,
}

export default AlertBanner
