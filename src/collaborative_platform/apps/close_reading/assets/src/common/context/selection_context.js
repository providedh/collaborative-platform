import React from 'react'
import PropTypes from 'prop-types'

export const SelectionContext = React.createContext(null)

export const WithSelectionContext = (props) => (
  <SelectionContext.Consumer>
    {context => React.cloneElement(props.children, { ...props, context }, null)}
  </SelectionContext.Consumer>
)

WithSelectionContext.propTypes = {
  children: PropTypes.element.isRequired
}
