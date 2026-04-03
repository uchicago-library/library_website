/**
 * ScanDeliverItem - A single Scan & Deliver request in process.
 */
import React from 'react'
import PropTypes from 'prop-types'
import { formatDate } from '../hooks'

function ScanDeliverItem({ request }) {
  const { articleTitle, sourceTitle, status, requestDate } = request

  return (
    <div className="mylib-item">
      <div className="mylib-item__status">
        <span className="mylib-item__badge mylib-item__badge--info">
          {status}
        </span>
      </div>
      <div className="mylib-item__title">{articleTitle || 'Untitled'}</div>
      {sourceTitle && <div className="mylib-item__source">{sourceTitle}</div>}
      {requestDate && (
        <div className="mylib-item__request-date">
          Requested {formatDate(requestDate)}
        </div>
      )}
    </div>
  )
}

ScanDeliverItem.propTypes = {
  request: PropTypes.shape({
    id: PropTypes.string.isRequired,
    articleTitle: PropTypes.string,
    sourceTitle: PropTypes.string,
    status: PropTypes.string,
    requestDate: PropTypes.string,
  }).isRequired,
}

export default ScanDeliverItem
