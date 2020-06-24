import React, { useState, useEffect } from 'react'

import {TEIentities} from 'common/types'
import {WithAppContext} from 'common/context/app'

export default function FormWithContext (props) {
  return (
    <WithAppContext>
      <Form {...props}/>
    </WithAppContext>
  )
}

function Form (props) {
  //const conf = props.context.configuration.entities[props.entity.type]
  const entityType = Object.hasOwnProperty.call(TEIentities, props.entity.type) 
    ?TEIentities[props.entity.type]
    :TEIentities['default']
  const categoryOptions = Object.keys(props.context.configuration.taxonomy).map(x => 
    <option key={x} value={x}>{x}</option>)
  const entityOptions = Object.keys(props.context.configuration.entities).map(x => 
    <option key={x} value={x}>{x}</option>)
  const propertyOptions = entityType.properties.map(x => 
    <option key={x} value={x}>{x}</option>)

  const defState = Object.assign({}, {
    locus: 'value',
    cert: 'medium',
    ana: [],
    assertedValue: '',
    match: '',
    desc: ''
  }, props.annotation === undefined ? {} : {
    ...props.annotation,
    ana: props.annotation.ana
      .split(' ')
      .map(x => x.split('#')[1])
  })

  const [form, update] = useState(defState)
  useEffect(() => {
    update(defState)
  }, [Object.hasOwnProperty.call(props, 'annotation')])


  function handleUpdate (key, value) {
    const newForm = Object.assign({}, form)
    newForm[key] = value

    if (key === 'locus') {
      if (value === 'name') {
        newForm.assertedValue = props.entity.type
      } else if (value === 'attribute') {
        newForm.match = entityType.properties[0]
      }
    }

    update(newForm)
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

  return <form className="p-2 rounded" style={{ backgroundColor: 'rgba(0,0,0,.03)' }}>
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
            <option value="attribute">Attribute</option>
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
      <div className={'col ' + (form.locus === 'attribute' ? '' : 'd-none')}>
        <div className="form-group">
          <label htmlFor="attributeName">Attribute</label>
          <select className="form-control form-control-sm"
            value={form.match}
            onChange={e => handleUpdate('match', e.target.value)}
            id="attributeName">
            {propertyOptions}
          </select>
        </div>
      </div>
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
    <div className="row mt-2">
      <div className="col">
        <button type="button"
          onClick={() => props.callback(form)}
          className="btn btn-sm btn-outline-primary">{props.submitText}</button>
      </div>
    </div>
  </form>
}