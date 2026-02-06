/**
 * AccountBlockWarning - Warning banner when account has blocks.
 */
import React from 'react'
import PropTypes from 'prop-types'

function AccountBlockWarning({ blocks }) {
  if (!blocks || blocks.length === 0) {
    return null
  }

  return (
    <div className="mylib-block-warning" role="alert">
      <div className="mylib-block-warning__icon" aria-hidden="true">
        &#9888;
      </div>
      <div className="mylib-block-warning__content">
        <strong>Account Restrictions</strong>
        <ul className="mylib-block-warning__list">
          {blocks.map(block => (
            <li key={block.message}>{block.message}</li>
          ))}
        </ul>
      </div>
    </div>
  )
}

export default AccountBlockWarning

AccountBlockWarning.propTypes = {
  blocks: PropTypes.arrayOf(
    PropTypes.shape({
      type: PropTypes.string,
      message: PropTypes.string.isRequired,
      blockBorrowing: PropTypes.bool,
      blockRenewals: PropTypes.bool,
      blockRequests: PropTypes.bool,
    }),
  ),
}

AccountBlockWarning.defaultProps = {
  blocks: [],
}
