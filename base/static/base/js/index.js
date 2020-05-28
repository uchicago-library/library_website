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

const Legend = (props) => {
  const { text } = props;
  return <legend>{text}</legend>;
};

export {
  Input, TextArea, Select, Label, Legend,
};
