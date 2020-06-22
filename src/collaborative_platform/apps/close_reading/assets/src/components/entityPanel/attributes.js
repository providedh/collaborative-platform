import React, { useState } from 'react'

import {WithAppContext} from 'common/context/app'

export default function CreateAttributeWithContext (props) {
  return (
    <WithAppContext>
      <CreateAttribute {...props}/>
    </WithAppContext>
  )
}

function CreateAttribute (props) {
  const [visible, show] = useState(false)

  const entityConf = props.context.configuration.entities[props.entity.type]
  if (! Object.hasOwnProperty.call(entityConf, 'properties')) { return '' }

  const attributeItems = props.entity.properties.map((attribute, i) => 
    <li key={i}>
      <span>{attribute.name} : </span>
      <span> {attribute.value}</span>
      <span className={attribute.saved === false?'text-danger':'d-none'}> (not saved)</span>
    </li>)

  const presentAttributes = new Set(props.entity.properties.map(x => x.name))
  const freeAttributes = entityConf.properties
    .filter(x => !presentAttributes.has(x))
  const attributeOptions = freeAttributes.map(x => <option key={x} value={x}>{x}</option>)
  
  return <div>
    <span>Attributes</span>
    <ul className="mb-1">
      {attributeItems}
    </ul>
    <div className={freeAttributes.length === 0 ? 'd-none' : ''}>
    <div className={visible === true ? 'd-none' : ''}>
      <button type="button" className="btn btn-link" onClick={()=>show(true)}>+ Add Attribute</button>
      </div>
      <div className={visible === false ? 'd-none' : ''}>
        <form>
          <div className="row">
            <div className="col">
              <div className="form-group">
                <label htmlFor="attribute">Attribute</label>
                <select className="form-control" id="attribute">
                  {attributeOptions}
                </select>
              </div>
            </div>  
            <div className="col">
              <label htmlFor="value">Value</label>
              <input type="text" className="form-control" id="value" placeholder="Attribute value ..."/>
            </div>      
          </div>
        </form>
      </div>
    </div>
    <hr className="mt-0"/>
  </div>
}