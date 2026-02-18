/**
 * ScMaterialItem - A Special Collections material request from Aeon.
 */
import React from 'react'
import PropTypes from 'prop-types'
import { formatDate } from '../hooks'

function ScMaterialItem({ request }) {
  const { title, author, callNumber, scheduledDate, status } = request

  return (
    <div className="mylib-item">
      <div className="mylib-item__title">{title || 'Untitled'}</div>
      {author && <div className="mylib-item__author">{author}</div>}
      {callNumber && (
        <div className="mylib-item__call-number">{callNumber}</div>
      )}
      {scheduledDate && (
        <div className="mylib-item__scheduled-date">
          Scheduled: {formatDate(scheduledDate)}
        </div>
      )}
      {status && <div className="mylib-item__status">{status}</div>}
    </div>
  )
}

ScMaterialItem.propTypes = {
  request: PropTypes.shape({
    id: PropTypes.string.isRequired,
    title: PropTypes.string,
    author: PropTypes.string,
    callNumber: PropTypes.string,
    scheduledDate: PropTypes.string,
    status: PropTypes.string,
  }).isRequired,
}

export default ScMaterialItem
