import React from 'react';

import AttributeDetails from './attributeDetails';

export default ({data})=>{

	let attributes = <h4>No attributes found for this entity</h4>;

	if(data.attributes.length > 0)
	attributes = data.attributes.map(
		attr=><AttributeDetails key={attr.name} tag={data.name} attribute={attr}/>);

	return(
		<li className="list-group-item onExpanded">
        	{attributes}              
		</li>);
};