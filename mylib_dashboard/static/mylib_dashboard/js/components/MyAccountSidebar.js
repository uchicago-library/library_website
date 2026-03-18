/**
 * MyAccountSidebar - My Account section with profile, fines, recalled items, and links.
 */
import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { formatCurrency } from '../hooks'

function LoadingPlaceholder({ width = '80%' }) {
  return (
    <span
      className="mylib-sidebar__loading"
      style={{ width: width || '80%' }}
      aria-hidden="true"
    />
  )
}

LoadingPlaceholder.propTypes = {
  width: PropTypes.string,
}

function MyAccountSidebar({
  profile = null,
  profileLoading = false,
  finesTotal = 0,
  finesLoading = false,
  recalledCount = 0,
  accountsFaqUrl = '',
  isAuthenticated = false,
}) {
  const [departmentExpanded, setDepartmentExpanded] = useState(false)

  const catalogBase = 'https://catalog.lib.uchicago.edu'
  const extIcon = <i className="fa fa-external-link" aria-hidden="true" />

  return (
    <aside className="mylib-sidebar">
      {/* My Account */}
      <div className="mylib-sidebar__section">
        <h3 className="mylib-sidebar__heading">My Account</h3>
        <ul className="mylib-sidebar__list">
          {/* Profile */}
          <li className="mylib-sidebar__item">
            <i className="fa fa-user mylib-sidebar__icon" aria-hidden="true" />
            {profileLoading ? (
              <LoadingPlaceholder width="100px" />
            ) : (
              <a
                href={`${catalogBase}/vufind/MyResearch/Profile`}
                className="mylib-sidebar__link"
              >
                {profile?.displayName || 'Profile'} {extIcon}
              </a>
            )}
          </li>

          {/* Saved Items */}
          <li className="mylib-sidebar__item">
            <i className="fa fa-star mylib-sidebar__icon" aria-hidden="true" />
            <a
              href={`${catalogBase}/vufind/MyResearch/Favorites`}
              className="mylib-sidebar__link"
            >
              Saved Items {extIcon}
            </a>
          </li>

          {/* Checked Out Items */}
          <li className="mylib-sidebar__item">
            <i className="fa fa-book mylib-sidebar__icon" aria-hidden="true" />
            <a
              href={`${catalogBase}/vufind/MyResearch/CheckedOut`}
              className="mylib-sidebar__link"
            >
              Checked Out Items {extIcon}
            </a>
          </li>

          {/* Fines */}
          <li className="mylib-sidebar__item">
            <i className="fa fa-usd mylib-sidebar__icon" aria-hidden="true" />
            {finesLoading ? (
              <LoadingPlaceholder width="120px" />
            ) : finesTotal > 0 ? (
              <a
                href={`${catalogBase}/vufind/MyResearch/Fines`}
                className="mylib-sidebar__link mylib-sidebar__warning"
              >
                You have {formatCurrency(finesTotal)} in fines. {extIcon}
              </a>
            ) : (
              <a
                href={`${catalogBase}/vufind/MyResearch/Fines`}
                className="mylib-sidebar__link"
              >
                Fines {extIcon}
              </a>
            )}
          </li>

          {/* Search History */}
          <li className="mylib-sidebar__item">
            <i
              className="fa fa-search mylib-sidebar__icon"
              aria-hidden="true"
            />
            <a
              href={`${catalogBase}/vufind/Search/History`}
              className="mylib-sidebar__link"
            >
              Search History {extIcon}
            </a>
          </li>

          {/* Recalled Items */}
          {recalledCount > 0 && (
            <li className="mylib-sidebar__item">
              <i
                className="fa fa-exclamation-circle mylib-sidebar__icon"
                aria-hidden="true"
              />
              <span className="mylib-sidebar__warning">
                You have {recalledCount} item{recalledCount !== 1 ? 's' : ''}{' '}
                recalled
              </span>
            </li>
          )}

          {/* Log In */}
          {!isAuthenticated && (
            <li className="mylib-sidebar__item">
              <i
                className="fa fa-sign-in mylib-sidebar__icon"
                aria-hidden="true"
              />
              <a
                href={`/Shibboleth.sso/Login?target=${encodeURIComponent(window.location.href)}`}
                className="mylib-sidebar__link"
              >
                Log In
              </a>
            </li>
          )}

          {/* Department Affiliation - Expandable */}
          {profile?.department && (
            <li className="mylib-sidebar__item mylib-sidebar__item--expandable">
              <button
                type="button"
                className="mylib-sidebar__expand-btn"
                onClick={() => setDepartmentExpanded(!departmentExpanded)}
                aria-expanded={departmentExpanded}
              >
                <i
                  className="fa fa-university mylib-sidebar__icon"
                  aria-hidden="true"
                />
                <span>My Lib department affiliation</span>
                <i
                  className={`fa fa-chevron-${departmentExpanded ? 'up' : 'down'} mylib-sidebar__chevron`}
                  aria-hidden="true"
                />
              </button>
              {departmentExpanded && (
                <div className="mylib-sidebar__expanded-content">
                  {profile.department}
                </div>
              )}
            </li>
          )}

          {/* Accounts FAQ */}
          {accountsFaqUrl && (
            <li className="mylib-sidebar__item">
              <i
                className="fa fa-question-circle mylib-sidebar__icon"
                aria-hidden="true"
              />
              <a href={accountsFaqUrl} className="mylib-sidebar__link">
                Accounts FAQ {extIcon}
              </a>
            </li>
          )}
        </ul>
      </div>

      {/* Manage Requests */}
      <div className="mylib-sidebar__section">
        <h3 className="mylib-sidebar__heading">Manage Requests</h3>
        <ul className="mylib-sidebar__list">
          <li className="mylib-sidebar__item">
            <i className="fa fa-flag mylib-sidebar__icon" aria-hidden="true" />
            <a
              href={`${catalogBase}/vufind/Requests/List`}
              className="mylib-sidebar__link"
            >
              Requested Items {extIcon}
            </a>
          </li>
          <li className="mylib-sidebar__item">
            <i
              className="fa fa-file-text-o mylib-sidebar__icon"
              aria-hidden="true"
            />
            <a
              href="https://requests.lib.uchicago.edu/illiad/illiad.dll"
              className="mylib-sidebar__link"
            >
              Interlibrary Loan {extIcon}
            </a>
          </li>
          <li className="mylib-sidebar__item">
            <i
              className="fa fa-folder-open mylib-sidebar__icon"
              aria-hidden="true"
            />
            <a
              href="https://forms2.lib.uchicago.edu/lib/aon/aeon.php"
              className="mylib-sidebar__link"
            >
              Special Collections {extIcon}
            </a>
          </li>
        </ul>
      </div>

      {/* Course Reserves */}
      <div className="mylib-sidebar__section">
        <h3 className="mylib-sidebar__heading">Course Reserves</h3>
        <ul className="mylib-sidebar__list">
          <li className="mylib-sidebar__item">
            <i
              className="fa fa-sticky-note-o mylib-sidebar__icon"
              aria-hidden="true"
            />
            <a
              href="https://acadtech-res.uchicago.edu/canvas/whichlogin/"
              className="mylib-sidebar__link"
            >
              Canvas {extIcon}
            </a>
          </li>
        </ul>
      </div>

      {/* Your Lists */}
      <div className="mylib-sidebar__section">
        <h3 className="mylib-sidebar__heading">Your Lists</h3>
        <ul className="mylib-sidebar__list">
          <li className="mylib-sidebar__item">
            <i className="fa fa-star mylib-sidebar__icon" aria-hidden="true" />
            <a
              href={`${catalogBase}/vufind/MyResearch/Favorites`}
              className="mylib-sidebar__link"
            >
              Saved Items {extIcon}
            </a>
          </li>
          <li className="mylib-sidebar__item">
            <i
              className="fa fa-plus-circle mylib-sidebar__icon"
              aria-hidden="true"
            />
            <a
              href={`${catalogBase}/vufind/MyResearch/EditList/NEW`}
              className="mylib-sidebar__link"
            >
              Create a List {extIcon}
            </a>
          </li>
        </ul>
      </div>
    </aside>
  )
}

MyAccountSidebar.propTypes = {
  profile: PropTypes.shape({
    displayName: PropTypes.string,
    department: PropTypes.string,
    patronGroup: PropTypes.string,
  }),
  profileLoading: PropTypes.bool,
  finesTotal: PropTypes.number,
  finesLoading: PropTypes.bool,
  recalledCount: PropTypes.number,
  accountsFaqUrl: PropTypes.string,
  isAuthenticated: PropTypes.bool,
}

export default MyAccountSidebar
