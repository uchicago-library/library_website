import React from 'react'
import ReactDOM from 'react-dom'

function Welcome(props) {
  return <h2>Mr. Hello {props.name}</h2>;
}

const element = <Welcome name="World" />;
ReactDOM.render(
  element,
  document.getElementById('news-feed')
);
