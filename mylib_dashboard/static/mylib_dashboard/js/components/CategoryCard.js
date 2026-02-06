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
import React, { useState } from 'react'
import PropTypes from 'prop-types'

function CardLoadingState() {
  return (
    <div className="mylib-card__loading">
      <div className="mylib-card__loading-item" />
      <div className="mylib-card__loading-item" />
      <div className="mylib-card__loading-item" />
    </div>
  )
}

function CardErrorState({ message, onRetry }) {
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

CardErrorState.defaultProps = {
  message: 'Unable to load data',
  onRetry: null,
}

function CardEmptyState({ message }) {
  return <div className="mylib-card__empty">{message || 'No items'}</div>
}

CardEmptyState.propTypes = {
  message: PropTypes.string,
}

CardEmptyState.defaultProps = {
  message: 'No items',
}

function CategoryCard({
  title,
  count,
  manageUrl,
  manageLabel,
  maxItems,
  isLoading,
  error,
  onRetry,
  emptyMessage,
  children,
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

  // Show more handler - increment by the initial maxItems value
  const handleShowMore = () => {
    const increment = maxItems || totalItems
    setVisibleCount(prev => Math.min(prev + increment, totalItems))
  }

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
    <div className="mylib-card">
      <div className="mylib-card__header">
        <h3 className="mylib-card__title">{title}</h3>
        {!isLoading && !error && count !== undefined && (
          <span className="mylib-card__count">{count}</span>
        )}
        {isLoading && (
          <span className="mylib-card__count mylib-card__count--loading" />
        )}
      </div>
      {manageUrl && (
        <a href={manageUrl} className="mylib-card__manage-link">
          {manageLabel}
        </a>
      )}
      <div className="mylib-card__content">{content}</div>
      {!isLoading && !error && !isEmpty && hasMore && (
        <button
          type="button"
          className="mylib-card__show-more"
          onClick={handleShowMore}
        >
          + Show {Math.min(remainingItems, maxItems || remainingItems)} more
          item
          {Math.min(remainingItems, maxItems || remainingItems) !== 1
            ? 's'
            : ''}
        </button>
      )}
      {manageUrl && (
        <a
          href={manageUrl}
          className="mylib-card__manage-link mylib-card__manage-link--bottom"
        >
          {manageLabel}
        </a>
      )}
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
  emptyMessage: PropTypes.string,
  children: PropTypes.node,
}

CategoryCard.defaultProps = {
  count: undefined,
  manageUrl: '',
  manageLabel: 'View all and manage',
  maxItems: 0,
  isLoading: false,
  error: null,
  onRetry: null,
  emptyMessage: 'No items',
  children: null,
}

export default CategoryCard
