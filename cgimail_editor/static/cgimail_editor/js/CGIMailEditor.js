/* eslint-disable jsx-a11y/label-has-associated-control */
import React, { useState, useEffect } from 'react'
import ReactDOM from 'react-dom/client'
import Select from 'react-select'
import Prism from 'prismjs'
import 'prismjs/components/prism-json'
import PropTypes from 'prop-types'

import schema from '../../../../base/static/base/js/CGIMailFormSchema'
import { Sections } from '../../../../base/static/base/js/CGIMailForm'

// Read data attributes from mount element
const DOM_ELEMENT = document.getElementById('cgimail-editor')
const SURROGATE_API_URL = DOM_ELEMENT.getAttribute('data-surrogate-api')
const GENERATE_API_URL = DOM_ELEMENT.getAttribute('data-generate-api')
const FETCH_DOCS_API_URL = DOM_ELEMENT.getAttribute('data-fetch-docs-api')
const AI_MODEL = DOM_ELEMENT.getAttribute('data-ai-model')
const TEMPLATE = DOM_ELEMENT.getAttribute('data-template') || ''
const SYSTEM_PROMPT = DOM_ELEMENT.getAttribute('data-system-prompt') || ''
const CSRF_TOKEN = DOM_ELEMENT.getAttribute('data-csrf-token')

// Validation using existing schema
const validator = require('is-my-json-valid')

function validateFormJSON(jsonObj) {
  const validate = validator(schema)
  const valid = validate(jsonObj)
  return {
    valid,
    errors: validate.errors || [],
  }
}

// API utilities
async function fetchSurrogates() {
  const response = await fetch(SURROGATE_API_URL, {
    credentials: 'same-origin',
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || 'Failed to fetch surrogates')
  }
  return response.json()
}

async function fetchDocs() {
  const response = await fetch(FETCH_DOCS_API_URL, {
    method: 'POST',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': CSRF_TOKEN,
    },
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || 'Failed to fetch documentation')
  }
  return response.json()
}

async function generateJSON(data) {
  const response = await fetch(GENERATE_API_URL, {
    method: 'POST',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': CSRF_TOKEN,
    },
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || 'Failed to generate JSON')
  }
  return response.json()
}

// Mode Toggle Component
function ModeToggle({ mode, onChange }) {
  return (
    <div className="mode-toggle">
      <div className="btn-group" role="group" aria-label="Mode selection">
        <button
          type="button"
          className={`btn ${mode === 'create' ? 'btn-primary' : 'btn-default'}`}
          onClick={() => onChange('create')}
        >
          Create New
        </button>
        <button
          type="button"
          className={`btn ${mode === 'edit' ? 'btn-primary' : 'btn-default'}`}
          onClick={() => onChange('edit')}
        >
          Edit Existing
        </button>
      </div>
    </div>
  )
}

ModeToggle.propTypes = {
  mode: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
}

// Surrogate Select Component
function SurrogateSelect({ surrogates, value, onChange, isFallback }) {
  const surrogateList = Array.isArray(surrogates) ? surrogates : []
  const options = surrogateList.map(s => ({ value: s, label: s }))

  return (
    <div className="form-group">
      <label htmlFor="surrogate-select">
        Recipient (Surrogate) <abbr title="required">*</abbr>
      </label>
      <Select
        inputId="surrogate-select"
        options={options}
        value={value}
        onChange={onChange}
        placeholder="Search for a surrogate..."
        isSearchable
        className="surrogate-select"
        classNamePrefix="react-select"
      />
      <small className="form-text text-muted">
        Select the email surrogate that will receive form submissions
        {isFallback && (
          <span className="text-warning"> (Using fallback list)</span>
        )}
      </small>
    </div>
  )
}

SurrogateSelect.propTypes = {
  surrogates: PropTypes.arrayOf(PropTypes.string).isRequired,
  value: PropTypes.shape({
    value: PropTypes.string,
    label: PropTypes.string,
  }),
  onChange: PropTypes.func.isRequired,
  isFallback: PropTypes.bool,
}

SurrogateSelect.defaultProps = {
  value: null,
  isFallback: false,
}

