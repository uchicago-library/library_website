/**
 * PagingRequestItem - A single paging request (item being retrieved).
 */
import React from 'react'
import PropTypes from 'prop-types'
import { formatDate } from '../hooks'

function PagingRequestItem({ request }) {
  const { title, callNumber, locationName, pickupLocation, requestDate } =
    request

  return (
    <div className="mylib-item">
      <div className="mylib-item__title">{title || 'Untitled'}</div>
      {callNumber && (
        <div className="mylib-item__call-number">{callNumber}</div>
      )}
      {locationName && (
        <div className="mylib-item__location">From: {locationName}</div>
      )}
      {pickupLocation && (
        <div className="mylib-item__pickup">Pickup: {pickupLocation}</div>
      )}
      {requestDate && (
        <div className="mylib-item__request-date">
          Requested {formatDate(requestDate)}
        </div>
      )}
    </div>
  )
}

PagingRequestItem.propTypes = {
  request: PropTypes.shape({
    id: PropTypes.string.isRequired,
    title: PropTypes.string,
    callNumber: PropTypes.string,
    locationName: PropTypes.string,
    pickupLocation: PropTypes.string,
    requestDate: PropTypes.string,
  }).isRequired,
}

export default PagingRequestItem
