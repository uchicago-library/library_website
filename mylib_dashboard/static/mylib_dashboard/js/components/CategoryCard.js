/**
 * CategoryCard - A card container for a category of items (e.g., Standard Loans).
 *
 * The maxItems prop controls how many items are initially displayed:
 * - If not set or 0, all items are shown
 * - If set to a positive number, only that many items are shown initially
 * - A "Show more" button allows users to reveal additional items in increments
 *
 * The isLoading prop shows a loading state inside the card while preserving
 * the card structure (title, manage link).
 */
import PropTypes from 'prop-types'
import React, { useState } from 'react'

function CardLoadingState() {
  return (
    <div className="mylib-card__loading">
      <div className="mylib-card__loading-item" />
      <div className="mylib-card__loading-item" />
      <div className="mylib-card__loading-item" />
    </div>
  )
}

function CardErrorState({ message = 'Unable to load data', onRetry = null }) {
  return (
    <div className="mylib-card__error">
      <p>{message || 'Unable to load data'}</p>
      {onRetry && (
        <button type="button" onClick={onRetry} className="mylib-card__retry">
          Try again
        </button>
      )}
    </div>
  )
}

CardErrorState.propTypes = {
  message: PropTypes.string,
  onRetry: PropTypes.func,
}

function CardEmptyState({ message = 'No items' }) {
  const text = message || 'No items'
  // Rich-text override fields are sanitized by Wagtail, so we render the
  // editor's HTML (which may include <a>, <b>, <i>) directly.
  if (typeof text === 'string') {
    return (
      <div
        className="mylib-card__empty"
        dangerouslySetInnerHTML={{ __html: text }}
      />
    )
  }
  return <div className="mylib-card__empty">{text}</div>
}

CardEmptyState.propTypes = {
  message: PropTypes.node,
}

function CategoryCard({
  title,
  count,
  manageUrl = '',
  manageLabel = 'All',
  maxItems = 0,
  isLoading = false,
  error = null,
  onRetry = null,
  emptyMessage = 'No items',
  children = null,
}) {
  // Track how many items are currently visible (starts at maxItems or all)
  const [visibleCount, setVisibleCount] = useState(maxItems || 0)

  // Convert children to array for slicing
  const childArray = React.Children.toArray(children)
  const totalItems = childArray.length

  // Determine what to display
  const effectiveLimit = visibleCount > 0 ? visibleCount : totalItems
  const displayedChildren = childArray.slice(0, effectiveLimit)
  const remainingItems = totalItems - effectiveLimit
  const hasMore = remainingItems > 0
  const isEmpty = !isLoading && !error && totalItems === 0

  // Show more handler - always reveal 10 additional items regardless of initial limit
  const handleShowMore = () => {
    setVisibleCount(prev => Math.min(prev + 10, totalItems))
  }

  // Check if manage link points to an external site
  const isExternal = manageUrl && /^https?:\/\//.test(manageUrl)

  // Determine content to render
  let content
  if (isLoading) {
    content = <CardLoadingState />
  } else if (error) {
    content = <CardErrorState message={error} onRetry={onRetry} />
  } else if (isEmpty) {
    content = <CardEmptyState message={emptyMessage} />
  } else {
    content = displayedChildren
  }

  return (
    <div className="mylib-card" data-ga-subcategory={`${title} Card`}>
      <div className="mylib-card__header">
        {!isLoading && !error && count !== undefined && (
          <span className="mylib-card__count">{count}</span>
        )}
        {isLoading && (
          <span className="mylib-card__count mylib-card__count--loading" />
        )}
        <h3 className="mylib-card__title">{title}</h3>
        {manageUrl && (
          <a
            href={manageUrl}
            className="mylib-card__manage-link"
            target={isExternal ? '_blank' : undefined}
            rel={isExternal ? 'noopener noreferrer' : undefined}
            data-ga-label={`All top`}
          >
            {'All '}
            {isExternal && (
              <i className="fa fa-external-link" aria-hidden="true" />
            )}
          </a>
        )}
        <button className="mylib-card__help-button" title={emptyMessage}>?</button>
      </div>
      <div className="mylib-card__body">
        <div className="mylib-card__content">{content}</div>
        {!isLoading && !error && !isEmpty && hasMore && (
          <button
            type="button"
            className="mylib-card__show-more"
            onClick={handleShowMore}
            data-ga-label="Show more items"
          >
            + Show {Math.min(remainingItems, 10)} more item
            {Math.min(remainingItems, 10) !== 1 ? 's' : ''}
          </button>
        )}
        {manageUrl && (
          <a
            href={manageUrl}
            className="mylib-card__manage-link mylib-card__manage-link--bottom"
            target={isExternal ? '_blank' : undefined}
            rel={isExternal ? 'noopener noreferrer' : undefined}
            data-ga-label={`${manageLabel} bottom`}
          >
            {manageLabel}{' '}
            {isExternal && (
              <i className="fa fa-external-link" aria-hidden="true" />
            )}
          </a>
        )}
      </div>
    </div>
  )
}

CategoryCard.propTypes = {
  title: PropTypes.string.isRequired,
  count: PropTypes.number,
  manageUrl: PropTypes.string,
  manageLabel: PropTypes.string,
  maxItems: PropTypes.number,
  isLoading: PropTypes.bool,
  error: PropTypes.string,
  onRetry: PropTypes.func,
  emptyMessage: PropTypes.node,
  children: PropTypes.node,
}

export default CategoryCard
