import React from 'react';

export const AppContext = React.createContext(null);

export const WithAppContext = (props)=>(
	<AppContext.Consumer>
    	{context=>React.cloneElement(props.children, {...props, context}, null)}
	</AppContext.Consumer>
);