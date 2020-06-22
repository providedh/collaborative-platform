import React, { useState } from 'react'

import {WithAppContext} from 'common/context/app'
import AnnotateForm from './annotate_form.js'

export default function CreateAnnotationWithContext (props) {
  return (
    <WithAppContext>
      <CreateAnnotation {...props}/>
    </WithAppContext>
  )
}

function authorName(resp, user, authors) {
  if (resp === user) {return 'I'}
  const author = authors.filter(x => x['xml:id'] === resp)[0]
  return `${author?.forename} ${author?.surname}`
}

function CreateAnnotation (props) {
  const [visible, show] = useState(false)

  const annotations = props.context.annotations.filter(x => x.target.slice(1) === props.entity['xml:id'])
  const annotationItems = annotations.map((annotation, i) => 
    <li key={i}>
      <span>{authorName(annotation.resp, props.context.user, props.context.authors)}</span>
      <span> marked with </span>
      <span className="text-primary">{annotation.cert}</span>
      <span> certainty: that the </span>
      <span className="text-primary">{annotation.locus}</span>
      <span className={annotation.match.length === 0 ? 'd-none' : ''}> of <span className="text-primary">{annotation.match}</span></span>
      <span> should be </span>
      <span className="text-primary">{annotation.assertedValue}.</span>
      <span className={annotation.desc.length === 0 ? 'd-none' : 'text-primary'}>
        <br/><b>"</b><i>{annotation.desc}</i><b>"</b>
      </span>
    </li>)

  return <div>
    <span className="d-block">Annotations</span>
    <ul className={(visible === true || annotationItems.length === 0) ? 'd-none' : ''}>
      {annotationItems}
    </ul>
    <div className={visible === false ? 'd-none' : ''}>
      <AnnotateForm entity={props.entity}/>
    </div>
    <button className="btn btn-link"
            type="button" 
            onClick={()=>show(!visible)}
            data-toggle="collapse" 
            data-target="#collapse" 
            aria-expanded="false" 
            aria-controls="collapse">{visible === true ? 'Cancel' : '+ Add annotation'}</button>
  </div>
}