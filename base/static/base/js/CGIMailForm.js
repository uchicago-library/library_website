import React from 'react'
import ReactDOM from 'react-dom/client'
import htmr from 'htmr'
import PropTypes from 'prop-types'

import {
  Input,
  TextArea,
  Select,
  Label,
  Legend,
  RequiredFieldsText,
  FormFieldHelpText,
} from './index'

import schema from './CGIMailFormSchema'

const DOM_ELEMENT = document.getElementById('cgi-mail-form')
const CGI_MAIL_SERVICE = DOM_ELEMENT.getAttribute('data-cgi-mail') || ''
const ITEM_SERVLET = DOM_ELEMENT.getAttribute('data-item-servlet') || ''
const SPRINGSHARE_PP = DOM_ELEMENT.getAttribute('data-springshare-pp') || ''
const FORM_JSON = JSON.parse(DOM_ELEMENT.getAttribute('data-json'))
const THANK_YOU_TXT = DOM_ELEMENT.getAttribute('data-thank-you') || ''
const QUERYSTRING = window.location.search
const URLPARAMS = new URLSearchParams(QUERYSTRING)

const validator = require('is-my-json-valid')

function getType(e) {
  if (e.type === 'text' || e.type === 'email' || e.type === 'hidden') {
    return 'input'
  }
  if (e.type === 'select') {
    return 'select'
  }
  if (e.type === 'textarea') {
    return 'textarea'
  }
  if (e.type === 'checkbox') {
    return 'checkbox'
  }
  if (e.type === 'radio') {
    return 'radio'
  }
  return 'unknown'
}

function getLabel(e) {
  const id = e.id || e.name || null
  const required = e.required || null
  const labelText = e.label || null
  if (labelText) {
    return <Label htmlFor={id} text={htmr(labelText)} required={required} />
  }
  return ''
}

function getHelpText(e) {
  const helpText = e.helpText || null
  if (helpText) {
    const id = e.helpText.id || null
    const text = e.helpText.text || null
    if (id && text) {
      return [id, <FormFieldHelpText id={id} text={text} />]
    }
  }
  return [null, null]
}

function getLegend(e) {
  const text = e.legend || null
  if (text) {
    return <Legend text={text} />
  }
  return ''
}

// TODO - This should be passed down from the container and update state
function defaultFieldMappings(e, state) {
  if (e.map && !(e.name in state)) {
    const src = e.map.src || null
    if (src === 'itemServlet') {
      if (Array.isArray(e.map.fields)) {
        return e.map.fields.map(v => state.itemInfo[v]).join(' ')
      }
      return state.itemInfo[e.map.fields]
    }
    if (src === 'GET') {
      if (Array.isArray(e.map.fields)) {
        return e.map.fields.map(v => URLPARAMS.get(v)).join(' ')
      }
      return URLPARAMS.get(e.map.fields) || null
    }
  }
  return ''
}

const SpringsharePPText = () => (
  <p className="springshare-pp">
    This form is powered by Springshare and complies with its{' '}
    <a href={SPRINGSHARE_PP}>privacy policy</a>.
  </p>
)

const ErrorMessage = props => {
  const { field, msg } = props
  return (
    <p>
      {field} {msg}
    </p>
  )
}

ErrorMessage.propTypes = {
  field: PropTypes.string.isRequired,
  msg: PropTypes.string.isRequired,
}

const InvalidJSON = props => {
  const { errors } = props
  return (
    <div className="alert alert-danger" role="alert">
      <h2>There is a problem with the form JSON</h2>
      {errors.map(e => (
        <ErrorMessage field={e.field} msg={e.message} />
      ))}
    </div>
  )
}

InvalidJSON.propTypes = {
  errors: PropTypes.arrayOf(PropTypes.object).isRequired,
}

const buildField = (elm, state, handleChange) => {
  const id = elm.id || elm.name || null
  const value =
    elm.value || state[id] || defaultFieldMappings(elm, state) || null
  const type = elm.type || null
  const name = elm.name || null
  const placeholder = elm.placeholder || null
  const required = elm.required || null
  const options = elm.options || null
  const htl = getHelpText(elm)
  const ariaDescribedBy = htl[0]
  const helpText = htl[1]

  if (getType(elm) === 'input') {
    return (
      <div className="form-group">
        {getLabel(elm)}
        <Input
          id={id}
          value={value}
          type={type}
          name={name}
          placeholder={placeholder}
          required={required}
          ariaDescribedBy={ariaDescribedBy}
          onChange={e => {
            handleChange(e)
          }}
        />
        {helpText}
      </div>
    )
  }
  if (getType(elm) === 'select') {
    return (
      <div className="form-group">
        {getLabel(elm)}
        <Select
          id={id}
          value={value}
          type={type}
          name={name}
          placeholder={placeholder}
          required={required}
          ariaDescribedBy={ariaDescribedBy}
          onChange={e => {
            handleChange(e)
          }}
          options={options}
        />
        {helpText}
      </div>
    )
  }
  if (getType(elm) === 'textarea') {
    return (
      <div className="form-group">
        {getLabel(elm)}
        <TextArea
          id={id}
          type={type}
          name={name}
          required={required}
          value={value}
          ariaDescribedBy={ariaDescribedBy}
          onChange={e => {
            handleChange(e)
          }}
        />
        {helpText}
      </div>
    )
  }
  if (getType(elm) === 'checkbox') {
    return (
      <div className="form-check">
        {getLabel(elm)}
        <input
          id={id}
          type={type}
          name={name}
          required={required}
          value={value}
        />
      </div>
    )
  }
  if (getType(elm) === 'radio') {
    return (
      <div className="form-check">
        {getLabel(elm)}
        <input
          id={id}
          type={type}
          name={name}
          required={required}
          value={value}
        />
      </div>
    )
  }
  return '[Unknown Field Type]'
}

