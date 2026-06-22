/**
 * AutoRenewalNotice - Dismissible notice with localStorage persistence.
 * Content is editable via Wagtail admin.
 */
import PropTypes from 'prop-types'
import React, { useEffect, useState } from 'react'

const STORAGE_KEY = 'mylib-auto-renewal-dismissed'

// Derive the dismiss token from the notice content itself (small polynomial hash),
// so the banner only re-appears when the content actually changes.
function hashContent(str) {
  let hash = 0
  for (let i = 0; i < str.length; i += 1) {
    hash = (hash * 31 + str.charCodeAt(i)) % 2147483647
  }
  return hash.toString(36)
}

function AutoRenewalNotice({ content = '' }) {
  const [isDismissed, setIsDismissed] = useState(true) // Start hidden to avoid flash
  const contentToken = hashContent(content)

  useEffect(() => {
    setIsDismissed(localStorage.getItem(STORAGE_KEY) === contentToken)
  }, [contentToken])

  const handleDismiss = () => {
    localStorage.setItem(STORAGE_KEY, contentToken)
    setIsDismissed(true)
  }

  // Don't render if dismissed or no content
  if (isDismissed || !content) {
    return null
  }

  return (
    <div
      className="mylib-notice"
      role="note"
      data-ga-category="Floating"
      data-ga-subcategory="Dismissible Notice"
    >
      <div
        className="mylib-notice__content"
        dangerouslySetInnerHTML={{ __html: content }} //eslint-disable-line react/no-danger
      />
      <button
        type="button"
        className="mylib-notice__dismiss"
        onClick={handleDismiss}
        aria-label="Dismiss notice"
        data-ga-label="Dismiss notice"
      >
        <span aria-hidden="true">&times;</span>
      </button>
    </div>
  )
}

AutoRenewalNotice.propTypes = {
  content: PropTypes.string,
}

export default AutoRenewalNotice
