/* Global React components go here. */

import React from 'react';
import PropTypes from 'prop-types';

const Input = (props) => {
  const {
    id, value, onChange, type, name, placeholder, required,
  } = props;
  return (
    <input
      id={id}
      type={type}
      onChange={onChange}
      name={name}
      placeholder={placeholder}
      value={value}
      required={required}
      className="form-control"
    />
  );
};

Input.defaultProps = {
  id: null,
  value: null,
  onChange: null,
  type: null,
  name: null,
  placeholder: null,
  required: null,
};

Input.propTypes = {
  id: PropTypes.string,
  value: PropTypes.string,
  onChange: PropTypes.func,
  type: PropTypes.string,
  name: PropTypes.string,
  placeholder: PropTypes.string,
  required: PropTypes.string,
};

const TextArea = (props) => {
  const {
    id, type, name, required, value, onChange,
  } = props;
  return (
    <textarea
      id={id}
      className="form-control"
      type={type}
      onChange={onChange}
      name={name}
      required={required}
      value={value}
    />
  );
};

TextArea.defaultProps = {
  id: null,
  value: null,
  onChange: null,
  type: null,
  name: null,
  required: null,
};

TextArea.propTypes = {
  id: PropTypes.string,
  value: PropTypes.string,
  onChange: PropTypes.func,
  type: PropTypes.string,
  name: PropTypes.string,
  required: PropTypes.string,
};

const Option = (props) => {
  const {
    disabled, selected, value, text,
  } = props;
  return (
    <option disabled={disabled} selected={selected} value={value}>
      {text}
    </option>
  );
};

Option.defaultProps = {
  disabled: null,
  selected: null,
  value: null,
  text: null,
};

Option.propTypes = {
  disabled: PropTypes.bool,
  selected: PropTypes.bool,
  value: PropTypes.string,
  text: PropTypes.string,
};

const makeOption = (elm) => {
  const disabled = elm.disabled || null;
  const value = elm.value || '';
  const selected = elm.selected || null;
  const text = elm.text || null;
  return (
    <Option disabled={disabled} value={value} selected={selected} text={text} />
  );
};

const Select = (props) => {
  const {
    id, value, onChange, type, name, required, options,
  } = props;
  return (
    <select
      className="form-control"
      id={id}
      type={type}
      onChange={onChange}
      name={name}
      value={value}
      required={required}
    >
      {options.map(e => makeOption(e))}
    </select>
  );
};

Select.defaultProps = {
  id: null,
  value: null,
  onChange: null,
  type: null,
  name: null,
  required: null,
};

Select.propTypes = {
  id: PropTypes.string,
  value: PropTypes.string,
  onChange: PropTypes.func,
  type: PropTypes.string,
  name: PropTypes.string,
  required: PropTypes.string,
  options: PropTypes.arrayOf(PropTypes.object).isRequired,
};

const Label = (props) => {
  const { htmlFor, text, required } = props;
  if (required) {
    return (
      <label htmlFor={htmlFor}>
        {text}
        {' '}
        <abbr title="required">*</abbr>
      </label>
    );
  }
  return <label htmlFor={htmlFor}>{text}</label>;
};

Label.defaultProps = {
  required: null,
};

Label.propTypes = {
  htmlFor: PropTypes.string.isRequired,
  text: PropTypes.string.isRequired,
  required: PropTypes.bool,
};

const Legend = (props) => {
  const { text } = props;
  return <legend>{text}</legend>;
};

Legend.propTypes = {
  text: PropTypes.string.isRequired,
};

const RequiredFieldsText = () => (
  <p class="required-intro">
    Required fields are followed by
    {' '}
    <abbr title="required">*</abbr>
  </p>
);

export {
  Input, TextArea, Select, Label, Legend, RequiredFieldsText,
};