// Output Display Component
function OutputDisplay({ json }) {
  const [copied, setCopied] = useState(false)

  // Format JSON once for all uses
  let formattedJSON = json
  try {
    formattedJSON = JSON.stringify(JSON.parse(json), null, 2)
  } catch (e) {
    // Keep original if parsing fails
  }

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(formattedJSON)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      // Fallback for older browsers
      const textarea = document.createElement('textarea')
      textarea.value = formattedJSON
      textarea.style.position = 'fixed'
      textarea.style.opacity = '0'
      document.body.appendChild(textarea)
      textarea.select()
      document.execCommand('copy')
      document.body.removeChild(textarea)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleDownload = () => {
    try {
      const blob = new Blob([formattedJSON], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'cgimail-form.json'
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (err) {
      console.error('Download failed:', err)
    }
  }

  const highlighted = Prism.highlight(formattedJSON, Prism.languages.json, 'json')

  return (
    <div className="output-display">
      <h3>Generated JSON</h3>
      <div className="output-actions">
        <button
          type="button"
          className="btn btn-sm btn-primary"
          onClick={handleCopy}
        >
          {copied ? 'Copied!' : 'Copy to Clipboard'}
        </button>
        <button
          type="button"
          className="btn btn-sm btn-default"
          onClick={handleDownload}
        >
          Download JSON
        </button>
      </div>
      <pre className="language-json">
        {/* eslint-disable-next-line react/no-danger */}
        <code dangerouslySetInnerHTML={{ __html: highlighted }} />
      </pre>
    </div>
  )
}

OutputDisplay.propTypes = {
  json: PropTypes.string.isRequired,
}

// Preview Panel Component
function PreviewPanel({ json }) {
  const [formData, setFormData] = useState(null)
  const [error, setError] = useState(null)
  const [previewState, setPreviewState] = useState({})

  useEffect(() => {
    try {
      const parsed = JSON.parse(json)
      setFormData(parsed)
      setError(null)
    } catch (e) {
      setError('Invalid JSON - cannot render preview')
      setFormData(null)
    }
  }, [json])

  const handleChange = e => {
    const { name, value } = e.target
    setPreviewState(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = e => {
    e.preventDefault()
    alert('This is a preview only. Form submission is disabled.')
    return false
  }

  if (error) {
    return (
      <div className="preview-panel">
        <h3>Form Preview</h3>
        <div className="alert alert-warning">{error}</div>
      </div>
    )
  }

  if (!formData || !formData.form) {
    return null
  }

  const { form } = formData

  return (
    <div className="preview-panel">
      <h3>Form Preview</h3>
      <div className="preview-container">
        <form onSubmit={handleSubmit} className="preview-form">
          {form.hasRequiredFields && (
            <p className="required-intro">
              Required fields are followed by <abbr title="required">*</abbr>
            </p>
          )}
          <Sections
            data={form.sections}
            handleChange={handleChange}
            state={previewState}
          />
          <button type="submit" className="btn btn-primary" disabled>
            Submit (Preview Only)
          </button>
        </form>
      </div>
      <p className="text-muted">
        <small>This is a preview only. Form submission is disabled.</small>
      </p>
    </div>
  )
}

PreviewPanel.propTypes = {
  json: PropTypes.string.isRequired,
}

// Loading Placeholder Component
function LoadingPlaceholder({ type }) {
  return (
    <div className={`loading-placeholder ${type}-placeholder`}>
      <div className="preload">
        <i className="fa fa-spinner fa-pulse fa-3x fa-fw" />
        <span>Generating...</span>
      </div>
    </div>
  )
}

LoadingPlaceholder.propTypes = {
  type: PropTypes.string.isRequired,
}

// Field Reference Component
function FieldReference() {
  return (
    <div className="field-reference">
      <h2>Field Types Reference</h2>
      <ul>
        <li>
          <strong>text</strong> - Single line text input
        </li>
        <li>
          <strong>email</strong> - Email input with validation
        </li>
        <li>
          <strong>textarea</strong> - Multi-line text area
        </li>
        <li>
          <strong>select</strong> - Dropdown with options
        </li>
        <li>
          <strong>hidden</strong> - Hidden field (rcpt, etc.)
        </li>
        <li>
          <strong>checkbox</strong> - Checkbox input
        </li>
        <li>
          <strong>radio</strong> - Radio button group
        </li>
      </ul>
      <h3>Grouping</h3>
      <ul>
        <li>
          <strong>fieldset</strong> - Group with legend
        </li>
        <li>
          <strong>group</strong> - Side-by-side columns
        </li>
      </ul>
      <h3>Common Properties</h3>
      <ul>
        <li>
          <code>required: true</code> - Mark as required
        </li>
        <li>
          <code>placeholder</code> - Placeholder text
        </li>
        <li>
          <code>helpText</code> - Help text below field
        </li>
        <li>
          <code>enabledWhen</code> - Conditional enable
        </li>
        <li>
          <code>disabledWhen</code> - Conditional disable
        </li>
      </ul>
    </div>
  )
}

// Main CGIMailEditor Component
function CGIMailEditor() {
  const [mode, setMode] = useState('create')
  const [surrogates, setSurrogates] = useState([])
  const [isFallback, setIsFallback] = useState(false)
  const [selectedSurrogate, setSelectedSurrogate] = useState(null)
  const [subject, setSubject] = useState('')
  const [description, setDescription] = useState('')
  const [existingJSON, setExistingJSON] = useState('')
  const [generatedJSON, setGeneratedJSON] = useState(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState(null)
  const [validationErrors, setValidationErrors] = useState(null)
  const [documentation, setDocumentation] = useState([])
  const [isLoadingSurrogates, setIsLoadingSurrogates] = useState(true)

  // Load surrogates on mount
  useEffect(() => {
    async function loadSurrogates() {
      try {
        setIsLoadingSurrogates(true)
        const data = await fetchSurrogates()
        setSurrogates(data.surrogates || [])
        setIsFallback(data.fallback || false)
      } catch (err) {
        setError('Failed to load surrogates: ' + err.message)
      } finally {
        setIsLoadingSurrogates(false)
      }
    }
    loadSurrogates()
  }, [])

  // Load documentation on mount
  useEffect(() => {
    async function loadDocs() {
      try {
        const data = await fetchDocs()
        setDocumentation(data.documentation || [])
      } catch (err) {
        console.error('Failed to load documentation:', err)
      }
    }
    loadDocs()
  }, [])

  // When in edit mode and JSON is generated, copy to existingJSON and clear generatedJSON
  // This allows subject/surrogate edits to update the preview after generation
  useEffect(() => {
    if (mode === 'edit' && generatedJSON) {
      setExistingJSON(generatedJSON)
      // Use setTimeout to avoid clearing before render
      setTimeout(() => setGeneratedJSON(null), 0)
    }
  }, [mode, generatedJSON])

  // Clear generatedJSON when switching modes
  useEffect(() => {
    setGeneratedJSON(null)
  }, [mode])

  // In edit mode, sync form fields from JSON when first entering edit mode
  // (This populates fields when switching modes or loading initial JSON)
  useEffect(() => {
    if (mode === 'edit' && existingJSON) {
      try {
        const parsed = JSON.parse(existingJSON)
        const hiddenElements = parsed.form?.sections?.[0]?.elements

        if (Array.isArray(hiddenElements)) {
          // Read rcpt value from JSON and update surrogate dropdown
          const rcptField = hiddenElements.find(el => el.name === 'rcpt')
          if (rcptField?.value) {
            const currentSurrogate = selectedSurrogate?.value
            if (currentSurrogate !== rcptField.value) {
              const matchingSurrogate = surrogates.find(s => s === rcptField.value)
              if (matchingSurrogate) {
                setSelectedSurrogate({ value: matchingSurrogate, label: matchingSurrogate })
              }
            }
          }

          // Read subject from JSON and update subject field
          const subjectField = hiddenElements.find(el => el.name === 'subject')
          if (subjectField?.value && subject !== subjectField.value) {
            setSubject(subjectField.value)
          }
        }
      } catch (e) {
        // Invalid JSON, ignore silently
      }
    }
    // Only run when switching to edit mode, not on every JSON change
  }, [mode])

  // In edit mode, sync JSON from form fields when fields change
  useEffect(() => {
    if (mode === 'edit' && existingJSON) {
      try {
        const parsed = JSON.parse(existingJSON)
        let updated = false

        // Get hidden section elements
        const hiddenElements = parsed.form?.sections?.[0]?.elements
        if (Array.isArray(hiddenElements)) {
          // Update rcpt field (surrogate)
          if (selectedSurrogate) {
            const rcptField = hiddenElements.find(el => el.name === 'rcpt')
            if (rcptField && rcptField.value !== selectedSurrogate.value) {
              rcptField.value = selectedSurrogate.value
              updated = true
            }
          }

          // Update subject field
          if (subject) {
            const subjectField = hiddenElements.find(el => el.name === 'subject')
            if (subjectField && subjectField.value !== subject) {
              subjectField.value = subject
              updated = true
            }
          }
        }

        // Only update state if something changed (prevents infinite loop)
        if (updated) {
          setExistingJSON(JSON.stringify(parsed, null, 2))
        }
      } catch (e) {
        // Invalid JSON, ignore silently
      }
    }
  }, [mode, selectedSurrogate, subject, existingJSON])

  const handleGenerate = async () => {
    setIsGenerating(true)
    setError(null)
    setValidationErrors(null)
    setGeneratedJSON(null)

    try {
      const result = await generateJSON({
        mode,
        surrogate: selectedSurrogate?.value || '',
        subject,
        description,
        existing_json: mode === 'edit' ? existingJSON : null,
        documentation,
        system_prompt: SYSTEM_PROMPT,
        model: AI_MODEL,
      })

      if (result.success) {
        // Try to parse and validate
        try {
          const jsonObj = JSON.parse(result.json)
          const validation = validateFormJSON(jsonObj)

          if (validation.valid) {
            setGeneratedJSON(result.json)
          } else {
            setValidationErrors(validation.errors)
            setGeneratedJSON(result.json) // Still show JSON for debugging
            setError(
              'Generated JSON failed validation. You may need to modify it manually.'
            )
          }
        } catch (parseError) {
          setError('Generated response is not valid JSON: ' + parseError.message)
          setGeneratedJSON(result.json) // Show raw response for debugging
        }
      } else {
        setError(result.error || 'Generation failed')
      }
    } catch (err) {
      setError('Error: ' + err.message)
    } finally {
      setIsGenerating(false)
    }
  }

  const loadTemplate = () => {
    setDescription(TEMPLATE)
    setMode('create')
  }

  const canGenerate = () => {
    if (mode === 'create') {
      return selectedSurrogate && subject && description
    }
    return existingJSON && description
  }

  const getPlaceholderText = () => {
    if (mode === 'create') {
      return 'Describe the form fields you want. Include field types, labels, whether fields are required, and any conditional logic...'
    }
    return 'Describe what changes you want to make to the existing form JSON...'
  }

  // Determine which JSON to display in preview/output
  // In edit mode, show existing JSON immediately; after generation, show generated JSON
  const jsonToDisplay = generatedJSON || (mode === 'edit' && existingJSON ? existingJSON : null)

  return (
    <div className="cgimail-editor">
      {/* Row 1: Form fields and Field Reference */}
      <div className="editor-main">
        <ModeToggle mode={mode} onChange={setMode} />

        <div className="editor-form">
          <SurrogateSelect
            surrogates={surrogates}
            value={selectedSurrogate}
            onChange={setSelectedSurrogate}
            isFallback={isFallback}
          />

          {isLoadingSurrogates && (
            <div className="text-muted">Loading surrogates...</div>
          )}

          <div className="form-group">
            <label htmlFor="subject">
              Subject Line <abbr title="required">*</abbr>
            </label>
            <input
              type="text"
              id="subject"
              className="form-control"
              value={subject}
              onChange={e => setSubject(e.target.value)}
              placeholder="e.g., Ask a Librarian Appointment Request"
            />
            <small className="form-text text-muted">
              Subject line for emails sent by this form
            </small>
          </div>

          {mode === 'edit' && (
            <div className="form-group">
              <label htmlFor="existing-json">
                Existing JSON <abbr title="required">*</abbr>
              </label>
              <textarea
                id="existing-json"
                className="form-control code-textarea"
                value={existingJSON}
                onChange={e => setExistingJSON(e.target.value)}
                placeholder="Paste your existing CGIMail form JSON here..."
                rows={8}
              />
            </div>
          )}

          <div className="form-group">
            <label htmlFor="description">
              {mode === 'create' ? 'Form Description' : 'Requested Changes'}{' '}
              <abbr title="required">*</abbr>
            </label>
            <textarea
              id="description"
              className="form-control"
              value={description}
              onChange={e => setDescription(e.target.value)}
              placeholder={getPlaceholderText()}
              rows={8}
            />
          </div>

          <div className="editor-actions">
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleGenerate}
              disabled={isGenerating || !canGenerate()}
            >
              {isGenerating ? 'Generating...' : 'Generate Form JSON'}
            </button>

            {TEMPLATE && (
              <button
                type="button"
                className="btn btn-default"
                onClick={loadTemplate}
              >
                Load Example
              </button>
            )}
          </div>

          {error && (
            <div className="alert alert-danger" role="alert">
              {error}
              {validationErrors && validationErrors.length > 0 && (
                <ul className="validation-errors">
                  {validationErrors.map((err, idx) => (
                    <li key={err.field || `error-${idx}`}>
                      {err.field}: {err.message}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>
      </div>

      <aside className="editor-sidebar">
        <FieldReference />
      </aside>

      {/* Row 2: Output and Preview */}
      <div className="output-column">
        {isGenerating ? (
          <LoadingPlaceholder type="output" />
        ) : jsonToDisplay ? (
          <OutputDisplay json={jsonToDisplay} />
        ) : null}
      </div>

      <div className="preview-column">
        {isGenerating ? (
          <LoadingPlaceholder type="preview" />
        ) : jsonToDisplay ? (
          <PreviewPanel json={jsonToDisplay} />
        ) : null}
      </div>
    </div>
  )
}

// Mount the component
const root = ReactDOM.createRoot(DOM_ELEMENT)
root.render(<CGIMailEditor />)
