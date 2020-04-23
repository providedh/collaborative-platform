import React from 'react'
import PropTypes from 'prop-types'

export const AppContext = React.createContext(null)

export const WithAppContext = (props) => (
  <AppContext.Consumer>
    {context => React.cloneElement(props.children, { ...props, context }, null)}
  </AppContext.Consumer>
)

WithAppContext.propTypes = {
  children: PropTypes.element.isRequired
}
