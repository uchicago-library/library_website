/**
 * MyAccountSidebar - Profile info, fines, recalled count, and external links.
 */
import React from 'react'
import PropTypes from 'prop-types'
import { formatCurrency } from '../hooks'

function MyAccountSidebar({
  profile,
  finesTotal,
  recalledCount,
  externalLinks,
}) {
  return (
    <aside className="mylib-sidebar">
      {/* Profile Section */}
      {profile && (
        <div className="mylib-sidebar__section">
          <h3 className="mylib-sidebar__heading">My Account</h3>
          <div className="mylib-sidebar__profile">
            <div className="mylib-sidebar__name">{profile.displayName}</div>
            {profile.department && (
              <div className="mylib-sidebar__department">
                {profile.department}
              </div>
            )}
            {profile.patronGroup && (
              <div className="mylib-sidebar__patron-group">
                {profile.patronGroup}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Account Summary */}
      <div className="mylib-sidebar__section">
        <h3 className="mylib-sidebar__heading">Account Summary</h3>
        <dl className="mylib-sidebar__stats">
          <div className="mylib-sidebar__stat">
            <dt>Fines</dt>
            <dd
              className={finesTotal > 0 ? 'mylib-sidebar__stat--warning' : ''}
            >
              {formatCurrency(finesTotal)}
            </dd>
          </div>
          {recalledCount > 0 && (
            <div className="mylib-sidebar__stat mylib-sidebar__stat--alert">
              <dt>Recalled Items</dt>
              <dd>{recalledCount}</dd>
            </div>
          )}
        </dl>
      </div>

      {/* External Links */}
      {externalLinks && (
        <div className="mylib-sidebar__section">
          <h3 className="mylib-sidebar__heading">Other Services</h3>
          <nav className="mylib-sidebar__links">
            {externalLinks.vufindAccountUrl && (
              <a
                href={externalLinks.vufindAccountUrl}
                className="mylib-sidebar__link"
                target="_blank"
                rel="noopener noreferrer"
              >
                Full Catalog Account
              </a>
            )}
            {externalLinks.illiadUrl && (
              <a
                href={externalLinks.illiadUrl}
                className="mylib-sidebar__link"
                target="_blank"
                rel="noopener noreferrer"
              >
                Interlibrary Loan (ILLiad)
              </a>
            )}
            {externalLinks.libcalUrl && (
              <a
                href={externalLinks.libcalUrl}
                className="mylib-sidebar__link"
                target="_blank"
                rel="noopener noreferrer"
              >
                Room Reservations (LibCal)
              </a>
            )}
          </nav>
        </div>
      )}
    </aside>
  )
}

MyAccountSidebar.propTypes = {
  profile: PropTypes.shape({
    displayName: PropTypes.string,
    department: PropTypes.string,
    patronGroup: PropTypes.string,
  }),
  finesTotal: PropTypes.number,
  recalledCount: PropTypes.number,
  externalLinks: PropTypes.shape({
    vufindAccountUrl: PropTypes.string,
    illiadUrl: PropTypes.string,
    libcalUrl: PropTypes.string,
  }),
}

MyAccountSidebar.defaultProps = {
  profile: null,
  finesTotal: 0,
  recalledCount: 0,
  externalLinks: null,
}

export default MyAccountSidebar
