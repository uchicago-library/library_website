import React from 'react';
import ReactDOM from 'react-dom';
import renderHTML from 'react-render-html';
import PropTypes from 'prop-types';

import {
  Input, TextArea, Select, Label, Legend,
} from './index';

import schema from './CGIMailFormSchema';

const DOM_ELEMENT = document.getElementById('cgi-mail-form');
const FORM_JSON = JSON.parse(DOM_ELEMENT.getAttribute('data-json'));
const THANK_YOU_TXT = DOM_ELEMENT.getAttribute('data-thank-you') || '';
const QUERYSTRING = window.location.search;
const URLPARAMS = new URLSearchParams(QUERYSTRING);

const validator = require('is-my-json-valid');

function getType(e) {
  if (e.type === 'text' || e.type === 'email' || e.type === 'hidden') {
    return 'input';
  }
  if (e.type === 'select') {
    return 'select';
  }
  if (e.type === 'textarea') {
    return 'textarea';
  }
  if (e.type === 'checkbox') {
    return 'checkbox';
  }
  return 'unknown';
}

function getLabel(e) {
  const id = e.name || null;
  const required = e.required || null;
  const labelText = e.label || null;
  if (labelText) {
    return <Label htmlFor={id} text={labelText} required={required} />;
  }
  return '';
}

function getLegend(e) {
  const text = e.legend || null;
  if (text) {
    return <Legend text={text} />;
  }
  return '';
}

// TODO - This should be passed down from the container and update state
function defaultFieldMappings(e, state) {
  if (e.map && !(e.name in state)) {
    const src = e.map.src || null;
    if (src === 'itemServlet') {
      if (Array.isArray(e.map.fields)) {
        return e.map.fields.map(v => state.itemInfo[v]).join(' ');
      }
      return state.itemInfo[e.map.fields];
    }
    if (src === 'GET') {
      if (Array.isArray(e.map.fields)) {
        return e.map.fields.map(v => URLPARAMS.get(v)).join(' ');
      }
      return URLPARAMS.get(e.map.fields) || null;
    }
  }
  return '';
}

const ErrorMessage = (props) => {
  const { field, msg } = props;
  return (
    <p>
      {field}
      {' '}
      {msg}
    </p>
  );
};

const InvalidJSON = (props) => {
  const { errors } = props;
  return (
    <div className="alert alert-danger" role="alert">
      <h2>There is a problem with the form JSON</h2>
      {errors.map(e => <ErrorMessage field={e.field} msg={e.message} />)}
    </div>
  );
};

const buildField = (elm, state, handleChange) => {
  const id = elm.name || null;
  const value = elm.value || state[id] || defaultFieldMappings(elm, state) || null;
  const type = elm.type || null;
  const name = elm.name || null;
  const placeholder = elm.placeholder || null;
  const required = elm.required || null;
  const options = elm.options || null;

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
          onChange={(e) => {
            handleChange(e);
          }}
        />
      </div>
    );
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
          onChange={(e) => {
            handleChange(e);
          }}
          options={options}
        />
      </div>
    );
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
          onChange={(e) => {
            handleChange(e);
          }}
        />
      </div>
    );
  }
  if (getType(elm) === 'checkbox') {
    return (
      <div className="form-group">
        {getLabel(elm)}
        <input id={id} type={type} name={name} required={required} />
      </div>
    );
  }
  return '[Unknown Field Type]';
};

const FormElements = (props) => {
  const { elements, handleChange, state } = props;
  return elements.map((elm) => {
    if (Object.keys(elm).includes('fieldset')) {
      return (
        <fieldset>
          {getLegend(elm.fieldset)}
          {elm.fieldset.elements.map(e => buildField(e, state, handleChange))}
        </fieldset>
      );
    }
    if (Object.keys(elm).includes('group')) {
      const len = elm.group.elements.length;
      const colNum = 12 / len;
      const divClassName = `col-sm-${String(colNum)}`;
      return (
        <div className="form-group row">
          {elm.group.elements.map(e => (
            <div className={divClassName}>
              {buildField(e, state, handleChange)}
            </div>
          ))}
        </div>
      );
    }
    return buildField(elm, state, handleChange);
  });
};

const SectionTitle = (props) => {
  const { title } = props;
  return <h2>{title}</h2> || '';
};

const Section = (props) => {
  const {
    title, elements, handleChange, state, hidden,
  } = props;
  if (hidden) {
    return (
      <FormElements elements={elements} handleChange={null} state={state} />
    );
  }
  return (
    <section>
      <SectionTitle title={title} />
      <FormElements
        elements={elements}
        handleChange={handleChange}
        state={state}
      />
    </section>
  );
};

const Sections = (props) => {
  const { data, handleChange, state } = props;
  return data.map(d => (
    <Section
      title={d.title}
      elements={d.elements}
      handleChange={handleChange}
      state={state}
      hidden={d.hidden || null}
    />
  ));
};

class FormContainer extends React.Component {
  constructor(props) {
    super(props);
    this.handleChange = this.handleChange.bind(this);
    this.state = {
      submitted: false,
      response: false,
      itemInfo: false,
      isLoadingItemInfo: true,
    };
  }

  handleRedirect = (res) => {
    if (res.status === 200) {
      res.text().then((body) => {
        this.setState({
          submitted: true,
          response: body,
        });
      });
    } else {
      // TODO - Failure message
    }
  }

  componentDidMount() {
    let itemServlet = 'http://forms2.lib.uchicago.edu/lib/searchform/itemServlet.php?format=json'; // TODO - make configurable
    const bib = URLPARAMS.get('bib') || null;
    const barcode = URLPARAMS.get('barcode') || null;
    let itemInfo = false;
    if (bib) {
      itemInfo = true;
      itemServlet = `${itemServlet}&bib=${bib}`;
    }
    if (barcode) {
      itemInfo = true;
      itemServlet = `${itemServlet}&barcode=${barcode}`;
    }
    if (itemInfo) {
      return fetch(`${itemServlet}`)
        .then(res => res.json())
        .then((res) => {
          this.setState({
            itemInfo: res,
            isLoadingItemInfo: false,
          });
        })
        .catch((error) => {
          console.error(error); // eslint-disable-line no-console
        });
    }
  }

  handleSubmit = (e) => {
    e.preventDefault();
    const form = document.forms[0];
    const data = new FormData(form);
    fetch('https://www.lib.uchicago.edu/cgi-bin/cgimail/cgimail', {
      // TODO - make url configurable
      method: 'POST',
      body: data,
    }).then(this.handleRedirect);
  }

  handleChange(e) {
    const { value } = e.target;
    this.setState({
      [e.target.name]: value,
    });
  }

  render() {
    const validate = validator(schema);
    validate(FORM_JSON);
    if (validate.errors) {
      return <InvalidJSON errors={validate.errors} />;
    }
    const { submitted, response } = this.state;
    const { form } = FORM_JSON;
    const formId = form.id || null;

    if (submitted && response) {
      return (
        <div className="form-container">
          {renderHTML(THANK_YOU_TXT)}
          {renderHTML(response)}
        </div>
      );
    }
    return (
      <div className="form-container">
        <form id={formId} onSubmit={this.handleSubmit}>
          <Sections
            data={form.sections}
            handleChange={this.handleChange}
            state={this.state}
          />
          <input type="submit" value="Submit" />
        </form>
      </div>
    );
  }
}

ReactDOM.render(<FormContainer />, DOM_ELEMENT);