const buildGroup = (elm, state, handleChange) => {
  const len = elm.group.elements.length
  const colNum = 12 / len
  const divClassName = `col-sm-${String(colNum)}`
  return (
    <div className="form-group row">
      {elm.group.elements.map(e => (
        <div className={divClassName}>{buildField(e, state, handleChange)}</div>
      ))}
    </div>
  )
}

const FormElements = props => {
  const { elements, handleChange, state } = props
  return elements.map(elm => {
    if (Object.keys(elm).includes('fieldset')) {
      return (
        <fieldset>
          {getLegend(elm.fieldset)}
          {elm.fieldset.elements.map(e =>
            Object.keys(e).includes('group')
              ? buildGroup(e, state, handleChange)
              : buildField(e, state, handleChange),
          )}
        </fieldset>
      )
    }
    if (Object.keys(elm).includes('group')) {
      return buildGroup(elm, state, handleChange)
    }
    return buildField(elm, state, handleChange)
  })
}

const SectionTitle = props => {
  const { title } = props
  return <h2>{title}</h2> || ''
}

SectionTitle.propTypes = {
  title: PropTypes.string.isRequired,
}

const Section = props => {
  const { title, description, elements, handleChange, state, hidden } = props
  if (hidden) {
    return (
      <FormElements elements={elements} handleChange={null} state={state} />
    )
  }
  return (
    <section>
      {title ? <SectionTitle title={title} /> : ''}
      {description ? <p>{description}</p> : ''}
      <FormElements
        elements={elements}
        handleChange={handleChange}
        state={state}
      />
    </section>
  )
}

Section.defaultProps = {
  title: null,
  description: null,
  hidden: null,
}

Section.propTypes = {
  title: PropTypes.string,
  description: PropTypes.string,
  elements: PropTypes.arrayOf(PropTypes.object).isRequired,
  handleChange: PropTypes.func.isRequired,
  state: PropTypes.object.isRequired, // eslint-disable-line react/forbid-prop-types
  hidden: PropTypes.bool,
}

const Sections = props => {
  const { data, handleChange, state } = props
  return data.map(d => (
    <Section
      title={d.title}
      description={d.description}
      elements={d.elements}
      handleChange={handleChange}
      state={state}
      hidden={d.hidden || null}
    />
  ))
}

const LoadingItemInfo = props => {
  const { loading } = props
  if (loading === true) {
    return <p className="text-success">Retrieving item information...</p>
  }
  return ''
}

class FormContainer extends React.Component {
  constructor(props) {
    super(props)
    this.handleChange = this.handleChange.bind(this)
    this.state = {
      submitted: false,
      response: false,
      itemInfo: false, // eslint-disable-line react/no-unused-state
      isLoadingItemInfo: false,
    }
  }

  componentDidMount() {
    let itemServlet = ITEM_SERVLET
    const bib = URLPARAMS.get('bib') || null
    const barcode = URLPARAMS.get('barcode') || null
    let itemInfo = false
    if (bib || barcode) {
      itemInfo = true
      this.setState({
        isLoadingItemInfo: true,
      })
      if (bib) {
        itemServlet = `${itemServlet}&bib=${bib}`
      }
      if (barcode) {
        itemServlet = `${itemServlet}&barcode=${barcode}`
      }
    }
    if (itemInfo) {
      return fetch(`${itemServlet}`)
        .then(res => res.json())
        .then(res => {
          this.setState({
            itemInfo: res, // eslint-disable-line react/no-unused-state
            isLoadingItemInfo: false,
          })
        })
        .catch(error => {
          console.error(error) // eslint-disable-line no-console
        })
    }
    return null
  }

  handleRedirect = res => {
    if (res.status === 200) {
      res.text().then(body => {
        this.setState({
          submitted: true,
          response: body,
        })
      })
    } else {
      // TODO - Failure message
    }
  }

  handleSubmit = e => {
    e.preventDefault()
    const form = document.forms.cgimail
    const data = new FormData(form)
    fetch(CGI_MAIL_SERVICE, {
      method: 'POST',
      body: data,
    }).then(this.handleRedirect)
  }

  handleChange(e) {
    const { value } = e.target
    this.setState({
      [e.target.name]: value,
    })
  }

  render() {
    const validate = validator(schema)
    validate(FORM_JSON)
    if (validate.errors) {
      return <InvalidJSON errors={validate.errors} />
    }
    const { submitted, response, isLoadingItemInfo } = this.state
    const { form } = FORM_JSON
    const formId = form.id || null
    const hasRequiredFields = form.hasRequiredFields || null
    const hasSpringsharePP = form.hasSpringsharePP || null

    if (submitted && response) {
      return (
        <div className="form-container">
          <div className="ty-message">{htmr(THANK_YOU_TXT)}</div>

          <div className="cgi-message">{htmr(response)}</div>
        </div>
      )
    }
    return (
      <div className="form-container">
        {hasRequiredFields ? <RequiredFieldsText /> : ''}
        <LoadingItemInfo loading={isLoadingItemInfo} />
        <form id={formId} name="cgimail" onSubmit={this.handleSubmit}>
          <Sections
            data={form.sections}
            handleChange={this.handleChange}
            state={this.state}
          />
          <input type="submit" value="Submit" />
        </form>
        {hasSpringsharePP ? <SpringsharePPText /> : ''}
      </div>
    )
  }
}

const root = ReactDOM.createRoot(DOM_ELEMENT)
root.render(<FormContainer />)
