/**
 * MyAccountSidebar - My Account section with profile, fines, recalled items, and links.
 */
import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { formatCurrency } from '../hooks'

function LoadingPlaceholder({ width }) {
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

LoadingPlaceholder.defaultProps = {
  width: '80%',
}

function MyAccountSidebar({
  profile,
  profileLoading,
  finesTotal,
  finesLoading,
  recalledCount,
  accountsFaqUrl,
}) {
  const [departmentExpanded, setDepartmentExpanded] = useState(false)

  return (
    <aside className="mylib-sidebar">
      <div className="mylib-sidebar__section">
        <h3 className="mylib-sidebar__heading">My Account</h3>
        <ul className="mylib-sidebar__list">
          {/* Profile */}
          <li className="mylib-sidebar__item">
            <i className="fa fa-user mylib-sidebar__icon" aria-hidden="true" />
            {profileLoading ? (
              <LoadingPlaceholder width="100px" />
            ) : (
              <span>Profile</span>
            )}
          </li>

          {/* Fines */}
          <li className="mylib-sidebar__item">
            <i className="fa fa-usd mylib-sidebar__icon" aria-hidden="true" />
            {finesLoading ? (
              <LoadingPlaceholder width="120px" />
            ) : finesTotal > 0 ? (
              <span className="mylib-sidebar__warning">
                You have {formatCurrency(finesTotal)} in fines.
              </span>
            ) : (
              <span>No fines</span>
            )}
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

          {/* Log Out */}
          <li className="mylib-sidebar__item">
            <i
              className="fa fa-sign-out mylib-sidebar__icon"
              aria-hidden="true"
            />
            <a href="/accounts/logout/" className="mylib-sidebar__link">
              Log Out
            </a>
          </li>

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
                Accounts FAQ
              </a>
            </li>
          )}
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
}

MyAccountSidebar.defaultProps = {
  profile: null,
  profileLoading: false,
  finesTotal: 0,
  finesLoading: false,
  recalledCount: 0,
  accountsFaqUrl: '',
}

export default MyAccountSidebar
