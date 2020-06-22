import React from "react";
import { render } from "react-dom";

import { App } from 'components/app'
import defaultTaxonomy from './default_taxonomy.js'

const app_config = {
  projectId: '12',
  user: 'annotator-1',
  fileId: '11',
  fileVersion: '12',
  fileName: 'Historical file',
  configuration: defaultTaxonomy
}

render(<App {...app_config}/>, document.getElementById('react-root'))
/*
function useRender (containerRef) {
  useEffect (()=>{
    const container = containerRef.current
    container.innerHTML = [
      "Echo’s <span> router is </span> based <span /> on radix tree, making route lookup really",
      " fast. It leverages sync pool to reuse memory and achieve zero",
      " dynamic memory allocation with no GC overhead.",
      " Routes can be registered by specifying HTTP method, path and ",
      " a matching handler. For example, code below registers a route ",
      "for method GET, path /hello and a handler which sends Hello, ",
      "World! HTTP response."
    ].join(' ')
    container.addEventListener ('mouseup', e=>handleSelection(container, e))
  }, [])
}

function handleSelection (container, selectionEvent) {
  const [selection, text] = processSelection(selectionEvent)

  if (selection == null) return

  const [start, end] = getSelection(container, selection)
  console.log(start, end)
}

function Container (props) {
  const useForceUpdate = () => useReducer(state => !state, false)[1];
  const forceUpdate = useForceUpdate();

  const containerRef = React.useRef()
  const selectorRef = React.useRef()
  useRender(containerRef)
  
  return <div>
    <div className="container" ref={containerRef}>
    l
    </div>
    <button onClick={forceUpdate}>Update</button>
    <div className="selector" ref={selectorRef}>
    </div>
  </div>
}
*/

