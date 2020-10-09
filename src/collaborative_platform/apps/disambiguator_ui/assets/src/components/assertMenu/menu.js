import React, {useState} from 'react'
import PropTypes from 'prop-types'

import {API} from 'common/helpers'
import styles from './styles.module.css' // eslint-disable-line no-unused-vars

function onAction(
    id,
    accept,
    certainty,
    categories,
    projectId,
    setCertainty,
    setCategories,
    refresh) {
  const payload = {id, decision: accept}
  if (accept === true) {
    payload.certainty = certainty
    payload.categories = categories
  }

  API.updateUnification(projectId, {}, payload)
    .then(d => {
      refresh()
    })
    .catch(err => console.error('Failed to update unification '+id+' for project ' + projectId, err))

  setCertainty('medium')
  setCategories([])
}

export default function Menu ({projectId, refresh, focused, configuration}) {
  if (focused === null) {return ''}
  const [unifying, setUnifying] = useState(false)
  const [certainty, setCertainty] = useState('medium')
  const [categories, setCategories] = useState([])

  const menuCssClasses = [
    styles.menu,
    unifying === true ? styles.unifying : ''
  ].join(' ')

  const selectedValues = select => Array
    .from(select.options)
    .filter(o => o.selected === true)
    .map(o => o.value)

  return (<div className={menuCssClasses}>
    <div className={styles.container}>
      <ul className="list-group list-group-horizontal">
        <li className="list-group-item">
          <button
            type="button"
            onClick={() => onAction(
              focused.id,
              false,
              null,
              null,
              projectId,
              setCertainty,
              setCategories,
              refresh)}
            className="btn btn-outline-danger">Reject</button>
        </li>
        <li className="list-group-item">
          <b>Confidence</b><br/> {Math.trunc(+focused.degree)}%
        </li>
        <li className="list-group-item">
          <button
            type="button"
            onClick={() => setUnifying(true)}
            className="btn btn-outline-success">Unify</button>
        </li>
      </ul>
    </div>
    <div className={styles.acceptMenu}>
      <form>
        <div className="form-group">
          <label htmlFor="confidenceSelect">Confidence</label>
          <select
              id="confidenceSelect"
              onChange={e => setCertainty(e.target.value)}
              className="form-control"
              value={certainty}>
            <option value="very low">Very low</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="very high">Very high</option>
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="categorySelect">Category</label>
          <select
              multiple={true}
              id="inputState"
              onChange={e => setCategories(selectedValues(e.target))}
              className="form-control"
              value={categories}>
            {Object.keys(configuration.taxonomy).map(category => 
              <option key={category} value={category}>{category}</option>)}
          </select>
        </div>
      </form>
      <ul className="list-group list-group-horizontal">
        <li className="list-group-item">
          <button
            type="button"
            onClick={() => setUnifying(false)}
            className="btn btn-danger">Cancel</button>
        </li>
        <li className="list-group-item">
          <button
            type="button"
            onClick={() => {
              onAction(focused.id,
                true,
                certainty,
                categories,
                projectId,
                setCertainty,
                setCategories,
                refresh)
              setUnifying(false)
            }}
            className="btn btn-success">Unify</button>
        </li>
      </ul>
    </div>
    <hr/>
  </div>)
}

Menu.propTypes = {
  currentIndex: PropTypes.number,
  unifications: PropTypes.arrayOf(PropTypes.object),
}
