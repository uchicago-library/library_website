/**
 * DownloadItem - A single electronic copy ready for download.
 */
import React from 'react'
import PropTypes from 'prop-types'
import { formatDate } from '../hooks'

function DownloadItem({ copy }) {
  const { articleTitle, sourceTitle, downloadUrl, dueDate } = copy

  return (
    <div className="mylib-item">
      <div className="mylib-item__title">{articleTitle || 'Untitled'}</div>
      {sourceTitle && <div className="mylib-item__source">{sourceTitle}</div>}
      {dueDate && (
        <div className="mylib-item__available-until">
          Available until {formatDate(dueDate)}
        </div>
      )}
      {downloadUrl && (
        <a
          href={downloadUrl}
          className="mylib-item__download-link"
          target="_blank"
          rel="noopener noreferrer"
        >
          Download PDF
        </a>
      )}
    </div>
  )
}

DownloadItem.propTypes = {
  copy: PropTypes.shape({
    id: PropTypes.string.isRequired,
    articleTitle: PropTypes.string,
    sourceTitle: PropTypes.string,
    downloadUrl: PropTypes.string,
    dueDate: PropTypes.string,
  }).isRequired,
}

export default DownloadItem
