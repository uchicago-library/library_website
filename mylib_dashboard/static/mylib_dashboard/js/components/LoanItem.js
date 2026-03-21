/**
 * LoanItem - A single loan item row within a category card.
 */
import React from 'react'
import PropTypes from 'prop-types'
import { formatDate } from '../hooks'

function LoanItem({ loan }) {
  const { title, author, dueDate, isOverdue, isDueSoon, isRecalled } = loan

  let statusBadge = null
  if (isRecalled) {
    statusBadge = (
      <span className="mylib-item__badge mylib-item__badge--recalled">
        recalled
      </span>
    )
  } else if (isOverdue) {
    statusBadge = (
      <span className="mylib-item__badge mylib-item__badge--overdue">
        overdue
      </span>
    )
  } else if (isDueSoon) {
    statusBadge = (
      <span className="mylib-item__badge mylib-item__badge--due-soon">
        due in 24h
      </span>
    )
  }

  return (
    <div className="mylib-item">
      {statusBadge && <div className="mylib-item__status">{statusBadge}</div>}
      <div className="mylib-item__details">
        <div className="mylib-item__title">{title}</div>
        {author && <div className="mylib-item__author">{author}</div>}
        <div className="mylib-item__due">
          {isRecalled ? 'New Due Date:' : 'Due Date:'} {formatDate(dueDate)}
        </div>
      </div>
    </div>
  )
}

LoanItem.propTypes = {
  loan: PropTypes.shape({
    id: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
    author: PropTypes.string,
    dueDate: PropTypes.string,
    isOverdue: PropTypes.bool,
    isDueSoon: PropTypes.bool,
    isRecalled: PropTypes.bool,
  }).isRequired,
}

export default LoanItem
