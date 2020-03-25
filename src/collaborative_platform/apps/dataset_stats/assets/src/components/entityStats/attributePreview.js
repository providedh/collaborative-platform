import React from 'react';
export default ({attr})=>{
	const {name, distinct_values, trend_percentage, trend_value, coverage} = attr;

	return(<span className="attributeSummary">
        <b>{name}=</b>
        <div className="attributeStats rounded">
          	<span>{distinct_values} distinct values</span>
          	<span className="big">{trend_percentage}% with value '{trend_value}'</span>
          	<span className="">{coverage}% tags have it</span>
        </div>
    </span>);
}