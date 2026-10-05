/**
 * ILLRequestItem - A single ILL request in process.
 */
import React from 'react'
import PropTypes from 'prop-types'
import { formatDate } from '../hooks'

function ILLRequestItem({ request }) {
  const { title, author, status, requestDate } = request

  return (
    <div className="mylib-item">
      <div className="mylib-item__status">
        <span className="mylib-item__badge mylib-item__badge--info">
          {status}
        </span>
      </div>
      <div className="mylib-item__title">{title || 'Untitled'}</div>
      {author && <div className="mylib-item__author">{author}</div>}
      {requestDate && (
        <div className="mylib-item__request-date">
          Requested {formatDate(requestDate)}
        </div>
      )}
    </div>
  )
}

ILLRequestItem.propTypes = {
  request: PropTypes.shape({
    id: PropTypes.string.isRequired,
    title: PropTypes.string,
    author: PropTypes.string,
    status: PropTypes.string,
    requestDate: PropTypes.string,
  }).isRequired,
}

export default ILLRequestItem
