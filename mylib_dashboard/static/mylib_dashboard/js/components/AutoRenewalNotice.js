/**
 * AutoRenewalNotice - Dismissible notice with localStorage persistence.
 * Content is editable via Wagtail admin.
 */
import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'

const STORAGE_KEY = 'mylib-auto-renewal-dismissed'

function AutoRenewalNotice({ content }) {
  const [isDismissed, setIsDismissed] = useState(true) // Start hidden to avoid flash

  useEffect(() => {
    const dismissed = localStorage.getItem(STORAGE_KEY)
    setIsDismissed(dismissed === 'true')
  }, [])

  const handleDismiss = () => {
    localStorage.setItem(STORAGE_KEY, 'true')
    setIsDismissed(true)
  }

  // Don't render if dismissed or no content
  if (isDismissed || !content) {
    return null
  }

  return (
    <div className="mylib-notice" role="note">
      <div
        className="mylib-notice__content"
        dangerouslySetInnerHTML={{ __html: content }}
      />
      <button
        type="button"
        className="mylib-notice__dismiss"
        onClick={handleDismiss}
        aria-label="Dismiss notice"
      >
        <span aria-hidden="true">&times;</span>
      </button>
    </div>
  )
}

AutoRenewalNotice.propTypes = {
  content: PropTypes.string,
}

AutoRenewalNotice.defaultProps = {
  content: '',
}

export default AutoRenewalNotice
