/**
 * AutoRenewalNotice - Dismissible notice with localStorage persistence.
 * Content is editable via Wagtail admin.
 */
import PropTypes from 'prop-types'
import React, { useEffect, useState } from 'react'

const STORAGE_KEY = 'mylib-auto-renewal-dismissed'

function AutoRenewalNotice({ content = '', versionToken = '' }) {
  const [isDismissed, setIsDismissed] = useState(true) // Start hidden to avoid flash
  const effectiveVersionToken = versionToken || 'default'

  useEffect(() => {
    const dismissedToken = localStorage.getItem(STORAGE_KEY)
    setIsDismissed(dismissedToken === effectiveVersionToken)
  }, [effectiveVersionToken])

  const handleDismiss = () => {
    localStorage.setItem(STORAGE_KEY, effectiveVersionToken)
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
  versionToken: PropTypes.string,
}

export default AutoRenewalNotice
