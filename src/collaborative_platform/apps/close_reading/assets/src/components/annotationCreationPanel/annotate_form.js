import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'

import { TEIentities } from 'common/types'
import { WithAppContext } from 'common/context/app'

export default function FormWithContext (props) {
  return (
    <WithAppContext>
      <Form {...props}/>
    </WithAppContext>
  )
}

function Form (props) {
  // const conf = props.context.configuration.entities[props.entity.type]
  const categoryOptions = Object.keys(props.context.configuration.taxonomy).map(x =>
    <option key={x} value={x}>{x}</option>)
  const entityOptions = Object.keys(props.context.configuration.entities)
    .filter(x => x !== 'text fragment')
    .map(x => <option key={x} value={x}>{x}</option>)

  const defState = {
    locus: 'value',
    cert: 'medium',
    ana: [],
    assertedValue: '',
    match: '',
    desc: ''
  }

  const [form, update] = useState(defState)
  useEffect(() => props.onChange(form))

  function handleUpdate (key, value) {
    const newForm = Object.assign({}, form)
    newForm[key] = value

    update(newForm)
    props.onChange(newForm)
  }

  let assertedValueInput = <div className="col">
    <label htmlFor="assertedValue">Value</label>
    <input className="form-control form-control-sm"
      type="text"
      value={form.assertedValue}
      onChange={e => handleUpdate('assertedValue', e.target.value)}
      id="assertedValue"/>
  </div>

  if (form.locus === 'name') {
    assertedValueInput = <div className="col">
      <div className="form-group">
        <label htmlFor="assertedValue">Asserted value</label>
        <select className="form-control form-control-sm"
          value={form.assertedValue}
          onChange={e => handleUpdate('assertedValue', e.target.value)}
          id="assertedValue">
          {entityOptions}
        </select>
      </div>
    </div>
  }

  return <React.Fragment>
    <div className="row">
      <div className="col">
        <div className="form-group">
          <label htmlFor="locus">Target</label>
          <select className="form-control form-control-sm"
            id="locus"
            value={form.locus}
            onChange={e => handleUpdate('locus', e.target.value)}>
            <option value="name">Tag name</option>
            <option value="value">Value</option>
          </select>
        </div>
      </div>
      <div className="col">
        <div className="form-group">
          <label htmlFor="certainty">Certainty level</label>
          <select className="form-control form-control-sm"
            id="certainty"
            value={form.cert}
            onChange={e => handleUpdate('cert', e.target.value)}>
            <option value="very low">Very low</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="very high">Very high</option>
          </select>
        </div>
      </div>
      <div className="col">
        <div className="form-group">
          <label htmlFor="category">Categories</label>
          <select multiple
            className="form-control form-control-sm"
            id="category"
            value={form.ana}
            onChange={e => handleUpdate('ana', [...e.target.selectedOptions].map(x => x.value))}>
            {categoryOptions}
          </select>
        </div>
      </div>
    </div>
    <div className="row">
      {assertedValueInput}
    </div>
    <div className="row">
      <div className="col">
        <label htmlFor="description">Description</label>
        <input className="form-control form-control-sm"
          type="text"
          onChange={e => handleUpdate('desc', e.target.value)}
          value={form.desc}
          id="description"/>
      </div>
    </div>
  </React.Fragment>
}

Form.propTypes = {
  submitText: PropTypes.string,
  callback: PropTypes.func,
  entity: PropTypes.string,
  context: PropTypes.shape({
    user: PropTypes.string,
    authors: PropTypes.array,
    annotations: PropTypes.array,
    entities: PropTypes.arrayOf(PropTypes.object),
    configuration: PropTypes.object
  }),
  onChange: PropTypes.func
}
